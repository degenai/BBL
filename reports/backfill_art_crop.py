#!/usr/bin/env python3
"""
backfill_art_crop — Add art_crop URL + locally cached art-only image to existing
enriched MTG cards.

Why: As of 2026-05-11 researchbot captures Scryfall's art_crop URL alongside
the full card image, but the first 597 MTG enrichments were captured before
that change and have only the framed card. The bbl-researcher vision pass
prefers art_crop when available (no card-frame metadata to confabulate).
This script walks the existing corpus and fills the gap.

Strategy: hit /cards/<uuid> on Scryfall using the UUID embedded in
reference_image_source_url, extract art_crop URL via _extract_art_crop,
download to cards/_images/.../<slug>--art.jpg, stamp art_crop_image +
art_crop_source_url into frontmatter.

Idempotent: skips cards that already have a non-empty art_crop_image.

Usage:
  python reports/backfill_art_crop.py [--dry-run] [--limit N] [--sleep S]
"""
from __future__ import annotations
import argparse, re, sys, time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from researchbot import (
    parse_frontmatter, update_frontmatter_field, http_get_json,
    _extract_art_crop, download_image, url_extension, local_image_path,
    USER_AGENT,
)

SCRYFALL = "https://api.scryfall.com"
UUID_RE = re.compile(r"/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.[a-z]+", re.I)


def scryfall_uuid_from_url(url: str) -> str | None:
    if not url:
        return None
    m = UUID_RE.search(url)
    return m.group(1) if m else None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--cards-dir", default="cards")
    p.add_argument("--images-dir", default="cards/_images")
    p.add_argument("--game", default="Magic: The Gathering")
    p.add_argument("--limit", type=int, default=10000)
    p.add_argument("--sleep", type=float, default=0.15)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    cards_dir = Path(args.cards_dir)
    images_dir = Path(args.images_dir)
    targets: list[tuple[Path, str]] = []
    skipped_has_art = 0
    skipped_no_uuid = 0
    skipped_not_enriched = 0

    for path in cards_dir.rglob("*.md"):
        if any(p in ("_images", "_hubs", "_symbols", "_artists") for p in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = parse_frontmatter(text)
        if (fm.get("game") or "").strip() != args.game:
            continue
        tags_raw = (fm.get("tags_hub") or "").strip()
        if not tags_raw or tags_raw in ("[]", '""', "''"):
            skipped_not_enriched += 1
            continue
        existing = (fm.get("art_crop_image") or "").strip()
        if existing:
            skipped_has_art += 1
            continue
        uuid = scryfall_uuid_from_url(fm.get("reference_image_source_url") or "")
        if not uuid:
            skipped_no_uuid += 1
            continue
        targets.append((path, uuid))

    print(f"Found {len(targets)} cards to backfill art_crop")
    print(f"  (skipped: {skipped_has_art} already have art_crop, "
          f"{skipped_not_enriched} not enriched, "
          f"{skipped_no_uuid} no extractable UUID)")
    if not targets:
        return 0

    targets = targets[: args.limit]
    print(f"Processing {len(targets)} (limit={args.limit}, sleep={args.sleep}s)\n")

    filled = 0
    failed = 0
    for i, (path, uuid) in enumerate(targets, 1):
        data = http_get_json(f"{SCRYFALL}/cards/{uuid}")
        time.sleep(args.sleep)
        if not data or data.get("object") == "error":
            print(f"[{i}/{len(targets)}] {path.name}  -> Scryfall miss (uuid={uuid})")
            failed += 1
            continue
        art_url = _extract_art_crop(data) or ""
        if not art_url:
            print(f"[{i}/{len(targets)}] {path.name}  -> no art_crop URL on Scryfall record")
            failed += 1
            continue
        if args.dry_run:
            print(f"[{i}/{len(targets)}] {path.name}  -> [dry-run] would cache {art_url}")
            filled += 1
            continue
        # Mirror the prep-loop naming: <slug>--art.<ext>, beside the full card image.
        ext_full = url_extension(data.get("image_uris", {}).get("png") or ".png")
        local_full = local_image_path(path, cards_dir, images_dir, ext_full)
        art_ext = url_extension(art_url)
        art_local = local_full.with_name(local_full.stem + "--art" + art_ext)
        if not download_image(art_url, art_local, force=False):
            print(f"[{i}/{len(targets)}] {path.name}  -> download failed for {art_url}")
            failed += 1
            continue
        art_rel = str(art_local).replace("\\", "/")
        text = path.read_text(encoding="utf-8")
        text = update_frontmatter_field(text, "art_crop_image", art_rel)
        text = update_frontmatter_field(text, "art_crop_source_url", art_url)
        path.write_text(text, encoding="utf-8")
        print(f"[{i}/{len(targets)}] {path.name}  -> cached {art_local.name}")
        filled += 1

    print(f"\n=== art_crop backfill report ===")
    print(f"  Filled:  {filled}")
    print(f"  Failed:  {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
