#!/usr/bin/env python3
"""bbl_edgelord_queue — list cards ready for Edgelord topology work.

Edgelord-ready = vision-enriched (tags_hub non-empty) + trivia-enriched
(`## Trivia` section present). Cards lacking either have insufficient
substrate for evidence-grounded edges or refusal-with-receipts decisions.

Edgelord retains FULL corpus-walking authority — this queue is just the
STARTING SLATE for a quad-pass dispatch, not the only cards it can touch.
Per Alex 2026-05-13: "edgelord should similarly to the others target nodes
with trivia and image enrichment not random, although this is just where
to start since it considers advanced total topology."

Optional filters:
  --unwired         only cards lacking `characters: [...]` / `symbols: [...]` /
                    `hubs: [...]` frontmatter (the highest-yield Edgelord slots)
  --by-set          group by set with counts instead of listing paths
  --game GAME       filter to one game
  --count           print only the total
  --limit N         cap output (default 100; 0 for unlimited)

Mirrors bbl_queue.py (vision-ready) and bbl_trivia_queue.py (trivia-ready)
contracts. Per `bbl-trivia-never-consider-preenriched`-style cleanliness:
each agent gets a pre-filtered list so it doesn't have to decide what to
skip. The agent's value is in the work it does, not in slate filtering.
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


def find_edgelord_ready(cards_dir: str, game_filter: str | None = None,
                        unwired_only: bool = False) -> list[str]:
    """Return list of card-MD paths with vision + trivia both done.

    Layer-node directories (cards/_characters/, cards/_symbols/, etc.) are
    skipped — only inventory cards qualify."""
    out: list[str] = []
    pattern = os.path.join(cards_dir, "**", "*.md")
    for path in glob.glob(pattern, recursive=True):
        norm = _norm(path)
        if "/_" in norm:
            continue
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
        if "## Trivia" not in body:
            continue
        if unwired_only:
            # Cards already wired to character/symbol/hub layers are
            # lower-value Edgelord starting points; their edges exist.
            # Look for non-empty arrays on these three fields (both forms).
            wired = False
            for field in ("characters", "symbols", "hubs"):
                fm_inline = re.search(rf"^{field}:\s*\[([^\]]*)\]", body, re.MULTILINE)
                fm_block = re.search(rf"^{field}:\s*\n\s+-\s+\S+", body, re.MULTILINE)
                if (fm_inline and fm_inline.group(1).strip()) or fm_block:
                    wired = True
                    break
            if wired:
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
                    help="Group by set with counts.")
    ap.add_argument("--game", default=None,
                    help="Filter to one game (e.g. Pokemon).")
    ap.add_argument("--count", action="store_true",
                    help="Print only the total count.")
    ap.add_argument("--unwired", action="store_true",
                    help="Only include cards lacking characters/symbols/hubs frontmatter (highest-yield starting points).")
    args = ap.parse_args()

    paths = find_edgelord_ready(args.cards_dir, args.game,
                                unwired_only=args.unwired)

    if args.count:
        print(len(paths))
        return 0

    if args.by_set:
        sets: Counter = Counter()
        for p in paths:
            parts = _norm(p).split("/")
            if len(parts) >= 3:
                sets[f"{parts[1]}/{parts[2]}"] += 1
        label = "unwired Edgelord-ready" if args.unwired else "Edgelord-ready"
        print(f"Total {label}: {len(paths)}")
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
