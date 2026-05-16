"""
Quote YAML scalar values containing characters that break Obsidian's parser.

The most common offender is `: ` (colon + space) inside oracle_text / flavor_text
values: YAML treats it as a key-value separator and the property panel renders
the whole field red-invalid. Wave 92 fix.

Rules — quote a top-level frontmatter scalar value if all of these are true:
  - It is a single-line value (no block-list, no block-literal, no folded)
  - It is currently UNQUOTED (not already starting with " or ')
  - It contains a YAML-ambiguous pattern: `: ` anywhere, or `#` anywhere,
    or starts with a YAML flow indicator
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Don't touch list-typed fields (those are handled by inline_to_block_yaml.py)
SKIP_FIELDS = {
    "tags_hub", "tags_filter", "characters", "symbols", "bundles",
    "aliases", "appears_on", "social", "related_characters",
    "ip_resolution_for", "vision_uncertainty",
}

# Characters / patterns that require the value to be quoted
def needs_quoting(value: str) -> bool:
    if not value:
        return False
    if value.startswith('"') and value.endswith('"'):
        return False
    if value.startswith("'") and value.endswith("'"):
        return False
    # Block-style markers (already valid)
    if value in ("|", ">", "|-", ">-", "|+", ">+"):
        return False
    if value == "[]":
        return False
    # `: ` inside the value is the killer
    if ": " in value:
        return True
    # `#` anywhere makes YAML start a comment
    if "#" in value:
        return True
    # Leading flow-indicator chars
    if value[0] in "[]{},&*!|>%@`":
        return True
    return False


def quote_value(value: str) -> str:
    # Double-quote and escape embedded double-quotes + backslashes
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def convert(content: str) -> tuple[str, int]:
    lines = content.split("\n")
    out: list[str] = []
    in_fm = False
    fm_marker_count = 0
    changed = 0

    for line in lines:
        if line.strip() == "---":
            fm_marker_count += 1
            out.append(line)
            in_fm = (fm_marker_count == 1)
            continue
        if in_fm and ":" in line:
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]
            # Block-list child line starts with "- " — skip
            if stripped.startswith("- "):
                out.append(line)
                continue
            field, sep, rest = stripped.partition(":")
            # Plain identifier check — YAML keys are alphanum + underscore
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", field):
                out.append(line)
                continue
            if field in SKIP_FIELDS:
                out.append(line)
                continue
            value = rest.lstrip()
            if needs_quoting(value):
                quoted = quote_value(value)
                # Preserve indentation and exact whitespace after colon
                trailing_ws = rest[: len(rest) - len(rest.lstrip())]
                if not trailing_ws:
                    trailing_ws = " "
                out.append(f"{indent}{field}:{trailing_ws}{quoted}")
                changed += 1
                continue
        out.append(line)
    return "\n".join(out), changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="cards")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("paths", nargs="*")
    args = ap.parse_args()

    if args.paths:
        targets = [Path(p) for p in args.paths]
    else:
        targets = sorted(Path(args.root).rglob("*.md"))

    if args.limit:
        targets = targets[: args.limit]

    files_changed = 0
    fields_changed = 0
    for p in targets:
        try:
            content = p.read_text(encoding="utf-8")
        except Exception as e:
            print(f"SKIP {p}: {e}", file=sys.stderr)
            continue
        new, n = convert(content)
        if n > 0:
            files_changed += 1
            fields_changed += n
            if args.dry_run:
                print(f"WOULD QUOTE {p} ({n} fields)")
            else:
                p.write_text(new, encoding="utf-8")
                print(f"QUOTED {p} ({n} fields)")

    suffix = " (dry run)" if args.dry_run else ""
    print(f"\n{files_changed} files, {fields_changed} fields quoted{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
