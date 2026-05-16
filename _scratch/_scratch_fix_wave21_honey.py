#!/usr/bin/env python3
"""Fix wave 21: Honey is a Supporter NPC (likely Hop+Leon's mother in Galar canon),
not an item — vision agent miss-classified. Set suspected_ip. Echoing Horn IS an item, empty placeholder."""
import os

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"

# Honey — NPC card, needs suspected_ip
honey_path = os.path.join(ROOT, "cards", "pokemon", "chilling-reign", "142-198-honey.md")
with open(honey_path, "r", encoding="utf-8") as f:
    body = f.read()
if "suspected_ip:" not in body:
    body = body.replace(
        "bundles: []\ntags_hub:",
        'bundles: []\nsuspected_ip: Honey (Pokémon Sword and Shield)\nip_confidence: med\nip_verified: false\ntags_hub:',
        1,
    )
    with open(honey_path, "w", encoding="utf-8") as f:
        f.write(body)
    print("Honey: SET suspected_ip (med confidence — trivia will verify)")
else:
    print("Honey: already had suspected_ip")

# Echoing Horn — true Item card, empty placeholder
horn_path = os.path.join(ROOT, "cards", "pokemon", "chilling-reign", "136-198-echoing-horn.md")
with open(horn_path, "r", encoding="utf-8") as f:
    body = f.read()
if "suspected_ip:" not in body:
    body = body.replace(
        "bundles: []\ntags_hub:",
        'bundles: []\nsuspected_ip: ""\nip_confidence: none\nip_verified: false\ntags_hub:',
        1,
    )
    with open(horn_path, "w", encoding="utf-8") as f:
        f.write(body)
    print("Echoing Horn: SET empty placeholder")
else:
    print("Echoing Horn: already had suspected_ip")

print("DONE")
