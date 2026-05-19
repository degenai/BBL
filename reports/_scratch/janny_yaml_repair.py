#!/usr/bin/env python3
"""Janny sweep — repair two YAML-parse-error patterns surfaced wave 127.

Pattern A: multi-line `oracle_text:` written as plain scalar.
  oracle_text: Sharpness (Colorless) 10
  Headbutt (ColorlessColorless) 20
  image_width: 868

  YAML sees line 2 ("Headbutt...") and tries to parse it as a new key,
  fails on missing colon. Fix: rewrite as block scalar with `|`.

  oracle_text: |-
    Sharpness (Colorless) 10
    Headbutt (ColorlessColorless) 20
  image_width: 868

Pattern B: unquoted `@`-prefix in list items (YAML reserves `@`).
  social:
    - @jenravennaart

  Fix: quote the value.

  social:
    - "@jenravennaart"

Both fixes are surgical line edits — we don't reformat the rest of the
frontmatter. Idempotent (re-running yields zero changes).

USAGE:
  python reports/_scratch/janny_yaml_repair.py --dry-run   # report only
  python reports/_scratch/janny_yaml_repair.py             # apply fixes
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent

# Frontmatter keys whose values are known to be multi-line free text
# (any of these found as a plain scalar with content following on
# unindented lines that don't look like new keys = needs block-scalar wrap)
MULTILINE_TEXT_KEYS = ("oracle_text", "flavor_text")

# Regex for "looks like a new YAML key at column 0" — used to detect
# where the multi-line value should stop being absorbed
KEY_LINE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*:( |$)")


def safe_print(s: str) -> None:
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("ascii", errors="replace").decode("ascii"))


def repair_multiline_text_keys(fm_lines):
    """Walk frontmatter lines; for each MULTILINE_TEXT_KEYS plain-scalar
    occurrence, gather absorbed continuation lines and rewrite as block scalar."""
    out: list[str] = []
    fixes = 0
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if not m or m.group(1) not in MULTILINE_TEXT_KEYS:
            out.append(line)
            i += 1
            continue

        key = m.group(1)
        first_value = m.group(2)

        # Already a block scalar? (e.g. `oracle_text: |` or `oracle_text: >`)
        if first_value.strip() in ("|", "|-", ">", ">-", "|+", ">+"):
            out.append(line)
            i += 1
            continue

        # Empty value? (`oracle_text:` with nothing after) — leave alone
        if not first_value.strip():
            out.append(line)
            i += 1
            continue

        # Gather continuation lines: any line that doesn't look like a
        # new top-level YAML key at column 0.
        gathered = [first_value]
        j = i + 1
        while j < len(fm_lines):
            nxt = fm_lines[j]
            # Empty line ends a plain scalar absorb in canonical YAML, but
            # researchbot's bug-written output doesn't insert blank lines —
            # so we treat blank line as still-in-value too. Stop only on
            # what looks like a new key.
            if KEY_LINE_RE.match(nxt):
                break
            # Don't absorb list-form lines either (`  - foo`)
            if nxt.startswith("- ") or nxt.startswith("  -"):
                break
            gathered.append(nxt)
            j += 1

        # If we only got the one value line (no continuation), it was a
        # legitimate single-line plain scalar — leave it alone.
        if len(gathered) == 1:
            out.append(line)
            i += 1
            continue

        # Rewrite as block scalar (use `|-` to preserve newlines + strip
        # trailing newline, matching researchbot's intent)
        out.append(f"{key}: |-\n")
        for g in gathered:
            # Strip any trailing newline; add 2-space indent
            stripped = g.rstrip("\n")
            out.append(f"  {stripped}\n")
        fixes += 1
        i = j  # skip absorbed lines

    return out, fixes


def repair_at_prefix_list_items(fm_lines):
    """Quote any list item that starts with `@` (or other YAML reserved
    indicator chars)."""
    out: list[str] = []
    fixes = 0
    for line in fm_lines:
        # Match `  - @whatever` or `- @whatever` (any indent, dash, space, @)
        m = re.match(r"^(\s*-\s+)(@[^\s\"'].*)$", line)
        if m:
            indent_dash = m.group(1)
            value = m.group(2).rstrip("\n")
            out.append(f'{indent_dash}"{value}"\n')
            fixes += 1
        else:
            out.append(line)
    return out, fixes


def process_file(path, dry_run):
    """Returns (touched, multiline_fixes, at_fixes, error_msg_if_still_broken)."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False, 0, 0, None

    fm_block = parts[1]
    # Confirm it's still broken before touching
    try:
        yaml.safe_load(fm_block)
        return False, 0, 0, None  # already valid
    except yaml.YAMLError:
        pass

    fm_lines = fm_block.splitlines(keepends=True)
    # Leading newline after opening --- usually present; preserve it
    fm_lines2, ml_fixes = repair_multiline_text_keys(fm_lines)
    fm_lines3, at_fixes = repair_at_prefix_list_items(fm_lines2)

    if ml_fixes == 0 and at_fixes == 0:
        # Couldn't repair — broken for some other reason
        try:
            yaml.safe_load(fm_block)
        except yaml.YAMLError as e:
            return False, 0, 0, str(e).split("\n")[0]
        return False, 0, 0, None

    new_fm = "".join(fm_lines3)

    # Validate the repair
    try:
        yaml.safe_load(new_fm)
    except yaml.YAMLError as e:
        return False, ml_fixes, at_fixes, f"STILL BROKEN: {str(e).split(chr(10))[0]}"

    if not dry_run:
        new_text = parts[0] + "---" + new_fm + "---" + parts[2]
        path.write_text(new_text, encoding="utf-8")
    return True, ml_fixes, at_fixes, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="report only")
    args = ap.parse_args()

    total_files_fixed = 0
    total_ml = 0
    total_at = 0
    still_broken = []

    for path in (REPO / "cards").rglob("*.md"):
        rel = str(path.relative_to(REPO)).replace("\\", "/")
        touched, ml, at, err = process_file(path, args.dry_run)
        if touched:
            total_files_fixed += 1
            total_ml += ml
            total_at += at
            if ml or at:
                tag = []
                if ml: tag.append(f"oracle_text x{ml}")
                if at: tag.append(f"@-quote x{at}")
                safe_print(f"  {'[DRY] ' if args.dry_run else ''}{rel}  ({', '.join(tag)})")
        elif err:
            still_broken.append((rel, err))

    safe_print("")
    mode = "DRY RUN" if args.dry_run else "APPLIED"
    safe_print(f"=== {mode} ===")
    safe_print(f"files repaired: {total_files_fixed}")
    safe_print(f"  oracle_text/flavor_text multiline fixes: {total_ml}")
    safe_print(f"  @-quote fixes: {total_at}")
    if still_broken:
        safe_print(f"\nstill broken ({len(still_broken)} — different root cause, NOT touched):")
        for rel, err in still_broken[:10]:
            safe_print(f"  {rel}")
            safe_print(f"    {err}")
        if len(still_broken) > 10:
            safe_print(f"  ... +{len(still_broken)-10} more")


if __name__ == "__main__":
    main()
