#!/usr/bin/env python3
"""
csv2mdbot — Convert Collectr CSV exports into BBL card-node graph.

Reads a Collectr inventory CSV and:
  1. Creates/updates one MD file per unique card.
  2. Sets quantity=0 for any node previously in graph but absent from new CSV
     (implied traded or sold).
  3. Moves any quantity=0 node to archive/.
  4. Preserves BBL-internal fields like held_for_lair across runs.

Usage:
    python csv2mdbot.py <csv_path> [--cards-dir cards] [--archive-dir archive] [--dry-run]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from bbl_schema import normalize_file  # wave 92.6 chokepoint
from typing import Iterable

# --- Configuration ---

DEFAULT_CARDS_DIR = "cards"
DEFAULT_ARCHIVE_DIR = "archive"
DEFAULT_SEALED_DIR = "sealed"
DEFAULT_SEALED_ARCHIVE_DIR = "sealed_archive"
DEFAULT_REPORTS_DIR = "reports"
LAST_HASH_FILE = ".last-csv-hash"
HISTORY_FILE = "history.md"

# CSV columns we expect (subset; Collectr export may have more)
COL_CATEGORY = "Category"
COL_SET = "Set"
COL_NAME = "Product Name"
COL_NUMBER = "Card Number"
COL_RARITY = "Rarity"
COL_VARIANCE = "Variance"
COL_GRADE = "Grade"
COL_CONDITION = "Card Condition"
COL_COST = "Average Cost Paid"
COL_QTY = "Quantity"
COL_PRICE_PREFIX = "Market Price"  # column header includes date suffix
COL_DATE_ADDED = "Date Added"
COL_NOTES = "Notes"

# Defaults that signal "vanilla" — skipped from filename for readability
DEFAULT_VARIANCE = "Normal"
DEFAULT_GRADE = "Ungraded"
DEFAULT_CONDITION = "Near Mint"

# Frontmatter fields that are BBL-internal (not in CSV) and must persist across runs.
# These are written by other agents (researchbot, lair architect) and must not be
# clobbered when csv2mdbot reconciles a new CSV.
PERSISTENT_FIELDS = ("held_for_lair", "bundles", "tags_hub", "tags_filter", "reference_image")

PERSISTENT_DEFAULTS = {
    "held_for_lair": "0",
    "bundles": "[]",
    "tags_hub": "[]",
    "tags_filter": "[]",
    "reference_image": "",
}


# --- Helpers ---

# Collectr-side set-name aliases. Collectr labels some sets with names that
# diverge from BBL's canonical folder/set values. The Collectr CSV is the
# inventory source-of-truth (what Alex physically owns) but the BBL graph
# uses the canonical name + folder slug. Aliases route a Collectr name to
# the canonical name BEFORE node_path() slugs it. Wave 97.5 fix — added
# after csv2mdbot's path matching would have re-zeroed all 34 cards that
# were migrated out of mystery-booster-cards/ to the-list/ in wave 96.8.
# Lowercased Collectr name -> canonical set name string.
COLLECTR_SET_NAME_ALIASES = {
    "mystery booster cards": "The List",
}


def slug(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "untitled"


def canonical_set_name(raw: str) -> str:
    """Return the canonical set name for a Collectr-style label.
    Pass-through if no alias entry exists."""
    return COLLECTR_SET_NAME_ALIASES.get((raw or "").lower().strip(), raw or "")


def find_price_column(fieldnames: Iterable[str]) -> tuple[str | None, str | None]:
    """Find the Market Price column (header includes date) and extract the date."""
    for f in fieldnames:
        if f.startswith(COL_PRICE_PREFIX):
            m = re.search(r"\d{4}-\d{2}-\d{2}", f)
            return f, (m.group(0) if m else None)
    return None, None


def unique_key(row: dict) -> tuple:
    return (
        row.get(COL_CATEGORY, "").strip(),
        canonical_set_name(row.get(COL_SET, "")).strip(),
        row.get(COL_NUMBER, "").strip(),
        row.get(COL_VARIANCE, "").strip() or DEFAULT_VARIANCE,
        row.get(COL_GRADE, "").strip() or DEFAULT_GRADE,
        row.get(COL_CONDITION, "").strip() or DEFAULT_CONDITION,
    )


def is_sealed(row: dict) -> bool:
    """Sealed-product heuristic: empty Card Number AND empty Rarity.
    Singles always have at least one. Sealed (booster boxes, ETBs, bundles,
    collection boxes, supply sets) have neither.
    """
    return (
        not row.get(COL_NUMBER, "").strip()
        and not row.get(COL_RARITY, "").strip()
    )


def sealed_unique_key(row: dict) -> tuple:
    """Sealed items don't have variance/grade/condition meaningfully, so key on
    game + set + product name."""
    return (
        row.get(COL_CATEGORY, "").strip(),
        canonical_set_name(row.get(COL_SET, "")).strip(),
        row.get(COL_NAME, "").strip(),
    )


def sealed_path(row: dict, base_dir: Path) -> Path:
    game = slug(row.get(COL_CATEGORY, ""))
    name = slug(row.get(COL_NAME, ""))
    return base_dir / game / f"{name}.md"


def node_path(row: dict, base_dir: Path) -> Path:
    """cards/<game>/<set>/<num>-<name-slug>[--variance][--condition].md

    Includes a fallback for the no-num case: if Collectr's CSV has an empty
    Card Number but a numbered version of the same card already exists on
    disk (because researchbot/backfill_no_num.py renamed it to <num>-<slug>.md
    using Scryfall's collector_number), prefer the existing numbered file
    over creating a stale `no-num-*` entry. This keeps the backfill from
    being undone on the next CSV upload."""
    game = slug(row.get(COL_CATEGORY, ""))
    set_ = slug(canonical_set_name(row.get(COL_SET, "")))
    num_raw = (row.get(COL_NUMBER, "") or "").strip()
    num = slug(num_raw or "no-num")
    name = slug(row.get(COL_NAME, ""))
    variance = (row.get(COL_VARIANCE, "") or DEFAULT_VARIANCE).strip()
    grade = (row.get(COL_GRADE, "") or DEFAULT_GRADE).strip()
    condition = (row.get(COL_CONDITION, "") or DEFAULT_CONDITION).strip()

    parts = [num, name] if num else [name]
    suffix = "-".join(filter(None, parts))

    if variance and variance != DEFAULT_VARIANCE:
        suffix += f"--{slug(variance)}"
    if grade and grade != DEFAULT_GRADE:
        suffix += f"--{slug(grade)}"
    if condition and condition != DEFAULT_CONDITION:
        suffix += f"--{slug(condition)}"

    canonical = base_dir / game / set_ / f"{suffix}.md"

    # No-num fallback: check if a numbered version of this card already exists.
    # Match any file whose name ends with `-<name-slug>.md` in the same set dir
    # and has a leading numeric (or alphanumeric collector-number) component.
    if not num_raw and not canonical.exists():
        set_dir = base_dir / game / set_
        if set_dir.exists():
            # Build the variance/condition suffix tail so we match the right variant
            tail = ""
            if variance and variance != DEFAULT_VARIANCE:
                tail += f"--{slug(variance)}"
            if grade and grade != DEFAULT_GRADE:
                tail += f"--{slug(grade)}"
            if condition and condition != DEFAULT_CONDITION:
                tail += f"--{slug(condition)}"
            target_tail = f"-{name}{tail}.md"
            for existing in set_dir.iterdir():
                if not existing.is_file() or not existing.name.endswith(target_tail):
                    continue
                if existing.name.startswith("no-num-"):
                    continue  # don't fall back to another no-num file
                return existing

    return canonical


# --- Frontmatter I/O (minimal, no PyYAML dependency) ---

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        # Strip matching surrounding quotes (yaml_safe_scalar wraps any value
        # containing `: ` etc. in double quotes; comparisons fail without strip).
        if len(v) >= 2 and ((v[0] == '"' and v[-1] == '"') or (v[0] == "'" and v[-1] == "'")):
            v = v[1:-1]
        out[k.strip()] = v
    return out


def load_persistent(path: Path) -> dict:
    """Read just the persistent BBL-internal fields off an existing node."""
    if not path.exists():
        return {}
    fm = parse_frontmatter(path.read_text(encoding="utf-8"))
    return {k: fm.get(k) for k in PERSISTENT_FIELDS if fm.get(k) is not None}


# Fields csv2mdbot OWNS — anything the CSV controls. These get overwritten on every run.
# Everything else (vision tags, IP flags, mood, body content, ## Vision section, ## Notes
# narrative) belongs to researchbot / apply_vision / the human and must be preserved.
CSV_MANAGED_FIELDS = (
    "name", "game", "set", "collector_number", "rarity", "variance", "grade",
    "condition", "quantity", "average_cost_paid", "market_price",
    "market_price_as_of", "date_added", "last_seen",
)


def _update_fm_field(text: str, field: str, value: str) -> str:
    """Surgical frontmatter field update. Replaces an existing `field: ...` line,
    or inserts before the closing `---`. Mirrors researchbot.update_frontmatter_field
    so csv2mdbot stays stdlib-only (no cross-module import on the hot path)."""
    pattern = rf"^{re.escape(field)}:.*$"
    if re.search(pattern, text, flags=re.MULTILINE):
        return re.sub(pattern, f"{field}: {value}", text, count=1, flags=re.MULTILINE)
    m = FRONTMATTER_RE.match(text)
    if not m:
        return text
    fm_end = m.end(1)
    return text[:fm_end] + f"\n{field}: {value}" + text[fm_end:]


def surgical_update_existing(path: Path, row: dict, price_col: str | None,
                             price_date: str | None, last_seen: str,
                             quantity_override: int | None = None) -> None:
    """Update an existing card MD in place. Touches ONLY csv-managed frontmatter
    fields. Leaves researchbot-managed frontmatter, body content, and the
    `## Vision` / `## Notes` sections completely alone.

    This is the fix for the body-wipe bug: csv2mdbot used to re-render the whole
    file from template on every run, destroying the vision narrative and image
    embed every time a new CSV landed. Now CSV is the source of truth only for
    fields it actually owns.
    """
    qty = quantity_override if quantity_override is not None else int(row.get(COL_QTY) or 0)
    text = path.read_text(encoding="utf-8")

    updates = {
        "name": yaml_safe_scalar(row.get(COL_NAME, "").strip()),
        "game": row.get(COL_CATEGORY, "").strip(),
        "set": yaml_safe_scalar(canonical_set_name(row.get(COL_SET, "")).strip()),
        "collector_number": row.get(COL_NUMBER, "").strip(),
        "rarity": row.get(COL_RARITY, "").strip(),
        "variance": row.get(COL_VARIANCE, "").strip() or DEFAULT_VARIANCE,
        "grade": row.get(COL_GRADE, "").strip() or DEFAULT_GRADE,
        "condition": row.get(COL_CONDITION, "").strip() or DEFAULT_CONDITION,
        "quantity": str(qty),
        "average_cost_paid": collapse_zero(row.get(COL_COST, "")),
        "market_price": collapse_zero(row.get(price_col, "")) if price_col else "0",
        "market_price_as_of": price_date or "",
        "date_added": row.get(COL_DATE_ADDED, "").strip(),
        "last_seen": last_seen,
    }
    for field, value in updates.items():
        text = _update_fm_field(text, field, value)

    path.write_text(text, encoding="utf-8")
    normalize_file(path)


# --- Rendering ---

# Notes that are just punctuation / whitespace / common CSV junk are treated as empty.
NOISE_NOTES_RE = re.compile(r"^[\s;,.\-_/\\|]*$")


def clean_notes(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw or NOISE_NOTES_RE.match(raw):
        return ""
    return raw


def collapse_zero(s: str) -> str:
    """Render zero-valued costs/prices as '0' instead of '0.0000'. Leave non-zero values alone."""
    s = (s or "").strip()
    if not s:
        return "0"
    try:
        return "0" if float(s) == 0.0 else s
    except ValueError:
        return s


def yaml_safe_scalar(value: str) -> str:
    """Render a value for a YAML scalar field, wrapping it in single quotes
    when the raw value would break YAML parsing.

    Triggers wrap on: a leading `"` (would open a double-quoted scalar that
    closes mid-string and leaves trailing garbage), embedded `: `, leading
    indicators (`#`, `&`, `*`, `!`, `|`, `>`, `%`, `@`, ``), or other YAML
    flow characters that confuse Obsidian's frontmatter parser. Pattern
    discovered wave 111: Bushiroad-style `\"<Modifier>\" <Character>` names
    (e.g. `\"104th Cadet Corps Class\" Marco`) rendered as red invalid YAML."""
    s = (value or "").strip()
    if not s:
        return ""
    needs_wrap = (
        s.startswith('"')
        or ": " in s
        or s[0] in "#&*!|>%@`"
        or s.startswith("- ")
    )
    if not needs_wrap:
        return s
    escaped = s.replace("'", "''")
    return f"'{escaped}'"


NODE_TEMPLATE_HEAD = """---
name: {name}
game: {game}
set: {set}
collector_number: {number}
rarity: {rarity}
variance: {variance}
grade: {grade}
condition: {condition}
quantity: {quantity}
held_for_lair: {held_for_lair}
bundles: {bundles}
tags_hub: {tags_hub}
tags_filter: {tags_filter}
reference_image: {reference_image}
average_cost_paid: {cost}
market_price: {price}
market_price_as_of: {price_date}
date_added: {date_added}
last_seen: {last_seen}
---

# {body_name} ({body_set})
"""


def render_node(row: dict, price_col: str | None, price_date: str | None,
                last_seen: str, persistent: dict, quantity_override: int | None = None) -> str:
    qty = quantity_override if quantity_override is not None else int(row.get(COL_QTY) or 0)
    # For each persistent field, prefer the existing value from disk, fall back to default
    persisted = {k: persistent.get(k, PERSISTENT_DEFAULTS[k]) for k in PERSISTENT_FIELDS}
    raw_name = row.get(COL_NAME, "").strip()
    raw_set = canonical_set_name(row.get(COL_SET, "")).strip()
    body = NODE_TEMPLATE_HEAD.format(
        name=yaml_safe_scalar(raw_name),
        body_name=raw_name,
        game=row.get(COL_CATEGORY, "").strip(),
        set=yaml_safe_scalar(raw_set),
        body_set=raw_set,
        number=row.get(COL_NUMBER, "").strip(),
        rarity=row.get(COL_RARITY, "").strip(),
        variance=row.get(COL_VARIANCE, "").strip() or DEFAULT_VARIANCE,
        grade=row.get(COL_GRADE, "").strip() or DEFAULT_GRADE,
        condition=row.get(COL_CONDITION, "").strip() or DEFAULT_CONDITION,
        quantity=qty,
        held_for_lair=persisted["held_for_lair"],
        bundles=persisted["bundles"],
        tags_hub=persisted["tags_hub"],
        tags_filter=persisted["tags_filter"],
        reference_image=persisted["reference_image"],
        cost=collapse_zero(row.get(COL_COST, "")),
        price=collapse_zero(row.get(price_col, "")) if price_col else "0",
        price_date=price_date or "",
        date_added=row.get(COL_DATE_ADDED, "").strip(),
        last_seen=last_seen,
    )
    notes = clean_notes(row.get(COL_NOTES, ""))
    if notes:
        body += f"\n## Notes\n\n{notes}\n"
    return body


SEALED_TEMPLATE_HEAD = """---
name: {name}
game: {game}
set: {set}
sealed: true
quantity: {quantity}
average_cost_paid: {cost}
market_price: {price}
market_price_as_of: {price_date}
date_added: {date_added}
last_seen: {last_seen}
---

# {name}
"""


def render_sealed(row: dict, price_col: str | None, price_date: str | None,
                  last_seen: str, quantity_override: int | None = None) -> str:
    qty = quantity_override if quantity_override is not None else int(row.get(COL_QTY) or 0)
    body = SEALED_TEMPLATE_HEAD.format(
        name=row.get(COL_NAME, "").strip(),
        game=row.get(COL_CATEGORY, "").strip(),
        set=canonical_set_name(row.get(COL_SET, "")).strip(),
        quantity=qty,
        cost=collapse_zero(row.get(COL_COST, "")),
        price=collapse_zero(row.get(price_col, "")) if price_col else "0",
        price_date=price_date or "",
        date_added=row.get(COL_DATE_ADDED, "").strip(),
        last_seen=last_seen,
    )
    notes = clean_notes(row.get(COL_NOTES, ""))
    if notes:
        body += f"\n## Notes\n\n{notes}\n"
    return body


# --- Main reconciliation ---


def _inject_archived_on(text: str, archived_on: str) -> str:
    """Add or update an `archived_on:` line in frontmatter."""
    if re.search(r"^archived_on:", text, flags=re.MULTILINE):
        return re.sub(r"^archived_on:.*$", f"archived_on: {archived_on}", text,
                      count=1, flags=re.MULTILINE)
    # Insert before closing --- of frontmatter
    m = FRONTMATTER_RE.match(text)
    if not m:
        return text
    fm_end = m.end(1)  # position just after frontmatter content, before \n---
    return text[:fm_end] + f"\narchived_on: {archived_on}" + text[fm_end:]


def _is_non_card_node(path: Path, fm: dict) -> bool:
    """Skip MDs that aren't inventory cards: hub concept pages, symbol pages
    (iconographic ideology entries), artist identity pages, character identity
    pages, image-cache sidecars, anything under an _underscore-prefixed
    directory inside cards/. Hub pages declare `type: hub`, symbol pages
    `type: symbol`, artist pages `type: artist`, character pages
    `type: character`; the path-based check is the belt-and-suspenders guard
    so we never accidentally zero/archive these."""
    if fm.get("type") in ("hub", "symbol", "artist", "character"):
        return True
    # Any path segment starting with `_` (e.g. cards/_hubs/, cards/_images/) is
    # not inventory. _images/ is for cached PNGs and doesn't contain MDs, but
    # the convention generalizes.
    for part in path.parts:
        if part.startswith("_"):
            return True
    return False


def _zero_and_archive_dir(active_dir: Path, archive_dir: Path,
                          seen_paths: set[Path], report: dict, dry_run: bool,
                          report_prefix: str = "") -> None:
    """Shared zero-out + archive logic for any active/archive pair (cards or sealed)."""
    if not active_dir.exists():
        return
    today = date.today().isoformat()

    # Zero out anything not seen this run
    for existing in active_dir.rglob("*.md"):
        if existing in seen_paths:
            continue
        text = existing.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if _is_non_card_node(existing, fm):
            continue
        new_text = re.sub(
            r"^(quantity:\s*)\d+",
            r"\g<1>0",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        if not dry_run:
            existing.write_text(new_text, encoding="utf-8")
            normalize_file(existing)
        report[f"{report_prefix}zeroed"] += 1

    # Archive any zero-quantity nodes (stamping archived_on)
    for existing in list(active_dir.rglob("*.md")):
        text = existing.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if _is_non_card_node(existing, fm):
            continue
        try:
            qty = int(fm.get("quantity") or 0)
        except ValueError:
            qty = 0
        if qty == 0:
            rel = existing.relative_to(active_dir)
            target = archive_dir / rel
            if dry_run:
                report[f"{report_prefix}archived"] += 1
                continue
            stamped = _inject_archived_on(text, today)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(stamped, encoding="utf-8")
            normalize_file(target)
            existing.unlink()
            report[f"{report_prefix}archived"] += 1
        else:
            report[f"{report_prefix}kept"] += 1


def _cleanup_misplaced_sealed_in_cards(cards_dir: Path, dry_run: bool) -> int:
    """One-shot migration: any node in cards/ with empty collector_number AND empty
    rarity in its frontmatter is a sealed product that was misclassified before the
    sealed-routing logic existed. Delete it so the main pass re-creates it in sealed/.
    Idempotent: noop if there are no misplaced nodes.

    **CRITICAL:** Must skip non-card nodes (hub / symbol / artist MDs under
    underscored directories). They also have no collector_number and no rarity
    because they're not cards. Without this guard the migration nukes the
    foundational layers. Caught the hard way 2026-05-11 — 3 hubs, 1 symbol, and
    1 artist MD were wiped in one csv2mdbot run before the guard was added."""
    if not cards_dir.exists():
        return 0
    moved = 0
    for path in list(cards_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        # Belt-and-suspenders: hubs/symbols/artists live under _underscored
        # directories AND declare type:hub/symbol/artist. Both checks live
        # in _is_non_card_node so we reuse it.
        if _is_non_card_node(path, fm):
            continue
        # collector_number and rarity both empty (or missing) = sealed
        cn = (fm.get("collector_number") or "").strip()
        rar = (fm.get("rarity") or "").strip()
        if not cn and not rar:
            if not dry_run:
                path.unlink()
            moved += 1
    return moved


def reconcile(csv_path: Path, cards_dir: Path, archive_dir: Path,
              sealed_dir: Path, sealed_archive_dir: Path, dry_run: bool) -> dict:
    today = date.today().isoformat()
    report = {
        "created": 0, "updated": 0, "zeroed": 0, "archived": 0, "kept": 0,
        "sealed_created": 0, "sealed_updated": 0, "sealed_zeroed": 0,
        "sealed_archived": 0, "sealed_kept": 0,
        "misplaced_sealed_cleaned": 0,
        "errors": [],
    }

    # Read CSV
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            report["errors"].append("CSV has no header")
            return report
        price_col, price_date = find_price_column(reader.fieldnames)
        rows = list(reader)

    # One-shot: clean up any sealed-looking nodes mistakenly in cards/ from older runs
    report["misplaced_sealed_cleaned"] = _cleanup_misplaced_sealed_in_cards(cards_dir, dry_run)

    # Split rows into card vs sealed
    card_rows = [r for r in rows if not is_sealed(r)]
    sealed_rows = [r for r in rows if is_sealed(r)]

    # --- Cards pass ---
    aggregated: dict[tuple, dict] = {}
    qty_sums: dict[tuple, int] = defaultdict(int)
    for row in card_rows:
        try:
            key = unique_key(row)
            qty_sums[key] += int(row.get(COL_QTY) or 0)
            aggregated[key] = row
        except (ValueError, TypeError) as e:
            report["errors"].append(f"Bad card row {row.get(COL_NAME, '?')}: {e}")

    seen_card_paths: set[Path] = set()
    for key, row in aggregated.items():
        path = node_path(row, cards_dir)
        archived_path = node_path(row, archive_dir)
        existed_in_cards = path.exists()
        existed_in_archive = archived_path.exists()

        if dry_run:
            if existed_in_cards:
                report["updated"] += 1
            else:
                report["created"] += 1
            seen_card_paths.add(path)
            continue

        path.parent.mkdir(parents=True, exist_ok=True)

        if existed_in_cards:
            # Surgical update — preserve vision tags, IP flags, ## Vision body, ## Notes.
            surgical_update_existing(
                path, row, price_col, price_date,
                last_seen=today, quantity_override=qty_sums[key],
            )
            seen_card_paths.add(path)
            report["updated"] += 1
        elif existed_in_archive:
            # Card returning from archive — surgical update its archived MD too,
            # then move it back into cards/.
            surgical_update_existing(
                archived_path, row, price_col, price_date,
                last_seen=today, quantity_override=qty_sums[key],
            )
            archived_path.replace(path)
            seen_card_paths.add(path)
            report["created"] += 1
        else:
            # Brand-new card — full template render is appropriate.
            content = render_node(
                row, price_col, price_date,
                last_seen=today, persistent={},
                quantity_override=qty_sums[key],
            )
            path.write_text(content, encoding="utf-8")
            normalize_file(path)
            seen_card_paths.add(path)
            report["created"] += 1

    _zero_and_archive_dir(cards_dir, archive_dir, seen_card_paths, report, dry_run)

    # --- Sealed pass ---
    sealed_agg: dict[tuple, dict] = {}
    sealed_qty: dict[tuple, int] = defaultdict(int)
    for row in sealed_rows:
        try:
            key = sealed_unique_key(row)
            sealed_qty[key] += int(row.get(COL_QTY) or 0)
            sealed_agg[key] = row
        except (ValueError, TypeError) as e:
            report["errors"].append(f"Bad sealed row {row.get(COL_NAME, '?')}: {e}")

    seen_sealed_paths: set[Path] = set()
    for key, row in sealed_agg.items():
        path = sealed_path(row, sealed_dir)
        archived_path = sealed_path(row, sealed_archive_dir)
        existed_in_sealed = path.exists()
        existed_in_archive = archived_path.exists()

        content = render_sealed(
            row, price_col, price_date,
            last_seen=today,
            quantity_override=sealed_qty[key],
        )

        if dry_run:
            if existed_in_sealed:
                report["sealed_updated"] += 1
            else:
                report["sealed_created"] += 1
            seen_sealed_paths.add(path)
            continue

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        normalize_file(path)
        seen_sealed_paths.add(path)

        if existed_in_archive and not existed_in_sealed:
            archived_path.unlink()
            report["sealed_created"] += 1
        elif existed_in_sealed:
            report["sealed_updated"] += 1
        else:
            report["sealed_created"] += 1

    _zero_and_archive_dir(sealed_dir, sealed_archive_dir, seen_sealed_paths, report, dry_run,
                          report_prefix="sealed_")

    return report


def compute_csv_hash(csv_path: Path) -> str:
    h = hashlib.sha256()
    with csv_path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_last_hash(reports_dir: Path) -> str | None:
    p = reports_dir / LAST_HASH_FILE
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8").strip() or None


def write_last_hash(reports_dir: Path, hex_hash: str) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / LAST_HASH_FILE).write_text(hex_hash, encoding="utf-8")


def append_history(reports_dir: Path, csv_path: Path, csv_hash: str, report: dict) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    history = reports_dir / HISTORY_FILE
    if not history.exists():
        history.write_text("# csv2mdbot run history\n\nAppend-only log of every non-skipped run.\n\n", encoding="utf-8")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = (
        f"- {ts}  `{csv_path.name}`  hash:`{csv_hash[:12]}`  "
        f"singles[c={report['created']} u={report['updated']} "
        f"z={report['zeroed']} a={report['archived']} k={report['kept']}]  "
        f"sealed[c={report['sealed_created']} u={report['sealed_updated']} "
        f"z={report['sealed_zeroed']} a={report['sealed_archived']} k={report['sealed_kept']}]"
    )
    if report["misplaced_sealed_cleaned"]:
        line += f"  migrated={report['misplaced_sealed_cleaned']}"
    if report["errors"]:
        line += f"  errors={len(report['errors'])}"
    with history.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv_path", type=Path, help="Path to Collectr CSV export")
    ap.add_argument("--cards-dir", type=Path, default=Path(DEFAULT_CARDS_DIR))
    ap.add_argument("--archive-dir", type=Path, default=Path(DEFAULT_ARCHIVE_DIR))
    ap.add_argument("--sealed-dir", type=Path, default=Path(DEFAULT_SEALED_DIR))
    ap.add_argument("--sealed-archive-dir", type=Path, default=Path(DEFAULT_SEALED_ARCHIVE_DIR))
    ap.add_argument("--reports-dir", type=Path, default=Path(DEFAULT_REPORTS_DIR))
    ap.add_argument("--dry-run", action="store_true",
                    help="Report what would happen without writing files")
    ap.add_argument("--force", action="store_true",
                    help="Run even if CSV hash matches the last run")
    args = ap.parse_args()

    if not args.csv_path.exists():
        print(f"ERROR: CSV not found: {args.csv_path}", file=sys.stderr)
        sys.exit(1)

    csv_hash = compute_csv_hash(args.csv_path)
    last_hash = read_last_hash(args.reports_dir)
    if last_hash == csv_hash and not args.force and not args.dry_run:
        print(f"CSV unchanged since last run (hash {csv_hash[:12]}). Skipping. Use --force to run anyway.")
        sys.exit(0)

    report = reconcile(args.csv_path, args.cards_dir, args.archive_dir,
                       args.sealed_dir, args.sealed_archive_dir, args.dry_run)

    print(f"\n=== csv2mdbot run report{' (DRY RUN)' if args.dry_run else ''} ===")
    print("  -- Singles --")
    print(f"    Created:  {report['created']}")
    print(f"    Updated:  {report['updated']}")
    print(f"    Zeroed:   {report['zeroed']}  (in graph, absent from CSV)")
    print(f"    Archived: {report['archived']} (qty=0 moved to {args.archive_dir})")
    print(f"    Kept:     {report['kept']}")
    print("  -- Sealed --")
    print(f"    Created:  {report['sealed_created']}")
    print(f"    Updated:  {report['sealed_updated']}")
    print(f"    Zeroed:   {report['sealed_zeroed']}")
    print(f"    Archived: {report['sealed_archived']} (qty=0 moved to {args.sealed_archive_dir})")
    print(f"    Kept:     {report['sealed_kept']}")
    if report["misplaced_sealed_cleaned"]:
        print(f"  -- Migration: {report['misplaced_sealed_cleaned']} sealed nodes "
              f"removed from {args.cards_dir} (re-created under {args.sealed_dir})")
    if report["errors"]:
        print(f"  Errors:   {len(report['errors'])}")
        for e in report["errors"][:10]:
            print(f"    - {e}")

    # Ergonomic hint: when new cards were created, the chronological review
    # queue is stale until those cards are enriched and the queue is rebuilt.
    new_cards = report["created"]
    if new_cards and not args.dry_run:
        print(f"\n  Note: {new_cards} new card(s) created. Next steps:")
        print(f"    1. python researchbot.py --prepare-only --limit 600 [--game ...]")
        print(f"    2. Run bbl-researcher batches on the ready queue.")
        print(f"    3. After enrichment + commit, run `python bbl_review.py build`")
        print(f"       to refresh the review queue with the new cards.")
        print(f"  (`python bbl_review.py status` warns when the queue is stale.)")

    if not args.dry_run:
        write_last_hash(args.reports_dir, csv_hash)
        append_history(args.reports_dir, args.csv_path, csv_hash, report)


if __name__ == "__main__":
    main()
