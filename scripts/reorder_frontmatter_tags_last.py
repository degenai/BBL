"""
Move the `tags:` block-list to the end of frontmatter on every card.

Obsidian's property panel renders top-level keys that follow a block-list
as orphaned (dashes instead of typed widgets). Moving `tags:` to the end
makes everything before it parse normally. Idempotent.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def process(path: Path, dry_run: bool) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    m = re.match(r"^(---\s*\n)(.*?)(\n---\s*\n)", text, re.DOTALL)
    if not m:
        return False
    open_marker, fm_text, close_marker = m.group(1), m.group(2), m.group(3)
    rest = text[m.end():]

    # Locate the `tags:` block-list (must be block form, not inline).
    tags_m = re.search(r"^tags:\s*\n((?:  -\s+.*(?:\n|$))+)", fm_text, re.MULTILINE)
    if not tags_m:
        return False
    # If `tags:` is already the last non-blank thing in frontmatter, skip.
    tail = fm_text[tags_m.end():]
    if not tail.strip():
        return False

    tags_block = fm_text[tags_m.start():tags_m.end()].rstrip("\n")
    before = fm_text[: tags_m.start()].rstrip("\n")
    after = tail.lstrip("\n").rstrip("\n")

    parts = []
    if before:
        parts.append(before)
    if after:
        parts.append(after)
    parts.append(tags_block)
    new_fm = "\n".join(parts)

    new_text = open_marker + new_fm + "\n" + close_marker + rest
    if new_text == text:
        return False
    if dry_run:
        return True
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="cards")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    targets = sorted(Path(args.root).rglob("*.md"))
    changed = 0
    for p in targets:
        if process(p, args.dry_run):
            changed += 1
            if changed <= 3:
                print(f"{'WOULD REORDER' if args.dry_run else 'REORDERED'} {p}")
    print(f"\n{changed} files {'would be' if args.dry_run else ''} reordered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
