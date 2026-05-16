"""
patch_color_magic_tags - apply color_magic_audit.json fixes to card frontmatter.

Reads `reports/color_magic_audit.json`. Three-bucket approach:
  A) wrong-extra-tag (has `wrong_extras` key): remove wrong_extras from tags_filter.
  B) missing-or-wrong-color where expected_tag != colorless-magic:
       replace all stated color tags in tags_filter with [expected_tag].
  C) missing-or-wrong-color where expected_tag == colorless-magic:
       skip — emit to human-review report; color tag may reflect functional
       faction identity (Talismans, Lockets, etc.) rather than casting cost.
       Curator decides per card.

Block-form YAML preservation: all non-color tags stay untouched.
Dry-run by default; --apply commits writes. Normalizes via bbl_schema after
each write for hygiene parity with other writers (wave 92.6 chokepoint).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from bbl_schema import normalize_file  # noqa: E402

AUDIT_PATH = ROOT / "reports" / "color_magic_audit.json"
HUMAN_REVIEW_DEFAULT = ROOT / "reports" / "color_magic_human_review.json"

COLOR_NAMES = {"white", "blue", "black", "red", "green"}

CANONICAL_COLOR_TAGS = {
    "white-magic", "blue-magic", "black-magic", "red-magic",
    "green-magic", "colorless-magic", "colorless", "multicolored",
}


def is_color_tag(tag: str) -> bool:
    if tag in CANONICAL_COLOR_TAGS:
        return True
    if tag.startswith("multicolor-"):
        parts = tag[len("multicolor-"):].split("-")
        return all(p in COLOR_NAMES for p in parts) and len(parts) >= 2
    return False


def rewrite_tags_filter(fm_text: str, tags_to_remove: set[str],
                        replacement_tag: str | None = None) -> tuple[str, bool]:
    """
    Read the block-form tags_filter list, remove tags_to_remove, optionally
    replace all color tags with replacement_tag, return (new_fm_text, changed).
    Preserves all non-color items exactly as written.
    """
    m = re.search(
        r"(^tags_filter:\s*\n)((?:  -\s+.*(?:\n|$))+)",
        fm_text, re.MULTILINE
    )
    if not m:
        return fm_text, False
    header = m.group(1)
    block = m.group(2)
    items = re.findall(r"^  -\s+(.+?)\s*$", block, re.MULTILINE)

    new_items: list[str] = []
    changed = False
    for raw in items:
        clean = raw.strip().strip('"').strip("'")
        if clean in tags_to_remove:
            changed = True
            continue
        if replacement_tag and is_color_tag(clean) and clean != replacement_tag:
            # Strip stale color tags; replacement is appended below if missing.
            changed = True
            continue
        new_items.append(clean)

    if replacement_tag and replacement_tag not in new_items:
        new_items.append(replacement_tag)
        changed = True

    if not changed:
        return fm_text, False

    new_block = header + "".join(f"  - {t}\n" for t in new_items)
    new_fm = fm_text[:m.start()] + new_block + fm_text[m.end():]
    return new_fm, True


def patch_file(card_path_rel: str, entry: dict, dry_run: bool) -> str:
    path = ROOT / card_path_rel
    if not path.exists():
        return f"MISSING: {card_path_rel}"
    text = path.read_text(encoding="utf-8")
    fm_m = re.match(r"^(---\s*\n)(.*?)(\n---\s*\n)", text, re.DOTALL)
    if not fm_m:
        return f"NO_FM: {card_path_rel}"

    fm_text = fm_m.group(2)
    sev = entry["severity"]

    if sev == "wrong-extra-tag":
        tags_to_remove = set(entry.get("wrong_extras", []))
        new_fm, changed = rewrite_tags_filter(fm_text, tags_to_remove)
    else:  # missing-or-wrong-color, non-colorless
        tags_to_remove = set(entry["stated_tags"])
        new_fm, changed = rewrite_tags_filter(
            fm_text, tags_to_remove,
            replacement_tag=entry["expected_tag"]
        )

    if not changed:
        return f"NO_CHANGE: {card_path_rel}"

    new_text = text[:fm_m.start(2)] + new_fm + text[fm_m.end(2):]
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
        normalize_file(path)
        return f"PATCHED: {card_path_rel}  ({sev})"
    return f"DRY: {card_path_rel}  ({sev})"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true",
                    help="Actually write files (default: dry-run).")
    ap.add_argument("--audit-in", type=Path, default=AUDIT_PATH)
    ap.add_argument("--human-review-out", type=Path, default=HUMAN_REVIEW_DEFAULT)
    args = ap.parse_args()

    entries = json.loads(args.audit_in.read_text(encoding="utf-8"))
    human_review = []
    results: list[str] = []

    for entry in entries:
        if entry["expected_tag"] == "colorless-magic":
            human_review.append(entry)
            continue
        result = patch_file(entry["path"], entry, dry_run=not args.apply)
        results.append(result)

    by_outcome: dict[str, int] = {}
    for r in results:
        prefix = r.split(":", 1)[0]
        by_outcome[prefix] = by_outcome.get(prefix, 0) + 1

    print(f"\n--- color_magic_tag patch report ({'APPLY' if args.apply else 'DRY RUN'}) ---")
    print(f"  Total audit entries:                  {len(entries)}")
    print(f"  Skipped (colorless-magic expected):   {len(human_review)}")
    print(f"  Auto-patchable processed:             {len(results)}")
    for outcome, n in sorted(by_outcome.items()):
        print(f"    {outcome}: {n}")

    # Print first 10 results then count
    print("\nFirst 10 results:")
    for r in results[:10]:
        print(f"  {r}")
    if len(results) > 10:
        print(f"  ... ({len(results) - 10} more)")

    args.human_review_out.write_text(
        json.dumps(human_review, indent=2), encoding="utf-8"
    )
    print(f"\nHuman-review JSON: {args.human_review_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
