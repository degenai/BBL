"""Off-wave Edgelord audit — layer-node directory sweep for broken-edge bugs.

Bug classes checked:
  1. Inline-quoted-string YAML lists (e.g. `related_hubs: "[rebellion]"`) on
     any list-typed frontmatter field of a layer node.
  2. Pre-convention path-key formats on `appears_on:` (set-prefixed
     `<set>/<num>-<stem>` instead of canonical `<game>/<set>/<num>-<stem>`).
  3. Broken wikilinks (`[[target]]` where `target.md` doesn't exist anywhere
     under cards/).
  4. Orphan reverse-pointers:
       - node.appears_on lists a card that no longer points back
         (forward gap from card->node).
       - card frontmatter references a node-slug that doesn't exist in the
         corresponding layer directory.

Output: prints a per-bug-class report. No file edits performed by this script —
caller (Edgelord) decides ship-vs-document based on scope.
"""
import os, re, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CARDS_DIR = os.path.join(ROOT, 'cards')

LAYER_DIRS = {
    'characters': os.path.join(CARDS_DIR, '_characters'),
    'symbols':    os.path.join(CARDS_DIR, '_symbols'),
    'hubs':       os.path.join(CARDS_DIR, '_hubs'),
    'artists':    os.path.join(CARDS_DIR, '_artists'),
}

# Card-side frontmatter field names by layer (used for forward/reverse pointer check).
CARD_SIDE_FIELD = {
    'characters': 'characters',
    'symbols':    'symbols',
    'hubs':       None,           # hubs are implicit via tags_hub; no per-card pointer field
    'artists':    'artist',       # scalar
}

# Common list-typed fields seen on layer nodes (bug class 1 inline-quoted-list scan).
LIST_FIELDS = [
    'aliases', 'appears_on', 'related_hubs', 'related_symbols',
    'related_characters', 'related_artists', 'tag_signals', 'tags',
    'member_cards', 'canonical_examples',
]

# ----- helpers -----

def read(path):
    with open(path, 'r', encoding='utf-8') as fh:
        return fh.read()

def split_frontmatter(content):
    if not content.startswith('---'):
        return '', content
    m = re.match(r'^---\n(.*?)\n---\n', content, re.S)
    if not m:
        return '', content
    return m.group(1), content[m.end():]

def field_block_lines(frontmatter, field):
    """Return list items if field is in block form, else None."""
    pat = re.compile(rf'^{re.escape(field)}:\s*\n((?:[ \t]+-[ \t]+.*\n)+)', re.M)
    m = pat.search(frontmatter + '\n')
    if not m:
        return None
    return [ln.strip().lstrip('- ').strip() for ln in m.group(1).split('\n') if ln.strip()]

def field_inline_string(frontmatter, field):
    """Detect bug-1 form: `field: "[a, b]"` or `field: '[a]'` (quoted string instead of YAML list)."""
    pat = re.compile(rf'^{re.escape(field)}:\s*(["\'])(\[.*?\])\1\s*$', re.M)
    m = pat.search(frontmatter)
    if m:
        return m.group(2)
    return None

def field_inline_list(frontmatter, field):
    """Detect inline YAML list: `field: [a, b]` (legal YAML but Alex prefers block form per wave 92)."""
    pat = re.compile(rf'^{re.escape(field)}:\s*\[(.*?)\]\s*$', re.M)
    m = pat.search(frontmatter)
    if m:
        body = m.group(1).strip()
        if body == '':
            return None  # empty arrays `field: []` are explicitly OK per Edgelord spec
        return [x.strip().strip('"').strip("'") for x in body.split(',') if x.strip()]
    return None

def field_scalar(frontmatter, field):
    pat = re.compile(rf'^{re.escape(field)}:\s*(.+?)\s*$', re.M)
    m = pat.search(frontmatter)
    if not m:
        return None
    v = m.group(1).strip()
    if v.startswith(('-', '[', '{', '|', '>')):
        return None
    return v.strip('"').strip("'")

# ----- bug 1: inline-quoted-string YAML lists -----

def scan_bug1_inline_quoted_lists():
    print('\n========================================')
    print('BUG CLASS 1: inline-quoted-string YAML lists')
    print('  (field: "[foo, bar]" instead of block form)')
    print('========================================')
    hits = []
    for layer, ld in LAYER_DIRS.items():
        for f in sorted(glob.glob(os.path.join(ld, '*.md'))):
            fm, _ = split_frontmatter(read(f))
            for field in LIST_FIELDS:
                v = field_inline_string(fm, field)
                if v is not None:
                    hits.append((layer, os.path.basename(f), field, v))
    if not hits:
        print('  (clean — no inline-quoted-list bugs found)')
    for layer, fname, field, v in hits:
        print(f'  {layer}/{fname}  field={field}  value={v}')
    return hits

# ----- bug 1b (related): inline YAML lists (legal but discouraged per wave 92) -----

def scan_bug1b_inline_yaml_lists():
    print('\n========================================')
    print('BUG CLASS 1b: inline YAML lists (legal but wave-92 prefers block form)')
    print('  (field: [foo, bar] instead of block form; empty [] is fine)')
    print('========================================')
    hits = []
    for layer, ld in LAYER_DIRS.items():
        for f in sorted(glob.glob(os.path.join(ld, '*.md'))):
            fm, _ = split_frontmatter(read(f))
            for field in LIST_FIELDS:
                v = field_inline_list(fm, field)
                if v is not None:
                    hits.append((layer, os.path.basename(f), field, v))
    if not hits:
        print('  (clean — no inline-list-with-content bugs found)')
    for layer, fname, field, v in hits:
        print(f'  {layer}/{fname}  field={field}  value={v}')
    return hits

# ----- bug 2: pre-convention appears_on path-keys -----

def scan_bug2_path_keys():
    print('\n========================================')
    print('BUG CLASS 2: pre-convention path-key format on appears_on')
    print('  (expects <game>/<set>/<num>-<stem>; flag if <set>/<num>-<stem>)')
    print('========================================')
    # Build canonical game-set lookup from cards/ dir tree
    known_games = set()
    for entry in os.listdir(CARDS_DIR):
        if entry.startswith('_'):
            continue
        if os.path.isdir(os.path.join(CARDS_DIR, entry)):
            known_games.add(entry)

    hits = []
    for layer, ld in LAYER_DIRS.items():
        for f in sorted(glob.glob(os.path.join(ld, '*.md'))):
            fm, _ = split_frontmatter(read(f))
            items = field_block_lines(fm, 'appears_on') or []
            for it in items:
                parts = it.split('/')
                # Canonical: <game>/<set>/<num>-<stem> => >= 3 parts AND first part is a known game
                if len(parts) < 3 or parts[0] not in known_games:
                    hits.append((layer, os.path.basename(f), it))
    if not hits:
        print('  (clean — all appears_on entries use canonical <game>/<set>/<num>-<stem> form)')
    for layer, fname, it in hits:
        print(f'  {layer}/{fname}  appears_on entry: {it!r}')
    return hits

# ----- bug 3: broken wikilinks in layer-node bodies -----

def scan_bug3_broken_wikilinks():
    print('\n========================================')
    print('BUG CLASS 3: broken wikilink targets in layer-node bodies')
    print('  ([[foo]] where no foo.md exists anywhere under cards/)')
    print('========================================')
    # Build set of all stems anywhere under cards/
    all_stems = set()
    for f in glob.glob(os.path.join(CARDS_DIR, '**', '*.md'), recursive=True):
        all_stems.add(os.path.basename(f).replace('.md', ''))

    hits = []
    wiki_re = re.compile(r'\[\[([^\]\|#]+)(?:\|[^\]]+)?\]\]')
    for layer, ld in LAYER_DIRS.items():
        for f in sorted(glob.glob(os.path.join(ld, '*.md'))):
            content = read(f)
            for m in wiki_re.finditer(content):
                target = m.group(1).strip()
                # Allow project-name pseudo-link
                if target in ('Bulk Graph Bundler',):
                    continue
                if target not in all_stems:
                    hits.append((layer, os.path.basename(f), target))
    if not hits:
        print('  (clean — all wikilinks resolve)')
    for layer, fname, target in hits:
        print(f'  {layer}/{fname}  broken link: [[{target}]]')
    return hits

# ----- bug 4: orphan reverse-pointers -----

def scan_bug4_orphan_pointers():
    print('\n========================================')
    print('BUG CLASS 4: orphan reverse-pointers')
    print('  (a) node.appears_on lists card with no frontmatter pointer back')
    print('  (b) card frontmatter references slug missing from layer dir')
    print('========================================')
    forward_gaps = []  # (layer, node_slug, card_relpath, why)
    missing_node_refs = []  # (layer, card_relpath, ref_slug)

    # Per-layer node sets
    for layer, ld in LAYER_DIRS.items():
        field = CARD_SIDE_FIELD[layer]
        if field is None:
            continue  # hubs: no per-card pointer field

        node_slugs = {os.path.basename(f).replace('.md', '')
                      for f in glob.glob(os.path.join(ld, '*.md'))}

        # (a) for each node, walk appears_on and verify the card points back
        for nf in sorted(glob.glob(os.path.join(ld, '*.md'))):
            nslug = os.path.basename(nf).replace('.md', '')
            fm, _ = split_frontmatter(read(nf))
            for rel in (field_block_lines(fm, 'appears_on') or []):
                card_path = os.path.join(CARDS_DIR, rel + '.md')
                if not os.path.exists(card_path):
                    forward_gaps.append((layer, nslug, rel, 'CARD-FILE-MISSING'))
                    continue
                cfm, _ = split_frontmatter(read(card_path))
                if field == 'artist':
                    val = field_scalar(cfm, 'artist')
                    # Artist node match is alias-based, not slug-equality, so skip the
                    # strict-equality check here and flag only file-missing cases.
                    # (artist_resolve.py handles alias resolution.)
                    continue
                else:
                    items = field_block_lines(cfm, field) or field_inline_list(cfm, field) or []
                    if nslug not in items:
                        forward_gaps.append((layer, nslug, rel, 'CARD-FRONTMATTER-MISSING-POINTER'))

        # (b) for each card with vision-passed, walk its layer field and verify node exists
        if field == 'artist':
            continue  # alias-based; skip
        all_cards = glob.glob(os.path.join(CARDS_DIR, '**', '*.md'), recursive=True)
        for cf in all_cards:
            norm = cf.replace('\\', '/')
            if any(seg in norm for seg in ('/_characters/', '/_hubs/', '/_symbols/', '/_artists/')):
                continue
            content = read(cf)
            if 'vision-passed' not in content:
                continue
            cfm, _ = split_frontmatter(content)
            items = field_block_lines(cfm, field) or field_inline_list(cfm, field) or []
            rel = norm.split('/cards/')[1].replace('.md', '') if '/cards/' in norm else cf
            for it in items:
                if it not in node_slugs:
                    missing_node_refs.append((layer, rel, it))

    if not forward_gaps and not missing_node_refs:
        print('  (clean — no orphan pointers detected)')
    for layer, n, rel, why in forward_gaps:
        print(f'  [FORWARD] layer={layer}  node={n}  card={rel}  ({why})')
    for layer, rel, ref in missing_node_refs:
        print(f'  [MISSING-NODE] layer={layer}  card={rel}  ref-slug={ref!r}')
    return forward_gaps, missing_node_refs

def main():
    print('=' * 60)
    print('Off-wave Edgelord audit — layer-node directory sweep')
    print('=' * 60)
    b1 = scan_bug1_inline_quoted_lists()
    b1b = scan_bug1b_inline_yaml_lists()
    b2 = scan_bug2_path_keys()
    b3 = scan_bug3_broken_wikilinks()
    b4a, b4b = scan_bug4_orphan_pointers()

    print('\n' + '=' * 60)
    print('SUMMARY')
    print('=' * 60)
    print(f'  Bug 1  (inline-quoted-string lists):        {len(b1)} hits')
    print(f'  Bug 1b (inline YAML lists with content):    {len(b1b)} hits')
    print(f'  Bug 2  (pre-convention appears_on keys):    {len(b2)} hits')
    print(f'  Bug 3  (broken wikilinks in node bodies):   {len(b3)} hits')
    print(f'  Bug 4a (forward-pointer gaps):              {len(b4a)} hits')
    print(f'  Bug 4b (missing-node refs from cards):      {len(b4b)} hits')

if __name__ == '__main__':
    main()
