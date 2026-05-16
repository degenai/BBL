#!/usr/bin/env python3
"""Patch wave 24 vision IP gaps."""
import os

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"

CARDS = [
    ("cards/pokemon/darkness-ablaze/159-189-bird-keeper.md", 'Bird Keeper (Pokémon Trainer class)', "med"),
    ("cards/pokemon/darkness-ablaze/158-189-billowing-smoke.md", "", "none"),
    ("cards/pokemon/crown-zenith/138-159-pokemon-catcher.md", "", "none"),
    ("cards/pokemon/chilling-reign/156-198-welcoming-lantern.md", "", "none"),
    ("cards/pokemon/darkness-ablaze/171-189-struggle-gloves.md", "", "none"),
]

for rel, ip_name, conf in CARDS:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    with open(p, "r", encoding="utf-8") as f:
        body = f.read()
    if "suspected_ip:" in body:
        print(f"  SKIP: {rel}")
        continue
    name_val = f'"{ip_name}"' if ip_name == "" else ip_name
    new_body = body.replace(
        "bundles: []\ntags_hub:",
        f'bundles: []\nsuspected_ip: {name_val}\nip_confidence: {conf}\nip_verified: false\ntags_hub:',
        1,
    )
    if new_body == body:
        print(f"  !! ANCHOR NOT FOUND: {rel}")
        continue
    with open(p, "w", encoding="utf-8") as f:
        f.write(new_body)
    print(f"  PATCHED: {rel}")

print("DONE")
