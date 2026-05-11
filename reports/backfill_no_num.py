#!/usr/bin/env python3
"""backfill_no_num — give no-num-* card MDs their actual collector numbers.

Collectr's CSV export drops `Card Number` for some sets (mostly old MTG: Chronicles,
6E, 8E, Mirrodin, Mercadian Masques, etc). csv2mdbot correctly falls back to
`no-num-<slug>` filenames when the field is empty, but the numbers exist on the
physical cards — Scryfall has them.

This script walks every `cards/<game>/<set>/no-num-<slug>.md`:
  1. Reads `reference_image_source_url` from frontmatter (already a Scryfall image
     URL with the card UUID inline — set by researchbot.py during prep)
  2. Extracts the UUID, hits `https://api.scryfall.com/cards/<uuid>` for the canonical
     `collector_number`
  3. Renames the MD file: `no-num-<slug>.md` -> `<num>-<slug>.md`
  4. Renames the cached image file if it exists
  5. Updates inside the MD: `collector_number:`, `reference_image:`, and any
     `![alt](old-path)` body embeds, all in place

Idempotent: a card that already has a number (or whose Scryfall lookup fails) is
left alone. Safe to re-run.

Usage:
    python reports/backfill_no_num.py [--dry-run] [--cards-dir cards]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

SCRYFALL_API = "https://api.scryfall.com"
USER_AGENT = "BBL-backfill-no-num/1.0 (degenai)"
SLEEP_BETWEEN = 0.15

# Pull the Scryfall card UUID out of an image URL like
#   https://cards.scryfall.io/png/front/9/a/9a0e90b8-bc38-4e1c-92ca-ac562cc57e31.png?...
UUID_RE = re.compile(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip()
    return out


def update_fm_field(text: str, field: str, value: str) -> str:
    pattern = rf"^{re.escape(field)}:.*$"
    if re.search(pattern, text, flags=re.MULTILINE):
        return re.sub(pattern, f"{field}: {value}", text, count=1, flags=re.MULTILINE)
    m = FRONTMATTER_RE.match(text)
    if not m:
        return text
    fm_end = m.end(1)
    return text[:fm_end] + f"\n{field}: {value}" + text[fm_end:]


def scryfall_get(uuid: str) -> dict | None:
    url = f"{SCRYFALL_API}/cards/{urllib.parse.quote(uuid)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  scryfall lookup failed for {uuid}: {e}", file=sys.stderr)
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cards-dir", type=Path, default=Path("cards"))
    ap.add_argument("--images-dir", type=Path, default=Path("cards/_images"))
    ap.add_argument("--dry-run", action="store_true", help="Report planned changes without writing")
    args = ap.parse_args()

    no_num_files = sorted(args.cards_dir.rglob("no-num-*.md"))
    print(f"Found {len(no_num_files)} no-num card MDs")
    if not no_num_files:
        return 0

    stats = {"renamed": 0, "skipped_no_url": 0, "skipped_no_uuid": 0,
             "skipped_no_number": 0, "skipped_lookup_fail": 0, "skipped_target_exists": 0}

    for md_path in no_num_files:
        rel = md_path.relative_to(args.cards_dir)
        text = md_path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)

        src_url = fm.get("reference_image_source_url", "") or fm.get("reference_image", "")
        if not src_url:
            print(f"[skip] {rel}: no reference_image_source_url")
            stats["skipped_no_url"] += 1
            continue

        m = UUID_RE.search(src_url)
        if not m:
            print(f"[skip] {rel}: no Scryfall UUID in source URL ({src_url[:60]}...)")
            stats["skipped_no_uuid"] += 1
            continue
        uuid = m.group(1)

        card = scryfall_get(uuid)
        time.sleep(SLEEP_BETWEEN)
        if not card:
            stats["skipped_lookup_fail"] += 1
            continue

        number = (card.get("collector_number") or "").strip()
        if not number:
            print(f"[skip] {rel}: Scryfall returned no collector_number")
            stats["skipped_no_number"] += 1
            continue

        # New slug = "<num>-<rest-after-no-num->"
        old_stem = md_path.stem  # "no-num-runesword"
        if not old_stem.startswith("no-num-"):
            continue
        new_stem = f"{number}-{old_stem[len('no-num-'):]}"
        new_md = md_path.with_name(new_stem + ".md")

        if new_md.exists():
            print(f"[skip] {rel}: target {new_md.name} already exists")
            stats["skipped_target_exists"] += 1
            continue

        # Locate the cached image. Path in frontmatter is project-relative
        # ("cards/_images/<game>/<set>/no-num-<slug>.png").
        old_image_rel = fm.get("reference_image", "") or ""
        old_image = Path(old_image_rel) if old_image_rel else None
        new_image_rel = ""
        new_image = None
        if old_image and old_image.name.startswith("no-num-"):
            new_image_name = f"{number}-{old_image.name[len('no-num-'):]}"
            new_image = old_image.with_name(new_image_name)
            new_image_rel = str(new_image).replace("\\", "/")

        print(f"[rename] {old_stem} -> {new_stem}  (#{number}, {card.get('name')})")
        if args.dry_run:
            stats["renamed"] += 1
            continue

        # Update text in place: frontmatter fields + body image embed if present.
        text = update_fm_field(text, "collector_number", number)
        if new_image_rel:
            text = update_fm_field(text, "reference_image", new_image_rel)
            # The body has `![<old-stem>](../../_images/<game>/<set>/<old-filename>.png)`.
            # Swap both the alt text and the filename to the new stem.
            text = text.replace(old_stem, new_stem)
            if old_image:
                text = text.replace(old_image.name, new_image_name)

        md_path.write_text(text, encoding="utf-8")
        md_path.rename(new_md)

        if new_image and old_image and old_image.exists():
            old_image.rename(new_image)

        stats["renamed"] += 1

    print("\n=== backfill_no_num report ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
