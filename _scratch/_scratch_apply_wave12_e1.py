#!/usr/bin/env python3
"""Apply wave 12 E1 — galarian-regional-forms node + 3 frontmatter pointers."""
import json, os

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"
SIDECAR = os.path.join(ROOT, "reports", "edges_pending", "galarian-regional-forms--node-proposal.json")

with open(SIDECAR, "r", encoding="utf-8") as f:
    sidecar = json.load(f)

fm = sidecar["proposed_md_body"]["frontmatter"]
fm_lines = ["---"]
fm_lines.append(f"type: {fm['type']}")
fm_lines.append(f"name: {fm['name']}")
fm_lines.append(f"aliases: [{', '.join(fm['aliases'])}]")
fm_lines.append(f"universe: {fm['universe']}")
fm_lines.append(f"faction: {fm['faction']}")
fm_lines.append(f"species: {fm['species']}")
fm_lines.append(f"canonical_source: \"{fm['canonical_source']}\"")
fm_lines.append(f"confidence: {fm['confidence']}")
fm_lines.append("appears_on:")
for p in fm["appears_on"]:
    fm_lines.append(f"  - {p}")
fm_lines.append(f"related_hubs: {fm.get('related_hubs', [])}")
fm_lines.append(f"related_symbols: {fm.get('related_symbols', [])}")
if "ip_resolution_for" in fm:
    fm_lines.append(f"ip_resolution_for: {fm['ip_resolution_for']}")
fm_lines.append("---")
fm_lines.append("")

body = sidecar["proposed_md_body"]["body_markdown"]
out = "\n".join(fm_lines) + body

node_path = os.path.join(ROOT, "cards", "_characters", "galarian-regional-forms.md")
with open(node_path, "w", encoding="utf-8") as f:
    f.write(out)
print(f"CREATED {node_path}")

CARDS = [
    "cards/pokemon/chilling-reign/054-198-galarian-slowpoke.md",
    "cards/pokemon/rebel-clash/047-192-galarian-darumaka.md",
    "cards/pokemon/rebel-clash/094-192-galarian-farfetch-d.md",
]
for rel in CARDS:
    abs_p = os.path.join(ROOT, rel.replace("/", os.sep))
    with open(abs_p, "r", encoding="utf-8") as f:
        content = f.read()
    fm_block = content.split("---")[1]
    if "characters:" in fm_block:
        print(f"  SKIP (characters already present): {rel}")
        continue
    new_content = content.replace(
        "bundles: []\ntags_hub:",
        'bundles: []\ncharacters: ["galarian-regional-forms"]\ntags_hub:',
        1,
    )
    if new_content == content:
        print(f"  !! ANCHOR NOT FOUND: {rel}")
        continue
    with open(abs_p, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  WIRED characters: {rel}")

print("DONE")
