#!/usr/bin/env python3
"""tts_dbs_extract — Extract high-res DBSCG card images from the KOLegend
TTS workshop mod (Steam Workshop ID 3133475660 — "Dragon Ball Super Card
Game Masters/Fusion World TS").

The mod's cached JSON has 9,449 Card objects with FaceURL fields pointing
to Steam's public CDN at 624-640px. That's ~2.4x Bandai's linear resolution
and covers the entire legacy DBSCG corpus plus Fusion World.

Workflow:
1. Parse the mod JSON for (nickname, face_url) pairs
2. Extract collector_number from each nickname (format: "(cost) Name - CN")
3. For each corpus card in cards/dragon-ball-super/*, look up its CN in the
   mod index. If match, download FaceURL into cards/_images/dragon-ball-super/
   <set>/<slug>.png replacing the existing Bandai 260px file.
4. Update card frontmatter: reference_image_source_url, image_width,
   image_height, image_quality. art_match_confidence stays high.

Usage:
    python scripts/tts_dbs_extract.py                  # dry-run (preview)
    python scripts/tts_dbs_extract.py --apply          # actually do it
    python scripts/tts_dbs_extract.py --apply --limit 10  # test on 10 cards first
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

# Hardcoded path to the KOLegend mod JSON in Alex's TTS cache.
# If the mod is unsubscribed/replaced, point this at whichever cached JSON
# has the largest FaceURL count (run: rg -c "FaceURL" *.json).
MOD_JSON = Path.home() / "Documents" / "My Games" / "Tabletop Simulator" / "Mods" / "Workshop" / "3133475660.json"

REPO_ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = REPO_ROOT / "cards" / "dragon-ball-super"
IMAGES_DIR = REPO_ROOT / "cards" / "_images" / "dragon-ball-super"

# Quality buckets — match researchbot.py constants
IMAGE_QUALITY_HIGH_MIN = 700
IMAGE_QUALITY_MED_MIN = 400

UA = "BBL-tts-extract/0.1 (alex.adamczyk@gmail.com)"


def find_card_objects(obj):
    """Recursively yield (nickname, face_url) tuples from a TTS save JSON."""
    if isinstance(obj, dict):
        if obj.get("Name") in ("Card", "CardCustom"):
            cd = obj.get("CustomDeck", {})
            face = None
            for v in cd.values():
                if isinstance(v, dict) and v.get("FaceURL"):
                    face = v["FaceURL"]
                    break
            yield (obj.get("Nickname", ""), face)
        for v in obj.values():
            yield from find_card_objects(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from find_card_objects(v)


CN_RE = re.compile(r"-\s*([A-Z]+[0-9]+-[A-Z0-9-]+)\s*$", re.IGNORECASE)


def parse_collector_number(nickname: str) -> str | None:
    """Extract DBSCG collector number from a TTS Nickname like
    '(7) God Break Son Goku - BT1-031'."""
    m = CN_RE.search(nickname.strip())
    if not m:
        return None
    return m.group(1).strip().upper()


def build_mod_index() -> dict[str, str]:
    """Returns {collector_number: face_url}. Dedupes on first occurrence."""
    if not MOD_JSON.exists():
        sys.exit(f"ERROR: Mod JSON not in TTS cache yet — load mod 3133475660 in TTS to populate.\n  Expected: {MOD_JSON}")
    with open(MOD_JSON, encoding="utf-8") as f:
        data = json.load(f)
    index: dict[str, str] = {}
    for nickname, face_url in find_card_objects(data):
        if not face_url:
            continue
        cn = parse_collector_number(nickname)
        if not cn:
            continue
        index.setdefault(cn, face_url)
    return index


def scan_corpus() -> list[tuple[str, Path]]:
    """Returns [(collector_number, card_md_path)] for all DBS corpus cards."""
    out = []
    for f in CARDS_DIR.rglob("*.md"):
        with open(f, encoding="utf-8") as fh:
            body = fh.read()
        m = re.search(r"^collector_number:\s*([^\n]+)", body, re.MULTILINE)
        if not m:
            continue
        cn = m.group(1).strip().upper()
        out.append((cn, f))
    return out


def measure_image(path: Path) -> tuple[int, int, str]:
    """(w, h, quality_bucket) — same logic as researchbot.measure_image."""
    try:
        from PIL import Image
    except ImportError:
        return 0, 0, "unknown"
    try:
        with Image.open(path) as im:
            w, h = im.size
    except Exception:
        return 0, 0, "unknown"
    if w >= IMAGE_QUALITY_HIGH_MIN:
        return w, h, "high"
    if w >= IMAGE_QUALITY_MED_MIN:
        return w, h, "med"
    return w, h, "low"


def download_image(url: str, dest: Path, force: bool = False) -> bool:
    """Mirror researchbot.download_image — local copy to avoid import surface."""
    if dest.exists() and not force:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            dest.write_bytes(r.read())
        return True
    except Exception as e:
        print(f"  [warn] download failed ({url[:80]}...): {e}", file=sys.stderr)
        return False


def update_frontmatter_field(text: str, field: str, value: str) -> str:
    """Idempotent: replace existing line or insert before --- close."""
    line_re = re.compile(rf"^{re.escape(field)}:\s*[^\n]*$", re.MULTILINE)
    new_line = f"{field}: {value}"
    if line_re.search(text):
        return line_re.sub(new_line, text, count=1)
    # Insert before the closing --- of the frontmatter
    return re.sub(r"^---\s*$", f"{new_line}\n---", text, count=1, flags=re.MULTILINE)


def existing_image_path(card_md: Path) -> Path:
    """Compute the local image path mirroring researchbot's layout:
    cards/dragon-ball-super/<set>/<slug>.md → cards/_images/dragon-ball-super/<set>/<slug>.png"""
    rel = card_md.relative_to(CARDS_DIR.parent)
    return CARDS_DIR.parent.parent / "cards" / "_images" / rel.with_suffix(".png")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true",
                    help="Actually download and update; otherwise dry-run preview.")
    ap.add_argument("--limit", type=int, default=0,
                    help="Cap number of cards processed (0 = all matching).")
    ap.add_argument("--force", action="store_true",
                    help="Re-download even if local image already exists.")
    args = ap.parse_args()

    print(f"Loading mod JSON: {MOD_JSON}")
    mod_index = build_mod_index()
    print(f"  Mod cards indexed by collector_number: {len(mod_index)}\n")

    corpus = scan_corpus()
    print(f"Corpus DBS cards: {len(corpus)}\n")

    matched = [(cn, md) for cn, md in corpus if cn in mod_index]
    missing = [cn for cn, md in corpus if cn not in mod_index]
    print(f"Matched in mod: {len(matched)} / {len(corpus)}  ({100*len(matched)//len(corpus)}%)")
    print(f"Missing from mod: {len(missing)}")
    if missing[:5]:
        print(f"  Sample missing CNs: {missing[:5]}")
    print()

    if not args.apply:
        print("DRY-RUN: pass --apply to actually download and update frontmatter.")
        return 0

    if args.limit and len(matched) > args.limit:
        matched = matched[:args.limit]
        print(f"LIMIT: processing first {len(matched)} matches only.\n")

    n_downloaded = n_skipped = n_updated = n_failed = 0
    for cn, md in matched:
        url = mod_index[cn]
        local_path = existing_image_path(md)
        # Force-download (the previous Bandai 260px file is what we're replacing)
        if download_image(url, local_path, force=args.force or True):
            w, h, q = measure_image(local_path)
            print(f"  {cn:12s}  -> {w}x{h} {q}  ({md.name})")
            n_downloaded += 1
            # Update frontmatter
            body = md.read_text(encoding="utf-8")
            body = update_frontmatter_field(body, "reference_image_source_url", url)
            body = update_frontmatter_field(body, "image_width", str(w))
            body = update_frontmatter_field(body, "image_height", str(h))
            body = update_frontmatter_field(body, "image_quality", q)
            md.write_text(body, encoding="utf-8")
            n_updated += 1
            time.sleep(0.1)  # courteous pacing against Steam CDN
        else:
            n_failed += 1

    print()
    print(f"=== TTS DBS extract done ===")
    print(f"  Downloaded:     {n_downloaded}")
    print(f"  Frontmatter:    {n_updated}")
    print(f"  Failed:         {n_failed}")
    print(f"  Missing in mod: {len(missing)} (these stay on Bandai/dbzexchange via researchbot.py)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
