#!/usr/bin/env python3
"""Janitor sweep — dissolve `### Related cards` bullets that duplicate
edges the cohort node already articulates.

Surfaced by snip-frenzy Edgelord #2 (wave 123) after the Solrock DAA-092
snip exposed the pattern across 6 elemental-monkey cards + 2 lunatone
cards. Cohort nodes (`elemental-monkey-trio`, `solrock-lunatone-pair`)
already carry the sibling-mirror tissue at the cohort scope; per-card
bullets restating "trio-companion / pair-counterpart" are redundant.

GUARDRAILS:
- Preserve cross-print same-species mirrors (e.g. Lunatone BUS-68
  pointing at "Lunatone other prints") — those are per-print continuity,
  not cohort redundancy.
- Skip simisage DAA-007 (no `## Connections` section yet; needs an
  enlightened-replacement pass that ADDS the Connections section
  before removing the bullets — not a clean janny op).
- Skip pansage BUS-12 "Simisear (Darkness Ablaze...) — already in corpus"
  bullet IF treated as a legitimate cross-corpus inventory note; per
  snip-frenzy sidecar `other_candidates_considered` it's also flagged
  redundant. Snipping per that judgment.

Per-file snip lists are hand-curated from snip-frenzy sidecar's
`other_candidates_considered` section.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

# Format: {card_path: [list of bullet substrings to remove from `### Related cards`]}
# Match is "line starts with `- ` and contains this substring" — substring picked
# to be unique enough not to match preserved bullets.
SNIPS = {
    "cards/pokemon/burning-shadows/12-147-pansage.md": [
        "Simisage (any set)",
        "Pansear (any set)",
        "Panpour (any set)",
        "Simisear (Darkness Ablaze",
    ],
    "cards/pokemon/burning-shadows/22-147-pansear.md": [
        "Panpour (Burning Shadows, 36/147)",
        "Pansage (multiple prints)",
        "Simisear (multiple prints)",
        # PRESERVE: [[elemental-monkey-trio]] cohort link bullet
    ],
    "cards/pokemon/burning-shadows/36-147-panpour.md": [
        "Pansear (Burning Shadows, 22/147)",
        "Pansage (multiple prints)",
        "Simipour (multiple prints)",
        # PRESERVE: [[elemental-monkey-trio]] cohort link bullet
    ],
    "cards/pokemon/burning-shadows/68-147-lunatone.md": [
        "Solrock (DAA-092)",
        # PRESERVE: "Lunatone (other prints)" — cross-print same-species
    ],
    "cards/pokemon/darkness-ablaze/006-189-pansage.md": [
        # PRESERVE first bullet: "Pansage (Burning Shadows, BUS-12)" — cross-print same-species
        "Pansear (various)",
        "Panpour (various)",
        "Simisage (various)",
    ],
    "cards/pokemon/darkness-ablaze/027-189-simisear.md": [
        # All 4 bullets are trio-sibling redundancy (Simisear has no other same-species
        # cross-print in corpus, so no cross-print mirror to preserve)
        "Pansear (any set)",
        "Simisage (any set)",
        "Simipour (any set)",
        "Pansage (Burning Shadows, no. 12/147)",
    ],
    "cards/pokemon/darkness-ablaze/072-189-lunatone.md": [
        "Solrock (Darkness Ablaze",
        # PRESERVE: "Lunatone (Burning Shadows" — cross-print same-species
    ],
    # SKIPPED: cards/pokemon/darkness-ablaze/007-189-simisage.md
    #   (no Connections section yet; needs enlightened-replacement
    #    pass that adds Connections before snipping)
}


def snip_bullets_in_related_cards_section(text, snip_substrings):
    """Remove bullet lines from the `### Related cards` section that contain
    any of the snip_substrings. Returns (new_text, snipped_lines)."""
    if not snip_substrings:
        return text, []
    lines = text.splitlines(keepends=True)
    in_section = False
    snipped = []
    out = []
    for line in lines:
        if line.startswith("### Related cards"):
            in_section = True
            out.append(line)
            continue
        if in_section and line.startswith("## "):
            # next section started
            in_section = False
            out.append(line)
            continue
        if in_section and line.startswith("### ") and not line.startswith("### Related cards"):
            in_section = False
            out.append(line)
            continue
        if in_section and line.startswith("- ") and any(s in line for s in snip_substrings):
            snipped.append(line.rstrip())
            continue
        out.append(line)
    return "".join(out), snipped


def main():
    total_snipped = 0
    files_touched = []
    for rel, snips in SNIPS.items():
        if not snips:
            continue
        path = REPO / rel
        if not path.exists():
            print(f"MISS {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        new_text, snipped = snip_bullets_in_related_cards_section(text, snips)
        if snipped:
            path.write_text(new_text, encoding="utf-8")
            files_touched.append(rel)
            total_snipped += len(snipped)
            print(f"\n{rel}  ({len(snipped)} snipped)")
            for s in snipped:
                print(f"  - {s[:120]}")
    print(f"\n=== total: {total_snipped} bullets snipped across {len(files_touched)} files ===")


if __name__ == "__main__":
    main()
