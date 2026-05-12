#!/usr/bin/env python3
"""
artist_resolve — Map any artist credit (Scryfall-stored, printed-card-credit, or
hand-typed) to a single canonical artist identity.

Why this exists: Scryfall's stored `artist` field is not always the same string
that appears on the printed card. Artists also evolve their published names
over time (rebranding, marriage, romanization changes). Different printings of
the same card by the same artist can carry different credits. The corpus
preserves the as-captured credit in card frontmatter (printing fidelity), and
this resolver layer maps any of those strings to a single canonical identity
for downstream consumers (bundle prose, storefront credit lines, lint dedupe).

Data source: `cards/_artists/<slug>.md` files with `type: artist` frontmatter
and an `aliases:` list. The canonical `name:` is the resolved value. The
`aliases:` list defines the strings that resolve to it.

API:
    from artist_resolve import resolve, load_index
    idx = load_index()                # call once, cache
    canonical = resolve("Ravenna Tran", idx)   # -> "Jenn Ravenna Tran"
    canonical = resolve("Mark Poole", idx)     # -> "Mark Poole" (no alias entry, returns as-is)

CLI for quick checks:
    python artist_resolve.py "Ravenna Tran"
    python artist_resolve.py --dump     # list all canonical->aliases mappings
    python artist_resolve.py --conflicts # show any alias that maps to multiple canonicals
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent
ARTISTS_DIR = REPO_ROOT / "cards" / "_artists"

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
_LIST_RE = re.compile(r"^([A-Za-z_]+):\s*\[(.*?)\]\s*$", re.M)
_SCALAR_RE = re.compile(r"^([A-Za-z_]+):\s*(.*?)\s*$", re.M)


def _parse_simple_frontmatter(text: str) -> dict:
    m = _FM_RE.match(text)
    if not m:
        return {}
    body = m.group(1)
    fm: dict = {}
    for lm in _LIST_RE.finditer(body):
        key = lm.group(1)
        raw = lm.group(2)
        items = [it.strip().strip('"').strip("'") for it in raw.split(",") if it.strip()]
        fm[key] = items
    for sm in _SCALAR_RE.finditer(body):
        key = sm.group(1)
        if key in fm:
            continue  # list parse already captured this
        val = sm.group(2).strip().strip('"').strip("'")
        fm[key] = val
    return fm


def load_index(artists_dir: Path = ARTISTS_DIR) -> dict[str, str]:
    """Return a {lower-cased credit-or-alias -> canonical name} map.
    Canonical entries map to themselves so any non-aliased input is preserved."""
    index: dict[str, str] = {}
    conflicts: list[tuple[str, str, str]] = []  # (alias, prior_canon, new_canon)
    if not artists_dir.exists():
        return index
    for md in artists_dir.glob("*.md"):
        try:
            txt = md.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = _parse_simple_frontmatter(txt)
        if fm.get("type") != "artist":
            continue
        canon = (fm.get("name") or "").strip()
        if not canon:
            continue
        # Canonical name resolves to itself
        index.setdefault(canon.lower(), canon)
        for alias in fm.get("aliases", []) or []:
            alias = alias.strip()
            if not alias:
                continue
            prior = index.get(alias.lower())
            if prior and prior != canon:
                conflicts.append((alias, prior, canon))
                continue
            index[alias.lower()] = canon
    if conflicts and __name__ == "__main__":
        print("# CONFLICTS — alias maps to multiple canonical names:", file=sys.stderr)
        for a, p, n in conflicts:
            print(f"  {a!r}: {p} vs {n}", file=sys.stderr)
    return index


def resolve(credit: str, index: dict[str, str] | None = None) -> str:
    """Resolve any artist credit string to its canonical name.
    Strings not present in the alias map pass through unchanged (most artists
    do not have an entry yet, and most don't need one). Resolution is
    case-insensitive after whitespace strip."""
    if not credit:
        return ""
    if index is None:
        index = load_index()
    key = credit.strip().lower()
    return index.get(key, credit.strip())


def _cli() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("credit", nargs="?", help="An artist credit string to resolve")
    p.add_argument("--dump", action="store_true", help="List all canonical artists + aliases")
    p.add_argument("--conflicts", action="store_true",
                   help="Report aliases that resolve to multiple canonicals")
    args = p.parse_args()

    idx = load_index()
    if args.dump:
        canon_to_aliases: dict[str, list[str]] = {}
        for alias_lower, canon in idx.items():
            if alias_lower == canon.lower():
                canon_to_aliases.setdefault(canon, [])
            else:
                canon_to_aliases.setdefault(canon, []).append(alias_lower)
        for canon in sorted(canon_to_aliases):
            aliases = sorted(canon_to_aliases[canon])
            if aliases:
                print(f"{canon}  <- {', '.join(aliases)}")
            else:
                print(canon)
        return 0
    if args.conflicts:
        # load_index already emits conflicts to stderr; nothing more to do
        return 0
    if not args.credit:
        p.print_help()
        return 1
    canon = resolve(args.credit, idx)
    print(canon)
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
