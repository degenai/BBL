#!/usr/bin/env python3
"""Quantify the vision-enriched-but-no-trivia gap across corpus."""
import os, re, glob

vision_done_no_trivia = []
both = []
neither = []
for f in glob.glob('cards/**/*.md', recursive=True):
    norm = f.replace('\\', '/')
    if '/_' in norm:
        continue
    try:
        body = open(f, encoding='utf-8').read()
    except Exception:
        continue
    m = re.search(r'tags_hub:\s*\[([^\]]*)\]', body)
    if not m or not m.group(1).strip():
        neither.append(f)
        continue
    if '## Trivia' in body:
        both.append(f)
    else:
        vision_done_no_trivia.append(f)

print(f'Vision-only (no trivia): {len(vision_done_no_trivia)}')
print(f'Vision + Trivia: {len(both)}')
print(f'Vision-not-done: {len(neither)}')
print()
# Group vision-only by set
from collections import Counter
sets = Counter()
for f in vision_done_no_trivia:
    parts = f.replace('\\', '/').split('/')
    # cards/<game>/<set>/<card.md>
    if len(parts) >= 3:
        sets[f'{parts[1]}/{parts[2]}'] += 1
print('Top 20 sets by vision-only-card count:')
for s, c in sets.most_common(20):
    print(f'  {c:4d}  {s}')
