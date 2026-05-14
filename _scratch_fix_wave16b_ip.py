#!/usr/bin/env python3
"""Retroactively add suspected_ip / ip_confidence / ip_verified to wave 16 batch B cards.
Vision agent skipped these fields under terse-mode + 7-card-batch context."""
import os, re

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"

CARDS = {
    "cards/pokemon/brilliant-stars/036-172-prinplup.md": "Prinplup (Pokemon)",
    "cards/pokemon/brilliant-stars/060-172-duskull.md": "Duskull (Pokemon)",
    "cards/pokemon/brilliant-stars/067-172-dedenne.md": "Dedenne (Pokemon)",
    "cards/pokemon/brilliant-stars/078-172-riolu.md": "Riolu (Pokemon)",
    "cards/pokemon/brilliant-stars/089-172-spiritomb.md": "Spiritomb (Pokemon)",
    "cards/pokemon/brilliant-stars/116-172-castform--reverse-holofoil.md": "Castform Normal Form (Pokemon)",
    "cards/pokemon/brilliant-stars/115-172-farfetch-d.md": "Farfetch'd (Pokemon, Kanto form)",
}

for rel, ip_name in CARDS.items():
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    with open(p, "r", encoding="utf-8") as f:
        body = f.read()
    if "suspected_ip:" in body:
        print(f"  SKIP (already has IP): {rel}")
        continue
    # Inject before closing --- of frontmatter
    parts = body.split("---", 2)
    if len(parts) < 3:
        print(f"  !! NO FRONTMATTER: {rel}")
        continue
    fm = parts[1]
    # Append IP fields to frontmatter
    addition = f"suspected_ip: {ip_name}\nip_confidence: high\nip_verified: false\n"
    new_fm = fm.rstrip() + "\n" + addition
    new_body = "---" + new_fm + "---" + parts[2]
    with open(p, "w", encoding="utf-8") as f:
        f.write(new_body)
    print(f"  PATCHED: {rel}")

print("DONE")
