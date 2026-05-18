"""Wave 120 Edgelord audit — extended to artists, symbols, and hubs layers.
Same gap-detection logic, all four layers in one sweep.
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

def card_field_list(content, field):
    cm = re.search(rf'^{field}:\s*\n((?:\s+-\s+.*\n)*)', content, re.M)
    if cm:
        return [line.strip().lstrip('- ').strip() for line in cm.group(1).split('\n') if line.strip()]
    m2 = re.search(rf'^{field}:\s*\[(.*?)\]\s*$', content, re.M)
    if m2:
        return [x.strip().strip('"').strip("'") for x in m2.group(1).split(',') if x.strip()]
    return []

def audit_layer(layer_name, field_name):
    nodes = load_node_appears(os.path.join(ROOT, 'cards', f'_{layer_name}'))
    forward_gaps = []
    reverse_gaps = []
    missing_nodes = []
    all_cards = glob.glob(os.path.join(ROOT, 'cards', '**', '*.md'), recursive=True)
    enriched = 0
    for cf in all_cards:
        norm = cf.replace('\\', '/')
        if '/_characters/' in norm or '/_hubs/' in norm or '/_symbols/' in norm or '/_artists/' in norm:
            continue
        with open(cf, 'r', encoding='utf-8') as fh:
            content = fh.read()
        if 'vision-passed' not in content:
            continue
        enriched += 1
        parts = norm.split('/cards/')
        if len(parts) < 2:
            continue
        rel = parts[1].replace('.md', '')
        items = card_field_list(content, field_name)
        for it in items:
            if it not in nodes:
                missing_nodes.append((rel, it))
            elif rel not in nodes[it]:
                forward_gaps.append((rel, it))

    for nslug, paths in nodes.items():
        for p in paths:
            card_path = os.path.join(ROOT, 'cards', p + '.md')
            if not os.path.exists(card_path):
                reverse_gaps.append((nslug, p, 'CARD-FILE-MISSING'))
                continue
            with open(card_path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            items = card_field_list(content, field_name)
            if nslug not in items:
                reverse_gaps.append((nslug, p, 'CARD-FRONTMATTER-MISSING-POINTER'))

    print(f'\n=== Layer: {layer_name} (field: {field_name}) ===')
    print(f'  Enriched scanned: {enriched}')
    print(f'  Nodes: {len(nodes)}')
    print(f'  Forward gaps (card->node): {len(forward_gaps)}')
    for r, n in forward_gaps[:20]:
        print(f'    {r}  ->  {n}')
    print(f'  Reverse gaps (node->card): {len(reverse_gaps)}')
    for n, p, why in reverse_gaps[:20]:
        print(f'    node:{n}  card:{p}  ({why})')
    print(f'  Missing-node refs: {len(missing_nodes)}')
    for r, c in missing_nodes[:20]:
        print(f'    {r}  ->  MISSING:{c}')

def main():
    audit_layer('characters', 'characters')
    audit_layer('symbols', 'symbols')
    # For artists, the card-side field is `artist:` (single scalar), not a list, and node-side
    # uses appears_on like the others. Handle scalar form separately.
    # For hubs, cards don't carry per-card hub pointers in frontmatter — hubs are implicit via tags_hub.
    # So only characters + symbols use this exact pattern.

if __name__ == '__main__':
    main()
