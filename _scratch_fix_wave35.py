#!/usr/bin/env python3
"""Wave 35 IP placeholders: 14 MH3 MTG cards missing suspected_ip scaffold."""
import os
ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"
PATCHES = [
    ("cards/magic-the-gathering/modern-horizons-3/19-ajani-fells-the-godsire.md", "", "none"),
    ("cards/magic-the-gathering/modern-horizons-3/191-izzet-generatorium.md", "", "none"),
    ("cards/magic-the-gathering/modern-horizons-3/21-charitable-levy.md", "", "none"),
    ("cards/magic-the-gathering/modern-horizons-3/31-indebted-spirit.md", "", "none"),
    ("cards/magic-the-gathering/modern-horizons-3/134-reiterating-bolt.md", "", "none"),
    ("cards/magic-the-gathering/modern-horizons-3/188-horrid-shadowspinner.md", "", "none"),
    ("cards/magic-the-gathering/modern-horizons-3/210-idol-of-false-gods.md", "", "none"),
    ("cards/magic-the-gathering/modern-horizons-3/14-twisted-riddlekeeper.md", "", "none"),
    ("cards/magic-the-gathering/modern-horizons-3/200-pyretic-rebirth.md", "", "none"),
    ("cards/magic-the-gathering/modern-horizons-3/204-snapping-voidcraw.md", "", "none"),
    ("cards/magic-the-gathering/modern-horizons-3/17-wastescape-battlemage.md", "", "none"),
    ("cards/magic-the-gathering/modern-horizons-3/203-scurry-of-gremlins.md", "", "none"),
    ("cards/magic-the-gathering/modern-horizons-3/280-fledgling-dragon.md", "", "none"),
    ("cards/magic-the-gathering/modern-horizons-3/184-expanding-ooze.md", "", "none"),
]
for rel, name, conf in PATCHES:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.exists(p):
        print(f"  !! MISSING: {rel}")
        continue
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
        print(f"  !! ANCHOR-MISS: {rel}")
        continue
    open(p, "w", encoding="utf-8").write(new_body)
    print(f"  PATCHED: {rel}")
print("DONE")
