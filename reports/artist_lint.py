#!/usr/bin/env python3
"""
artist_lint — Sanity-check the `artist:` frontmatter field after a backfill or prep run.

What we want to catch:
  - Coverage gaps: enriched MTG cards still missing artist
  - Empty / whitespace-only / placeholder values ("Unknown", "?", "None")
  - Suspicious lengths: 1-char names, 100+-char fields (probably ate the next field)
  - Encoding artifacts: control characters, BOM, mojibake markers
  - All-caps or all-lowercase names (artists usually have title-case credits)
  - Duplicate-collapse opportunities (same artist with different capitalization or
    trailing whitespace would create two distinct top-N entries)

What we do NOT catch:
  - "Is this actually the right artist for this card?" — that's the human spot-check.

Output: console report + markdown file at reports/artist_lint_<date>.md.

Usage:
  python reports/artist_lint.py [--game GAME] [--sample N]
"""
from __future__ import annotations
import argparse, datetime, os, re, sys, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from researchbot import parse_frontmatter

PLACEHOLDER_VALUES = {"unknown", "n/a", "na", "?", "none", "null", "tbd", ""}
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def is_card_node(path: Path) -> bool:
    parts = path.parts
    return not any(p in ("_images", "_hubs", "_symbols") for p in parts)


def classify(name: str) -> list[str]:
    """Return zero or more sanity-flag strings for an artist value."""
    flags = []
    if name is None:
        return ["missing field"]
    raw = name
    name = name.strip()
    if not name:
        return ["empty/whitespace"]
    if name.lower() in PLACEHOLDER_VALUES:
        flags.append(f"placeholder value ({name!r})")
    if len(name) == 1:
        flags.append("single-char name")
    if len(name) > 80:
        flags.append(f"suspiciously long ({len(name)} chars)")
    if CONTROL_CHAR_RE.search(name):
        flags.append("contains control characters")
    if name != raw:
        flags.append("leading/trailing whitespace")
    if name == name.upper() and any(c.isalpha() for c in name):
        flags.append("ALL CAPS")
    if name == name.lower() and any(c.isalpha() for c in name) and " " in name:
        flags.append("all lowercase")
    # Mojibake markers — broken UTF-8 decoding artifacts commonly look like "Ã©" or "â€™"
    if any(seq in name for seq in ("Ã©", "Ã¨", "Ã¢", "Ã¼", "â€™", "â€œ", "â€")):
        flags.append("possible mojibake")
    return flags


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--cards-dir", default="cards")
    p.add_argument("--game", default="Magic: The Gathering")
    p.add_argument("--sample", type=int, default=15,
                   help="How many random rows to dump for human spot-check")
    p.add_argument("--out", default=None,
                   help="Markdown report path (default: reports/artist_lint_<date>.md)")
    args = p.parse_args()

    cards_dir = Path(args.cards_dir)
    enriched_total = 0
    filled = 0
    missing = 0
    flagged: list[tuple[str, str, list[str]]] = []  # (path, artist, flags)
    by_artist: Counter = Counter()
    artist_to_cards: dict[str, list[str]] = defaultdict(list)
    case_collisions: dict[str, set[str]] = defaultdict(set)

    for path in cards_dir.rglob("*.md"):
        if not is_card_node(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = parse_frontmatter(text)
        if (fm.get("game") or "").strip() != args.game:
            continue
        tags_raw = (fm.get("tags_hub") or "").strip()
        if not tags_raw or tags_raw in ("[]", '""', "''"):
            continue
        enriched_total += 1
        artist_raw = fm.get("artist")
        if artist_raw is None or not str(artist_raw).strip():
            missing += 1
            flagged.append((str(path), repr(artist_raw), ["missing or empty"]))
            continue
        artist = str(artist_raw).strip()
        filled += 1
        by_artist[artist] += 1
        artist_to_cards[artist].append(str(path))
        case_collisions[artist.lower()].add(artist)
        issues = classify(artist_raw)
        # don't dupe-flag the "missing/empty" cases above
        issues = [i for i in issues if i not in ("missing/empty",)]
        if issues:
            flagged.append((str(path), artist, issues))

    # Build report
    date_str = datetime.date.today().isoformat()
    out_path = Path(args.out) if args.out else REPO_ROOT / "reports" / f"artist_lint_{date_str}.md"

    lines: list[str] = []
    lines.append(f"# Artist lint — {args.game}")
    lines.append(f"_Run date: {date_str}_")
    lines.append("")
    lines.append(f"- **Enriched cards in scope:** {enriched_total}")
    lines.append(f"- **Artist filled:** {filled} ({100*filled/max(enriched_total,1):.1f}%)")
    lines.append(f"- **Artist missing:** {missing} ({100*missing/max(enriched_total,1):.1f}%)")
    lines.append(f"- **Unique artists:** {len(by_artist)}")
    lines.append(f"- **Cards flagged by sanity checks:** {len(flagged)}")
    lines.append("")

    # Top artists
    lines.append("## Top 30 artists by card count")
    lines.append("")
    for artist, count in by_artist.most_common(30):
        lines.append(f"- **{count}** — {artist}")
    lines.append("")

    # Case collisions (same name, different capitalization → suggests dedupe)
    collisions = {k: v for k, v in case_collisions.items() if len(v) > 1}
    if collisions:
        lines.append("## Case collisions (likely typos / inconsistent capitalization)")
        lines.append("")
        for lower, variants in sorted(collisions.items()):
            lines.append(f"- `{lower}` appears as: {sorted(variants)}")
        lines.append("")

    # Sanity flags
    if flagged:
        lines.append("## Sanity flags")
        lines.append("")
        for fpath, artist, issues in flagged[:200]:
            rel = os.path.relpath(fpath, REPO_ROOT)
            lines.append(f"- `{rel}` — artist={artist!r} — {', '.join(issues)}")
        if len(flagged) > 200:
            lines.append(f"- _(+{len(flagged) - 200} more not shown)_")
        lines.append("")

    # Human spot-check sample — pick a few from different artists so Alex sees variety
    lines.append(f"## Random sample for spot-check ({args.sample} cards)")
    lines.append("")
    import random
    rng = random.Random(date_str)
    all_filled = [(p, fm_artist) for artist, paths in artist_to_cards.items() for p in paths
                  for fm_artist in [artist]]
    sample = rng.sample(all_filled, min(args.sample, len(all_filled)))
    for cpath, artist in sample:
        rel = os.path.relpath(cpath, REPO_ROOT)
        # Pull set + name from path for a more readable line
        try:
            stem = Path(cpath).stem
        except Exception:
            stem = cpath
        lines.append(f"- {stem} — artist=**{artist}** — `{rel}`")
    lines.append("")

    text = "\n".join(lines)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")

    print(text)
    print(f"\n[wrote {out_path}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
