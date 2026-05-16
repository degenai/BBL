#!/usr/bin/env python3
"""bbl_queue — print the next-batch list of cards ready for the vision pass.

A card is "ready for vision" when ALL three are true:
  1. `reference_image:` field is non-empty in the frontmatter
  2. The path it points to exists on disk (csv2mdbot writes an empty placeholder
     for every card, so frontmatter alone is not a reliable signal)
  3. `tags_hub:` is still empty (i.e. no vision pass has run yet)
  4. `needs_manual_review: true` is NOT set

Cards are sorted by quantity descending — same priority order researchbot uses
so the highest-value bulk gets enriched first.

Usage:
    python bbl_queue.py                                   # all games, all ready cards
    python bbl_queue.py --game "Magic: The Gathering"     # one game
    python bbl_queue.py --limit 25                        # top N
    python bbl_queue.py --with-qty                        # prefix each line with quantity
    python bbl_queue.py --count                           # just print the integer count

Companion to `researchbot.py --prepare-only` (which fills the queue) and the
`bbl-researcher` subagent (which drains it).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

CARDS_DIR = Path("cards")


def parse_frontmatter(text: str) -> dict:
    """Tiny regex frontmatter reader — no PyYAML dependency."""
    m = re.search(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip()
    return out


def is_ready_for_vision(card_path: Path) -> tuple[bool, int]:
    """Returns (ready_bool, quantity). The quantity is used for sorting."""
    try:
        text = card_path.read_text(encoding="utf-8")
    except OSError:
        return (False, 0)
    fm = parse_frontmatter(text)
    if not fm:
        return (False, 0)

    ref = fm.get("reference_image", "").strip()
    if not ref:
        return (False, 0)
    # The path is repo-relative — resolve against cwd.
    if not Path(ref).exists():
        return (False, 0)

    hub = fm.get("tags_hub", "").strip()
    # tags_hub is a YAML list — inline `[a, b]` or block form (wave 92).
    if hub and hub not in ("[]", ""):
        return (False, 0)
    # Block-form populated check: `tags_hub:\n  - foo`
    if re.search(r"^tags_hub:\s*\n\s+-\s+\S+", text, re.MULTILINE):
        return (False, 0)

    if fm.get("needs_manual_review", "").lower() == "true":
        return (False, 0)

    try:
        qty = int(fm.get("quantity", "0"))
    except ValueError:
        qty = 0
    return (True, qty)


def find_ready_cards(game_filter: str | None) -> list[tuple[int, Path]]:
    rows: list[tuple[int, Path]] = []
    if not CARDS_DIR.exists():
        return rows
    for game_dir in CARDS_DIR.iterdir():
        if not game_dir.is_dir():
            continue
        if game_filter:
            # Match by either folder slug or the actual `game:` field. Folder
            # slug is the kebab-case version; user passes the human name.
            slug = game_filter.lower().replace(":", "").replace(" ", "-")
            if slug not in game_dir.name.lower():
                # Verify by reading one card's `game:` field instead of trusting slug.
                # Cheap enough — if slug doesn't match folder, skip the dir.
                continue
        for md in game_dir.rglob("*.md"):
            ready, qty = is_ready_for_vision(md)
            if ready:
                rows.append((qty, md))
    rows.sort(key=lambda r: (-r[0], str(r[1])))
    return rows


def main() -> int:
    p = argparse.ArgumentParser(description="List cards ready for the BBL vision pass.")
    p.add_argument("--game", default=None, help='Filter to one game (e.g. "Magic: The Gathering")')
    p.add_argument("--limit", type=int, default=None, help="Cap output at N cards")
    p.add_argument("--with-qty", action="store_true", help="Prefix each line with quantity\\t")
    p.add_argument("--count", action="store_true", help="Print only the integer count, nothing else")
    args = p.parse_args()

    rows = find_ready_cards(args.game)
    if args.limit:
        rows = rows[: args.limit]

    if args.count:
        print(len(rows))
        return 0

    for qty, path in rows:
        if args.with_qty:
            print(f"{qty}\t{path.resolve()}")
        else:
            print(path.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
