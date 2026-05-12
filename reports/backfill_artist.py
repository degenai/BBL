#!/usr/bin/env python3
"""
backfill_artist — One-shot pass to populate `artist:` frontmatter on enriched MTG cards.

The artist field went un-captured for the first 597 MTG enrichments because researchbot
only pulled image_url + collector_number from Scryfall, not artist. Researchbot is now
fixed (commit pending). This script walks the existing corpus and backfills the gap.

Strategy:
  1. Find every card with reference_image_source_url that points at a Scryfall UUID
     (cards.scryfall.io/.../<uuid>.png pattern).
  2. Hit /cards/<uuid> on the Scryfall API — exact lookup, no fuzzy fallback, no
     wrong-printing risk because the UUID identifies the specific printing we cached.
  3. Stamp the artist into frontmatter via update_frontmatter_field.

Idempotent: skips cards that already have a non-empty `artist:` value.

Usage:
  python reports/backfill_artist.py [--dry-run] [--limit N] [--sleep S]
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, urllib.request
from pathlib import Path

# Force UTF-8 stdout — artist names contain accented characters (Magic artists like
# Igor Kieryluk, Jaime Jones, Slawomir Maniak, Eric Deschamps, etc) and Windows
# defaults to cp1252 which can't render every glyph.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from researchbot import (
    parse_frontmatter, update_frontmatter_field, http_get_json, USER_AGENT,
)

SCRYFALL = "https://api.scryfall.com"
UUID_RE = re.compile(r"/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.[a-z]+", re.I)


def scryfall_uuid_from_url(url: str) -> str | None:
    if not url:
        return None
    m = UUID_RE.search(url)
    return m.group(1) if m else None


def fetch_artist(uuid: str) -> str:
    """Hit /cards/<uuid> and extract artist. Handles double-faced via card_faces[0]."""
    data = http_get_json(f"{SCRYFALL}/cards/{uuid}")
    if not data or data.get("object") == "error":
        return ""
    artist = (data.get("artist") or "").strip()
    if artist:
        return artist
    faces = data.get("card_faces") or []
    if faces and isinstance(faces, list):
        return (faces[0].get("artist") or "").strip()
    return ""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--cards-dir", default="cards")
    p.add_argument("--game", default="Magic: The Gathering")
    p.add_argument("--limit", type=int, default=10000)
    p.add_argument("--sleep", type=float, default=0.1, help="Seconds between Scryfall calls")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    cards_dir = Path(args.cards_dir)
    targets: list[tuple[Path, str]] = []
    skipped_has_artist = 0
    skipped_no_uuid = 0
    skipped_not_enriched = 0

    for path in cards_dir.rglob("*.md"):
        if "_images" in path.parts or "_hubs" in path.parts or "_symbols" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = parse_frontmatter(text)
        if (fm.get("game") or "").strip() != args.game:
            continue
        # Only backfill enriched cards (tags_hub non-empty) — unenriched cards will
        # get artist on their next prep run via the fixed researchbot.
        tags_raw = (fm.get("tags_hub") or "").strip()
        if not tags_raw or tags_raw in ("[]", '""', "''"):
            skipped_not_enriched += 1
            continue
        existing_artist = (fm.get("artist") or "").strip()
        if existing_artist:
            skipped_has_artist += 1
            continue
        uuid = scryfall_uuid_from_url(fm.get("reference_image_source_url") or "")
        if not uuid:
            skipped_no_uuid += 1
            continue
        targets.append((path, uuid))

    print(f"Found {len(targets)} cards to backfill")
    print(f"  (skipped: {skipped_has_artist} already have artist, "
          f"{skipped_not_enriched} not enriched, "
          f"{skipped_no_uuid} no extractable UUID)")
    if not targets:
        return 0

    targets = targets[: args.limit]
    print(f"Processing {len(targets)} (limit={args.limit}, sleep={args.sleep}s)\n")

    filled = 0
    failed = 0
    for i, (path, uuid) in enumerate(targets, 1):
        artist = fetch_artist(uuid)
        time.sleep(args.sleep)
        if not artist:
            print(f"[{i}/{len(targets)}] {path.name}  -> no artist returned (uuid={uuid})")
            failed += 1
            continue
        if args.dry_run:
            print(f"[{i}/{len(targets)}] {path.name}  -> [dry-run] would stamp artist={artist}")
            filled += 1
            continue
        text = path.read_text(encoding="utf-8")
        text = update_frontmatter_field(text, "artist", artist)
        path.write_text(text, encoding="utf-8")
        print(f"[{i}/{len(targets)}] {path.name}  -> {artist}")
        filled += 1

    print(f"\n=== backfill report ===")
    print(f"  Filled:  {filled}")
    print(f"  Failed:  {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
