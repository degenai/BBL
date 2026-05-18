#!/usr/bin/env python3
"""One-shot manual prep for 3 tithe-candidate cards.

researchbot.py has a parse_frontmatter bug that fails to strip YAML quoting
around `game: "Magic: The Gathering"` — so freshly-imported MTG cards never
get their `no image strategy` lookup to succeed in --prepare-only. Bypassed
here by fetching Scryfall + downloading images + stamping frontmatter via
literal Edit. Mirrors researchbot's output format closely enough that
bbl-researcher (vision) will pick the cards up via bbl_queue.py.
"""
import json
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CARDS = [
    {
        "path": REPO / "cards/magic-the-gathering/war-of-the-spark/107-tithebearer-giant.md",
        "name": "Tithebearer Giant",
        "set_code": "war",
        "set_dir": "war-of-the-spark",
    },
    {
        "path": REPO / "cards/magic-the-gathering/throne-of-eldraine/95-malevolent-noble.md",
        "name": "Malevolent Noble",
        "set_code": "eld",
        "set_dir": "throne-of-eldraine",
    },
    {
        "path": REPO / "cards/magic-the-gathering/throne-of-eldraine/86-eye-collector.md",
        "name": "Eye Collector",
        "set_code": "eld",
        "set_dir": "throne-of-eldraine",
    },
]


def url_to(path: Path) -> str:
    return str(path).replace("\\", "/")


def fetch_scryfall(name: str, set_code: str) -> dict:
    q = urllib.parse.quote(name)
    url = f"https://api.scryfall.com/cards/named?exact={q}&set={set_code}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "BBL-manual-prep/0.1 (alex.adamczyk@gmail.com)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def measure(path: Path) -> tuple[int, int, str]:
    """Quick width/height/quality via Pillow if available, else (0,0,'unknown')."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            w, h = im.size
            q = "high" if w >= 700 else "med" if w >= 400 else "low"
            return w, h, q
    except Exception:
        return 0, 0, "unknown"


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return
    req = urllib.request.Request(url, headers={
        "User-Agent": "BBL-manual-prep/0.1",
    })
    with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def update_field(text: str, field: str, value: str) -> str:
    pat = rf"^{re.escape(field)}:.*$"
    rep = f"{field}: {value}"
    if re.search(pat, text, flags=re.MULTILINE):
        return re.sub(pat, lambda _m: rep, text, count=1, flags=re.MULTILINE)
    # insert before closing ---
    m = re.match(r"---\n(.*?)\n---", text, re.DOTALL)
    end = m.end(1)
    return text[:end] + f"\n{field}: {value}" + text[end:]


def flatten_for_yaml(s: str) -> str:
    """Escape newlines for single-line YAML scalar."""
    if s is None:
        return ""
    return s.replace("\n", "\\n").replace('"', '\\"')


import urllib.parse  # noqa: E402

for card in CARDS:
    print(f"=== {card['name']} ===")
    data = fetch_scryfall(card["name"], card["set_code"])

    img_url = data["image_uris"]["png"]
    art_url = data["image_uris"]["art_crop"]
    artist = data.get("artist", "")
    cn = data.get("collector_number", "")
    flavor = data.get("flavor_text", "")
    oracle = data.get("oracle_text", "")
    mana = data.get("mana_cost", "")

    img_local = REPO / "cards/_images/magic-the-gathering" / card["set_dir"] / f"{cn}-{slug(card['name'])}.png"
    art_local = REPO / "cards/_images/magic-the-gathering" / card["set_dir"] / f"{cn}-{slug(card['name'])}--art.jpg"

    download(img_url, img_local)
    download(art_url, art_local)
    w, h, q = measure(img_local)
    print(f"  img: {url_to(img_local)} ({w}x{h} {q})")

    text = card["path"].read_text(encoding="utf-8")
    text = update_field(text, "reference_image", url_to(img_local.relative_to(REPO)))
    text = update_field(text, "reference_image_source_url", img_url)
    text = update_field(text, "art_crop_image", url_to(art_local.relative_to(REPO)))
    text = update_field(text, "art_crop_source_url", art_url)
    text = update_field(text, "artist", artist)
    text = update_field(text, "collector_number", cn)
    if mana:
        text = update_field(text, "mana_cost", f'"{mana}"')
    if flavor:
        text = update_field(text, "flavor_text", f'"{flatten_for_yaml(flavor)}"')
    if oracle:
        text = update_field(text, "oracle_text", flatten_for_yaml(oracle))
    if w:
        text = update_field(text, "image_width", str(w))
        text = update_field(text, "image_height", str(h))
        text = update_field(text, "image_quality", q)
    # ensure tags_hub stays empty (the vision-queue signal)
    text = update_field(text, "tags_hub", "[]")

    card["path"].write_text(text, encoding="utf-8")
    print(f"  wrote {card['path'].name}")

print("\nDone. Run `python bbl_queue.py` to verify all 3 land in vision queue.")
