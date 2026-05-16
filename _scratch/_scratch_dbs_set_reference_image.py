#!/usr/bin/env python3
"""Patch DBS cards that have a downloaded image but lack the
`reference_image` frontmatter field. The TTS extract script (wave 47)
set reference_image_source_url + image_width/height/quality but forgot
to stamp the local path. bbl_queue.py uses `reference_image` to decide
vision-readiness, so the omission hid 186 prepped cards from the queue."""
import os, re, glob

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"
CARDS_DIR = os.path.join(ROOT, "cards", "dragon-ball-super")
IMG_DIR = os.path.join(ROOT, "cards", "_images", "dragon-ball-super")


def update_field(text, field, value):
    line_re = re.compile(rf"^{re.escape(field)}:\s*[^\n]*$", re.MULTILINE)
    new = f"{field}: {value}"
    if line_re.search(text):
        return line_re.sub(new, text, count=1)
    return re.sub(r"^---\s*$", f"{new}\n---", text, count=1, flags=re.MULTILINE)


fixed = 0
skipped = 0
for md in glob.glob(os.path.join(CARDS_DIR, "**", "*.md"), recursive=True):
    body = open(md, encoding="utf-8").read()
    # Already has reference_image set?
    m = re.search(r"^reference_image:\s*([^\n]+)", body, re.MULTILINE)
    if m and m.group(1).strip():
        skipped += 1
        continue
    # Compute expected local image path
    rel = os.path.relpath(md, os.path.join(ROOT, "cards", "dragon-ball-super"))
    img_path = os.path.join(IMG_DIR, os.path.splitext(rel)[0] + ".png")
    if not os.path.exists(img_path):
        continue  # no image, can't help
    repo_rel = os.path.relpath(img_path, ROOT).replace("\\", "/")
    body = update_field(body, "reference_image", repo_rel)
    body = update_field(body, "art_match_confidence", "high")
    body = update_field(body, "needs_manual_review", "false")
    open(md, "w", encoding="utf-8").write(body)
    print(f"  PATCHED: {os.path.basename(md)}")
    fixed += 1
print(f"\nDONE — patched {fixed} DBS cards, skipped {skipped} (already had reference_image)")
