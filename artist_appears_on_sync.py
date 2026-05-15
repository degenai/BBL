#!/usr/bin/env python3
"""
artist_appears_on_sync — Sync `appears_on:` on each artist node by walking the
corpus and resolving every card's `artist:` field through artist_resolve.

Why: the artist layer's design (alias-disambiguation across Scryfall vs
printed-card credit drift) doesn't render in Obsidian graph view until each
artist node's `appears_on:` lists every card that resolves to it. The
resolver gives us canonical name from any alias; this script inverts the
lookup and stamps the result.

Idempotent. Diff-reporting (additions + surplus flagged for manual review;
surplus is NOT auto-removed in case a hand-edit added a contextually-valid
entry the resolver doesn't see).

After running, `python layer_appears_on_render.py` picks up the new
appears_on and writes the body `## Appears on` section.

Run from repo root: python artist_appears_on_sync.py
"""
from __future__ import annotations
import re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
CARDS_DIR = ROOT / "cards"
ARTISTS_DIR = CARDS_DIR / "_artists"

from artist_resolve import load_index  # noqa: E402


def parse_appears_on(front: str) -> list[str]:
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
        for item in raw[1:-1].split(","):
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


def get_node_name(front: str) -> str | None:
    m = re.search(r'^name\s*:\s*"?(.+?)"?\s*$', front, re.MULTILINE)
    return m.group(1).strip() if m else None


def write_appears_on(path: Path, entries: list[str]) -> bool:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False
    front, body = parts[1], parts[2]

    new_block = "appears_on:\n" + "".join(f"  - {e}\n" for e in entries)
    if re.search(r"^appears_on\s*:", front, re.MULTILINE):
        new_front = re.sub(
            r"^appears_on\s*:\s*(\[[^\]]*\]|\n(?:\s+-\s+.*\n?)+)",
            new_block.rstrip("\n"),
            front,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        # insert before --- closing
        new_front = front.rstrip() + "\n" + new_block
    if new_front == front:
        return False
    path.write_text(parts[0] + "---" + new_front + "---" + body, encoding="utf-8")
    return True


def main() -> int:
    idx = load_index()

    # Walk all cards, build {canonical -> [card-path-no-ext]}
    hits: dict[str, list[str]] = {}
    for p in CARDS_DIR.rglob("*.md"):
        if any(part.startswith("_") for part in p.parts):
            continue
        text = p.read_text(encoding="utf-8")
        front = text.split("---", 2)[1] if text.count("---") >= 2 else ""
        m = re.search(r"^artist\s*:\s*(.+)$", front, re.MULTILINE)
        if not m:
            continue
        raw = m.group(1).strip().strip("\"").strip("'")
        if not raw:
            continue
        canonical = idx.get(raw.lower())
        if canonical:
            rel = p.relative_to(CARDS_DIR).as_posix()[:-3]  # strip .md
            hits.setdefault(canonical, []).append(rel)

    # Sort each hit list for stable output
    for c in hits:
        hits[c].sort()

    total_changed = 0
    print("== Artist appears_on sync ==")
    for node_path in sorted(ARTISTS_DIR.glob("*.md")):
        text = node_path.read_text(encoding="utf-8")
        front = text.split("---", 2)[1] if text.count("---") >= 2 else ""
        canonical = get_node_name(front)
        if not canonical:
            print(f"  SKIP {node_path.name} (no name field)")
            continue
        resolved = hits.get(canonical, [])
        existing = parse_appears_on(front)
        existing_set = set(existing)
        resolved_set = set(resolved)
        additions = sorted(resolved_set - existing_set)
        surplus = sorted(existing_set - resolved_set)

        print(f"\n  {node_path.name} [{canonical}]")
        print(f"    existing: {len(existing)}, resolved: {len(resolved)}, additions: {len(additions)}, surplus (flagged): {len(surplus)}")
        for a in additions:
            print(f"      + {a}")
        for s in surplus:
            print(f"      ? {s} (NOT auto-removed)")

        # Merged set: union resolved ∪ existing surplus (so we don't lose hand-edits)
        merged = sorted(resolved_set | existing_set)
        if merged != existing:
            if write_appears_on(node_path, merged):
                total_changed += 1
                print(f"    -> WROTE {len(merged)} entries")

    print()
    print(f"Total artist nodes changed: {total_changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
