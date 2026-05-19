"""Fetch DA-hosted Michi insert candidates.

For each candidate: curl the DeviantArt artwork page with a browser UA,
extract the largest signed wixmp CDN URL, download the image to
`assets/michi-inserts/<bundle-slug>/<filename>`, write a `.meta.json`
sidecar with source + artist + permission_status metadata.

Wave 116-117 scaffolding for the Drone bundle's Michi binder pages.

Run from project root: `python scripts/fetch_michi_inserts.py`
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

BUNDLE_SLUG = "drone"
ASSET_ROOT = Path("assets/michi-inserts") / BUNDLE_SLUG
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Curated by wave-116 art scout. Aspect_ratio_slots = (cols, rows) for
# CSS grid spanning; theme_fit is short attribution-context text used in
# downstream copy.
CANDIDATES = [
    {
        "slug": "factory-tyrant-miku-dazzel",
        "source_url": "https://www.deviantart.com/dazzel-almond/art/Factory-Tyrant-Miku-728587296",
        "artist": "Dazzel-Almond",
        "aspect_slots": [1, 1],
        "theme_fit": "Factory Tyrant Miku in Sadistic Music Factory module — direct headline echo",
    },
    {
        "slug": "factory-tyrant-miku-patchedup",
        "source_url": "https://www.deviantart.com/patchedup-artist/art/Bright-color-warning-Factory-Tyrant-Miku-912235356",
        "artist": "PatchedUp-Artist",
        "aspect_slots": [1, 1],
        "theme_fit": "Second Factory Tyrant Miku interpretation — alternate cover option",
    },
    {
        "slug": "assembly-line-krzywonos",
        "source_url": "https://www.deviantart.com/damiankrzywonos/art/Assembly-Line-steampunk-concept-illustration-658382404",
        "artist": "DamianKrzywonos",
        "aspect_slots": [2, 1],
        "theme_fit": "Steampunk assembly line concept — horizontal 1x2 panel, production-floor grounder",
    },
    {
        "slug": "conveyor-belts-huang",
        "source_url": "https://www.deviantart.com/diana-huang/art/Draw-Factory-Conveyor-Belts-491967037",
        "artist": "Diana-Huang",
        "aspect_slots": [2, 1],
        "theme_fit": "Conveyor belt tutorial-illustration — horizontal 1x2 panel, pure production-line iconography",
    },
    {
        "slug": "robot-factory-novaillusion",
        "source_url": "https://www.deviantart.com/novaillusion/art/Robot-Factory-429353862",
        "artist": "novaillusion",
        "aspect_slots": [1, 1],
        "theme_fit": "Robot factory — rows of mass-produced units, mass-production iconography",
    },
    {
        "slug": "dieselpunk-city-adrianward",
        "source_url": "https://www.deviantart.com/adrianward/art/Dieselpunk-Industrial-City-760297733",
        "artist": "AdrianWard",
        "aspect_slots": [2, 1],
        "theme_fit": "Dieselpunk industrial city — railroad cutting through labor districts beneath central towers",
    },
    {
        "slug": "damnation-factory-worker-dazzy",
        "source_url": "https://www.deviantart.com/dazzyallen/art/Damnation-Factory-Worker-253594787",
        "artist": "DazzyAllen",
        "aspect_slots": [1, 1],
        "theme_fit": "Single worker-character study — drone-as-damned-soul-on-shift register",
    },
    {
        "slug": "steampunk-worker-sparrow",
        "source_url": "https://www.deviantart.com/sparrow-chan/art/Steampunk-factory-worker-517583978",
        "artist": "sparrow-chan",
        "aspect_slots": [1, 1],
        "theme_fit": "Steampunk factory-worker commission — human-scale grounder",
    },
    {
        "slug": "dieselpunk-concept-tapedamage",
        "source_url": "https://www.deviantart.com/tapedamage/art/Dieselpunk-Character-Concept-Art-926284280",
        "artist": "TapeDamage",
        "aspect_slots": [1, 1],
        "theme_fit": "Dieselpunk worker concept — blue-collar fantasy register",
    },
    {
        "slug": "victorian-automaton-inkimagine",
        "source_url": "https://www.deviantart.com/inkimagine/art/Victorian-Steampunk-Automaton-1056599519",
        "artist": "InkImagine",
        "aspect_slots": [1, 1],
        "theme_fit": "Victorian automaton — drone-as-built-thing-not-born-thing close-up",
    },
]


# Pattern in the srcset that grabs the largest variant. The DA page emits
# `images-wixmp-...jpg?token=...` URLs at multiple widths in a srcset; we
# want the widest. The "/v1/fill/" or "/v1/fit/" path segment is followed
# by `w_NNNN` indicating width.
URL_RE = re.compile(
    r"https://images-wixmp-[a-z0-9.-]+/[^\s\"'<>`)]+"
)
WIDTH_RE = re.compile(r"/w_(\d+),")


def fetch_page(url: str) -> str | None:
    """curl with browser UA. Returns page HTML or None on failure."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "-A", USER_AGENT, url],
            capture_output=True,
            timeout=30,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0 or not result.stdout:
            return None
        return result.stdout
    except Exception as e:
        print(f"  fetch_page error: {e}", file=sys.stderr)
        return None


def pick_largest_wixmp(html: str) -> str | None:
    """From the DA page HTML, return the wixmp image URL with the highest
    encoded width. Falls back to longest URL if width parsing fails."""
    urls = set(URL_RE.findall(html))
    if not urls:
        return None

    def width_of(u: str) -> int:
        m = WIDTH_RE.search(u)
        return int(m.group(1)) if m else 0

    sized = [(width_of(u), u) for u in urls]
    sized.sort(key=lambda t: (t[0], len(t[1])), reverse=True)
    return sized[0][1] if sized else None


def download_image(url: str, dest: Path) -> bool:
    """curl-download an image to dest. Returns True on success."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "-A", USER_AGENT, "-o", str(dest), url],
            capture_output=True,
            timeout=60,
        )
        if result.returncode != 0:
            return False
        return dest.exists() and dest.stat().st_size > 1024
    except Exception as e:
        print(f"  download error: {e}", file=sys.stderr)
        return False


def write_meta(dest_image: Path, candidate: dict, image_url: str) -> None:
    meta = {
        "image_file": dest_image.name,
        "source_url": candidate["source_url"],
        "creator_handle": candidate["artist"],
        "host_domain": "images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com",
        "resolved_image_url": image_url,
        "permission_status": "for-internal-comp-only",
        "panel_dimensions_slots": candidate["aspect_slots"],
        "theme_fit": candidate["theme_fit"],
        "bundle_slug": BUNDLE_SLUG,
        "fetched_at": "2026-05-17",
    }
    meta_path = dest_image.with_suffix(dest_image.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def main() -> int:
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"Fetching {len(CANDIDATES)} Michi insert candidates into {ASSET_ROOT}")
    ok = 0
    fail = 0
    for c in CANDIDATES:
        print(f"\n[{c['slug']}]")
        print(f"  source: {c['source_url']}")
        html = fetch_page(c["source_url"])
        if not html:
            print("  FAIL: page fetch failed")
            fail += 1
            continue
        img_url = pick_largest_wixmp(html)
        if not img_url:
            print("  FAIL: no wixmp URL found in page")
            fail += 1
            continue
        # Determine extension from URL path before query string
        path_part = img_url.split("?", 1)[0]
        ext = ".jpg"
        for candidate_ext in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            if path_part.lower().endswith(candidate_ext):
                ext = candidate_ext
                break
        dest = ASSET_ROOT / f"{c['slug']}{ext}"
        if download_image(img_url, dest):
            write_meta(dest, c, img_url)
            size_kb = dest.stat().st_size // 1024
            print(f"  OK ({size_kb} KB): {dest}")
            ok += 1
        else:
            print(f"  FAIL: download failed for {img_url[:120]}")
            fail += 1
    print(f"\n{ok} ok / {fail} fail / {len(CANDIDATES)} total")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
