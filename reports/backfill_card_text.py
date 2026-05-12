#!/usr/bin/env python3
"""
backfill_card_text — Stamp `flavor_text:` and `oracle_text:` into existing card
MD frontmatter for cards that were prepared before researchbot started capturing
those fields at prep time (2026-05-11).

Why: the bbl-triviabot agent currently re-fetches Scryfall for every card to
read flavor text, and that's a WebFetch-403 path requiring the curl-with-UA
workaround. If both fields are in the local card frontmatter, triviabot never
needs to hit Scryfall for canonical card text — eliminates a whole class of
per-agent failures and saves tool calls per run.

Strategy:
  - MTG cards: extract Scryfall UUID from reference_image_source_url, hit
    /cards/<uuid>, pull flavor_text + oracle_text via _extract_card_text_scryfall.
  - Pokémon cards: re-query PokemonTCG.io by name + set, pull flavor +
    rules/abilities/attacks via _extract_card_text_pokemontcg.

Idempotent: skips cards that already have both fields populated. Use --force
to overwrite (rare — useful if you change the flattening rules).

Usage:
  python reports/backfill_card_text.py [--game G] [--dry-run] [--limit N] [--sleep S]
"""
from __future__ import annotations
import argparse, re, sys, time, urllib.parse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from researchbot import (
    parse_frontmatter, update_frontmatter_field, http_get_json,
    _extract_card_text_scryfall, _extract_card_text_pokemontcg,
    SCRYFALL_API, POKEMONTCG_API,
)

UUID_RE = re.compile(r"/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.[a-z]+", re.I)


def scryfall_uuid_from_url(url: str) -> str | None:
    if not url:
        return None
    m = UUID_RE.search(url)
    return m.group(1) if m else None


def is_non_card_path(path: Path) -> bool:
    return any(p in ("_images", "_hubs", "_symbols", "_artists", "_characters") for p in path.parts)


def fetch_mtg(uuid: str) -> tuple[str, str]:
    data = http_get_json(f"{SCRYFALL_API}/cards/{uuid}")
    if not data or data.get("object") == "error":
        return "", ""
    return _extract_card_text_scryfall(data)


def fetch_pokemon(name: str, set_name: str) -> tuple[str, str]:
    """Re-query PokemonTCG.io by name + set, pull text. Returns ("","") on miss."""
    if not name:
        return "", ""

    def _q(q: str) -> dict | None:
        url = f"{POKEMONTCG_API}/cards?q={urllib.parse.quote(q)}&pageSize=1"
        data = http_get_json(url)
        if not data:
            return None
        cards = data.get("data") or []
        return cards[0] if cards else None

    card = None
    if set_name:
        card = _q(f'name:"{name}" set.name:"{set_name}"')
    if not card:
        card = _q(f'name:"{name}"')
    if not card:
        return "", ""
    return _extract_card_text_pokemontcg(card)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--cards-dir", default="cards")
    p.add_argument("--game", default=None,
                   help="Restrict to one game (default: all MTG + Pokémon)")
    p.add_argument("--limit", type=int, default=10000)
    p.add_argument("--sleep", type=float, default=0.15)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true",
                   help="Re-stamp even when both fields are already populated")
    args = p.parse_args()

    cards_dir = Path(args.cards_dir)
    targets: list[tuple[Path, dict]] = []
    skipped_both_filled = 0
    skipped_no_strategy = 0

    for path in cards_dir.rglob("*.md"):
        if is_non_card_path(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = parse_frontmatter(text)
        game = (fm.get("game") or "").strip()
        if not game:
            continue
        if args.game and game != args.game:
            continue
        if game not in ("Magic: The Gathering", "Pokemon"):
            skipped_no_strategy += 1
            continue
        existing_flavor = (fm.get("flavor_text") or "").strip()
        existing_oracle = (fm.get("oracle_text") or "").strip()
        if not args.force and existing_flavor and existing_oracle:
            skipped_both_filled += 1
            continue
        targets.append((path, fm))

    print(f"Found {len(targets)} cards to backfill card text")
    print(f"  (skipped: {skipped_both_filled} already have both fields, "
          f"{skipped_no_strategy} on games with no text source)")
    if not targets:
        return 0

    targets = targets[: args.limit]
    print(f"Processing {len(targets)} (limit={args.limit}, sleep={args.sleep}s)\n")

    filled = 0
    failed = 0
    for i, (path, fm) in enumerate(targets, 1):
        game = (fm.get("game") or "").strip()
        name = (fm.get("name") or "").strip()
        set_ = (fm.get("set") or "").strip()
        flavor, oracle = "", ""
        if game == "Magic: The Gathering":
            uuid = scryfall_uuid_from_url(fm.get("reference_image_source_url") or "")
            if not uuid:
                print(f"[{i}/{len(targets)}] {path.name}  -> no Scryfall UUID, skip")
                failed += 1
                continue
            flavor, oracle = fetch_mtg(uuid)
        elif game == "Pokemon":
            flavor, oracle = fetch_pokemon(name, set_)
        time.sleep(args.sleep)
        if not flavor and not oracle:
            print(f"[{i}/{len(targets)}] {path.name}  -> source returned no text")
            failed += 1
            continue
        if args.dry_run:
            preview = (flavor or oracle)[:80]
            print(f"[{i}/{len(targets)}] {path.name}  -> [dry-run] would stamp: {preview!r}")
            filled += 1
            continue
        text = path.read_text(encoding="utf-8")
        if flavor:
            text = update_frontmatter_field(text, "flavor_text", flavor)
        if oracle:
            text = update_frontmatter_field(text, "oracle_text", oracle)
        path.write_text(text, encoding="utf-8")
        bits = []
        if flavor: bits.append("flavor")
        if oracle: bits.append("oracle")
        print(f"[{i}/{len(targets)}] {path.name}  -> {'+'.join(bits)}")
        filled += 1

    print(f"\n=== card-text backfill report ===")
    print(f"  Filled:  {filled}")
    print(f"  Failed:  {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
