#!/usr/bin/env python3
"""Janny sweep — round 2 YAML repair for patterns not handled by round 1.

Pattern C: Weiss-Schwarz card names with embedded double-quoted segment.
  name: "Confusion" Armin
  name: "104th Cadet Corps Class" Marco

  YAML parses `"Confusion"` as a complete quoted scalar; the trailing
  ` Armin` confuses the parser. Fix: wrap the whole value in single
  quotes (which allow embedded double quotes verbatim).

  name: '"Confusion" Armin'

  This pattern is endemic to Weiss-Schwarz card names where the
  bracketed-quoted-prefix is the card's situational subtitle. Likely to
  recur on every future WS ingest until csv2mdbot is patched to quote.

Pattern D: TAB-indented frontmatter key (Vraska's Finisher only).
  ---
  \tname: Vraska's Finisher
  game: ...

  YAML forbids tabs for indentation. The tab is also useless here —
  the key is at top-level and should be at column 0. Fix: strip the
  leading tab.

Both fixes are surgical. Idempotent.

USAGE:
  python reports/_scratch/janny_yaml_repair_round2.py --dry-run
  python reports/_scratch/janny_yaml_repair_round2.py
"""
import argparse
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent


def safe_print(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("ascii", errors="replace").decode("ascii"))


def repair_ws_quoted_prefix(fm_lines):
    """Pattern C: `name: "Foo" Bar` → `name: '"Foo" Bar'`"""
    out = []
    fixes = 0
    # Allow optional whitespace between closing quote and trail
    pat = re.compile(r'^(\s*)([A-Za-z_][A-Za-z0-9_-]*):\s+("[^"]+")(\s*)(\S.*)$')
    for line in fm_lines:
        m = pat.match(line.rstrip("\n"))
        if m:
            indent, key, quoted, sep, trail = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
            # Preserve original spacing (or insert space if none — readable canonical form)
            sep_out = sep if sep else " "
            full_value = f"{quoted}{sep_out}{trail}"
            # Wrap in single quotes (escape any existing single quotes by doubling)
            escaped = full_value.replace("'", "''")
            out.append(f"{indent}{key}: '{escaped}'\n")
            fixes += 1
        else:
            out.append(line)
    return out, fixes


def repair_tab_indent(fm_lines):
    """Pattern D: leading TAB on a top-level frontmatter key → strip."""
    out = []
    fixes = 0
    for line in fm_lines:
        if line.startswith("\t") and re.match(r"\t+[A-Za-z_][A-Za-z0-9_-]*:", line):
            out.append(line.lstrip("\t"))
            fixes += 1
        else:
            out.append(line)
    return out, fixes


def process_file(path, dry_run):
    text = path.read_text(encoding="utf-8", errors="ignore")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False, 0, 0, None

    fm_block = parts[1]
    try:
        yaml.safe_load(fm_block)
        return False, 0, 0, None
    except yaml.YAMLError:
        pass

    fm_lines = fm_block.splitlines(keepends=True)
    fm_lines2, ws_fixes = repair_ws_quoted_prefix(fm_lines)
    fm_lines3, tab_fixes = repair_tab_indent(fm_lines2)

    if ws_fixes == 0 and tab_fixes == 0:
        try:
            yaml.safe_load(fm_block)
            return False, 0, 0, None
        except yaml.YAMLError as e:
            return False, 0, 0, str(e).split("\n")[0]

    new_fm = "".join(fm_lines3)
    try:
        yaml.safe_load(new_fm)
    except yaml.YAMLError as e:
        return False, ws_fixes, tab_fixes, f"STILL BROKEN: {str(e).split(chr(10))[0]}"

    if not dry_run:
        new_text = parts[0] + "---" + new_fm + "---" + parts[2]
        path.write_text(new_text, encoding="utf-8")
    return True, ws_fixes, tab_fixes, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    fixed = 0
    ws_total = 0
    tab_total = 0
    still_broken = []
    for path in (REPO / "cards").rglob("*.md"):
        rel = str(path.relative_to(REPO)).replace("\\", "/")
        touched, ws, tab, err = process_file(path, args.dry_run)
        if touched:
            fixed += 1
            ws_total += ws
            tab_total += tab
            tag = []
            if ws: tag.append(f"ws-quote x{ws}")
            if tab: tag.append(f"tab-strip x{tab}")
            safe_print(f"  {'[DRY] ' if args.dry_run else ''}{rel}  ({', '.join(tag)})")
        elif err:
            still_broken.append((rel, err))

    mode = "DRY RUN" if args.dry_run else "APPLIED"
    safe_print(f"\n=== {mode} ===")
    safe_print(f"files repaired: {fixed}")
    safe_print(f"  ws-quoted-prefix fixes: {ws_total}")
    safe_print(f"  tab-strip fixes: {tab_total}")
    if still_broken:
        safe_print(f"\nstill broken ({len(still_broken)}):")
        for rel, err in still_broken[:10]:
            safe_print(f"  {rel}")
            safe_print(f"    {err}")


if __name__ == "__main__":
    main()
