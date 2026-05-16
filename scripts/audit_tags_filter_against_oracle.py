"""
audit_tags_filter_against_oracle - MTG color-magic tag audit.

Per the wave-49 finding (Manifest Dread + Dragon Trainer + Bulma): the vision
agent has historically inferred `tags_filter` color-magic values from art
palette instead of mana cost, producing factually wrong color tags. The
wave-92.5 spec amendment (bbl-researcher.md line 44) forbids palette-as-
color-source going forward, but the existing corpus carries inherited debt.

This audit walks every MTG card with `mana_cost` populated, derives the
ground-truth color identity from the mana symbols, and flags any
disagreement with the card's `tags_filter` color entries.

Output: per-mismatch one-liner + summary counts. Read-only; does NOT patch.

Usage:
    python scripts/audit_tags_filter_against_oracle.py
    python scripts/audit_tags_filter_against_oracle.py --json out.json
    python scripts/audit_tags_filter_against_oracle.py --limit 50
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
MTG_DIR = ROOT / "cards" / "magic-the-gathering"

# Canonical color-magic tags this audit cares about. Flavor tags like
# `nature-magic`, `dark-magic`, `elemental-magic` are NOT checked — they
# describe theme, not mechanical color identity.
CANONICAL_COLOR_TAGS = {
    "white-magic": frozenset({"W"}),
    "blue-magic": frozenset({"U"}),
    "black-magic": frozenset({"B"}),
    "red-magic": frozenset({"R"}),
    "green-magic": frozenset({"G"}),
    "colorless-magic": frozenset(),
    "colorless": frozenset(),
    "multicolored": "MULTI_GENERIC",  # any 2+ color combination
}

COLOR_SYMBOL_TO_LETTER = {
    "W": "W", "U": "U", "B": "B", "R": "R", "G": "G",
}

COLOR_LETTER_TO_NAME = {
    "W": "white", "U": "blue", "B": "black", "R": "red", "G": "green",
}


def parse_mana_cost(mana_cost: str) -> frozenset[str]:
    """Return the set of color letters {W,U,B,R,G} present in a Scryfall
    mana_cost string like `{1}{G}` or `{X}{U}{R}` or `{2/W}{W/U}`. Hybrid
    symbols count as both colors. Generic, X, snow, and other non-color
    symbols are ignored."""
    if not mana_cost:
        return frozenset()
    cleaned = mana_cost.strip(' "\'')
    if not cleaned:
        return frozenset()
    # Match all bracketed symbols
    symbols = re.findall(r"\{([^}]+)\}", cleaned)
    colors: set[str] = set()
    for sym in symbols:
        # Split hybrid symbols like W/U, 2/W, R/P
        parts = sym.split("/")
        for p in parts:
            p = p.upper().strip()
            if p in COLOR_SYMBOL_TO_LETTER:
                colors.add(COLOR_SYMBOL_TO_LETTER[p])
    return frozenset(colors)


def derive_expected_tag(actual_colors: frozenset[str]) -> str:
    """Map the actual color set to the canonical color-magic tag."""
    if not actual_colors:
        return "colorless-magic"
    if len(actual_colors) == 1:
        letter = next(iter(actual_colors))
        return f"{COLOR_LETTER_TO_NAME[letter]}-magic"
    # Multicolor — pick the deterministic name. BBL convention is
    # `multicolor-<c1>-<c2>` in WUBRG order.
    wubrg_order = [c for c in "WUBRG" if c in actual_colors]
    names = [COLOR_LETTER_TO_NAME[l] for l in wubrg_order]
    return f"multicolor-{'-'.join(names)}"


def parse_block_list(fm_text: str, field: str) -> list[str]:
    """Read a block-form list field's items."""
    m = re.search(rf"^{re.escape(field)}:\s*\n((?:  -\s+.*(?:\n|$))+)",
                  fm_text, re.MULTILINE)
    if not m:
        # Try inline form as fallback (shouldn't exist post-wave-92)
        inline = re.search(rf"^{re.escape(field)}:\s*\[([^\]]*)\]\s*$",
                           fm_text, re.MULTILINE)
        if inline:
            inner = inline.group(1).strip()
            if not inner:
                return []
            return [v.strip().strip('"').strip("'") for v in inner.split(",")]
        return []
    items = re.findall(r"^  -\s+(.+?)\s*$", m.group(1), re.MULTILINE)
    return [v.strip().strip('"').strip("'") for v in items if v.strip()]


def extract_color_tags(tags_filter: list[str]) -> set[str]:
    """Return the set of canonical color-magic tags on the card."""
    out: set[str] = set()
    for t in tags_filter:
        if t in CANONICAL_COLOR_TAGS:
            out.add(t)
            continue
        if t.startswith("multicolor-"):
            # Verify it's a legitimate 2+ color combo string, not a flavor riff
            tail = t[len("multicolor-"):]
            parts = tail.split("-")
            if all(p in COLOR_LETTER_TO_NAME.values() for p in parts) and len(parts) >= 2:
                out.add(t)
    return out


def parse_frontmatter(text: str) -> str | None:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    return m.group(1) if m else None


def _multicolor_set(tag: str) -> frozenset[str] | None:
    """Parse a `multicolor-<c1>-<c2>...` tag back into the color-letter set.
    Returns None if the tag isn't a well-formed multicolor combo."""
    if not tag.startswith("multicolor-"):
        return None
    parts = tag[len("multicolor-"):].split("-")
    name_to_letter = {v: k for k, v in COLOR_LETTER_TO_NAME.items()}
    letters: set[str] = set()
    for p in parts:
        if p not in name_to_letter:
            return None
        letters.add(name_to_letter[p])
    if len(letters) < 2:
        return None
    return frozenset(letters)


def _is_color_equivalent(stated: str, expected: str) -> bool:
    """Return True if stated tag matches expected, allowing for:
    - `colorless` ≡ `colorless-magic`
    - `multicolor-X-Y` ≡ `multicolor-Y-X` (order-independent)
    """
    if stated == expected:
        return True
    colorless_aliases = {"colorless", "colorless-magic"}
    if stated in colorless_aliases and expected in colorless_aliases:
        return True
    stated_set = _multicolor_set(stated)
    expected_set = _multicolor_set(expected)
    if stated_set and expected_set and stated_set == expected_set:
        return True
    return False


def audit_card(path: Path) -> dict | None:
    """Return mismatch dict, or None if card passes / is skipped."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    fm = parse_frontmatter(text)
    if not fm:
        return None
    mana_cost_m = re.search(r"^mana_cost:\s*(.*?)\s*$", fm, re.MULTILINE)
    if not mana_cost_m:
        return None
    mana_cost = mana_cost_m.group(1).strip(' "\'')
    actual_colors = parse_mana_cost(mana_cost)
    expected_tag = derive_expected_tag(actual_colors)

    # Devoid exception: cards with the Devoid keyword are mechanically
    # colorless regardless of mana cost (BFZ Eldrazi). The vision-tagger
    # correctly calls them colorless; this audit must agree.
    oracle_text_m = re.search(r"^oracle_text:\s*(.*?)\s*$", fm, re.MULTILINE)
    oracle_text = oracle_text_m.group(1).strip(' "\'') if oracle_text_m else ""
    is_devoid = "Devoid" in oracle_text
    if is_devoid:
        expected_tag = "colorless-magic"

    tags_filter = parse_block_list(fm, "tags_filter")
    if not tags_filter:
        return None
    stated_color_tags = extract_color_tags(tags_filter)
    if not stated_color_tags:
        return None

    # Match: any stated tag color-equivalent to expected
    matched = any(_is_color_equivalent(s, expected_tag) for s in stated_color_tags)
    # `multicolored` generic counts as a match for any 2+ color expected
    if "multicolored" in stated_color_tags and len(actual_colors) >= 2:
        matched = True

    if matched:
        # Check for ALSO-present wrong tags (e.g., correct green-magic AND wrong blue-magic)
        wrong_extras = {s for s in stated_color_tags
                        if not _is_color_equivalent(s, expected_tag)
                        and s != "multicolored"}
        if not wrong_extras:
            return None
        return {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "mana_cost": mana_cost,
            "expected_tag": expected_tag,
            "stated_tags": sorted(stated_color_tags),
            "wrong_extras": sorted(wrong_extras),
            "severity": "wrong-extra-tag",
            "devoid": is_devoid,
        }
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "mana_cost": mana_cost,
        "expected_tag": expected_tag,
        "stated_tags": sorted(stated_color_tags),
        "severity": "missing-or-wrong-color",
        "devoid": is_devoid,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--json", type=Path, default=None,
                    help="Optional output path for JSON dump of mismatches.")
    args = ap.parse_args()

    targets = sorted(MTG_DIR.rglob("*.md"))
    if args.limit:
        targets = targets[: args.limit]

    mismatches: list[dict] = []
    examined = 0
    skipped = 0
    for p in targets:
        result = audit_card(p)
        if result is None:
            skipped += 1
            continue
        examined += 1
        mismatches.append(result)

    examined_total = examined + skipped
    print(f"\n--- Color-magic tag audit ({examined_total} MTG cards scanned) ---")
    print(f"  Cards with mana_cost + color tags compared: {examined}")
    print(f"  Cards skipped (no mana_cost, not vision-passed, or no color claim): {skipped}")
    print(f"  Mismatches: {len(mismatches)}")
    print()

    by_severity: dict[str, list[dict]] = {}
    for m in mismatches:
        by_severity.setdefault(m["severity"], []).append(m)

    for severity, items in by_severity.items():
        print(f"\n=== {severity} ({len(items)}) ===")
        for m in items[:50]:
            extras = f"  (also wrong: {m.get('wrong_extras')})" if m.get("wrong_extras") else ""
            print(f"  {m['path']}")
            print(f"    mana_cost={m['mana_cost']!r}  expected={m['expected_tag']!r}  stated={m['stated_tags']}{extras}")
        if len(items) > 50:
            print(f"  ... and {len(items) - 50} more")

    if args.json:
        args.json.write_text(json.dumps(mismatches, indent=2), encoding="utf-8")
        print(f"\nJSON dump: {args.json}")

    return 0 if not mismatches else 2


if __name__ == "__main__":
    sys.exit(main())
