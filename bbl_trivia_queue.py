#!/usr/bin/env python3
"""bbl_trivia_queue — list cards ready for trivia enrichment.

Trivia-ready = vision-enriched (tags_hub non-empty) + NO `## Trivia` section.

Mirrors the contract of bbl_queue.py for vision-ready cards. Both queues feed
their respective agents a pre-filtered list so the agent never has to decide
whether to skip a card. Per `bbl-trivia-never-consider-preenriched` memory:
the agent's job is pure creation, not audit. Audit work routes through
janitor_triage or a future dedicated auditor agent.

Usage:
    python bbl_trivia_queue.py                 # print first 100 paths
    python bbl_trivia_queue.py --limit 50      # cap output
    python bbl_trivia_queue.py --by-set        # group by set with counts
    python bbl_trivia_queue.py --game Pokemon  # filter to one game
    python bbl_trivia_queue.py --count         # just print total
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from collections import Counter


def _norm(p: str) -> str:
    return p.replace("\\", "/")


def find_trivia_ready(cards_dir: str, game_filter: str | None = None) -> list[str]:
    """Return list of card-MD paths that have vision but lack trivia.

    Layer-node directories (cards/_characters/, cards/_symbols/, etc.) are
    skipped — only inventory cards qualify."""
    out: list[str] = []
    pattern = os.path.join(cards_dir, "**", "*.md")
    for path in glob.glob(pattern, recursive=True):
        norm = _norm(path)
        # Skip layer-node directories
        if "/_" in norm:
            continue
        # Optional game filter — cards live at cards/<game-slug>/<set>/<card.md>
        if game_filter:
            game_slug = game_filter.lower().replace(" ", "-").replace(":", "")
            if f"/{game_slug}/" not in norm.lower():
                continue
        try:
            with open(path, encoding="utf-8") as f:
                body = f.read()
        except OSError:
            continue
        # Vision-done check: tags_hub populated (inline OR block form, wave 92)
        m_inline = re.search(r"tags_hub:\s*\[([^\]]*)\]", body)
        m_block = re.search(r"^tags_hub:\s*\n\s+-\s+\S+", body, re.MULTILINE)
        inline_ok = m_inline and m_inline.group(1).strip()
        if not (inline_ok or m_block):
            continue
        # Trivia-absent check
        if "## Trivia" in body:
            continue
        out.append(path)
    out.sort()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cards-dir", default="cards")
    ap.add_argument("--limit", type=int, default=100,
                    help="Cap output (default 100). Use 0 for unlimited.")
    ap.add_argument("--by-set", action="store_true",
                    help="Group by set with counts instead of listing paths.")
    ap.add_argument("--game", default=None,
                    help="Filter to one game (e.g. Pokemon, Magic: The Gathering).")
    ap.add_argument("--count", action="store_true",
                    help="Print only the total count.")
    args = ap.parse_args()

    paths = find_trivia_ready(args.cards_dir, args.game)

    if args.count:
        print(len(paths))
        return 0

    if args.by_set:
        sets: Counter = Counter()
        for p in paths:
            parts = _norm(p).split("/")
            # cards/<game>/<set>/<card>
            if len(parts) >= 3:
                sets[f"{parts[1]}/{parts[2]}"] += 1
        print(f"Total trivia-ready: {len(paths)}")
        print()
        for s, c in sets.most_common():
            print(f"  {c:4d}  {s}")
        return 0

    limit = args.limit if args.limit > 0 else len(paths)
    for p in paths[:limit]:
        print(p)
    if args.limit > 0 and len(paths) > args.limit:
        print(f"... ({len(paths) - args.limit} more — use --limit 0 for all)",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
