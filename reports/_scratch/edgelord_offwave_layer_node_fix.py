"""Off-wave Edgelord fix script — applies the mechanical fixes the sweep surfaced.

Fixes applied:
  1. Bug-1 cleanup: convert `field: "[a, b]"` (inline-quoted-string YAML list)
     to block-form YAML list, on layer-node files only. Field whitelist below.
  2. Bug-3b/4a cleanup: dan-murayama-scott.md frontmatter corruption — the
     line `<key>: <value><newline-eating>related_hubs: []` becomes two
     separate frontmatter lines.
  3. Bug-4a cleanup: son-goku forward-pointer gaps — both son-goku cards get
     a `characters:\n  - son-goku` block added to their frontmatter (placed
     after the existing `tags:` block, before the closing `---`).

Bigger findings (real missing-node wikilinks, cross-vault bbl-* memory links)
are NOT touched here — those need separate Nodeley waves or a memory-vault
policy decision. Listed in this script's docstring for reference.

Run from project root:  python reports/_scratch/edgelord_offwave_layer_node_fix.py
"""
import os, re, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CARDS_DIR = os.path.join(ROOT, 'cards')

LAYER_DIRS = [
    os.path.join(CARDS_DIR, '_characters'),
    os.path.join(CARDS_DIR, '_symbols'),
    os.path.join(CARDS_DIR, '_hubs'),
    os.path.join(CARDS_DIR, '_artists'),
]

# Fields where the bug-1 pattern was observed; restrict the rewrite to these
# to avoid touching any unintentional adjacent matches.
BUG1_FIELDS = [
    'aliases', 'appears_on', 'related_hubs', 'related_symbols',
    'related_characters', 'related_artists', 'tag_signals', 'tags',
    'member_cards', 'canonical_examples',
]

def read(p):
    with open(p, 'r', encoding='utf-8') as fh:
        return fh.read()

def write(p, c):
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(c)

# ---- fix 1: inline-quoted-string YAML lists ----

def fix_bug1():
    n_files_touched = 0
    n_fields_fixed = 0
    for ld in LAYER_DIRS:
        for f in sorted(glob.glob(os.path.join(ld, '*.md'))):
            content = read(f)
            new = content
            changed = False
            for field in BUG1_FIELDS:
                pat = re.compile(
                    rf'^({re.escape(field)}):\s*(["\'])(\[(.*?)\])\2\s*$',
                    re.M,
                )
                def repl(m):
                    body = m.group(4).strip()
                    if body == '':
                        return f'{m.group(1)}: []'
                    items = [x.strip().strip('"').strip("'")
                             for x in body.split(',') if x.strip()]
                    block = '\n'.join(f'  - {i}' for i in items)
                    return f'{m.group(1)}:\n{block}'
                new2, count = pat.subn(repl, new)
                if count > 0:
                    new = new2
                    changed = True
                    n_fields_fixed += count
            if changed:
                write(f, new)
                n_files_touched += 1
                print(f'  fixed bug-1 in {os.path.relpath(f, ROOT)}')
    print(f'  -> bug-1 totals: {n_files_touched} files, {n_fields_fixed} fields')
    return n_files_touched, n_fields_fixed

# ---- fix 2: dan-murayama-scott.md corruption ----

def fix_bug3b_dan_murayama_scott():
    f = os.path.join(CARDS_DIR, '_artists', 'dan-murayama-scott.md')
    content = read(f)
    new = content
    # Frontmatter corruption: appears_on entry has eaten a `related_hubs: []` field.
    bad_fm = '  - magic-the-gathering/throne-of-eldraine/134-raging-redcaprelated_hubs: []'
    good_fm = '  - magic-the-gathering/throne-of-eldraine/134-raging-redcap\nrelated_hubs: []'
    if bad_fm in new:
        new = new.replace(bad_fm, good_fm)
        print('  fixed dan-murayama-scott frontmatter corruption')
    # Body wikilink: same broken stem
    bad_link = '- [[134-raging-redcaprelated_hubs: []]]'
    good_link = '- [[134-raging-redcap]]'
    if bad_link in new:
        new = new.replace(bad_link, good_link)
        print('  fixed dan-murayama-scott body wikilink')
    if new != content:
        write(f, new)
        return True
    return False

# ---- fix 3: son-goku forward-pointer gaps ----

SON_GOKU_CARDS = [
    'dragon-ball-super/galactic-battle/bt1-060-son-goku.md',
    'dragon-ball-super/union-force/bt2-072-bundle-of-curiosity-son-goku.md',
]

def fix_bug4a_son_goku():
    n = 0
    for rel in SON_GOKU_CARDS:
        f = os.path.join(CARDS_DIR, rel)
        if not os.path.exists(f):
            print(f'  SKIP missing: {rel}')
            continue
        content = read(f)
        # If `characters:` already exists, don't touch
        if re.search(r'^characters:', content, re.M):
            print(f'  already has characters: field: {rel}')
            continue
        # Insert before the closing `---` of frontmatter
        m = re.match(r'^(---\n.*?\n)(---\n)', content, re.S)
        if not m:
            print(f'  no frontmatter detected: {rel}')
            continue
        fm_body, fm_close = m.group(1), m.group(2)
        insertion = 'characters:\n  - son-goku\n'
        new_content = fm_body + insertion + fm_close + content[m.end():]
        write(f, new_content)
        print(f'  added characters: [son-goku] to {rel}')
        n += 1
    print(f'  -> bug-4a son-goku: {n} cards patched')
    return n

def main():
    print('Off-wave Edgelord fix — three mechanical fixes:')
    print('  1. inline-quoted-string YAML list -> block form (layer nodes)')
    print('  2. dan-murayama-scott.md frontmatter corruption')
    print('  3. son-goku forward-pointer gaps (2 cards)')
    print()
    print('--- BUG 1 ---')
    fix_bug1()
    print()
    print('--- BUG 3b/4a (dan-murayama-scott) ---')
    fix_bug3b_dan_murayama_scott()
    print()
    print('--- BUG 4a (son-goku) ---')
    fix_bug4a_son_goku()

if __name__ == '__main__':
    main()
