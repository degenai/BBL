#!/usr/bin/env python3
"""apply_vision — write a vision JSON payload onto a card-MD via researchbot.update_card.

Used by the bbl-researcher Claude Code subagent: the subagent generates the structured
vision JSON, drops it on disk, and calls this helper to apply it. Single source of truth
for the on-disk format stays in researchbot.update_card.

Usage:
    python apply_vision.py <card_md_path> <vision_json_path>

The vision JSON file must contain a top-level object with these keys (extras ignored):
    subject, subject_known_ip, suspected_ip, ip_confidence, ip_verified,
    description, facing, composition, mode, figure_count,
    foreground, foreground_palette, background, background_palette,
    setting, architecture, time_of_day, weather,
    mood, genre_cues, lighting,
    objects, animals_creatures, food_drink, clothing_style, iconography, emotion,
    tags_hub, tags_filter

If `tags_hub` is empty the helper exits non-zero — that's the contract: the subagent
must produce hub tags for a successful enrichment.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from researchbot import parse_frontmatter, update_card  # type: ignore


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("card_md", type=Path, help="Path to the card-node MD file")
    ap.add_argument("vision_json", type=Path, help="Path to a JSON file with vision payload")
    ap.add_argument("--art-confidence", default="high", choices=["high", "low", "none"])
    ap.add_argument("--manual-review-reason", default="")
    args = ap.parse_args()

    if not args.card_md.exists():
        print(f"ERROR: card MD not found: {args.card_md}", file=sys.stderr)
        return 1
    if not args.vision_json.exists():
        print(f"ERROR: vision JSON not found: {args.vision_json}", file=sys.stderr)
        return 1

    try:
        vision = json.loads(args.vision_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: vision JSON malformed: {e}", file=sys.stderr)
        return 1

    if not isinstance(vision, dict):
        print("ERROR: vision JSON top-level must be an object", file=sys.stderr)
        return 1

    if not vision.get("tags_hub"):
        print("ERROR: vision JSON has empty tags_hub — refuse to apply.", file=sys.stderr)
        return 2

    # Read frontmatter for the cached image path so the body embed survives the rewrite.
    fm = parse_frontmatter(args.card_md.read_text(encoding="utf-8"))
    local_rel = fm.get("reference_image", "") or ""
    source_url = fm.get("reference_image_source_url", "") or local_rel

    update_card(
        path=args.card_md,
        image_url=source_url,
        vision=vision,
        dry_run=False,
        art_confidence=args.art_confidence,
        manual_review_reason=args.manual_review_reason,
        local_image_rel=local_rel,
    )
    print(f"applied: {args.card_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
