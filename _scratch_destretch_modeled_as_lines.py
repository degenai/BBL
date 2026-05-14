#!/usr/bin/env python3
"""Second sweep: 'Modeled as a ... node' Caveats lines are uniformly schema-precedent framing.
ALL wikilinks on such lines are 'like X did' architectural citations. Demote all of them.
Real-thematic peers also appear in See also sections; those edges are preserved there."""
import os, re, glob

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"

DIRS = [
    "cards/_characters",
    "cards/_artists",
    "cards/_symbols",
    "cards/_hubs",
]

def demote_wikilinks_on_line(line):
    return re.sub(r"\[\[([^\]]+)\]\]", r"`\1`", line)

total_lines_changed = 0
files_changed = 0

for d in DIRS:
    pattern = os.path.join(ROOT, d.replace("/", os.sep), "*.md")
    for p in glob.glob(pattern):
        with open(p, "r", encoding="utf-8") as f:
            lines = f.readlines()
        changed = False
        for i, line in enumerate(lines):
            # "Modeled as a ... node" or "- **Modeled as" — schema-precedent Caveats line
            if "Modeled as a" in line and "[[" in line:
                new_line = demote_wikilinks_on_line(line)
                if new_line != line:
                    lines[i] = new_line
                    changed = True
                    total_lines_changed += 1
                    rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
                    print(f"  DEMOTED line {i+1}: {rel}")
        if changed:
            with open(p, "w", encoding="utf-8") as f:
                f.writelines(lines)
            files_changed += 1

print(f"DONE — {total_lines_changed} lines demoted across {files_changed} files")
