"""One-shot migration: rewrite bare-filename Obsidian image embeds in card MDs to
path-qualified wikilinks so Obsidian resolves them unambiguously across sets.

Before: ![[254-island-254.png]]
After:  ![[images/magic-the-gathering/throne-of-eldraine/254-island-254.png]]

Pulls the canonical path from each MD's frontmatter `reference_image` field. Skips
cards where the embed is already path-qualified or where reference_image is empty.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CARDS = REPO / "cards"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
REFIMG_RE = re.compile(r"^reference_image:\s*(.+?)\s*$", re.MULTILINE)
EMBED_RE = re.compile(r"!\[\[([^\]]+)\]\]")


def parse_reference_image(text: str) -> str | None:
    fm_match = FRONTMATTER_RE.match(text)
    if not fm_match:
        return None
    fm = fm_match.group(1)
    m = REFIMG_RE.search(fm)
    if not m:
        return None
    val = m.group(1).strip().strip('"').strip("'")
    return val or None


def fix_one(path: Path) -> str:
    """Returns 'fixed', 'already-ok', 'no-embed', 'no-ref', or 'mismatch'."""
    text = path.read_text(encoding="utf-8")
    ref = parse_reference_image(text)
    if not ref:
        return "no-ref"
    ref = ref.replace("\\", "/")
    expected_basename = Path(ref).name

    embeds = EMBED_RE.findall(text)
    if not embeds:
        return "no-embed"

    changed = False
    for embed in embeds:
        # Skip non-image embeds (defensive — shouldn't happen in this vault).
        if not embed.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            continue
        if embed == ref:
            continue  # already path-qualified to the right path
        if embed == expected_basename:
            # Bare filename — replace with full path.
            text = text.replace(f"![[{embed}]]", f"![[{ref}]]", 1)
            changed = True
        else:
            # Embed points somewhere unexpected — leave it but flag.
            return f"mismatch: embed={embed} ref={ref}"

    if changed:
        path.write_text(text, encoding="utf-8")
        return "fixed"
    return "already-ok"


def main() -> int:
    counts: dict[str, int] = {}
    mismatches: list[tuple[Path, str]] = []
    for md in CARDS.rglob("*.md"):
        result = fix_one(md)
        key = result.split(":", 1)[0]
        counts[key] = counts.get(key, 0) + 1
        if result.startswith("mismatch"):
            mismatches.append((md, result))

    for k in sorted(counts):
        print(f"{k}: {counts[k]}")
    if mismatches:
        print("\nmismatches (left untouched, inspect manually):")
        for path, reason in mismatches:
            print(f"  {path.relative_to(REPO)}  -- {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
