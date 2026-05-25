"""Verify the corpus-wide sweep cleared all `field: \\"...` lines.
Run from repo root: python reports/_scratch/verify_yaml_quote_wrap.py
"""
import re, pathlib

# Match a frontmatter line where the value begins with a literal backslash-quote
# (the buggy JSON-escape-leak pattern). In Python raw string: r'\\"' is two
# chars: literal backslash, literal quote.
BAD_RE = re.compile(r'^[a-z_]+: +\\"')

hits = 0
for p in pathlib.Path('cards').rglob('*.md'):
    if '_images' in str(p):
        continue
    try:
        t = p.read_text(encoding='utf-8')
    except Exception:
        continue
    m = re.search(r'^---\n(.*?)\n---', t, re.S)
    if not m:
        continue
    fm = m.group(1)
    for ln in fm.splitlines():
        if BAD_RE.match(ln):
            hits += 1
            if hits <= 5:
                print(f'  {p} | {ln[:90]}')
            break

print(f'\nRemaining backslash-quote prefix lines: {hits}')
