#!/usr/bin/env python3
"""Patch empty-IP placeholder fields on wave 20 item cards (vision agent skipped them per known issue)."""
import os

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"
CARDS = [
    "cards/pokemon/chilling-reign/154-198-single-strike-scroll-of-piercing.md",
    "cards/pokemon/chilling-reign/140-198-fog-crystal.md",
    "cards/pokemon/cosmic-eclipse/206-236-tag-call.md",
    "cards/pokemon/cosmic-eclipse/192-236-great-catcher.md",
]

for rel in CARDS:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    with open(p, "r", encoding="utf-8") as f:
        body = f.read()
    if "suspected_ip:" in body:
        print(f"  SKIP (has IP): {rel}")
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
