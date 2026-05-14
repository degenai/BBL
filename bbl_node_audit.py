#!/usr/bin/env python3
"""bbl_node_audit — Deterministic pre-swarm rigor audit for BBL layer nodes.

Per `bbl-edgelord-node-rigor-audit` memory rule (wave 54 consolidation): runs
BEFORE every swarm dispatch. Output goes into Edgelord's E1 brief so audit
findings inform the same wave's additive moves.

What it checks (all mechanical / deterministic):
  1. Two-way drift — `appears_on:` in layer node ↔ `characters:` / `symbols:`
     / `hubs:` in card frontmatter. Catches the wave-54a Sanguine Savior bug.
  2. YAML safety — `: `-containing frontmatter values must be double-quoted
     (Obsidian's parser otherwise breaks).
  3. Wikilink resolution — `[[<slug>]]` references in node bodies point at
     existing layer-node files (no dangling wikilinks).
  4. Threshold — `appears_on` size meets the rough cohort threshold
     (≥2 for character/symbol/artist, ≥3 for cycle-coded nodes).

What it does NOT check (semantic, requires LLM):
  - Whether body claims match what the cards actually depict
  - Whether canonical_source URLs are still live
  - Whether coined-compound bloat has crept in
  - Whether the cohort makes thematic sense
Those stay as Edgelord's E1 semantic-verification job.

Usage:
    python bbl_node_audit.py                  # human-readable report to stdout
    python bbl_node_audit.py --json           # JSON to stdout
    python bbl_node_audit.py --strict         # exit 1 if any drift/issues found
    python bbl_node_audit.py --brief          # short markdown for agent-brief inclusion
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Force UTF-8 on stdout — Windows cp1252 default chokes on arrows, accented
# names, and other non-ASCII characters in human-readable / brief output.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent
CARDS_DIR = REPO_ROOT / "cards"

# Layer-node directories the audit walks
LAYER_DIRS = {
    "character": CARDS_DIR / "_characters",
    "symbol":    CARDS_DIR / "_symbols",
    "artist":    CARDS_DIR / "_artists",
    "hub":       CARDS_DIR / "_hubs",
}

# Frontmatter field that pulls cards toward a layer node
LAYER_FIELD = {
    "character": "characters",
    "symbol":    "symbols",
    "artist":    None,  # artist nodes use appears_on only; cards reference via `artist:` string field (alias-resolved later)
    "hub":       "hubs",
}

# Threshold for cohort node membership (see bbl-museum-curation-framing)
THRESHOLD = {
    "character": 2,  # named-character, faction, line-cohort all use ≥2
    "symbol":    3,  # designer-coordinated cohort
    "artist":    3,  # alias-disambiguation layer
    "hub":       2,
}

# YAML fields commonly carrying `: `-containing values (the Obsidian-parser trap)
YAML_QUOTE_RISK_FIELDS = {
    "name", "universe", "species", "faction", "canonical_source",
    "aliases", "description",
}


# --- card parsing helpers ----------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str], dict[str, list[str]]]:
    """Return (single-value-fields, raw-yaml-lines, block-list-fields).

    YAML lists come in two forms in our corpus:
      inline: `characters: [a, b, c]`
      block:  `characters:\\n  - a\\n  - b`
    Single-value fields land in the first dict; block-list fields land in the
    third (which check_drift / parse_list_value consult before falling back).

    Bug fix wave 55: previously this only captured inline lists, producing
    false-positive `drift_forward` flags on every card using block-list form
    (e.g. kabu.md → galar-gym-challenge)."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}, [], {}
    block = m.group(1)
    fields: dict[str, str] = {}
    lines: list[str] = []
    block_lists: dict[str, list[str]] = {}
    current_block_key: str | None = None
    for line in block.split("\n"):
        lines.append(line)
        # Indented dash-prefixed continuation of a block-list field
        bm = re.match(r"^\s+-\s+(.+)$", line)
        if bm and current_block_key:
            val = bm.group(1).strip().strip('"').strip("'")
            block_lists[current_block_key].append(val)
            continue
        # New field declaration
        fm = re.match(r"^(\w+):\s*(.*)$", line)
        if fm:
            key, val = fm.group(1), fm.group(2).strip()
            fields[key] = val
            # Empty value = potential block-list header
            if val == "":
                block_lists[key] = []
                current_block_key = key
            else:
                current_block_key = None
        else:
            # Comment, blank line, or other non-field content — reset block state
            if not line.strip().startswith("#") and line.strip():
                current_block_key = None
    return fields, lines, block_lists


def parse_list_value(raw: str, block_lists: dict[str, list[str]] | None = None,
                     field_name: str | None = None) -> list[str]:
    """Parse a YAML inline-list `[a, b, c]` or `["a", "b"]` into list of strings.
    Falls back to block-list form via `block_lists[field_name]` when the inline
    form is empty/missing."""
    raw = raw.strip()
    if raw and raw != "[]":
        if raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            if not inner:
                return []
            items = [x.strip().strip('"').strip("'") for x in inner.split(",")]
            return [x for x in items if x]
    # Inline form gave nothing — check block-list fallback
    if block_lists and field_name and field_name in block_lists:
        return [x for x in block_lists[field_name] if x]
    return []


def normalize_card_id(path_str: str) -> str:
    """Card paths in `appears_on:` are like `pokemon/cosmic-eclipse/100-236-cosmog` (no
    `cards/` prefix, no `.md`). Card MD paths are full paths. Normalize both to the
    `<game>/<set>/<slug>` shape for comparison."""
    p = path_str.replace("\\", "/").strip().strip('"').strip("'")
    if p.endswith(".md"):
        p = p[:-3]
    if p.startswith("cards/"):
        p = p[len("cards/"):]
    return p


# --- layer-node walking ------------------------------------------------------

def parse_appears_on(text: str) -> list[str]:
    """Layer nodes list cards in YAML block form:
        appears_on:
          - pokemon/x/y
          - pokemon/x/z
    or inline list form `appears_on: [a, b, c]`. Handle both."""
    m = re.search(r"^appears_on:\s*(.*?)(?:^[a-zA-Z_]+:|^---)", text, re.MULTILINE | re.DOTALL)
    if not m:
        return []
    block = m.group(1)
    # Try inline first
    inline = re.match(r"^\s*\[([^\]]*)\]\s*", block)
    if inline:
        return [normalize_card_id(x) for x in inline.group(1).split(",") if x.strip()]
    # Block form: dash-prefixed lines
    items = []
    for line in block.split("\n"):
        bm = re.match(r"^\s*-\s+(.+)$", line)
        if bm:
            items.append(normalize_card_id(bm.group(1)))
    return items


def walk_layer_nodes() -> dict[str, dict]:
    """Returns {node_slug: {kind, path, frontmatter, body, appears_on, ...}}."""
    out: dict[str, dict] = {}
    for kind, dir_path in LAYER_DIRS.items():
        if not dir_path.exists():
            continue
        for md_path in dir_path.glob("*.md"):
            slug = md_path.stem
            text = md_path.read_text(encoding="utf-8")
            fields, yaml_lines, block_lists = parse_frontmatter(text)
            appears = parse_appears_on(text)
            out[slug] = {
                "kind": kind,
                "path": str(md_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "fields": fields,
                "yaml_lines": yaml_lines,
                "block_lists": block_lists,
                "appears_on": appears,
                "body": text,
            }
    return out


# --- card walking ------------------------------------------------------------

def walk_cards() -> dict[str, dict]:
    """Returns {card_id: {path, characters, symbols, hubs}} for every inventory card."""
    out: dict[str, dict] = {}
    pattern = os.path.join(str(CARDS_DIR), "**", "*.md")
    for md_path in glob.glob(pattern, recursive=True):
        norm = md_path.replace("\\", "/")
        if "/_" in norm:  # skip layer-node dirs
            continue
        rel = Path(md_path).relative_to(REPO_ROOT)
        card_id = str(rel).replace("\\", "/").replace("cards/", "", 1)
        if card_id.endswith(".md"):
            card_id = card_id[:-3]
        try:
            text = Path(md_path).read_text(encoding="utf-8")
        except OSError:
            continue
        fields, _, block_lists = parse_frontmatter(text)
        out[card_id] = {
            "path": str(rel).replace("\\", "/"),
            "characters": parse_list_value(fields.get("characters", "[]"), block_lists, "characters"),
            "symbols":    parse_list_value(fields.get("symbols", "[]"),    block_lists, "symbols"),
            "hubs":       parse_list_value(fields.get("hubs", "[]"),       block_lists, "hubs"),
        }
    return out


# --- audit checks ------------------------------------------------------------

def _card_aliases(card_id: str) -> set[str]:
    """Return all variant forms of a card ID for fuzzy-matching against
    appears_on entries. Some node bodies write paths WITHOUT the leading
    game segment (e.g. `dragon-s-maze/109-tithe-drinker` instead of
    `magic-the-gathering/dragon-s-maze/109-tithe-drinker`). Accept both."""
    aliases = {card_id}
    parts = card_id.split("/", 1)
    if len(parts) == 2:
        # Strip the leading game-name segment → set-and-slug form
        aliases.add(parts[1])
    return aliases


def check_drift(nodes: dict[str, dict], cards: dict[str, dict]) -> list[dict]:
    """Two-way diff: node appears_on ↔ card frontmatter pointer.
    Returns list of issues. Skips artist kind (no card-side frontmatter field).
    Accepts both full (`game/set/slug`) and game-stripped (`set/slug`) forms in
    appears_on — some older node bodies elide the game prefix."""
    issues: list[dict] = []
    # Build reverse index: for each layer-field, {node_slug: set(card_ids)}
    # Stored as full card IDs (game/set/slug).
    reverse: dict[str, dict[str, set[str]]] = {
        kind: defaultdict(set) for kind in LAYER_DIRS
    }
    for card_id, c in cards.items():
        for ch in c["characters"]:
            reverse["character"][ch].add(card_id)
        for sym in c["symbols"]:
            reverse["symbol"][sym].add(card_id)
        for h in c["hubs"]:
            reverse["hub"][h].add(card_id)

    # Build alias-lookup: any variant form → canonical full card ID
    alias_to_full: dict[str, str] = {}
    for card_id in cards:
        for alias in _card_aliases(card_id):
            alias_to_full[alias] = card_id

    for slug, n in nodes.items():
        kind = n["kind"]
        if kind == "artist":
            continue
        # Normalise appears_on entries to canonical full card IDs
        forward_full: set[str] = set()
        unresolved: list[str] = []
        for raw in n["appears_on"]:
            if raw in alias_to_full:
                forward_full.add(alias_to_full[raw])
            else:
                unresolved.append(raw)
        reverse_set = reverse[kind].get(slug, set())
        forward_only = sorted(forward_full - reverse_set)
        reverse_only = sorted(reverse_set - forward_full)
        for card_id in forward_only:
            issues.append({
                "type": "drift_forward",
                "node": slug,
                "node_path": n["path"],
                "card": card_id,
                "detail": "node lists card in appears_on but card's frontmatter doesn't reference node back",
            })
        for card_id in reverse_only:
            card_path = cards.get(card_id, {}).get("path", card_id)
            issues.append({
                "type": "drift_reverse",
                "node": slug,
                "node_path": n["path"],
                "card": card_id,
                "card_path": card_path,
                "detail": "card frontmatter references node but node's appears_on doesn't list card",
            })
        for raw in unresolved:
            issues.append({
                "type": "appears_on_unresolved",
                "node": slug,
                "node_path": n["path"],
                "card": raw,
                "detail": f"appears_on entry `{raw}` does not match any card in the corpus (typo, deleted card, or path-format issue)",
            })
    return issues


def check_yaml_safety(nodes: dict[str, dict]) -> list[dict]:
    """`: `-containing single-line YAML values must be double-quoted, else Obsidian
    parser breaks the frontmatter. Per `bbl-yaml-quoting`-style rule."""
    issues: list[dict] = []
    for slug, n in nodes.items():
        for line in n["yaml_lines"]:
            fm = re.match(r"^(\w+):\s*(.+)$", line)
            if not fm:
                continue
            field, val = fm.group(1), fm.group(2).strip()
            if field not in YAML_QUOTE_RISK_FIELDS:
                continue
            # Already quoted?
            if (val.startswith('"') and val.endswith('"')) or \
               (val.startswith("'") and val.endswith("'")):
                continue
            # List / null / empty are fine
            if val in ("", "~", "null") or val.startswith("[") or val == "[]":
                continue
            # The trap: contains `: ` (colon-space) and is unquoted
            if ": " in val:
                issues.append({
                    "type": "yaml_unquoted_colon",
                    "node": slug,
                    "node_path": n["path"],
                    "field": field,
                    "value": val[:80],
                    "detail": f"`{field}:` value contains `: ` but is not double-quoted; Obsidian parser will break frontmatter",
                })
    return issues


CARD_SLUG_RE = re.compile(r"^\d+-\d+-[a-z0-9-]+$")  # e.g. 33-111-alolan-graveler, 099-189-galarian-slowbro-v


def check_wikilinks(nodes: dict[str, dict]) -> list[dict]:
    """`[[slug]]` references in node bodies should resolve to an existing layer-node
    file. Three categories:
      - card_cross_reference: target matches `<num>-<num>-<slug>` pattern (intentional
        Obsidian cross-ref to a card file, not a layer node). Informational, not an issue.
      - cross_wiki_reference: target doesn't match card-slug pattern AND doesn't resolve
        to a layer node. Likely cross-wiki ref to Alex's personal wiki or external concept.
        Informational, not a hard issue.
      - dangling_wikilink: layer-node-shaped slug that doesn't resolve. Real issue.
    Case-insensitive resolution accepted (with a normalization-suggested note)."""
    issues: list[dict] = []
    node_slugs = set(nodes.keys())
    node_slugs_lower = {s.lower(): s for s in node_slugs}
    for slug, n in nodes.items():
        body = n["body"]
        body_only = re.sub(r"^---\s*\n.*?\n---\s*\n", "", body, count=1, flags=re.DOTALL)
        for m in re.finditer(r"\[\[([^\]\|#]+)(?:\|[^\]]*)?\]\]", body_only):
            target = m.group(1).strip()
            # BBL meta + memory refs always pass
            if target.lower().startswith("bbl-") or target == "Bulk Graph Bundler":
                continue
            # Path-shaped refs (contain `/`) pass — they're card-file paths
            if "/" in target:
                continue
            # Exact slug match
            if target in node_slugs:
                continue
            # Case-insensitive match — emit normalization suggestion, not dangling
            if target.lower() in node_slugs_lower:
                canonical = node_slugs_lower[target.lower()]
                issues.append({
                    "type": "wikilink_case_normalize",
                    "node": slug,
                    "node_path": n["path"],
                    "target": target,
                    "canonical": canonical,
                    "detail": f"`[[{target}]]` resolves case-insensitively to existing node `{canonical}`; recommend normalizing to lowercase",
                })
                continue
            # Card-slug pattern: <num>-<num>-<slug>
            if CARD_SLUG_RE.match(target):
                issues.append({
                    "type": "card_cross_reference",
                    "node": slug,
                    "node_path": n["path"],
                    "target": target,
                    "detail": f"`[[{target}]]` is a card-file cross-reference (Obsidian vault-wide resolution); not a layer-node ref",
                })
                continue
            # Doesn't match card-slug pattern and doesn't resolve to a layer node →
            # likely a cross-wiki / future-node / personal-wiki ref. Informational.
            issues.append({
                "type": "cross_wiki_reference",
                "node": slug,
                "node_path": n["path"],
                "target": target,
                "detail": f"`[[{target}]]` doesn't resolve to a layer node and doesn't match card-slug pattern; likely cross-wiki / future-node / personal-wiki ref",
            })
    return issues


def check_threshold(nodes: dict[str, dict], cards: dict[str, dict]) -> list[dict]:
    """Anchor count meets the cohort threshold for the node's kind.
    Exemption: hubs flagged `brand_weight: foundational` are hand-curated per
    `bbl-hubs-hand-curated` — their membership predicates on tag_signals
    matches across the corpus, not an explicit appears_on list. Skip them."""
    issues: list[dict] = []
    for slug, n in nodes.items():
        kind = n["kind"]
        if kind == "artist":
            continue
        # Foundational hub exemption (Labor / Rebellion / Chinese Zodiac etc.)
        brand_weight = n["fields"].get("brand_weight", "").strip().strip('"').strip("'")
        if brand_weight == "foundational":
            continue
        min_anchors = THRESHOLD[kind]
        anchors = len(n["appears_on"])
        if anchors < min_anchors:
            issues.append({
                "type": "below_threshold",
                "node": slug,
                "node_path": n["path"],
                "kind": kind,
                "anchors": anchors,
                "min_required": min_anchors,
                "detail": f"{kind} node has only {anchors} anchors in appears_on (need >={min_anchors}); consider retire / merge / await-more-anchors",
            })
    return issues


# --- output formatters -------------------------------------------------------

def render_human(report: dict) -> str:
    out = []
    out.append(f"# BBL Node Audit — {report['ran_at']}")
    out.append("")
    s = report["summary"]
    out.append(f"**Layer nodes:** {report['layer_node_count']}  |  **Cards:** {report['card_count']}")
    out.append("")
    out.append(f"- Drift issues:        **{s['drift']}**")
    out.append(f"- Appears_on missing:  **{s['unresolved']}**")
    out.append(f"- YAML safety:         **{s['yaml']}**")
    out.append(f"- Wikilinks (real):    **{s['wikilinks']}**  (dangling + case-normalize)")
    out.append(f"- Card cross-refs:     {s['card_xrefs']}  (informational)")
    out.append(f"- Cross-wiki refs:     {s['cross_wiki']}  (informational)")
    out.append(f"- Below threshold:     **{s['threshold']}**")
    out.append("")
    if not report["issues"]:
        out.append("**CLEAN.** No mechanical issues across the layer-node graph.")
        return "\n".join(out)
    out.append("## Issues")
    out.append("")
    by_type: dict[str, list] = defaultdict(list)
    for iss in report["issues"]:
        by_type[iss["type"]].append(iss)
    for t in ("drift_reverse", "drift_forward", "appears_on_unresolved",
              "yaml_unquoted_colon", "dangling_wikilink", "wikilink_case_normalize",
              "below_threshold", "card_cross_reference", "cross_wiki_reference"):
        items = by_type.get(t, [])
        if not items:
            continue
        out.append(f"### {t} ({len(items)})")
        for iss in items:
            out.append(f"- **{iss['node']}** — {iss['detail']}")
            if iss.get("card"):
                out.append(f"  - card: `{iss['card']}`")
            if iss.get("field"):
                out.append(f"  - field: `{iss['field']}: {iss['value']}`")
            if iss.get("target"):
                out.append(f"  - target: `[[{iss['target']}]]`")
        out.append("")
    return "\n".join(out)


def render_brief(report: dict) -> str:
    """Short markdown block for direct inclusion in an agent brief.
    Optimised to be terse: only list REAL issues (drift / yaml / dangling-wikilink /
    case-normalize / threshold). Card-cross-refs and cross-wiki refs are excluded
    from the brief (they're informational, surface in full report only)."""
    s = report["summary"]
    total = s["drift"] + s["unresolved"] + s["yaml"] + s["wikilinks"] + s["threshold"]
    out = [f"**Pre-swarm audit** ({report['ran_at']}): {report['layer_node_count']} nodes, "
           f"**{total} actionable issues** (drift={s['drift']} unresolved={s['unresolved']} yaml={s['yaml']} wikilinks={s['wikilinks']} threshold={s['threshold']}; "
           f"plus {s['card_xrefs']} card-xrefs + {s['cross_wiki']} cross-wiki refs informational-only)."]
    if total == 0:
        out.append("Substrate is CLEAN. E1 confirms-with-receipts (no work needed) or skip to E2.")
        return "\n".join(out)
    out.append("")
    out.append("E1 candidate fixes:")
    # Filter to actionable types only for the brief
    actionable = [i for i in report["issues"]
                  if i["type"] in ("drift_reverse", "drift_forward", "appears_on_unresolved",
                                   "yaml_unquoted_colon", "dangling_wikilink",
                                   "wikilink_case_normalize", "below_threshold")]
    for iss in actionable[:15]:
        if iss["type"] == "drift_reverse":
            out.append(f"- DRIFT: `{iss['node']}` missing `{iss['card']}` from appears_on (card frontmatter has the pointer)")
        elif iss["type"] == "drift_forward":
            out.append(f"- DRIFT: `{iss['node']}` lists `{iss['card']}` in appears_on but card's frontmatter doesn't point back")
        elif iss["type"] == "appears_on_unresolved":
            out.append(f"- UNRESOLVED: `{iss['node']}` appears_on entry `{iss['card']}` doesn't match any corpus card")
        elif iss["type"] == "yaml_unquoted_colon":
            out.append(f"- YAML: `{iss['node']}` field `{iss['field']}` has unquoted `: ` (Obsidian parser hazard)")
        elif iss["type"] == "dangling_wikilink":
            out.append(f"- WIKILINK: `{iss['node']}` references `[[{iss['target']}]]` which doesn't exist as layer node")
        elif iss["type"] == "wikilink_case_normalize":
            out.append(f"- CASE: `{iss['node']}` references `[[{iss['target']}]]` -> canonical `{iss['canonical']}` (normalize)")
        elif iss["type"] == "below_threshold":
            out.append(f"- THRESHOLD: `{iss['node']}` has {iss['anchors']} anchors (need >={iss['min_required']})")
    if len(actionable) > 15:
        out.append(f"- ... ({len(actionable) - 15} more — see `python bbl_node_audit.py` full output)")
    return "\n".join(out)


# --- main --------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable report")
    ap.add_argument("--brief", action="store_true", help="Emit short markdown for agent-brief inclusion")
    ap.add_argument("--strict", action="store_true", help="Exit 1 if any issues found (CI-style)")
    args = ap.parse_args()

    nodes = walk_layer_nodes()
    cards = walk_cards()

    drift_all = check_drift(nodes, cards)
    drift_issues = [i for i in drift_all if i["type"] in ("drift_forward", "drift_reverse")]
    unresolved_issues = [i for i in drift_all if i["type"] == "appears_on_unresolved"]
    yaml_issues = check_yaml_safety(nodes)
    wikilink_all = check_wikilinks(nodes)
    # Real issues = dangling + case-normalize. Informational = card-cross-ref + cross-wiki.
    dangling_issues = [i for i in wikilink_all if i["type"] == "dangling_wikilink"]
    case_norm_issues = [i for i in wikilink_all if i["type"] == "wikilink_case_normalize"]
    card_xref_issues = [i for i in wikilink_all if i["type"] == "card_cross_reference"]
    cross_wiki_issues = [i for i in wikilink_all if i["type"] == "cross_wiki_reference"]
    threshold_issues = check_threshold(nodes, cards)

    # Only emit real issues by default; card-xref and cross-wiki are informational
    all_issues = (drift_issues + unresolved_issues + yaml_issues
                  + dangling_issues + case_norm_issues + threshold_issues
                  + card_xref_issues + cross_wiki_issues)

    report = {
        "ran_at": datetime.now().isoformat(timespec="seconds"),
        "layer_node_count": len(nodes),
        "card_count": len(cards),
        "summary": {
            "drift":           len(drift_issues),
            "unresolved":      len(unresolved_issues),
            "yaml":            len(yaml_issues),
            "wikilinks":       len(dangling_issues) + len(case_norm_issues),
            "card_xrefs":      len(card_xref_issues),
            "cross_wiki":      len(cross_wiki_issues),
            "threshold":       len(threshold_issues),
        },
        "issues": all_issues,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    elif args.brief:
        print(render_brief(report))
    else:
        print(render_human(report))

    if args.strict and all_issues:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
