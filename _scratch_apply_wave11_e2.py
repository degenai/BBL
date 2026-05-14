#!/usr/bin/env python3
"""Apply wave 11 E2 — Turffield Stadium joins galar-gym-challenge node as place-card endpoint."""
import os

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"

# --- 1. Update galar-gym-challenge.md node ---
node_path = os.path.join(ROOT, "cards", "_characters", "galar-gym-challenge.md")
with open(node_path, "r", encoding="utf-8") as f:
    node = f.read()

# Add to appears_on YAML list (after milo entry)
old_appears = "  - pokemon/rebel-clash/161-192-milo\nrelated_hubs:"
new_appears = "  - pokemon/rebel-clash/161-192-milo\n  - pokemon/champion-s-path/68-73-turffield-stadium\nrelated_hubs:"
assert old_appears in node, "appears_on anchor not found in galar-gym-challenge.md"
node = node.replace(old_appears, new_appears)

# Add bullet after Milo bullet in "Cards in our corpus" section
milo_bullet = "- **Milo** (Rebel Clash 161, Grass-type, Turffield major-division) — the league progression's first Gym"
# Find the milo bullet's line and inject after it (preserve whatever continuation follows)
# Use the line-ending convention: find "first Gym" + the rest of that paragraph, insert new bullet on next line break.
# Simpler: assume milo bullet line ends at the next \n; insert Turffield bullet immediately after.
# Locate end of milo bullet (next blank line OR next "- **" or "##")
m_idx = node.find(milo_bullet)
assert m_idx != -1, "Milo bullet not found"
# Find end of milo's bullet — search forward to next "\n- **" or "\n\n" or "\n## "
search_from = m_idx + len(milo_bullet)
# Look for the next bullet OR next section header
candidates = []
for marker in ["\n- **", "\n## ", "\n### "]:
    j = node.find(marker, search_from)
    if j != -1:
        candidates.append(j)
end_of_milo = min(candidates) if candidates else len(node)

new_bullet = "\n- **Turffield Stadium** (Champion's Path no. 68/73, Stadium trainer card, Grass-type Search effect, aky CG Works art) — Milo's home Gym town as civic-architecture establishing shot: the domed sports stadium with grass-textured roof and red structural trim, surrounded by the town's red-roofed buildings, with a small figure (red coat, matching Milo's canonical palette) on a foreground balcony looking out toward the dome. The Champion's Path set was organized around the eight Galar gym towns and each gym received a dedicated Pin Collection product — this is Turffield's Stadium-card representation of the league's institutional fabric extended into a place-card slot. First place-card endpoint on this node; validates the institutional-iconography spec."
node = node[:end_of_milo] + new_bullet + node[end_of_milo:]

with open(node_path, "w", encoding="utf-8") as f:
    f.write(node)
print(f"UPDATED node {node_path}")

# --- 2. Update Turffield Stadium card ---
card_path = os.path.join(ROOT, "cards", "pokemon", "champion-s-path", "68-73-turffield-stadium.md")
with open(card_path, "r", encoding="utf-8") as f:
    card = f.read()

# Add characters: pointer in frontmatter after bundles: []
card = card.replace(
    "bundles: []\ntags_hub:",
    'bundles: []\ncharacters: ["galar-gym-challenge"]\ntags_hub:',
    1,
)

# Append ## Connections section at end of file
connections = """
## Connections

- [[_characters/galar-gym-challenge]] — Turffield is the first stop on Galar's eight-gym league progression, and Milo is its Grass-type Gym Leader; this Stadium card is the civic-architecture establishing shot of his home Gym town (the dome's green grass-textured roof matches Milo's typing; the small red-coated figure on the foreground balcony matches Milo's canonical palette). Champion's Path was structured around the eight Galar gym towns with one Pin Collection product per gym — this is Turffield's place-card representation of the league's institutional fabric, parallel to Milo's Supporter-card representation in Rebel Clash 161/192. `[Bulbapedia: Turffield]` `[Bulbapedia: Milo]` `[Pokemon.com: Champion's Path Pin Collections]`
- [[../rebel-clash/161-192-milo]] — person-card + place-card co-anchor of the Turffield major-division Gym slot. Milo's Rebel Clash 161 Supporter art shows him in pastoral pose with leaf-topiary backdrop (the gym's pastoral character at the trainer level); this Stadium card shows the same town's civic-sporting venue (the gym's institutional character at the place level). Together they cover the two registers of Milo's Gym town in BBL inventory. `[Corpus: cards/pokemon/rebel-clash/161-192-milo.md trivia]`
"""
card = card.rstrip() + "\n" + connections

with open(card_path, "w", encoding="utf-8") as f:
    f.write(card)
print(f"UPDATED card {card_path}")

print("DONE")
