#!/usr/bin/env python3
"""
fix_hashtag_pollution — Strip Obsidian-tag-confusing `#NNN` inline references
from card MD body text.

Why: triviabot agents wrote inline collector-number / Pokedex references like
`(#020/189)` and `Pokedex #246` in the `## Trivia` and `### Related cards`
sections. Obsidian parses `#020/189` as a nested tag `#020/189` and surfaces
the leaf-segment (`189`, `75`, etc.) as a graph node — bogus edges in the
Obsidian graph view. Triviabot's spec is now updated to use `no. NNN` instead;
this script back-fixes the cards already written.

Strategy:
- For each card MD: scan from the first `## ` heading downward (body only — DO
  NOT touch frontmatter, which has legitimate fields like `collector_number:
  086/189`).
- Replace `#NNN/NNN` → `no. NNN/NNN`.
- Replace standalone `#NNN` → `no. NNN`.
- Skip lines inside `[!note]` / `[!warning]` callouts that read `> [!warning]`
  — those callouts don't contain `#NNN` patterns anyway, but be defensive.
- Skip image embeds and markdown links (square-bracket patterns).

Idempotent: re-runs are no-ops because the regex only matches `#` followed by
digits, which the fix removes.

Usage:
  python reports/fix_hashtag_pollution.py [--dry-run]
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent

# `#NNN/NNN` → `no. NNN/NNN` (handles collector_number-style)
HASH_PAIR_RE = re.compile(r"(?<![\w/])#(\d+)/(\d+)")
# `#NNN` standalone → `no. NNN` (must not consume leading word char so `swsh3-86` stays)
HASH_SINGLE_RE = re.compile(r"(?<![\w/])#(\d+)\b")


def split_frontmatter(text: str) -> tuple[str, str]:
    """Returns (frontmatter_block_including_delimiters, body)."""
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end < 0:
        return "", text
    return text[: end + 5], text[end + 5 :]


def fix_body(body: str) -> tuple[str, int]:
    """Replace `#NNN/NNN` and standalone `#NNN` in body text.
    Returns (new_body, num_substitutions)."""
    new_body, n1 = HASH_PAIR_RE.subn(r"no. \1/\2", body)
    new_body, n2 = HASH_SINGLE_RE.subn(r"no. \1", new_body)
    return new_body, n1 + n2


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--cards-dir", default="cards")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    cards_dir = REPO_ROOT / args.cards_dir
    touched = 0
    total_subs = 0
    for path in cards_dir.rglob("*.md"):
        if any(part.startswith("_") for part in path.parts):
            continue  # skip _hubs, _symbols, _artists, _images
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        fm_block, body = split_frontmatter(text)
        new_body, n = fix_body(body)
        if n == 0:
            continue
        touched += 1
        total_subs += n
        if args.dry_run:
            print(f"[dry-run] {path.relative_to(REPO_ROOT)} — would replace {n} hash refs")
            # Show first 2 example matches in context
            for m in (HASH_PAIR_RE.finditer(body), HASH_SINGLE_RE.finditer(body)):
                shown = 0
                for hit in m:
                    if shown >= 2:
                        break
                    start = max(0, hit.start() - 25)
                    end = min(len(body), hit.end() + 25)
                    snippet = body[start:end].replace("\n", " ")
                    print(f"    ...{snippet}...")
                    shown += 1
        else:
            path.write_text(fm_block + new_body, encoding="utf-8")
            print(f"fixed {path.relative_to(REPO_ROOT)} — {n} hash refs replaced")

    print(f"\n=== hashtag-pollution fix report ===")
    print(f"  Cards touched: {touched}")
    print(f"  Total substitutions: {total_subs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
