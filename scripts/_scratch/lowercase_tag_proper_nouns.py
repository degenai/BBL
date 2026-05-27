"""
CBG-006b fix: lowercase proper-noun tag entries in tags_hub / tags_filter.

Vision agents on a subset of cards emitted capitalized proper-noun tags (Eldrazi, Zendikar,
Ravnica, Emeria, Kamigawa, Ixalan). The rest of the corpus uses lowercase, fragmenting
Obsidian's tag-aggregation + breaking bbl_queue.py / hub-frequency analysis.

Affected at audit time: 21 instances on 20 unique cards (44-retreat-to-emeria carries both
Zendikar AND Emeria). 14 in BFZ; 6 elsewhere (DGM-2 / CHK-1 / EMN-1 / LCI-1 / WAR-1).

Source-side prevention (TODO): amend apply_vision.py vision-emission step to lowercase
proper-noun tags at the apply step.
"""
import os

ROOT = 'cards'
DRIFT_TAGS = {
    'Eldrazi': 'eldrazi',
    'Zendikar': 'zendikar',
    'Ravnica': 'ravnica',
    'Emeria': 'emeria',
    'Kamigawa': 'kamigawa',
    'Ixalan': 'ixalan',
}

fixed = 0
for root, dirs, files in os.walk(ROOT):
    if '_images' in root or '_views' in root:
        continue
    for fn in files:
        if not fn.endswith('.md'):
            continue
        p = os.path.join(root, fn)
        with open(p, encoding='utf-8') as f:
            lines = f.readlines()
        out = []
        in_tags = False
        changed = False
        for ln in lines:
            if ln.startswith('tags_hub:') or ln.startswith('tags_filter:'):
                in_tags = True
                out.append(ln)
                continue
            if in_tags:
                if ln.startswith('  - '):
                    tag = ln[4:].rstrip()
                    if tag in DRIFT_TAGS:
                        new_ln = '  - ' + DRIFT_TAGS[tag] + '\n'
                        out.append(new_ln)
                        changed = True
                        continue
                    out.append(ln)
                    continue
                if not ln.startswith('  ') and ln.strip():
                    in_tags = False
            out.append(ln)
        if changed:
            with open(p, 'w', encoding='utf-8', newline='\n') as f:
                f.writelines(out)
            fixed += 1
print(f'Lowercased proper-noun tags on {fixed} cards.')
