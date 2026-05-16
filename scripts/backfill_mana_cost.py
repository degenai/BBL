"""
Backfill `mana_cost:` frontmatter on existing MTG cards that lack it.

Wave 92.5 fix: bbl-researcher spec told agents to "parse mana-cost symbols"
but the field was never stamped at prep-time, causing repeated color-magic
mis-tag failures (Manifest Dread, Dragon Trainer, Bulma).

researchbot.py now captures mana_cost on new MTG cards. This script
backfills the ~500+ already-prepped MTG cards that were processed before
the capture was wired. Idempotent: skips cards that already have the
field.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import researchbot  # noqa: E402


FM_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def has_mana_cost(fm_text: str) -> bool:
    return bool(re.search(r"^mana_cost:", fm_text, re.MULTILINE))


def read_field(fm_text: str, field: str) -> str:
    m = re.search(rf"^{re.escape(field)}:\s*(.*?)\s*$", fm_text, re.MULTILINE)
    return m.group(1).strip(' "\'') if m else ""


def stamp_field(text: str, field: str, value: str) -> str:
    return researchbot.update_frontmatter_field(text, field, value)


def process(path: Path, set_map: dict, dry_run: bool) -> str:
    text = path.read_text(encoding="utf-8")
    m = FM_PATTERN.match(text)
    if not m:
        return "skip:no-frontmatter"
    fm_text = m.group(1)
    if has_mana_cost(fm_text):
        return "skip:already-stamped"
    name = read_field(fm_text, "name")
    set_name = read_field(fm_text, "set")
    if not name:
        return "skip:no-name"
    # Fetch fresh Scryfall lookup — reuse researchbot's path
    result = researchbot.find_image_scryfall(name, set_name, set_map)
    img, conf, num, artist, art_crop, flavor, oracle, mana_cost = result
    if not mana_cost:
        return "skip:no-mana-cost-returned"
    if dry_run:
        return f"would-stamp: {mana_cost}"
    new_text = stamp_field(text, "mana_cost", mana_cost)
    path.write_text(new_text, encoding="utf-8")
    return f"stamped: {mana_cost}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="cards/magic-the-gathering")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    set_map = researchbot.fetch_scryfall_set_map()

    targets = sorted(Path(args.root).rglob("*.md"))
    if args.limit:
        targets = targets[: args.limit]

    counts = {"stamped": 0, "skip:already-stamped": 0, "skip:no-name": 0,
              "skip:no-mana-cost-returned": 0, "skip:no-frontmatter": 0,
              "would-stamp": 0, "error": 0}
    for i, p in enumerate(targets, 1):
        try:
            result = process(p, set_map, args.dry_run)
        except Exception as e:
            print(f"[{i}/{len(targets)}] ERROR {p}: {e}", file=sys.stderr)
            counts["error"] += 1
            continue
        # Bucket by prefix
        prefix = result.split(":", 1)[0]
        # Normalize "stamped" / "would-stamp" / "skip:*"
        if prefix in ("stamped", "would-stamp"):
            counts[prefix] += 1
            print(f"[{i}/{len(targets)}] {result} <- {p.name}")
        else:
            counts[result] = counts.get(result, 0) + 1

    print(f"\n--- Summary ({len(targets)} files) ---")
    for k, v in sorted(counts.items()):
        if v:
            print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
