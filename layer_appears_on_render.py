#!/usr/bin/env python3
"""
layer_appears_on_render — Renders the `appears_on:` YAML list on each layer
node (cards/_characters, cards/_symbols, cards/_artists) into an in-body
`## Appears on` section with `[[basename]]` wikilinks.

Why: Obsidian's graph view only draws edges from `[[wikilinks]]` in body
markdown (or wikilink-typed frontmatter). YAML string lists don't render as
edges. Without this rendering, the layer-node clique floats disconnected
from the ~1954 anchor cards it aggregates.

Idempotent: if a `## Appears on` section already exists, it is replaced.
Section is inserted before the *first* terminal section if one matches
(`## Canonical sources`, `## See also`, `## Notes`), otherwise appended at
end-of-file. Sentinel HTML comment marks the auto-generated block.

Card basenames are globally unique except for `255-island-255` (×2). For
collisions, the full subpath display alias is used.

Usage:
    python layer_appears_on_render.py            # render all layer dirs
    python layer_appears_on_render.py --dry-run  # report only
    python layer_appears_on_render.py --layer _characters  # restrict
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent
CARDS_DIR = REPO_ROOT / "cards"
LAYER_DIRS = ["_characters", "_symbols", "_artists"]

SENTINEL = "<!-- auto-generated from appears_on; do not edit by hand -->"
SECTION_HEADING = "## Appears on"
TERMINAL_HEADINGS = ["## Canonical sources", "## See also", "## Notes"]


def build_basename_index() -> tuple[dict[str, str], set[str]]:
    """Map card-stem -> relative path. Returns (index, set-of-duplicates)."""
    counts: Counter[str] = Counter()
    index: dict[str, str] = {}
    for p in CARDS_DIR.rglob("*.md"):
        if any(part.startswith("_") for part in p.parts):
            continue
        rel = p.relative_to(CARDS_DIR).as_posix()
        # strip ".md"
        rel_no_ext = rel[:-3] if rel.endswith(".md") else rel
        stem = p.stem
        counts[stem] += 1
        # store first-found; collisions handled separately
        if stem not in index:
            index[stem] = rel_no_ext
    dupes = {s for s, c in counts.items() if c > 1}
    return index, dupes


def parse_appears_on(front: str) -> list[str]:
    """Extract appears_on entries from frontmatter YAML."""
    # match list-form or flow-form
    m = re.search(
        r"^appears_on\s*:\s*(\[[^\]]*\]|\n(?:\s+-\s+.*\n?)+)",
        front,
        re.MULTILINE,
    )
    if not m:
        return []
    raw = m.group(1).strip()
    entries: list[str] = []
    if raw.startswith("["):
        inner = raw[1:-1]
        for item in inner.split(","):
            item = item.strip().strip("'\"")
            if item:
                entries.append(item)
    else:
        for line in raw.splitlines():
            line = line.strip()
            if line.startswith("-"):
                val = line[1:].strip().strip("'\"")
                if val:
                    entries.append(val)
    return entries


def entry_to_wikilink(entry: str, basename_idx: dict[str, str], dupes: set[str]) -> str:
    """Convert an appears_on entry to a body wikilink.

    Entry forms seen in corpus:
      - magic-the-gathering/war-of-the-spark/26-prison-realm  (path-like, no .md)
      - 26-prison-realm                                       (bare basename)
    """
    entry = entry.strip().strip("\"'")
    # strip .md if accidentally included
    if entry.endswith(".md"):
        entry = entry[:-3]
    # extract basename
    basename = entry.rsplit("/", 1)[-1]
    if basename in dupes:
        # use full subpath as link target with basename as display
        return f"[[{entry}|{basename}]]"
    return f"[[{basename}]]"


def render_section(entries: list[str], basename_idx: dict[str, str], dupes: set[str]) -> str:
    if not entries:
        return ""
    lines = [SECTION_HEADING, "", SENTINEL, ""]
    for e in entries:
        lines.append(f"- {entry_to_wikilink(e, basename_idx, dupes)}")
    lines.append("")
    return "\n".join(lines)


def splice_into_body(body: str, new_section: str) -> str:
    """Insert/replace the `## Appears on` section in body markdown.

    If section already exists, replace from heading to next `## ` (any) or EOF.
    Otherwise insert before first terminal heading if present, else append.
    """
    # detect existing section
    existing = re.search(
        r"^## Appears on\s*$.*?(?=^## |\Z)",
        body,
        re.MULTILINE | re.DOTALL,
    )
    if existing:
        return body[: existing.start()] + new_section + body[existing.end():]

    # find first terminal heading to insert before
    insert_at = len(body)
    for h in TERMINAL_HEADINGS:
        m = re.search(rf"^{re.escape(h)}\s*$", body, re.MULTILINE)
        if m and m.start() < insert_at:
            insert_at = m.start()

    sep = "" if body[:insert_at].endswith("\n\n") else ("\n" if body[:insert_at].endswith("\n") else "\n\n")
    return body[:insert_at] + sep + new_section + ("\n" if insert_at < len(body) else "") + body[insert_at:]


def process_layer_file(path: Path, basename_idx: dict[str, str], dupes: set[str], dry_run: bool) -> tuple[bool, int]:
    """Return (changed, num_anchors)."""
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False, 0
    front, body = parts[1], parts[2]
    entries = parse_appears_on(front)
    if not entries:
        return False, 0

    section = render_section(entries, basename_idx, dupes)
    new_body = splice_into_body(body, section)
    if new_body == body:
        return False, len(entries)

    if not dry_run:
        new_text = parts[0] + "---" + front + "---" + new_body
        path.write_text(new_text, encoding="utf-8")
    return True, len(entries)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--layer", choices=LAYER_DIRS + ["all"], default="all")
    args = ap.parse_args()

    basename_idx, dupes = build_basename_index()
    if dupes:
        print(f"[basename collisions: {len(dupes)}] -> will emit full-path wikilinks for: {sorted(dupes)}")

    target_dirs = LAYER_DIRS if args.layer == "all" else [args.layer]
    total_files = 0
    total_changed = 0
    total_anchors = 0
    for layer in target_dirs:
        d = CARDS_DIR / layer
        if not d.exists():
            continue
        for f in sorted(d.glob("*.md")):
            total_files += 1
            changed, n = process_layer_file(f, basename_idx, dupes, args.dry_run)
            if changed:
                total_changed += 1
                total_anchors += n
                print(f"  {'[DRY] ' if args.dry_run else ''}{f.relative_to(REPO_ROOT)} -> {n} anchors")

    print()
    print(f"Files seen:    {total_files}")
    print(f"Files changed: {total_changed}{' (dry-run)' if args.dry_run else ''}")
    print(f"Total anchors rendered: {total_anchors}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
