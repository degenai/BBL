#!/usr/bin/env python3
"""Wave 31: 5 Pokemon species IP gaps + 3 item placeholders."""
import os
ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"
PATCHES = [
    ("cards/pokemon/unified-minds/18-236-steenee.md", "Steenee", "high"),
    ("cards/pokemon/unified-minds/105-236-cubone.md", "Cubone", "high"),
    ("cards/pokemon/unified-minds/157-236-druddigon.md", "Druddigon", "high"),
    ("cards/pokemon/shining-fates/031-072-shinx.md", "Shinx", "high"),
    ("cards/pokemon/team-up/129-tauros.md", "Tauros", "high"),
    ("cards/pokemon/team-up/156-viridian-forest.md", "", "none"),
    ("cards/pokemon/rebel-clash/171-192-capture-energy.md", "", "none"),
    ("cards/pokemon/unbroken-bonds/170-energy-spinner.md", "", "none"),
]
for rel, name, conf in PATCHES:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    with open(p, "r", encoding="utf-8") as f:
        body = f.read()
    if "suspected_ip:" in body:
        print(f"  SKIP: {rel}")
        continue
    name_val = f'"{name}"' if name == "" else name
    new_body = body.replace(
        "bundles: []\ntags_hub:",
        f'bundles: []\nsuspected_ip: {name_val}\nip_confidence: {conf}\nip_verified: false\ntags_hub:',
        1,
    )
    if new_body == body:
        print(f"  !! ANCHOR NOT FOUND: {rel}")
        continue
    open(p, "w", encoding="utf-8").write(new_body)
    print(f"  PATCHED: {rel}")
print("DONE")
