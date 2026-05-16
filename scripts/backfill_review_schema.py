"""
Backfill `review_good: false`, `review_bad: false`, `review_notes: ""`
onto cards with `needs_manual_review: true` that don't already have the
fields. Idempotent. Skips cards that already have any of the three fields
set (preserves existing 5-parasect-style verdicts).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def needs_review(fm_text: str) -> bool:
    m = re.search(r"^needs_manual_review:\s*true\s*$", fm_text, re.MULTILINE)
    return bool(m)


def has_field(fm_text: str, field: str) -> bool:
    return bool(re.search(rf"^{re.escape(field)}:", fm_text, re.MULTILINE))


def fm_block(text: str):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None
    return m.end(1), m.group(1)


def process(path: Path, dry_run: bool) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    fb = fm_block(text)
    if not fb:
        return False
    fm_end, fm_text = fb
    if not needs_review(fm_text):
        return False
    additions = []
    if not has_field(fm_text, "review_good"):
        additions.append("review_good: false")
    if not has_field(fm_text, "review_bad"):
        additions.append("review_bad: false")
    if not has_field(fm_text, "review_notes"):
        additions.append('review_notes: ""')
    if not additions:
        return False
    if dry_run:
        return True
    insertion = "\n".join(additions) + "\n"
    new_text = text[:fm_end] + "\n" + insertion + text[fm_end:]
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
            if changed <= 5:
                print(f"{'WOULD BACKFILL' if args.dry_run else 'BACKFILLED'} {p}")
    print(f"\n{changed} files {'would be' if args.dry_run else ''} backfilled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
