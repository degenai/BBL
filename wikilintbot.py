#!/usr/bin/env python3
"""wikilintbot — Lint the BBL card-node graph.

Modeled on the wikilint suite at ~/.claude/wiki/scripts/lint/. Protocol over
subagent: deterministic Python checks first; LLM judgment only where needed
(none in v1).

Scans cards/, sealed/, archive/, sealed_archive/ and reports structural,
tag, and inventory-consistency issues. Report-only — no auto-fix until the
findings catalog is validated.

Usage:
    python wikilintbot.py                       # run all checks
    python wikilintbot.py --only tier_confusion  # one check
    python wikilintbot.py --skip singleton_tags  # all but one
    python wikilintbot.py --report reports/wikilint_2026-05-07.md  # also write MD report
    python wikilintbot.py --stale-days 60       # tweak stale threshold
    python wikilintbot.py --quiet               # only print failures
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable, Iterable

# Force UTF-8 on Windows so the report's arrows and dashes don't choke cp1252.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


# --- Defaults ---

DEFAULT_CARDS_DIR = "cards"
DEFAULT_ARCHIVE_DIR = "archive"
DEFAULT_SEALED_DIR = "sealed"
DEFAULT_SEALED_ARCHIVE_DIR = "sealed_archive"
DEFAULT_STALE_DAYS = 60

REQUIRED_CARD_FIELDS = (
    "name", "game", "set", "collector_number", "rarity", "variance", "grade",
    "condition", "quantity", "held_for_lair", "tags_hub", "tags_filter",
    "average_cost_paid", "market_price", "date_added", "last_seen",
)
REQUIRED_SEALED_FIELDS = (
    "name", "game", "set", "sealed", "quantity", "average_cost_paid",
    "market_price", "date_added", "last_seen",
)

# Tags that must NEVER appear in tags_hub. Color-magic, mechanical taxonomy,
# compositional, structural, rarity, card-type. These are filter-tier — they
# combine with thematic tags but never anchor a Discrete Lair.
COLOR_MAGIC = {
    "blue-magic", "red-magic", "white-magic", "green-magic", "black-magic",
    "blue-mono", "red-mono", "white-mono", "green-mono", "black-mono",
    "multicolor", "multicolor-white-black", "multicolor-blue-red",
    "multicolor-red-green", "multicolor-green-white", "multicolor-white-blue",
    "multicolor-black-green", "multicolor-blue-black", "multicolor-red-white",
    "multicolor-green-blue", "multicolor-black-red",
}
COMPOSITION_TAGS = {
    "solo", "duo", "group", "crowd", "no-figure",
    "2-figures", "3-figures", "multiple-figures",
    "close-up", "mid-shot", "wide-shot", "wide",
    "scene-mode", "portrait-mode", "action-mode", "narrative-mode", "abstract-mode",
    "faces-left", "faces-right", "faces-forward", "faces-away",
    "forward-facing", "three-quarter-facing", "left-facing", "right-facing",
    "male-figure", "female-figure", "no-face",
}
RARITY_TYPE_TAGS = {
    "common", "uncommon", "rare", "mythic", "promo",
    "instant", "sorcery", "enchantment", "enchantment-aura", "land", "artifact",
    "foil", "holo", "non-holo",
}
# creature-* family is structural — flagged via prefix check, not enumerated.
KNOWN_FILTER_ONLY = COLOR_MAGIC | COMPOSITION_TAGS | RARITY_TYPE_TAGS

# Tags that genuinely look thematic and should be flagged if found in tags_filter.
# Conservative list — easy to extend.
KNOWN_HUB_THEMATIC = {
    "cat", "sunset", "pie", "cozy", "gothic", "service-worker", "labor",
    "villain", "comic-relief", "fire", "forest", "ocean", "ritual", "witch",
    "ghost", "spirit", "dragon", "knight", "wizard", "cleric", "soldier",
    "pegasus", "treefolk", "mushroom", "waterfall",
}


# --- Frontmatter parser (matches researchbot/csv2mdbot minimal format) ---

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip()
    return out


def parse_tag_list(raw: str) -> list[str]:
    """tags_hub / tags_filter is rendered as a JSON-style array literal."""
    raw = (raw or "").strip()
    if not raw or raw == "[]":
        return []
    try:
        v = json.loads(raw)
        if isinstance(v, list):
            return [str(x) for x in v]
    except json.JSONDecodeError:
        pass
    return []


# --- Card / Finding model ---

@dataclass
class Card:
    path: Path
    fm: dict
    text: str
    is_sealed: bool
    is_archived: bool

    @property
    def name(self) -> str:
        return self.fm.get("name", "")

    @property
    def quantity(self) -> int:
        try:
            return int(self.fm.get("quantity") or 0)
        except ValueError:
            return 0

    @property
    def held_for_lair(self) -> int:
        try:
            return int(self.fm.get("held_for_lair") or 0)
        except ValueError:
            return -1  # signal "non-numeric"

    @property
    def tags_hub(self) -> list[str]:
        return parse_tag_list(self.fm.get("tags_hub", ""))

    @property
    def tags_filter(self) -> list[str]:
        return parse_tag_list(self.fm.get("tags_filter", ""))


SEVERITIES = ("error", "warn", "info")


@dataclass
class Finding:
    check: str
    severity: str  # error | warn | info
    path: Path | None
    message: str

    def fmt(self) -> str:
        loc = f" {self.path}" if self.path else ""
        return f"[{self.severity}]{loc} — {self.message}"


# --- Loader ---

def _is_non_card_node(path: Path, fm: dict) -> bool:
    """Skip MDs that aren't inventory cards: hub concept pages (frontmatter
    `type: hub`), anything under an _underscore-prefixed directory inside
    cards/ (e.g. cards/_hubs/, cards/_images/). Mirrors csv2mdbot's same guard
    so the two scripts agree on what counts as inventory."""
    if fm.get("type") == "hub":
        return True
    for part in path.parts:
        if part.startswith("_"):
            return True
    return False


def load_cards(cards_dir: Path, sealed_dir: Path,
               archive_dir: Path, sealed_archive_dir: Path) -> list[Card]:
    """Walk all four dirs and return Card objects with parsed frontmatter.
    Hub concept pages (cards/_hubs/*.md with type: hub) are deliberately
    skipped — they're conceptual anchors, not inventory."""
    cards: list[Card] = []

    def walk(root: Path, is_sealed: bool, is_archived: bool):
        if not root.exists():
            return
        for p in root.rglob("*.md"):
            try:
                text = p.read_text(encoding="utf-8")
            except Exception as e:
                # Surface read failures as a separate sentinel finding-like Card
                # so downstream checks can detect them via empty fm.
                cards.append(Card(p, {"_read_error": str(e)}, "", is_sealed, is_archived))
                continue
            fm = parse_frontmatter(text)
            if _is_non_card_node(p, fm):
                continue
            cards.append(Card(p, fm, text, is_sealed, is_archived))

    walk(cards_dir, is_sealed=False, is_archived=False)
    walk(sealed_dir, is_sealed=True, is_archived=False)
    walk(archive_dir, is_sealed=False, is_archived=True)
    walk(sealed_archive_dir, is_sealed=True, is_archived=True)
    return cards


# --- Checks ---

KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def check_missing_frontmatter(cards: list[Card], **opts) -> list[Finding]:
    findings: list[Finding] = []
    for c in cards:
        if "_read_error" in c.fm:
            findings.append(Finding("missing_frontmatter", "error", c.path,
                                    f"could not read file: {c.fm['_read_error']}"))
            continue
        required = REQUIRED_SEALED_FIELDS if c.is_sealed else REQUIRED_CARD_FIELDS
        missing = [f for f in required if not c.fm.get(f) and c.fm.get(f) != "0"]
        # "0" is a valid value for held_for_lair, market_price, etc.
        # Filter false positives: empty string fields that are intentionally blank.
        missing = [m for m in missing if c.fm.get(m, None) is None]
        if missing:
            findings.append(Finding("missing_frontmatter", "warn", c.path,
                                    f"missing fields: {', '.join(missing)}"))
    return findings


def check_qty_sanity(cards: list[Card], **opts) -> list[Finding]:
    findings: list[Finding] = []
    for c in cards:
        if "_read_error" in c.fm:
            continue
        qty = c.quantity
        if not c.is_archived and qty == 0:
            findings.append(Finding("qty_sanity", "warn", c.path,
                                    "qty=0 in active dir (should be archived)"))
        if c.is_archived and qty > 0:
            findings.append(Finding("qty_sanity", "warn", c.path,
                                    f"qty={qty} in archive dir (should be reactivated)"))
    return findings


def check_sealed_misclassification(cards: list[Card], **opts) -> list[Finding]:
    findings: list[Finding] = []
    for c in cards:
        if c.is_sealed or "_read_error" in c.fm:
            continue
        cn = (c.fm.get("collector_number") or "").strip()
        rar = (c.fm.get("rarity") or "").strip()
        if not cn and not rar:
            findings.append(Finding("sealed_misclassification", "warn", c.path,
                                    "node in cards/ has empty collector_number AND rarity (probably sealed)"))
    return findings


def check_duplicate_nodes(cards: list[Card], **opts) -> list[Finding]:
    findings: list[Finding] = []
    keys: dict[tuple, list[Path]] = defaultdict(list)
    for c in cards:
        if c.is_sealed or "_read_error" in c.fm or c.is_archived:
            continue
        key = (
            c.fm.get("game", "").strip(),
            c.fm.get("set", "").strip(),
            c.fm.get("collector_number", "").strip(),
            c.fm.get("variance", "").strip() or "Normal",
            c.fm.get("grade", "").strip() or "Ungraded",
            c.fm.get("condition", "").strip() or "Near Mint",
        )
        keys[key].append(c.path)
    for key, paths in keys.items():
        if len(paths) > 1:
            findings.append(Finding("duplicate_nodes", "error", None,
                                    f"key {key} -> {len(paths)} files: " + ", ".join(str(p) for p in paths)))
    return findings


def check_held_for_lair_sanity(cards: list[Card], **opts) -> list[Finding]:
    findings: list[Finding] = []
    for c in cards:
        if "_read_error" in c.fm or c.is_sealed:
            continue
        h = c.held_for_lair
        if h == -1:
            findings.append(Finding("held_for_lair_sanity", "error", c.path,
                                    f"held_for_lair has non-numeric value: {c.fm.get('held_for_lair')!r}"))
            continue
        if h > c.quantity:
            findings.append(Finding("held_for_lair_sanity", "error", c.path,
                                    f"held_for_lair={h} exceeds quantity={c.quantity} (over-committed)"))
        if h < 0:
            findings.append(Finding("held_for_lair_sanity", "error", c.path,
                                    f"held_for_lair={h} is negative"))
    return findings


def check_stale_last_seen(cards: list[Card], stale_days: int = DEFAULT_STALE_DAYS,
                          **opts) -> list[Finding]:
    findings: list[Finding] = []
    cutoff = date.today() - timedelta(days=stale_days)
    for c in cards:
        if c.is_archived or "_read_error" in c.fm:
            continue
        ls = (c.fm.get("last_seen") or "").strip()
        if not ls:
            continue
        try:
            d = datetime.strptime(ls, "%Y-%m-%d").date()
        except ValueError:
            findings.append(Finding("stale_last_seen", "warn", c.path,
                                    f"last_seen unparseable: {ls!r}"))
            continue
        if d < cutoff:
            findings.append(Finding("stale_last_seen", "info", c.path,
                                    f"last_seen={ls} ({(date.today()-d).days} days ago, threshold {stale_days})"))
    return findings


def check_missing_reference_image(cards: list[Card], **opts) -> list[Finding]:
    """If reference_image points at a path, the file should exist."""
    findings: list[Finding] = []
    for c in cards:
        if c.is_sealed or "_read_error" in c.fm or c.is_archived:
            continue
        ri = (c.fm.get("reference_image") or "").strip()
        if not ri:
            continue
        if ri.startswith("http"):
            continue  # remote URL, can't verify cheaply
        # Project-relative path; resolve against project root (cwd).
        p = Path(ri)
        if not p.exists():
            findings.append(Finding("missing_reference_image", "error", c.path,
                                    f"reference_image -> {ri} but file is missing"))
    return findings


def check_missing_tags(cards: list[Card], **opts) -> list[Finding]:
    """Card has reference_image but both tag tiers empty -> vision pass didn't complete."""
    findings: list[Finding] = []
    for c in cards:
        if c.is_sealed or "_read_error" in c.fm or c.is_archived:
            continue
        ri = (c.fm.get("reference_image") or "").strip()
        if not ri:
            continue
        amc = (c.fm.get("art_match_confidence") or "").strip()
        if amc in ("low", "none"):
            continue  # deferred to manual review by design
        if not c.tags_hub and not c.tags_filter:
            findings.append(Finding("missing_tags", "info", c.path,
                                    "reference_image set but tags_hub and tags_filter both empty (vision pass pending or failed)"))
    return findings


def check_tier_confusion(cards: list[Card], **opts) -> list[Finding]:
    findings: list[Finding] = []
    for c in cards:
        if c.is_sealed or "_read_error" in c.fm:
            continue
        # Hub-tier offenders: filter-only tags found in tags_hub
        for t in c.tags_hub:
            if t in KNOWN_FILTER_ONLY:
                findings.append(Finding("tier_confusion", "warn", c.path,
                                        f"tags_hub contains filter-tier tag '{t}' -> move to tags_filter"))
                continue
            if t.startswith("creature-"):
                findings.append(Finding("tier_confusion", "warn", c.path,
                                        f"tags_hub contains creature-type tag '{t}' -> move to tags_filter"))
        # Filter-tier offenders: known thematic tags in tags_filter
        for t in c.tags_filter:
            if t in KNOWN_HUB_THEMATIC:
                findings.append(Finding("tier_confusion", "warn", c.path,
                                        f"tags_filter contains thematic tag '{t}' -> move to tags_hub"))
    return findings


def check_format_drift(cards: list[Card], **opts) -> list[Finding]:
    findings: list[Finding] = []
    for c in cards:
        if c.is_sealed or "_read_error" in c.fm:
            continue
        for tier_name, tags in (("tags_hub", c.tags_hub), ("tags_filter", c.tags_filter)):
            for t in tags:
                if not KEBAB_RE.match(t):
                    findings.append(Finding("format_drift", "warn", c.path,
                                            f"{tier_name} contains non-kebab-case tag '{t}'"))
    return findings


def check_intra_tier_duplicates(cards: list[Card], **opts) -> list[Finding]:
    findings: list[Finding] = []
    for c in cards:
        if c.is_sealed or "_read_error" in c.fm:
            continue
        for tier_name, tags in (("tags_hub", c.tags_hub), ("tags_filter", c.tags_filter)):
            counts = Counter(tags)
            dupes = [t for t, n in counts.items() if n > 1]
            if dupes:
                findings.append(Finding("intra_tier_duplicates", "warn", c.path,
                                        f"{tier_name} has duplicate(s): {', '.join(dupes)}"))
    return findings


def check_cross_tier_duplicates(cards: list[Card], **opts) -> list[Finding]:
    findings: list[Finding] = []
    for c in cards:
        if c.is_sealed or "_read_error" in c.fm:
            continue
        both = set(c.tags_hub) & set(c.tags_filter)
        if both:
            findings.append(Finding("cross_tier_duplicates", "warn", c.path,
                                    f"tag(s) in both tags_hub AND tags_filter: {', '.join(sorted(both))}"))
    return findings


def check_singleton_tags(cards: list[Card], **opts) -> list[Finding]:
    """Tags used by exactly one card. Either typo or too-narrow — flag for review."""
    findings: list[Finding] = []
    hub_counts: Counter = Counter()
    filter_counts: Counter = Counter()
    for c in cards:
        if c.is_sealed or "_read_error" in c.fm or c.is_archived:
            continue
        hub_counts.update(c.tags_hub)
        filter_counts.update(c.tags_filter)
    singletons_hub = {t for t, n in hub_counts.items() if n == 1}
    singletons_filter = {t for t, n in filter_counts.items() if n == 1}
    # Report aggregated, not per-card — too noisy otherwise.
    if singletons_hub:
        findings.append(Finding("singleton_tags", "info", None,
                                f"{len(singletons_hub)} singleton tags_hub tags (used by exactly 1 card): "
                                + ", ".join(sorted(singletons_hub)[:30])
                                + (" ..." if len(singletons_hub) > 30 else "")))
    if singletons_filter:
        findings.append(Finding("singleton_tags", "info", None,
                                f"{len(singletons_filter)} singleton tags_filter tags: "
                                + ", ".join(sorted(singletons_filter)[:30])
                                + (" ..." if len(singletons_filter) > 30 else "")))
    return findings


# NOTE: removed `check_vocabulary_drift` (singular/plural collapse).
# Plural and singular forms can carry distinct visual content — `sword` (one
# blade) vs `swords` (a rack of them) anchor different lairs. Collapsing them
# is a synonym/semantics decision, not a string-edit-distance one. Pushed to
# the Phase 5 janitor pass, which will reassess the populated tag graph
# holistically (true synonyms like cat/feline, redundant pairs, hub<->filter
# tier swaps). See subagents.md.


# --- Registry ---

CHECKS: dict[str, Callable[..., list[Finding]]] = {
    # structural
    "missing_frontmatter": check_missing_frontmatter,
    "qty_sanity": check_qty_sanity,
    "sealed_misclassification": check_sealed_misclassification,
    "duplicate_nodes": check_duplicate_nodes,
    "held_for_lair_sanity": check_held_for_lair_sanity,
    "stale_last_seen": check_stale_last_seen,
    "missing_reference_image": check_missing_reference_image,
    # tags
    "missing_tags": check_missing_tags,
    "tier_confusion": check_tier_confusion,
    "format_drift": check_format_drift,
    "intra_tier_duplicates": check_intra_tier_duplicates,
    "cross_tier_duplicates": check_cross_tier_duplicates,
    "singleton_tags": check_singleton_tags,
}


# --- Fixes (conservative — only the well-defined, unambiguous transforms) ---

def _render_tag_list(tags: list[str]) -> str:
    if not tags:
        return "[]"
    safe = [str(t).replace('"', '\\"') for t in tags]
    return "[" + ", ".join(f'"{t}"' for t in safe) + "]"


def _replace_fm_field(text: str, field: str, value: str) -> str:
    """Replace `field: ...` in frontmatter; matches the format used by researchbot/csv2mdbot."""
    pattern = rf"^{re.escape(field)}:.*$"
    if re.search(pattern, text, flags=re.MULTILINE):
        return re.sub(pattern, f"{field}: {value}", text, count=1, flags=re.MULTILINE)
    # Field absent — insert before closing --- of frontmatter.
    m = FRONTMATTER_RE.match(text)
    if not m:
        return text
    fm_end = m.end(1)
    return text[:fm_end] + f"\n{field}: {value}" + text[fm_end:]


def _is_filter_tier(tag: str) -> bool:
    return tag in KNOWN_FILTER_ONLY or tag.startswith("creature-")


def fix_card_tags(c: Card, dry_run: bool = False) -> tuple[bool, list[str]]:
    """Apply tier_confusion + cross_tier_duplicates fixes to one card.
    Returns (changed?, action_log)."""
    actions: list[str] = []
    hub = list(c.tags_hub)
    flt = list(c.tags_filter)

    # 1. Move filter-tier tags from hub to filter.
    moved_to_filter: list[str] = []
    new_hub: list[str] = []
    for t in hub:
        if _is_filter_tier(t):
            moved_to_filter.append(t)
            if t not in flt:
                flt.append(t)
        else:
            new_hub.append(t)
    if moved_to_filter:
        actions.append(f"moved {len(moved_to_filter)} tag(s) hub->filter: {', '.join(moved_to_filter)}")
    hub = new_hub

    # 2. Resolve cross-tier dupes. Filter-tier wins for filter-tier tags; otherwise hub wins.
    cross = set(hub) & set(flt)
    for t in cross:
        if _is_filter_tier(t):
            hub = [x for x in hub if x != t]
            actions.append(f"cross-tier dupe '{t}' resolved -> filter-only")
        else:
            flt = [x for x in flt if x != t]
            actions.append(f"cross-tier dupe '{t}' resolved -> hub-only")

    # 3. Dedupe within each tier, preserving order.
    hub_dedup = list(dict.fromkeys(hub))
    flt_dedup = list(dict.fromkeys(flt))
    if len(hub_dedup) != len(hub):
        actions.append(f"removed {len(hub) - len(hub_dedup)} intra-tier dupe(s) from tags_hub")
    if len(flt_dedup) != len(flt):
        actions.append(f"removed {len(flt) - len(flt_dedup)} intra-tier dupe(s) from tags_filter")
    hub, flt = hub_dedup, flt_dedup

    if not actions:
        return False, []

    if not dry_run:
        text = c.text
        text = _replace_fm_field(text, "tags_hub", _render_tag_list(hub))
        text = _replace_fm_field(text, "tags_filter", _render_tag_list(flt))
        c.path.write_text(text, encoding="utf-8")
    return True, actions


def apply_fixes(cards: list[Card], dry_run: bool) -> int:
    fixed = 0
    for c in cards:
        if c.is_sealed or "_read_error" in c.fm or c.is_archived:
            continue
        changed, actions = fix_card_tags(c, dry_run=dry_run)
        if changed:
            fixed += 1
            label = "[dry-run] would fix" if dry_run else "fixed"
            print(f"  {label} {c.path}")
            for a in actions:
                print(f"    - {a}")
    return fixed


# --- Reporting ---

def print_section(name: str, findings: list[Finding], quiet: bool = False) -> None:
    if not findings:
        if not quiet:
            print(f"  {name}: clean")
        return
    by_sev = Counter(f.severity for f in findings)
    bits = " / ".join(f"{by_sev[s]} {s}" for s in SEVERITIES if by_sev[s])
    print(f"  {name}: {len(findings)} ({bits})")
    for f in findings[:50]:
        print(f"    {f.fmt()}")
    if len(findings) > 50:
        print(f"    ... +{len(findings) - 50} more")


def write_md_report(report_path: Path, all_findings: dict[str, list[Finding]],
                    cards: list[Card]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# wikilintbot report — {date.today().isoformat()}",
        "",
        f"Scanned {len(cards)} files across cards/, sealed/, archive/, sealed_archive/.",
        "",
    ]
    total = sum(len(v) for v in all_findings.values())
    lines.append(f"**Total findings: {total}**")
    lines.append("")
    for check, findings in all_findings.items():
        if not findings:
            continue
        lines.append(f"## {check} ({len(findings)})")
        lines.append("")
        for f in findings:
            loc = f" `{f.path}`" if f.path else ""
            lines.append(f"- **[{f.severity}]**{loc} — {f.message}")
        lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


# --- Main ---

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cards-dir", type=Path, default=Path(DEFAULT_CARDS_DIR))
    ap.add_argument("--archive-dir", type=Path, default=Path(DEFAULT_ARCHIVE_DIR))
    ap.add_argument("--sealed-dir", type=Path, default=Path(DEFAULT_SEALED_DIR))
    ap.add_argument("--sealed-archive-dir", type=Path, default=Path(DEFAULT_SEALED_ARCHIVE_DIR))
    ap.add_argument("--only", nargs="+", choices=CHECKS.keys(),
                    help="Run only these checks")
    ap.add_argument("--skip", nargs="+", choices=CHECKS.keys(),
                    help="Skip these checks")
    ap.add_argument("--report", type=Path, default=None,
                    help="Also write a Markdown report at this path")
    ap.add_argument("--stale-days", type=int, default=DEFAULT_STALE_DAYS,
                    help=f"Days before last_seen counts as stale (default {DEFAULT_STALE_DAYS})")
    ap.add_argument("--quiet", action="store_true",
                    help="Suppress 'check: clean' lines, only print failures")
    ap.add_argument("--fix", action="store_true",
                    help="Apply safe auto-fixes for tier_confusion + cross_tier_duplicates "
                         "+ intra_tier_duplicates. Other findings remain report-only.")
    ap.add_argument("--fix-dry-run", action="store_true",
                    help="Show what --fix would change without writing.")
    args = ap.parse_args()

    if not args.cards_dir.exists():
        print(f"ERROR: cards dir not found: {args.cards_dir}", file=sys.stderr)
        sys.exit(1)

    cards = load_cards(args.cards_dir, args.sealed_dir,
                       args.archive_dir, args.sealed_archive_dir)
    print(f"Scanning {len(cards)} files\n")

    to_run = list(CHECKS.keys())
    if args.only:
        to_run = list(args.only)
    elif args.skip:
        to_run = [c for c in to_run if c not in args.skip]

    all_findings: dict[str, list[Finding]] = {}
    opts = {"stale_days": args.stale_days}
    for name in to_run:
        check = CHECKS[name]
        try:
            findings = check(cards, **opts)
        except Exception as e:
            findings = [Finding(name, "error", None, f"check raised: {e}")]
        all_findings[name] = findings
        print_section(name, findings, quiet=args.quiet)

    total = sum(len(v) for v in all_findings.values())
    by_sev = Counter()
    for v in all_findings.values():
        by_sev.update(f.severity for f in v)

    print()
    print("=" * 50)
    print(f"Total findings: {total}", end="")
    if total:
        bits = ", ".join(f"{by_sev[s]} {s}" for s in SEVERITIES if by_sev[s])
        print(f"  ({bits})")
    else:
        print()
        print("Graph is clean.")

    if args.report:
        write_md_report(args.report, all_findings, cards)
        print(f"Wrote Markdown report: {args.report}")

    if args.fix or args.fix_dry_run:
        print()
        print("Applying safe auto-fixes (tier_confusion + cross_tier_duplicates + intra_tier_duplicates):")
        n = apply_fixes(cards, dry_run=args.fix_dry_run)
        verb = "would fix" if args.fix_dry_run else "fixed"
        print(f"  {verb} {n} card(s)")

    # Exit non-zero if any errors (warnings + info don't fail the run).
    sys.exit(1 if by_sev.get("error", 0) else 0)


if __name__ == "__main__":
    main()
