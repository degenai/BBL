#!/usr/bin/env python3
"""Fix the bug in tts_dbs_extract.py wave 47: fields were inserted ABOVE
the opening `---` (so they became body content above the frontmatter).
This script:
1. Strips any stray pre-frontmatter lines (reference_image_source_url /
   image_width / image_height / image_quality that landed above the first ---)
2. Re-inserts them properly INSIDE the frontmatter (before the closing ---)
3. Sets `reference_image:` to the local cached image path (was empty)
4. Sets art_match_confidence + needs_manual_review correctly"""
import os, re, glob

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"
CARDS_DIR = os.path.join(ROOT, "cards", "dragon-ball-super")
IMG_DIR_REL = "cards/_images/dragon-ball-super"

FIELDS_TO_MIGRATE = ["reference_image_source_url", "image_width", "image_height", "image_quality"]


def fix_card(md_path: str) -> bool:
    body = open(md_path, encoding="utf-8").read()
    lines = body.split("\n")

    # Find the first --- line; everything before it that's a `field: value`
    # form is misplaced. Collect them and trim from the top.
    first_dash = None
    for i, ln in enumerate(lines):
        if ln.strip() == "---":
            first_dash = i
            break
    if first_dash is None:
        return False

    migrated: dict[str, str] = {}
    if first_dash > 0:
        # Cards with misplaced fields have content above ---
        pre = lines[:first_dash]
        for ln in pre:
            m = re.match(r"^(\w+):\s*(.*)$", ln)
            if m:
                migrated[m.group(1)] = m.group(2).strip()
        # Strip the misplaced lines
        lines = lines[first_dash:]

    # Find the close --- of frontmatter
    close_dash = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            close_dash = i
            break
    if close_dash is None:
        return False

    fm_lines = lines[1:close_dash]
    rest = lines[close_dash:]

    # Build a dict of existing frontmatter
    fm: dict[str, str] = {}
    for ln in fm_lines:
        m = re.match(r"^(\w+):\s*(.*)$", ln)
        if m:
            fm[m.group(1)] = m.group(2).strip()

    # Merge migrated values (only if existing field is empty)
    for k, v in migrated.items():
        if not fm.get(k):
            fm[k] = v

    # Set reference_image to the cached local image
    if not fm.get("reference_image") and fm.get("image_width"):
        # Card name → image path: cards/_images/dragon-ball-super/<set>/<slug>.png
        rel = os.path.relpath(md_path, ROOT).replace("\\", "/")
        # cards/dragon-ball-super/<set>/<slug>.md → cards/_images/dragon-ball-super/<set>/<slug>.png
        img_path = rel.replace("cards/dragon-ball-super/", IMG_DIR_REL + "/").replace(".md", ".png")
        if os.path.exists(os.path.join(ROOT, img_path)):
            fm["reference_image"] = img_path
            fm["art_match_confidence"] = "high"
            fm["needs_manual_review"] = "false"

    # Rebuild frontmatter preserving original order + appending new keys
    seen = set()
    new_fm_lines = []
    for ln in fm_lines:
        m = re.match(r"^(\w+):\s*(.*)$", ln)
        if m:
            k = m.group(1)
            new_fm_lines.append(f"{k}: {fm.get(k, m.group(2))}")
            seen.add(k)
        else:
            new_fm_lines.append(ln)
    # Append any keys from migrated/new that weren't already in frontmatter
    for k in FIELDS_TO_MIGRATE + ["reference_image", "art_match_confidence", "needs_manual_review"]:
        if k in fm and k not in seen:
            new_fm_lines.append(f"{k}: {fm[k]}")
            seen.add(k)

    new_body = "---\n" + "\n".join(new_fm_lines) + "\n" + "\n".join(rest)
    if new_body != body:
        open(md_path, "w", encoding="utf-8").write(new_body)
        return True
    return False


fixed = 0
for md in glob.glob(os.path.join(CARDS_DIR, "**", "*.md"), recursive=True):
    if fix_card(md):
        fixed += 1
print(f"DONE — repaired {fixed} DBS cards")
