#!/usr/bin/env python3
"""Wave 27 cleanup: 3 lint dupes + 2 IP-placeholder gaps."""
import os, re

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"

# IP placeholders for 2 generic Trainer-class cards
PLACEHOLDERS = [
    "cards/pokemon/fusion-strike/224-264-adventurer-s-discovery.md",
    "cards/pokemon/fusion-strike/232-264-dancer.md",
]
for rel in PLACEHOLDERS:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    with open(p, "r", encoding="utf-8") as f:
        body = f.read()
    if "suspected_ip:" in body:
        print(f"  SKIP IP placeholder: {rel}")
        continue
    new_body = body.replace(
        "bundles: []\ntags_hub:",
        'bundles: []\nsuspected_ip: ""\nip_confidence: none\nip_verified: false\ntags_hub:',
        1,
    )
    with open(p, "w", encoding="utf-8") as f:
        f.write(new_body)
    print(f"  PATCHED IP placeholder: {rel}")

# Dunsparce: 'rare' from hub → filter
p = os.path.join(ROOT, "cards", "pokemon", "fusion-strike", "207-264-dunsparce.md")
with open(p, "r", encoding="utf-8") as f:
    body = f.read()
# Read first to find current tag lists
m_hub = re.search(r'^tags_hub:\s*\[(.*?)\]\s*$', body, re.MULTILINE)
m_fil = re.search(r'^tags_filter:\s*\[(.*?)\]\s*$', body, re.MULTILINE)
if m_hub and '"rare"' in m_hub.group(1):
    new_hub = m_hub.group(0).replace(', "rare"', '').replace('"rare", ', '').replace('"rare"', '')
    body = body.replace(m_hub.group(0), new_hub)
    if m_fil and '"rare"' not in m_fil.group(1):
        body = body.replace(m_fil.group(0), m_fil.group(0).replace(']', ', "rare"]'))
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    print("  FIXED Dunsparce: moved 'rare' hub→filter")

# Meowth FUS-199: remove 'regional-form' from hub (dupe with filter)
p = os.path.join(ROOT, "cards", "pokemon", "fusion-strike", "199-264-meowth.md")
with open(p, "r", encoding="utf-8") as f:
    body = f.read()
m_hub = re.search(r'^tags_hub:\s*\[(.*?)\]\s*$', body, re.MULTILINE)
if m_hub and '"regional-form"' in m_hub.group(1):
    new_hub = m_hub.group(0).replace(', "regional-form"', '').replace('"regional-form", ', '').replace('"regional-form"', '')
    body = body.replace(m_hub.group(0), new_hub)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    print("  FIXED Meowth FUS-199: removed 'regional-form' from hub")

# Alolan Graveler GUR-41: remove 'evolution' + 'regional-form' from hub
p = os.path.join(ROOT, "cards", "pokemon", "guardians-rising", "41-145-alolan-graveler.md")
with open(p, "r", encoding="utf-8") as f:
    body = f.read()
m_hub = re.search(r'^tags_hub:\s*\[(.*?)\]\s*$', body, re.MULTILINE)
if m_hub:
    new_hub = m_hub.group(0)
    for tag in ['evolution', 'regional-form']:
        new_hub = new_hub.replace(f', "{tag}"', '').replace(f'"{tag}", ', '').replace(f'"{tag}"', '')
    if new_hub != m_hub.group(0):
        body = body.replace(m_hub.group(0), new_hub)
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        print("  FIXED Alolan Graveler GUR-41: removed 'evolution' + 'regional-form' from hub")

print("DONE")
