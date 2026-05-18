"""Wave 120 Edgelord audit — find sync drift between card-side `characters:` frontmatter
and node-side `appears_on:` pointers. Looks for two patterns:

1. CARD->NODE-UNWIRED: card frontmatter points to node X, but node X's appears_on doesn't list this card
2. NODE->CARD-UNWIRED: node X's appears_on lists card, but card frontmatter `characters:` is empty or missing X

Helps Edgelord surface the genuinely unwired-or-half-wired anchors that one-pass-fix attaches resolve.
"""
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_node_appears(node_dir):
    nodes = {}
    for f in glob.glob(os.path.join(node_dir, '*.md')):
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()
        slug = os.path.basename(f).replace('.md', '')
        m = re.search(r'^appears_on:\s*\n((?:\s+-\s+.*\n)*)', content, re.M)
        if m:
            appears = [line.strip().lstrip('- ').strip() for line in m.group(1).split('\n') if line.strip()]
        else:
            appears = []
        nodes[slug] = set(appears)
    return nodes

def card_chars(content):
    cm = re.search(r'^characters:\s*\n((?:\s+-\s+.*\n)*)', content, re.M)
    if not cm:
        # also support inline form
        m2 = re.search(r'^characters:\s*\[(.*?)\]\s*$', content, re.M)
        if m2:
            return [x.strip().strip('"').strip("'") for x in m2.group(1).split(',') if x.strip()]
        return []
    return [line.strip().lstrip('- ').strip() for line in cm.group(1).split('\n') if line.strip()]

def main():
    nodes = load_node_appears(os.path.join(ROOT, 'cards', '_characters'))
    forward_gaps = []   # card -> node-missing
    reverse_gaps = []   # node -> card-missing
    missing_nodes = []  # card points to non-existent node

    all_cards = glob.glob(os.path.join(ROOT, 'cards', '**', '*.md'), recursive=True)
    enriched = []
    for cf in all_cards:
        # Skip layer nodes
        norm = cf.replace('\\', '/')
        if '/_characters/' in norm or '/_hubs/' in norm or '/_symbols/' in norm or '/_artists/' in norm:
            continue
        with open(cf, 'r', encoding='utf-8') as fh:
            content = fh.read()
        if 'vision-passed' not in content:
            continue
        enriched.append(cf)
        # Path-key form: game/set/cardstem (no leading 'cards/', no '.md')
        parts = norm.split('/cards/')
        if len(parts) < 2:
            continue
        rel = parts[1].replace('.md', '')
        chars = card_chars(content)
        for c in chars:
            if c not in nodes:
                missing_nodes.append((rel, c))
            elif rel not in nodes[c]:
                forward_gaps.append((rel, c))

    # Reverse: each node's appears_on entries should have card-side characters: containing the node
    for nslug, paths in nodes.items():
        for p in paths:
            card_path = os.path.join(ROOT, 'cards', p + '.md')
            if not os.path.exists(card_path):
                reverse_gaps.append((nslug, p, 'CARD-FILE-MISSING'))
                continue
            with open(card_path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            chars = card_chars(content)
            if nslug not in chars:
                reverse_gaps.append((nslug, p, 'CHARACTERS-FRONTMATTER-MISSING-POINTER'))

    print(f'=== Enriched cards scanned: {len(enriched)} ===')
    print(f'=== Forward (card->node) gaps: {len(forward_gaps)} ===')
    for r, n in forward_gaps[:40]:
        print(f'  {r}  ->  {n}')
    print(f'=== Reverse (node->card) gaps: {len(reverse_gaps)} ===')
    for n, p, why in reverse_gaps[:40]:
        print(f'  node:{n}  card:{p}  ({why})')
    print(f'=== Missing-node references: {len(missing_nodes)} ===')
    for r, c in missing_nodes[:40]:
        print(f'  {r}  ->  MISSING:{c}')

if __name__ == '__main__':
    main()
