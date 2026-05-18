#!/usr/bin/env python3
"""Add artist credit to each card in tithe.json so the per-card meta line
can render '... · art by <artist>'. Artists pulled from the 2nd-pass trivia
harvest. Idempotent."""
import json
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent.parent / "Diamondlegendz/bundle-previewer/sample-bundles/tithe.json"

ARTISTS = {
    "Wicked Guardian":     "Matt Stewart",
    "Charity Extractor":   "Matt Stewart",
    "Pitiless Pontiff":    "Yongjae Choi",
    "Mortify":             "Anthony Palumbo",
    "Tithe Drinker":       "Slawomir Maniak",
    "Lawmage's Binding":   "Mark Behm",
    "Indebted Spirit":     "L.A. Draws",
    "Charitable Levy":     "Eli Minaya",
    "Tithebearer Giant":   "Wisnu Tan",
    "Malevolent Noble":    "Randy Vargas",
    "Eye Collector":       "Uriah Voth",
    "Secure the Scene":    "Zoltan Boros",
}

data = json.loads(BUNDLE.read_text(encoding="utf-8"))
changed = 0
for c in data["cards"]:
    artist = ARTISTS.get(c["name"])
    if artist and c.get("artist") != artist:
        c["artist"] = artist
        changed += 1

BUNDLE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"updated {changed} cards in {BUNDLE.name}")
