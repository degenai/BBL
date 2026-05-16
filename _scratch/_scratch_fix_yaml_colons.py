#!/usr/bin/env python3
"""Fix unquoted colons in YAML frontmatter values across all character/symbol/artist/hub nodes.
Obsidian's YAML parser breaks when a value contains a colon followed by space, treating it as
nested mapping. The fix: wrap any single-line value containing ' : ' or ending with ':' in quotes."""
import os, re, glob

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"

# Fields where we know unquoted-colon values may appear (single-line values, not lists)
SUSPECT_FIELDS = {"universe", "species", "faction", "canonical_source"}

# Regex: ^<field>: <value> where value contains ': ' and is NOT already quoted
def needs_quoting(value):
    v = value.strip()
    if not v: return False
    # already quoted (double or single)
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")): return False
    # tilde-only (~) is YAML null
    if v == "~": return False
    # square-bracket list
    if v.startswith("[") and v.endswith("]"): return False
    # contains a colon followed by space — YAML chokes
    return ": " in v

def fix_file(path):
    with open(path, "r", encoding="utf-8") as f:
        body = f.read()
    parts = body.split("---", 2)
    if len(parts) < 3: return 0
    fm = parts[1]
    changes = 0
    new_lines = []
    for line in fm.split("\n"):
        m = re.match(r"^(\w+):\s*(.+)$", line)
        if not m:
            new_lines.append(line)
            continue
        field, value = m.group(1), m.group(2)
        if field in SUSPECT_FIELDS and needs_quoting(value):
            # escape existing double quotes inside the value
            escaped = value.replace('"', '\\"')
            new_lines.append(f'{field}: "{escaped}"')
            changes += 1
        else:
            new_lines.append(line)
    if changes > 0:
        new_fm = "\n".join(new_lines)
        new_body = "---" + new_fm + "---" + parts[2]
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_body)
    return changes

total = 0
for d in ["cards/_characters", "cards/_symbols", "cards/_artists", "cards/_hubs"]:
    for p in glob.glob(os.path.join(ROOT, d.replace("/", os.sep), "*.md")):
        n = fix_file(p)
        if n:
            rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
            print(f"  QUOTED {n} field(s): {rel}")
            total += n
print(f"DONE — {total} value-quotings applied")
