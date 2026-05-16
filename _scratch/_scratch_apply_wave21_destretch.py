#!/usr/bin/env python3
"""Apply wave 21 E1 stretch-edge audit demotions. Per-line replacements only —
don't blast global [[slug]] tokens since some occurrences elsewhere may be legit."""
import json, os, re

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"
SIDECAR = os.path.join(ROOT, "reports", "edges_pending", "wave21-e1-stretch-edge-audit.json")

with open(SIDECAR, "r", encoding="utf-8") as f:
    audit = json.load(f)

demotions_by_file = {}
for c in audit["demotion_candidates"]:
    if c["verdict"] != "demote":
        continue
    f = c["file"]
    line_no = c["line"]
    # Extract slugs from wikilink string (may be "[[a]] / [[b]]")
    slugs = re.findall(r"\[\[([^\]]+)\]\]", c["wikilink"])
    demotions_by_file.setdefault(f, []).append((line_no, slugs))

applied = 0
for rel_file, ops in demotions_by_file.items():
    p = os.path.join(ROOT, rel_file.replace("/", os.sep))
    with open(p, "r", encoding="utf-8") as fh:
        lines = fh.readlines()
    file_changed = False
    for line_no, slugs in ops:
        idx = line_no - 1
        if idx >= len(lines):
            print(f"  !! LINE OUT OF RANGE: {rel_file}:{line_no}")
            continue
        before = lines[idx]
        after = before
        for slug in slugs:
            after = after.replace(f"[[{slug}]]", f"`{slug}`")
        if after != before:
            lines[idx] = after
            file_changed = True
            applied += 1
            print(f"  DEMOTED {rel_file}:{line_no} — {slugs}")
        else:
            print(f"  !! NO MATCH on line {rel_file}:{line_no} for {slugs}")
    if file_changed:
        with open(p, "w", encoding="utf-8") as fh:
            fh.writelines(lines)

print(f"DONE — {applied} demotions applied across {len(demotions_by_file)} files")
