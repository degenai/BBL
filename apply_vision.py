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
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# List fields that should be rendered in block form, not inline JSON.
_BLOCK_LIST_FIELDS = {
    "tags_hub", "tags_filter", "characters", "symbols", "bundles",
    "aliases", "appears_on", "social", "related_characters",
    "ip_resolution_for", "vision_uncertainty",
}


def _normalize_to_block_form(card_md: Path) -> None:
    try:
        content = card_md.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [warn] read failed for block-form normalize: {e}", file=sys.stderr)
        return
    lines = content.split("\n")
    out: list[str] = []
    in_fm = False
    fm_marker_count = 0
    changed = False
    for line in lines:
        if line.strip() == "---":
            fm_marker_count += 1
            out.append(line)
            in_fm = (fm_marker_count == 1)
            continue
        if in_fm and ":" in line and "[" in line:
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]
            field, _, rest = stripped.partition(":")
            rest = rest.strip()
            if (
                field in _BLOCK_LIST_FIELDS
                and rest.startswith("[") and rest.endswith("]")
                and rest != "[]"
            ):
                try:
                    items = json.loads(rest)
                except json.JSONDecodeError:
                    inner = rest[1:-1].strip()
                    items = [v.strip().strip('"').strip("'") for v in inner.split(",")]
                    items = [v for v in items if v]
                if isinstance(items, list) and items:
                    out.append(f"{indent}{field}:")
                    for item in items:
                        out.append(f"{indent}  - {item}")
                    changed = True
                    continue
        out.append(line)
    if changed:
        card_md.write_text("\n".join(out), encoding="utf-8")
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
    # Normalize inline-list frontmatter to block form so Obsidian's property panel
    # renders chips instead of a single red string. Wave 92 fix.
    _normalize_to_block_form(args.card_md)
    print(f"applied: {args.card_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
