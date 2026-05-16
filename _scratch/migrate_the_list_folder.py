"""
migrate_the_list_folder - one-shot migration script for the Mystery-Booster-mis-namer.

Collectr labels The List (PLST) inserts as "Mystery Booster Cards"; 34 cards got
ingested under cards/magic-the-gathering/mystery-booster-cards/ with that wrong
folder slug AND with set: Mystery Booster Cards in their frontmatter. A partial
remediation added the_list_source_set but never corrected the set: field or
moved the folder. This script does the rest:

  1. git mv each MD to cards/magic-the-gathering/the-list/<slug>.md
  2. git mv each PNG + art-crop JPG to cards/_images/magic-the-gathering/the-list/
  3. For each moved MD: substitute four path strings to point at the-list/
  4. Normalize each via bbl_schema (wave 92.6 hygiene)

Idempotent: re-running after a successful migration is a no-op.

Wave 96.8 Nurse Joy prescription.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from bbl_schema import normalize_file  # noqa: E402

OLD_MDS_DIR = ROOT / "cards" / "magic-the-gathering" / "mystery-booster-cards"
NEW_MDS_DIR = ROOT / "cards" / "magic-the-gathering" / "the-list"
OLD_IMG_DIR = ROOT / "cards" / "_images" / "magic-the-gathering" / "mystery-booster-cards"
NEW_IMG_DIR = ROOT / "cards" / "_images" / "magic-the-gathering" / "the-list"

# String substitutions applied to each moved MD body.
SUBS = [
    ("set: Mystery Booster Cards", "set: The List"),
    ("reference_image: cards/_images/magic-the-gathering/mystery-booster-cards/",
     "reference_image: cards/_images/magic-the-gathering/the-list/"),
    ("art_crop_image: cards/_images/magic-the-gathering/mystery-booster-cards/",
     "art_crop_image: cards/_images/magic-the-gathering/the-list/"),
    ("](../../_images/magic-the-gathering/mystery-booster-cards/",
     "](../../_images/magic-the-gathering/the-list/"),
]


def git_mv(src: Path, dst: Path) -> bool:
    """git mv with -f. Returns True on success."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["git", "mv", "-f", str(src), str(dst)],
            cwd=str(ROOT), check=True, capture_output=True, text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [warn] git mv failed for {src.name}: {e.stderr.strip()}", file=sys.stderr)
        return False


def patch_md(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    new_text = text
    for old, new in SUBS:
        new_text = new_text.replace(old, new)
    if new_text == text:
        return 0
    path.write_text(new_text, encoding="utf-8")
    normalize_file(path)
    return 1


def main() -> int:
    if not OLD_MDS_DIR.exists():
        print(f"Source MD dir not found: {OLD_MDS_DIR}")
        print("(Migration may already be done. Verifying...)")
        n = len(list(NEW_MDS_DIR.glob("*.md"))) if NEW_MDS_DIR.exists() else 0
        print(f"the-list/ currently has {n} MDs.")
        return 0

    NEW_MDS_DIR.mkdir(parents=True, exist_ok=True)
    NEW_IMG_DIR.mkdir(parents=True, exist_ok=True)

    mds = sorted(OLD_MDS_DIR.glob("*.md"))
    print(f"Migrating {len(mds)} MDs...")

    moved_mds = 0
    moved_images = 0
    patched_mds = 0

    for md in mds:
        slug = md.stem
        new_md = NEW_MDS_DIR / f"{slug}.md"
        if git_mv(md, new_md):
            moved_mds += 1
            # Patch the moved MD
            patched_mds += patch_md(new_md)
        # Move corresponding image files
        for ext in (".png", ".jpg"):
            old_img = OLD_IMG_DIR / f"{slug}{ext}"
            if old_img.exists():
                new_img = NEW_IMG_DIR / f"{slug}{ext}"
                if git_mv(old_img, new_img):
                    moved_images += 1
            # art-crop variant
            old_art = OLD_IMG_DIR / f"{slug}--art{ext}"
            if old_art.exists():
                new_art = NEW_IMG_DIR / f"{slug}--art{ext}"
                if git_mv(old_art, new_art):
                    moved_images += 1

    # Clean up empty source dirs
    for d in (OLD_MDS_DIR, OLD_IMG_DIR):
        if d.exists():
            try:
                d.rmdir()
                print(f"  removed empty dir: {d.relative_to(ROOT)}")
            except OSError as e:
                remaining = list(d.iterdir())
                print(f"  [warn] {d.relative_to(ROOT)} not empty ({len(remaining)} items): {e}")

    print(f"\n--- Migration summary ---")
    print(f"  MDs moved:        {moved_mds}")
    print(f"  Images moved:     {moved_images}")
    print(f"  MDs patched:      {patched_mds}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
