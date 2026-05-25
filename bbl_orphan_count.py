#!/usr/bin/env python3
"""bbl_orphan_count — detect cards whose `characters:` frontmatter pointer
has no matching body-prose wikilink.

This is the "one-sided cohort edge" / "orphan-edge" pattern: the graph
metadata wires both sides (card frontmatter + cohort `appears_on:`) but
the card body has no statement connecting the card to the cohort.
Bundle authoring downstream wants prose, not metadata, so these need
back-edge bullets written.

Surfaced wave 158, escalated wave 192 corpus sweep to 504. Architecture
for closure: route orphan-mirror writes through Opus-mode triviabot
extension with parent-reviewed batches; this script is the manifest +
richness-assessor that gates that dispatch.

Per the wave-194 architecture decision (token-budget reframe; parent-
context-retention concern): triviabot is the natural writer, parent is
the natural reviewer. This script gates which cohorts are dispatch-
eligible: thin cohorts route to manual Edgelord forever (acceptable
permanent backlog); rich cohorts route to triviabot batches.

Usage:
    python bbl_orphan_count.py                    # summary only
    python bbl_orphan_count.py --manifest         # full per-cohort dispatch list
    python bbl_orphan_count.py --cohort foo       # restrict to one cohort
    python bbl_orphan_count.py --tier high        # restrict to one richness tier
    python bbl_orphan_count.py --json             # machine-readable
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

CARDS_DIR = Path("cards")
CHARACTERS_DIR = CARDS_DIR / "_characters"
LAYER_DIRS = {"_characters", "_symbols", "_hubs", "_artists", "_images"}


@dataclass
class CohortInfo:
    slug: str
    path: Path
    exists: bool = False
    word_count: int = 0
    substantive_paragraphs: int = 0  # paragraphs >=50 words
    bulleted_lists: int = 0
    flavor_quotes: int = 0  # `> "..."` block-quote lines
    appears_on_count: int = 0

    @property
    def richness_tier(self) -> str:
        # high: dense + multi-archetype + well-populated cohort.
        # Triviabot can write bullets confidently with strong source-grounding.
        if (self.word_count >= 800
                and self.substantive_paragraphs >= 4
                and self.appears_on_count >= 4):
            return "high"
        # medium: enough material for source-grounded bullets but thinner.
        # Triviabot-eligible with parent reviewing more carefully.
        if self.word_count >= 400 and self.substantive_paragraphs >= 2:
            return "medium"
        # low: thin cohort. Confab risk too high. Defer to manual Edgelord.
        return "low"


@dataclass
class OrphanRecord:
    card_path: Path
    cohort_slug: str


# ---------- parsers ----------

def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Returns (frontmatter_dict, body_text). Block-form list values are
    preserved as multi-line strings under their field key so the caller
    can re-tokenize them; this matters for `characters:` and `appears_on:`."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        return {}, text
    fm: dict[str, str] = {}
    fm_text = m.group(1)
    body = m.group(2)
    current_key: str | None = None
    current_block: list[str] = []
    for line in fm_text.splitlines():
        m2 = re.match(r"^([a-z_][a-z0-9_]*):\s*(.*)$", line)
        if m2:
            if current_key is not None:
                fm[current_key] = "\n".join(current_block).strip()
            current_key = m2.group(1)
            current_block = [m2.group(2)]
        elif current_key is not None and re.match(r"^[ \t]+", line):
            # indented continuation (block-list item or multi-line value)
            current_block.append(line)
    if current_key is not None:
        fm[current_key] = "\n".join(current_block).strip()
    return fm, body


def extract_list_field(fm: dict[str, str], field: str) -> list[str]:
    """Return list of slug values from a list-shaped frontmatter field,
    handling both inline `[a, b]` and block `\\n  - a\\n  - b` forms."""
    raw = fm.get(field, "").strip()
    if not raw or raw in ("[]", "~"):
        return []
    inline = re.match(r"^\[(.*)\]$", raw)
    if inline:
        return [s.strip().strip("\"'") for s in inline.group(1).split(",") if s.strip()]
    slugs: list[str] = []
    for line in raw.splitlines():
        bm = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if bm:
            slug = bm.group(1).strip().strip("\"'")
            if slug:
                slugs.append(slug)
    return slugs


def body_has_wikilink_to(body: str, slug: str) -> bool:
    """Does the body contain a `[[slug]]` wikilink (case-insensitive)?"""
    return bool(re.search(rf"\[\[{re.escape(slug)}(?:\|[^\]]*)?\]\]", body, re.IGNORECASE))


# ---------- richness assessor ----------

def measure_cohort_richness(path: Path) -> CohortInfo:
    info = CohortInfo(slug=path.stem, path=path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return info
    info.exists = True
    fm, body = parse_frontmatter(text)
    info.appears_on_count = len(extract_list_field(fm, "appears_on"))
    # Strip auto-generated `## Appears on` section before measuring word count
    # — that section is rendered boilerplate, not authored substrate.
    body_measure = re.sub(
        r"^## Appears on.*?(?=^## |\Z)", "", body,
        flags=re.MULTILINE | re.DOTALL
    )
    words = re.findall(r"\b\w+\b", body_measure)
    info.word_count = len(words)
    paragraphs = re.split(r"\n\s*\n", body_measure)
    info.substantive_paragraphs = sum(
        1 for p in paragraphs if len(re.findall(r"\b\w+\b", p)) >= 50
    )
    info.bulleted_lists = sum(
        1 for p in paragraphs if re.search(r"^\s*[-*]\s", p, re.MULTILINE)
    )
    info.flavor_quotes = sum(
        1 for line in body_measure.splitlines() if line.lstrip().startswith(">")
    )
    return info


# ---------- corpus scanner ----------

def scan_orphans() -> tuple[list[OrphanRecord], dict[str, CohortInfo]]:
    orphans: list[OrphanRecord] = []
    cohort_cache: dict[str, CohortInfo] = {}
    for card_path in CARDS_DIR.rglob("*.md"):
        if any(part in LAYER_DIRS for part in card_path.parts):
            continue
        try:
            text = card_path.read_text(encoding="utf-8")
        except OSError:
            continue
        fm, body = parse_frontmatter(text)
        slugs = extract_list_field(fm, "characters")
        for slug in slugs:
            if body_has_wikilink_to(body, slug):
                continue
            orphans.append(OrphanRecord(card_path=card_path, cohort_slug=slug))
            if slug not in cohort_cache:
                cohort_cache[slug] = measure_cohort_richness(
                    CHARACTERS_DIR / f"{slug}.md"
                )
    return orphans, cohort_cache


# ---------- output ----------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--manifest", action="store_true",
                   help="print full per-cohort dispatch manifest")
    p.add_argument("--cohort", help="restrict to one cohort slug")
    p.add_argument("--tier", choices=["high", "medium", "low"],
                   help="restrict to one richness tier")
    p.add_argument("--json", action="store_true", help="machine-readable JSON output")
    args = p.parse_args()

    orphans, cohort_cache = scan_orphans()

    by_cohort: dict[str, list[OrphanRecord]] = defaultdict(list)
    for o in orphans:
        by_cohort[o.cohort_slug].append(o)

    if args.cohort:
        by_cohort = {k: v for k, v in by_cohort.items() if k == args.cohort}
    if args.tier:
        by_cohort = {
            k: v for k, v in by_cohort.items()
            if cohort_cache.get(k, CohortInfo(slug=k, path=Path(""))).richness_tier == args.tier
        }

    if args.json:
        out = {
            "total_orphans": sum(len(v) for v in by_cohort.values()),
            "distinct_cohorts": len(by_cohort),
            "cohorts": {
                slug: {
                    "richness": cohort_cache.get(slug, CohortInfo(slug=slug, path=Path(""))).richness_tier,
                    "exists": cohort_cache.get(slug, CohortInfo(slug=slug, path=Path(""))).exists,
                    "word_count": cohort_cache.get(slug, CohortInfo(slug=slug, path=Path(""))).word_count,
                    "substantive_paragraphs": cohort_cache.get(slug, CohortInfo(slug=slug, path=Path(""))).substantive_paragraphs,
                    "appears_on": cohort_cache.get(slug, CohortInfo(slug=slug, path=Path(""))).appears_on_count,
                    "orphan_count": len(orphans_list),
                    "orphans": [str(o.card_path) for o in orphans_list],
                }
                for slug, orphans_list in sorted(by_cohort.items())
            },
        }
        print(json.dumps(out, indent=2))
        return 0

    # text summary
    tier_counts: dict[str, int] = defaultdict(int)
    missing_node_count = 0
    for slug, orphans_list in by_cohort.items():
        info = cohort_cache.get(slug, CohortInfo(slug=slug, path=Path("")))
        if not info.exists:
            missing_node_count += len(orphans_list)
            continue
        tier_counts[info.richness_tier] += len(orphans_list)

    total = sum(len(v) for v in by_cohort.values())
    print(f"=== BBL orphan-edge count ===")
    print(f"Total orphans: {total}")
    print(f"  - high-richness cohorts:   {tier_counts['high']:4d}  (triviabot-eligible)")
    print(f"  - medium-richness cohorts: {tier_counts['medium']:4d}  (triviabot-eligible, parent reviews carefully)")
    print(f"  - low-richness cohorts:    {tier_counts['low']:4d}  (defer to manual Edgelord)")
    print(f"  - missing cohort nodes:    {missing_node_count:4d}  (broken pointers — needs Edgelord judgment)")
    print(f"")
    print(f"Distinct cohorts referenced: {len(by_cohort)}")

    if args.manifest:
        print(f"\n=== Per-cohort manifest ===")
        tier_order = {"high": 0, "medium": 1, "low": 2}
        def sort_key(kv):
            info = cohort_cache.get(kv[0], CohortInfo(slug=kv[0], path=Path("")))
            tier = info.richness_tier if info.exists else "missing"
            return (tier_order.get(tier, 3), -len(kv[1]))
        for slug, orphans_list in sorted(by_cohort.items(), key=sort_key):
            info = cohort_cache.get(slug, CohortInfo(slug=slug, path=Path("")))
            label = info.richness_tier if info.exists else "MISSING-NODE"
            print(f"\n  {slug} [{label}] — {len(orphans_list)} orphans  ({info.word_count} words, {info.appears_on_count} members)")
            for o in orphans_list[:5]:
                print(f"    {o.card_path}")
            if len(orphans_list) > 5:
                print(f"    ... +{len(orphans_list) - 5} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
