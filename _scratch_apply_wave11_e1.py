#!/usr/bin/env python3
"""Apply wave 11 E1 — elemental-monkey-trio node + 3 frontmatter pointers."""
import json, os

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"
SIDECAR = os.path.join(ROOT, "reports", "edges_pending", "elemental-monkey-trio--node-proposal.json")

with open(SIDECAR, "r", encoding="utf-8") as f:
    sidecar = json.load(f)

# Build frontmatter YAML manually (project style; no PyYAML)
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
fm_lines.append(f"related_hubs: {fm['related_hubs']}")
fm_lines.append(f"related_symbols: {fm['related_symbols']}")
fm_lines.append("---")
fm_lines.append("")

body = sidecar["proposed_md_body"]["body_markdown"]
out = "\n".join(fm_lines) + body

node_path = os.path.join(ROOT, "cards", "_characters", "elemental-monkey-trio.md")
with open(node_path, "w", encoding="utf-8") as f:
    f.write(out)
print(f"CREATED {node_path}")

# Apply 3 frontmatter pointers
CARDS = [
    "cards/pokemon/burning-shadows/12-147-pansage.md",
    "cards/pokemon/darkness-ablaze/007-189-simisage.md",
    "cards/pokemon/darkness-ablaze/027-189-simisear.md",
]
for rel in CARDS:
    abs_p = os.path.join(ROOT, rel.replace("/", os.sep))
    with open(abs_p, "r", encoding="utf-8") as f:
        content = f.read()
    if "characters:" in content.split("---")[1]:
        print(f"  SKIP (characters already present): {rel}")
        continue
    # Insert characters: line after bundles: line in frontmatter
    new_content = content.replace(
        "bundles: []\ntags_hub:",
        'bundles: []\ncharacters: ["elemental-monkey-trio"]\ntags_hub:',
        1,
    )
    if new_content == content:
        print(f"  !! ANCHOR NOT FOUND: {rel}")
        continue
    with open(abs_p, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  WIRED characters: {rel}")

print("DONE")
