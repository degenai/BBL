#!/usr/bin/env python3
"""Migration: relocate the image cache from images/ to cards/_images/.

Why
---
The Obsidian vault is rooted at cards/, which means anything outside cards/ is
invisible to Obsidian's image-resolver — `![](../../../images/...)` renders as
"could not be found." The fix is to move the image cache *inside* the vault so
embeds resolve cleanly. PNG files aren't graphed by Obsidian (only .md files
become nodes), so this preserves the "card-only graph" constraint.

What this does (run AFTER `git mv images cards/_images`):
1. For every card MD, rewrite frontmatter `reference_image: images/...`
   → `reference_image: cards/_images/...`.
2. Rewrite the embed line in the ## Vision section:
   `![<slug>](../../../images/...)` → `![<slug>](../../_images/...)`.
   (Two ups instead of three because the image cache is now a sibling of the
   <game> directories, not three folders up.)

Idempotent — re-running on already-migrated cards is a no-op.

Run from project root:
    python reports/migrate_images_into_cards.py            # apply
    python reports/migrate_images_into_cards.py --dry-run  # preview
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Frontmatter line: `reference_image: images/<game>/<set>/<slug>.<ext>`
FM_REF_OLD_RE = re.compile(
    r"^(reference_image:\s*)images/", re.M
)

# Body embed: any of the historical formats pointing at the old images/ tree.
# We replace each with the new ../../_images/... form.
EMBED_OLD_RE_VARIANTS = [
    # Standard markdown ![alt](../../../images/<rel>)
    re.compile(r"!\[(?P<alt>[^\]]*)\]\(\.\./\.\./\.\./images/(?P<rel>[^)]+)\)"),
    # Wikilink-style ![[images/<rel>]] (older format that may still survive in odd cards)
    re.compile(r"!\[\[images/(?P<rel>[^\]]+)\]\]"),
    # Already-broken project-relative wikilink ![[/images/<rel>]] (defensive)
    re.compile(r"!\[\[/images/(?P<rel>[^\]]+)\]\]"),
]


def migrate_text(text: str, slug: str) -> tuple[str, dict]:
    """Returns (new_text, info-dict)."""
    info = {"fm_changed": False, "embed_changed": False}

    # 1. Frontmatter rewrite.
    new_text, n = FM_REF_OLD_RE.subn(r"\1cards/_images/", text)
    if n > 0:
        info["fm_changed"] = True
        text = new_text

    # 2. Body embed rewrite — try each known shape, replace once.
    for rx in EMBED_OLD_RE_VARIANTS:
        m = rx.search(text)
        if not m:
            continue
        rel = m.group("rel")
        replacement = f"![{slug}](../../_images/{rel})"
        text = text[: m.start()] + replacement + text[m.end():]
        info["embed_changed"] = True
        break

    return text, info


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="Show what would change without writing.")
    args = ap.parse_args()

    cards_dir = ROOT / "cards"
    if not cards_dir.exists():
        print(f"ERROR: cards/ not found at {cards_dir}", file=sys.stderr)
        return 1

    n_cards = 0
    n_fm = 0
    n_embed = 0

    for card_md in cards_dir.rglob("*.md"):
        n_cards += 1
        text = card_md.read_text(encoding="utf-8")
        new_text, info = migrate_text(text, card_md.stem)
        if not info["fm_changed"] and not info["embed_changed"]:
            continue
        if info["fm_changed"]:
            n_fm += 1
        if info["embed_changed"]:
            n_embed += 1
        if not args.dry_run:
            card_md.write_text(new_text, encoding="utf-8")

    verb = "would change" if args.dry_run else "changed"
    print(f"Walked {n_cards} card MDs:")
    print(f"  {verb} frontmatter reference_image: {n_fm}")
    print(f"  {verb} body embed:                  {n_embed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
