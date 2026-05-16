"""One-shot: represent the existing Tithe sample bundle in the BBL corpus.

- Stamps `bundles: [tithe]` on each of the 9 unique cards (block form per
  wave 92 YAML discipline; normalizes via bbl_schema after write).
- Writes `bundles/proposed/tithe.json` at schema v0.3.
- Defaults bundle state to `proposed` — Alex can promote to `accepted`
  manually (sets held_for_lair) or `assembled` (subtracts quantity + archives
  zeroed-out cards).

One-shot script. Not part of the bundler agent flow.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from bbl_schema import normalize_file

ROOT = Path(__file__).parent.parent
SRC_BUNDLE = Path(r"C:\Users\alexa\Desktop\Diamondlegendz\bundle-previewer\sample-bundles\tithe.json")
DEST_DIR = ROOT / "bundles" / "proposed"
DEST_FILE = DEST_DIR / "tithe.json"

# Card path-keys in <game>/<set>/<file-stem> shape
CARD_PATHS = {
    "Wicked Guardian": "magic-the-gathering/throne-of-eldraine/109-wicked-guardian",
    "Charity Extractor": "magic-the-gathering/war-of-the-spark/81-charity-extractor",
    "Pitiless Pontiff": "magic-the-gathering/ravnica-allegiance/194-pitiless-pontiff",
    "Mortify": "magic-the-gathering/ravnica-allegiance/192-mortify",
    "Tithe Drinker": "magic-the-gathering/dragon-s-maze/109-tithe-drinker",
    "Lawmage's Binding": "magic-the-gathering/ravnica-allegiance/190-lawmage-s-binding",
    "Lunarch Mantle": "magic-the-gathering/the-list/24-lunarch-mantle",
    "Reverent Hoplite": "magic-the-gathering/theros-beyond-death/33-reverent-hoplite",
    "Secure the Scene": "magic-the-gathering/core-set-2021/35-secure-the-scene",
}


def stamp_bundles_field(md_path: Path, bundle_slug: str) -> bool:
    text = md_path.read_text(encoding="utf-8")
    m = re.match(r"^(---\s*\n)(.*?)(\n---\s*\n)", text, re.DOTALL)
    if not m:
        print(f"  no frontmatter: {md_path}")
        return False
    fm_text = m.group(2)
    # Existing bundles field?
    inline = re.search(r"^bundles:\s*\[(.*?)\]\s*$", fm_text, re.MULTILINE)
    block = re.search(r"^bundles:\s*\n((?:  -\s+.*\n)+)", fm_text, re.MULTILINE)
    if block:
        items = re.findall(r"^  -\s+(.*?)\s*$", block.group(1), re.MULTILINE)
        if bundle_slug in items:
            return False
        new_block = block.group(0).rstrip("\n") + f"\n  - {bundle_slug}\n"
        new_fm = fm_text[: block.start()] + new_block + fm_text[block.end():]
    elif inline:
        inner = inline.group(1).strip()
        items = [x.strip().strip('"').strip("'") for x in inner.split(",")] if inner else []
        if bundle_slug in items:
            return False
        items.append(bundle_slug)
        new_inline = "bundles:\n" + "\n".join(f"  - {x}" for x in items if x)
        new_fm = fm_text[: inline.start()] + new_inline + fm_text[inline.end():]
    else:
        # No bundles field at all (rare); append before close marker
        new_fm = fm_text.rstrip("\n") + f"\nbundles:\n  - {bundle_slug}"
    new_text = m.group(1) + new_fm + m.group(3) + text[m.end():]
    md_path.write_text(new_text, encoding="utf-8")
    normalize_file(md_path)
    return True


def build_v3_bundle(src: dict) -> dict:
    """Upgrade v0.2 sample bundle to v0.3 schema."""
    new_cards = []
    for card in src["cards"]:
        path_key = CARD_PATHS[card["name"]]
        new_cards.append({
            "card_md_path": path_key,
            "name": card["name"],
            "set": card["set"],
            "collector_number": card["collector_number"],
            "qty_in_bundle": card.get("qty_in_bundle", 1),
            "tags_matched": card.get("tags_matched", []),
            "market_price_usd": card.get("market_price_usd", 0.0),
            "market_price_as_of": card.get("market_price_as_of", ""),
            "market_price_source": card.get("market_price_source", ""),
            "image_url": card.get("image_url", ""),
            "art_crop_url": card.get("art_crop_url", ""),
            "why_it_fits": card.get("why_it_fits", ""),
        })
    return {
        "schema_version": "0.3",
        "status": "proposed",
        "slug": "tithe",
        "series_label": src.get("series_label", "Discrete Lair"),
        "catalog_id": src.get("catalog_id", ""),
        "title": src["title"],
        "subtitle": src.get("subtitle", ""),
        "narrative": src["narrative"],
        "hubs": src.get("hubs", []),
        "anchor_tags": src.get("anchor_tags", []),
        "intent_tags": src.get("intent_tags", []),
        "cards": new_cards,
        "cohesion": src.get("cohesion", {}),
        "pricing": src.get("pricing", {}),
        "checkout": src.get("checkout", {}),
        "overlap_bundles": [],
        "lifecycle": {
            "proposed_at": src.get("metadata", {}).get("generated_at", date.today().isoformat()),
            "accepted_at": None,
            "assembled_at": None,
        },
        "metadata": {
            **src.get("metadata", {}),
            "ported_to_v3_at": date.today().isoformat(),
            "ported_to_v3_by": "scripts/stamp_tithe_bundle.py",
            "note": "Originally hand-curated v0.2 (manual-curation-v0). Imported into BBL corpus 2026-05-16 wave 92.5 as the first canonical proposed bundle record. State left at `proposed` pending Alex's acceptance decision.",
        },
    }


def main():
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    src = json.loads(SRC_BUNDLE.read_text(encoding="utf-8"))

    # Step 1 — stamp bundles: [tithe] on each card
    stamped_count = 0
    for card_name, path_key in CARD_PATHS.items():
        md_path = ROOT / "cards" / f"{path_key}.md"
        if not md_path.exists():
            print(f"MISS: {md_path}")
            continue
        changed = stamp_bundles_field(md_path, "tithe")
        status = "STAMPED" if changed else "already-has-tithe"
        print(f"  {status}: {card_name}")
        if changed:
            stamped_count += 1

    # Step 2 — write v0.3 bundle JSON
    v3 = build_v3_bundle(src)
    DEST_FILE.write_text(json.dumps(v3, indent=2), encoding="utf-8")
    print(f"\nWrote {DEST_FILE} (schema v0.3)")
    print(f"Stamped bundles:[tithe] on {stamped_count} cards")


if __name__ == "__main__":
    main()
