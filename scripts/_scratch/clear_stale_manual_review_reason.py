"""
CBG-006a fix: clear stale `manual_review_reason:` on cards where `needs_manual_review: false`.

researchbot.py re-prep flips `needs_manual_review` true→false when image source is found on
retry but doesn't clear the `manual_review_reason` field. The stale reason leaks into
Obsidian's property panel + downstream consumers.

Affected at audit time: 259 cards (152 MTG + 107 Pokemon). Run from repo root.

Source-side prevention (TODO): amend researchbot.py prep path — on successful image find,
call `update_frontmatter_field(card_path, 'manual_review_reason', '')`.
"""
import os, re

ROOT = 'cards'
PATTERN_FALSE = re.compile(r'^needs_manual_review: false\s*$', re.M)
PATTERN_REASON = re.compile(r'^manual_review_reason: \S.*$', re.M)

fixed = 0
for root, dirs, files in os.walk(ROOT):
    if '_images' in root or '_views' in root:
        continue
    for fn in files:
        if not fn.endswith('.md'):
            continue
        p = os.path.join(root, fn)
        with open(p, encoding='utf-8') as f:
            t = f.read()
        if not PATTERN_FALSE.search(t):
            continue
        if not PATTERN_REASON.search(t):
            continue
        new_t = PATTERN_REASON.sub('manual_review_reason:', t, count=1)
        if new_t != t:
            with open(p, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_t)
            fixed += 1
print(f'Cleared stale manual_review_reason on {fixed} cards.')
