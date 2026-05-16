#!/usr/bin/env python3
"""De-stretch: convert schema-precedent wikilinks to backtick-code-style.

Rule: wikilink iff the connection is real-thematic-narrative (institutional contrast,
shared lore axis). Backtick iff the citation is purely architectural precedent
("we put cohort nodes on the character layer like X did"). The latter produces
false Obsidian graph edges suggesting Pokemon cycles are semantically connected
to MTG Duskmourn Nightmares.

Targets (Pokemon nodes citing MTG-only cycle nodes as schema precedent):
- castform-forms-cycle / charizard-line / elemental-monkey-trio /
  galar-starters-trio / galarian-regional-forms → fear-of-cycle, dsk-unlucky-lands-cycle

Real-thematic wikilinks that STAY:
- alola-elite-four → galar-gym-challenge (institutional contrast)
- aether-rangers ↔ orzhov-syndicate (labor/extraction axis)
- galar-gym-challenge → azorius-senate / orzhov-syndicate (apparatus-of-extraction)
"""
import os, re

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"

# Pokemon nodes citing MTG cycle nodes as schema precedent only
TARGETS = [
    "cards/_characters/castform-forms-cycle.md",
    "cards/_characters/charizard-line.md",
    "cards/_characters/elemental-monkey-trio.md",
    "cards/_characters/galar-starters-trio.md",
    "cards/_characters/galarian-regional-forms.md",
]

# Wikilink-strings to neutralize to backtick-code-style
STRETCH_LINKS = ["fear-of-cycle", "dsk-unlucky-lands-cycle"]

for rel in TARGETS:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    with open(p, "r", encoding="utf-8") as f:
        body = f.read()
    original = body
    for slug in STRETCH_LINKS:
        # Replace [[slug]] with `slug`
        body = body.replace(f"[[{slug}]]", f"`{slug}`")
    if body != original:
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        n_changes = original.count("[[fear-of-cycle]]") + original.count("[[dsk-unlucky-lands-cycle]]")
        print(f"  DESTRETCHED {n_changes} wikilink(s): {rel}")
    else:
        print(f"  SKIP (no changes): {rel}")

print("DONE")
