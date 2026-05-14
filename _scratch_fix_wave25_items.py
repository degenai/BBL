#!/usr/bin/env python3
"""Patch empty-IP placeholders on 8 wave 25 item/stadium cards."""
import os
ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"
CARDS = [
    "cards/pokemon/fates-collide/94-chaos-tower.md",
    "cards/pokemon/evolutions/73-108-blastoise-spirit-link.md",
    "cards/pokemon/evolutions/89-108-venusaur-spirit-link.md",
    "cards/pokemon/evolutions/77-108-energy-retrieval.md",
    "cards/pokemon/evolutions/78-108-full-heal.md",
    "cards/pokemon/burning-shadows/126-147-weakness-policy.md",
    "cards/pokemon/chilling-reign/137-198-expedition-uniform.md",
    "cards/pokemon/crimson-invasion/97-111-peeking-red-card.md",
]
for rel in CARDS:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    with open(p, "r", encoding="utf-8") as f:
        body = f.read()
    if "suspected_ip:" in body:
        print(f"  SKIP: {rel}")
        continue
    new_body = body.replace(
        "bundles: []\ntags_hub:",
        'bundles: []\nsuspected_ip: ""\nip_confidence: none\nip_verified: false\ntags_hub:',
        1,
    )
    if new_body == body:
        print(f"  !! ANCHOR NOT FOUND: {rel}")
        continue
    with open(p, "w", encoding="utf-8") as f:
        f.write(new_body)
    print(f"  PATCHED: {rel}")
print("DONE")
