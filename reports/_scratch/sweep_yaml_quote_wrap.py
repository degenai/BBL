"""Sweep cards/ for frontmatter values that were JSON-escaped (start with \")
but never wrapped in outer YAML double-quotes. Wraps them.

Root cause: researchbot._flatten_for_frontmatter() escapes value content to
JSON-style (\", \n, \\) but update_frontmatter_field() writes it without an
outer quote wrap, so the resulting YAML line `flavor_text: \"X\"` is invalid.

Fix: wrap each affected line's value in outer double quotes. YAML then sees
the inner \" and \n as proper escape sequences within a quoted scalar.

Run from repo root:
    python reports/_scratch/sweep_yaml_quote_wrap.py            # dry-run
    python reports/_scratch/sweep_yaml_quote_wrap.py --apply    # write
"""
from __future__ import annotations
import argparse, re, pathlib, sys


def fix_text(text: str) -> tuple[str, int]:
    """Return (new_text, fields_fixed_count)."""
    fmm = re.search(r'^---\n(.*?)\n---', text, re.S)
    if not fmm:
        return text, 0
    fm = fmm.group(1)
    new_lines = []
    fixed = 0
    for ln in fm.splitlines():
        # Match `key: \"..."  any content`. The value starts with literal `\"`
        # (backslash-doublequote) — JSON-escape leak that never got the outer
        # YAML quote.
        m = re.match(r'^([a-z_][a-z0-9_]*): +(\\".*)$', ln)
        if m:
            key, val = m.group(1), m.group(2)
            # Wrap the existing escape-laden value in outer double quotes.
            # YAML will then parse \", \n, \\ as escape sequences within
            # the double-quoted scalar and produce the intended string.
            new_lines.append(f'{key}: "{val}"')
            fixed += 1
        else:
            new_lines.append(ln)
    if fixed == 0:
        return text, 0
    new_fm = '\n'.join(new_lines)
    # Splice the fixed frontmatter back into the document.
    new_text = text[:fmm.start(1)] + new_fm + text[fmm.end(1):]
    return new_text, fixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='write changes; default is dry-run')
    args = ap.parse_args()

    total_files = 0
    total_fields = 0
    for p in pathlib.Path('cards').rglob('*.md'):
        if '_images' in str(p):
            continue
        try:
            t = p.read_text(encoding='utf-8')
        except Exception:
            continue
        new_t, fixed = fix_text(t)
        if fixed == 0:
            continue
        total_files += 1
        total_fields += fixed
        if args.apply:
            p.write_text(new_t, encoding='utf-8')

    mode = 'APPLIED' if args.apply else 'DRY-RUN'
    print(f'{mode}: {total_fields} fields across {total_files} cards', file=sys.stderr)


if __name__ == '__main__':
    main()
