#!/usr/bin/env python3
"""Janny sweep — convert schema-precedent [[nicol-bolas]] wikilinks to
backticks across character node bodies.

The user surfaced via mobile graph view that ~25 character nodes have
DIRECT wikilink edges to nicol-bolas. Audit traced these to the wave-71
"Modeled as a character-layer solo node like [[nicol-bolas]]" pattern
and the "Following the [[nicol-bolas]] precedent..." pattern that
proliferated across solo-character-node commissioning waves.

Per bbl-wikilink-vs-backtick-discipline:
- Wikilinks for real-thematic edges only
- Backticks for schema/architectural-precedent citations

Heuristic detection of schema-precedent context (any line containing
[[nicol-bolas]] AND one of these phrases gets converted):
  - "precedent"
  - "Modeled as"
  - "Following the"
  - "single-character pattern"
  - "structural-template"
  - "sibling solo-character-node"
  - "Like [[" or "like [[" (peer-listing pattern)
  - "structural precedent"
  - "multi-aspect single-character"
  - "character-anchor membership"

PRESERVE (manual review needed):
- kaya.md line 117 — canonical WAR adversarial-sibling (real story edge)
- bardock.md line 141 — cross-universe structural-parallel (borderline,
  but reads as REAL curatorial thesis pairing not just template citation)

Idempotent. Run via:
  python reports/_scratch/janny_bolas_schema_precedent_sweep.py
"""
from pathlib import Path
import re

REPO = Path(__file__).resolve().parent.parent.parent

# Phrases that flag the context as schema-precedent (snip-eligible)
SCHEMA_PHRASES = [
    "precedent",
    "Modeled as",
    "modeled as",
    "Following the",
    "following the",
    "single-character pattern",
    "structural-template",
    "structural template",
    "sibling solo-character-node",
    "single-character precedent",
    "multi-aspect single-character",
    "character-anchor membership",
    "structural precedent",
    "structural-precedent",
    "Like [[",
    "like [[",
    "single named individual",
    "named individual rather than a faction",
    "previously-flagged-and-now-commissioned",
    "anchor-attribution",
    "anchor count clears",
    "threshold rigor-bar",
    "load-bearing-name",
    "cross-universe structural-parallel",  # bardock line 141 — also schema-shaped
]

# Files / specific lines to preserve (real-thematic edges).
# Key: rel_path. Value: list of line-number ranges (inclusive 1-based) NOT to touch.
PRESERVE_LINES = {
    "cards/_characters/kaya.md": [(117, 117)],  # canonical adversarial-sibling for WAR Gatewatch resistance
}


def is_schema_context(line: str) -> bool:
    return any(p in line for p in SCHEMA_PHRASES)


def in_preserve_range(rel: str, lineno: int) -> bool:
    ranges = PRESERVE_LINES.get(rel, [])
    return any(a <= lineno <= b for (a, b) in ranges)


def safe_print(s: str) -> None:
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("ascii", errors="replace").decode("ascii"))


def main():
    matches = list((REPO / "cards").rglob("*.md"))
    total_snipped = 0
    total_preserved = 0
    files_touched = []
    for path in matches:
        rel = str(path.relative_to(REPO)).replace("\\", "/")
        if rel == "cards/_characters/nicol-bolas.md":
            continue  # don't touch the node itself
        if "/_hubs/" in rel:
            continue  # hub bodies use [[character]] differently
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "[[nicol-bolas]]" not in text:
            continue
        lines = text.splitlines(keepends=True)
        new_lines = []
        snipped_here = []
        preserved_here = []
        for i, line in enumerate(lines, 1):
            if "[[nicol-bolas]]" not in line:
                new_lines.append(line)
                continue
            if in_preserve_range(rel, i):
                preserved_here.append((i, line.rstrip()[:140]))
                new_lines.append(line)
                continue
            if is_schema_context(line):
                # convert ALL [[nicol-bolas]] on this line to `nicol-bolas`
                new_line = line.replace("[[nicol-bolas]]", "`nicol-bolas`")
                snipped_here.append((i, line.rstrip()[:140]))
                new_lines.append(new_line)
            else:
                preserved_here.append((i, line.rstrip()[:140]))
                new_lines.append(line)
        if snipped_here:
            path.write_text("".join(new_lines), encoding="utf-8")
            files_touched.append(rel)
            total_snipped += len(snipped_here)
            safe_print(f"\n{rel}")
            for ln, content in snipped_here:
                safe_print(f"  SNIP L{ln}: {content}")
            for ln, content in preserved_here:
                safe_print(f"  KEEP L{ln}: {content}")
        else:
            for ln, content in preserved_here:
                safe_print(f"\n{rel} (NO snips — manual review)")
                safe_print(f"  KEEP L{ln}: {content}")
                total_preserved += 1

    safe_print(f"\n=== total: {total_snipped} wikilinks -> backticks across {len(files_touched)} files ===")
    safe_print(f"=== preserved: {total_preserved} occurrences (real-thematic or manual-review) ===")


if __name__ == "__main__":
    main()
