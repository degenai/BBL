"""
Shared frontmatter normalization helpers — the single source of truth for
how BBL cards render in Obsidian's property panel.

Three idempotent normalizations:

  1. `normalize_block_form_lists(text)` — inline `field: [a, b]` -> block form.
     Inline-quoted lists render as one red string in Obsidian; block form
     renders as chips. Wave 92 fix.

  2. `normalize_scalar_quoting(text)` — quote any unquoted scalar value that
     contains `: ` (colon-space) or other YAML-ambiguous patterns. Embedded
     colon-space in oracle_text / flavor_text breaks Obsidian's YAML parser
     and makes the whole property panel red. Wave 92 fix.

  3. `normalize_tags_last(text)` — move the `tags:` block-list to the end of
     frontmatter. Obsidian parses top-level keys that follow a block-list as
     orphaned (dashes instead of typed widgets). Wave 92.5 fix.

`normalize_all(text)` runs all three in order. `normalize_file(path)` is the
convenience wrapper that reads, normalizes, and writes back only if changed.

Any writer (apply_vision.py, researchbot.update_card, csv2mdbot.py, manual
edits) should call `normalize_file()` after writing so the corpus stays clean.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# Block-form list fields (multi-text in Obsidian property panel).
BLOCK_LIST_FIELDS = frozenset({
    "tags_hub", "tags_filter", "characters", "symbols", "bundles",
    "aliases", "appears_on", "social", "related_characters",
    "ip_resolution_for", "vision_uncertainty", "tag_signals",
    "member_cards", "related_hubs",
})

# Scalar fields whose values commonly contain `: ` and must be quoted.
# (Block-list fields and known boolean / numeric fields are excluded.)
_SCALAR_SKIP_FIELDS = BLOCK_LIST_FIELDS | frozenset({
    "quantity", "held_for_lair", "average_cost_paid", "market_price",
    "image_width", "image_height",
    "date_added", "last_seen", "market_price_as_of",
    "needs_manual_review", "ip_verified", "subject_known_ip",
    "review_good", "review_bad",
})


def _split_frontmatter(text: str) -> tuple[str, str, str] | None:
    """Return (open_marker, fm_text, close_marker + rest) or None if no FM."""
    m = re.match(r"^(---\s*\n)(.*?)(\n---\s*\n)", text, re.DOTALL)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3) + text[m.end():]


def normalize_block_form_lists(text: str) -> tuple[str, int]:
    """Inline JSON list -> YAML block form. Returns (new_text, n_fields_changed)."""
    fb = _split_frontmatter(text)
    if not fb:
        return text, 0
    open_marker, fm_text, rest = fb
    lines = fm_text.split("\n")
    out: list[str] = []
    changed = 0
    for line in lines:
        if ":" in line and "[" in line:
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]
            field, _, rhs = stripped.partition(":")
            rhs = rhs.strip()
            if (
                field in BLOCK_LIST_FIELDS
                and rhs.startswith("[") and rhs.endswith("]")
                and rhs != "[]"
            ):
                try:
                    items = json.loads(rhs)
                except json.JSONDecodeError:
                    inner = rhs[1:-1].strip()
                    items = [v.strip().strip('"').strip("'") for v in inner.split(",")]
                    items = [v for v in items if v]
                if isinstance(items, list) and items:
                    out.append(f"{indent}{field}:")
                    for item in items:
                        out.append(f"{indent}  - {item}")
                    changed += 1
                    continue
        out.append(line)
    if changed == 0:
        return text, 0
    return open_marker + "\n".join(out) + rest, changed


def _needs_quoting(value: str) -> bool:
    if not value:
        return False
    if value.startswith('"') and value.endswith('"'):
        return False
    if value.startswith("'") and value.endswith("'"):
        return False
    if value in ("|", ">", "|-", ">-", "|+", ">+", "[]", "~"):
        return False
    if ": " in value:
        return True
    if "#" in value:
        return True
    if value[0] in "[]{},&*!|>%@`":
        return True
    return False


def normalize_scalar_quoting(text: str) -> tuple[str, int]:
    """Quote unquoted scalars containing `: ` / `#` / flow indicators.
    Returns (new_text, n_fields_changed)."""
    fb = _split_frontmatter(text)
    if not fb:
        return text, 0
    open_marker, fm_text, rest = fb
    lines = fm_text.split("\n")
    out: list[str] = []
    changed = 0
    for line in lines:
        if ":" not in line:
            out.append(line)
            continue
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        if stripped.startswith("- "):
            out.append(line)
            continue
        field, _, rhs = stripped.partition(":")
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", field):
            out.append(line)
            continue
        if field in _SCALAR_SKIP_FIELDS:
            out.append(line)
            continue
        value = rhs.lstrip()
        if _needs_quoting(value):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            trailing_ws = rhs[: len(rhs) - len(rhs.lstrip())] or " "
            out.append(f"{indent}{field}:{trailing_ws}\"{escaped}\"")
            changed += 1
            continue
        out.append(line)
    if changed == 0:
        return text, 0
    return open_marker + "\n".join(out) + rest, changed


def normalize_tags_last(text: str) -> tuple[str, int]:
    """Move `tags:` block-list to the end of frontmatter (Obsidian rendering fix).
    Returns (new_text, 1) if reordered, (text, 0) if no change needed."""
    fb = _split_frontmatter(text)
    if not fb:
        return text, 0
    open_marker, fm_text, rest = fb
    tags_m = re.search(r"^tags:\s*\n((?:  -\s+.*(?:\n|$))+)", fm_text, re.MULTILINE)
    if not tags_m:
        return text, 0
    tail = fm_text[tags_m.end():]
    if not tail.strip():
        return text, 0
    tags_block = fm_text[tags_m.start():tags_m.end()].rstrip("\n")
    before = fm_text[: tags_m.start()].rstrip("\n")
    after = tail.lstrip("\n").rstrip("\n")
    parts = [p for p in (before, after, tags_block) if p]
    new_fm = "\n".join(parts)
    return open_marker + new_fm + "\n" + rest.lstrip("\n"), 1


def normalize_all(text: str) -> tuple[str, dict[str, int]]:
    """Run all three normalizations in order. Returns (new_text, counts_dict)."""
    counts: dict[str, int] = {}
    text, n = normalize_block_form_lists(text)
    counts["block_lists"] = n
    text, n = normalize_scalar_quoting(text)
    counts["scalars_quoted"] = n
    text, n = normalize_tags_last(text)
    counts["tags_reordered"] = n
    return text, counts


def normalize_file(path: Path) -> dict[str, int]:
    """Read, normalize, write back if changed. Returns counts dict (empty on no-op)."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return {}
    new, counts = normalize_all(content)
    if new != content:
        path.write_text(new, encoding="utf-8")
    return counts
