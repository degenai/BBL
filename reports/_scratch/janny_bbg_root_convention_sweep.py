#!/usr/bin/env python3
"""Janny sweep — convert [[Bulk Graph Bundler]] wikilinks to backticks.

cards/Bulk Graph Bundler.md is a 0-byte file with 115 incoming wikilinks
acting as a "project-root convention" citation across the corpus. In
Obsidian's graph view it surfaces as a massive center hub by sheer edge
count, but it carries zero substrate — pure architectural-template
citation, exact same pattern as the wave-124 nicol-bolas sweep and the
wave-127 cell-saga-apparatus sweep.

Per bbl-wikilink-vs-backtick-discipline: backticks for schema /
architectural-precedent / project-root citations; wikilinks reserved for
real-thematic edges only.

This sweep:
1. Converts every [[Bulk Graph Bundler]] in cards/**/*.md to `Bulk Graph Bundler`.
2. Does NOT delete the empty MD file (parent will rm separately).
3. Skips cards/Bulk Graph Bundler.md itself (the empty file — caller deletes).

Idempotent.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
TARGET = "[[Bulk Graph Bundler]]"
REPLACE = "`Bulk Graph Bundler`"


def safe_print(s: str) -> None:
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("ascii", errors="replace").decode("ascii"))


def main():
    total = 0
    files_touched = []
    for path in (REPO / "cards").rglob("*.md"):
        rel = str(path.relative_to(REPO)).replace("\\", "/")
        if rel == "cards/Bulk Graph Bundler.md":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if TARGET not in text:
            continue
        count = text.count(TARGET)
        new_text = text.replace(TARGET, REPLACE)
        path.write_text(new_text, encoding="utf-8")
        files_touched.append(rel)
        total += count
        safe_print(f"  {rel}  ({count}x)")

    safe_print(f"\n=== total: {total} wikilinks -> backticks across {len(files_touched)} files ===")


if __name__ == "__main__":
    main()
