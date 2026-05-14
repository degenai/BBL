#!/usr/bin/env python3
"""Wave 33 IP placeholders: 6 items/stadiums + 1 Trainer-class (League Staff)."""
import os
ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"
PATCHES = [
    ("cards/pokemon/vivid-voltage/161-185-wyndon-stadium.md", "", "none"),
    ("cards/pokemon/vivid-voltage/153-185-league-staff.md", "Galar League Staff (Pokemon Trainer class)", "med"),
    ("cards/pokemon/vivid-voltage/152-185-hero-s-medal.md", "", "none"),
    ("cards/pokemon/vivid-voltage/150-185-circhester-bath.md", "", "none"),
    ("cards/pokemon/vivid-voltage/162-185-aromatic-grass-energy.md", "", "none"),
    ("cards/pokemon/vivid-voltage/163-185-coating-metal-energy.md", "", "none"),
    ("cards/pokemon/vivid-voltage/159-185-rocky-helmet.md", "", "none"),
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
        print(f"  !! ANCHOR: {rel}")
        continue
    open(p, "w", encoding="utf-8").write(new_body)
    print(f"  PATCHED: {rel}")
print("DONE")
