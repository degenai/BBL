---
type: hub
name: Chinese Zodiac
aliases: [chinese-zodiac, zodiac, wuxing, shengxiao, lunar-zodiac, china-zodiac]
tag_signals: [rat, ox, tiger, rabbit, dragon, snake, horse, goat, sheep, ram, monkey, rooster, chicken, dog, pig, boar, wood-element, fire-element, earth-element, metal-element, water-element, lunar-new-year, agrarian]
anchored_lairs: []
brand_weight: foundational
linked_project: pokemon-zodiac
---

# Chinese Zodiac

A foundational [[Bulk Graph Bundler]] hub. The Wuxing × shengxiao (Chinese zodiac) grid as a curatorial framework. Foundationally tied to the [[diamondlegendz]] [[pokemon-zodiac]] project, which already encodes the **functional-agrarian China-max ruleset** — twelve zodiac slots × five Wuxing elements, sixty cells, ~25 honestly open. The grid is the rubric. BBL supplies cards.

> The zodiac framework reads bulk through a lens that's defensibly cultural-design-history rather than "themed boosters." It's curation-as-scholarship: each cell either fills cleanly or stays honestly open, and the gaps themselves are content.

## What This Hub Anchors

Card art depicting any of the twelve zodiac animals under the functional-agrarian criteria, plus the five Wuxing elements where they map onto TCG type-honest mechanics.

**Animal-slot criteria** (from [[pokemon-zodiac]], applies equally to MTG/other):
- 鼠 Rat: any rodent (rat, mouse, squirrel, beaver — agrarian pest)
- 牛 Ox: domestic cattle, working bovine
- 虎 Tiger: actual striped tigers only (lions orphaned, Buddhist-imported)
- 兔 Rabbit: domestic rabbit / hare
- 龍 Dragon: Chinese loong + carp-dragon only (Western heraldic dragons orphaned)
- 蛇 Snake: any serpent
- 馬 Horse: domestic horse, working equine
- 羊 Goat: goat/sheep/ram (horned ruminant)
- 猴 Monkey: simian
- 雞 Rooster: chicken specifically (no other birds)
- 狗 Dog: domestic dog only (wolves/foxes/jackals orphaned)
- 豬 Pig: domestic swine, boar

**Element criteria** (TCG-type-honest, MTG colors equivalent):
- 木 Wood: Forest / Green
- 火 Fire: Mountain / Red
- 土 Earth: Plains-as-mundane, Wastes, Ground/Rock
- 金 Metal: Artifact / Steel-type
- 水 Water: Island / Blue / Ice

## Tag-Cluster Signals

Any animal-slot tag from the list above + element-typing in `tags_filter`. The MD frontmatter `collector_number` and `set` give the printing context; `name` gives the lore framing; `tags_hub` gives the figurative content. Cross-reference all three.

## Narrative Seeds (lair titles, not yet built)

- **"China-max Zodiac Set"** — bulk Pokémon commons filling all ~35 closed cells in one bundle. Ships with the pokemon-zodiac poster as the persuasion device. The narrative is the framework itself, already written.
- **"Wood Element"** (or any single element row) — a 12-cell single-row set at a lower price point. Repeat for Fire/Earth/Metal/Water.
- **"Swords of Justice"** — Cobalion + Terrakion + Virizion + Keldeo as a four-cell mini-bundle (the surviving Goat-row trio across two element rows). Tiny, sharp, complete.
- **"What doesn't fit"** — an orphan-as-thesis lair: the Charizard line + Tyranitar + Galar wolves + Lucario, framed as *the dex going Western, Japanese, fantastical*. The orphan-category footnotes from pokemon-zodiac become the bundle's interpretive copy.
- **"MTG Zodiac"** — same framework applied to MTG cards. Already in inventory: snake-row dense (Toxin Sliver, Moss Viper, Kraul Stinger), rat-row real, dragon-row tight under loong-only criterion, goat-row anchored by Karametra's Blessing + minotaurs. The grid auto-builds from existing tags.

## Why This Hub Earns Foundational Status

It's the only hub that comes with a *pre-built rubric*. [[labor]] and [[rebellion]] are conceptual lenses Alex writes lairs through. Chinese Zodiac is also that, but additionally it's a 60-cell grid with hard rules already published at diamondlegendz. That makes it the cleanest first BBL-native bundle application — narrative pre-written, sourcing well-defined, even the poster artwork exists. The other two hubs require Alex to author each narrative from scratch.

## Anti-Patterns

This hub is NOT:
- "Zodiac-adjacent" cards. The ruleset is type-honest. Western dragons are orphaned. Lions are orphaned. Foxes are orphaned. No mushy inclusion to make the grid look full.
- Vietnamese / other regional zodiac variants. The [[pokemon-zodiac]] project is China-max for cultural-and-commercial alignment (AAPI diaspora collectors are predominantly Chinese tradition, TPC drops Year-of-Dragon Charizard never Year-of-Cat). BBL follows the same line.
- A purely aesthetic "animals" hub. The zodiac framework is mythological / agrarian / cosmological. A bundle of cute cats doesn't fit; a bundle of agrarian-rat-pest cards does.

## Design Note

This hub is **deliberately card-edge disconnected** in Obsidian's graph view. The node itself is visible — it sits in the layer-node clique linked to other layer nodes via body wikilinks — but **no edges connect this hub to any individual card** by design, even when a card depicts one of the twelve zodiac animals directly (the wire flows via character / symbol nodes, not via hub-name-matching).

The `tag_signals` listed above are an *informational* indirection — cards with overlapping `tags_hub` are *candidates* for Chinese Zodiac lair assembly under the functional-agrarian criteria, not auto-anchored members. There is no `appears_on:` or `anchored_cards:` field on this node, and there won't be.

Why: rendering all tag-signal-matched cards as graph edges would balloon Chinese Zodiac to ~115 anchors (mostly drift — "dragon" alone matches 39 MTG cards, most of which are Western heraldic dragons explicitly *orphaned* under the China-max ruleset). The auto-render would directly contradict the rubric's orphan-honest scholarship. And more fundamentally — *cards are inventory, bundles are destructive*. When a Discrete Lair assembles, those cards leave the corpus on sale; any field pinning specific cards as canonical hub-anchors would be wrong the moment they ship. See `bbl-bundles-are-destructive-on-graph.md` (wave 81 P3 decision, 2026-05-14).

The triple-thesis ([[_triple-thesis]]) is the root crystal; hubs stand on their own as narrative thesis-anchors; bundle-by-bundle assembly does the rest. `anchored_lairs:` is the right tier of relationship — bundle-level, not card-level — and survives the inventory churn.

## See Also

- [[pokemon-zodiac]] — the scholarly project this hub leans on; the rubric, ruleset, poster, and orphan footnotes already exist there
- [[labor]] — sibling hub; the zodiac is a peasant cosmology, all animal slots are agrarian-functional
- [[rebellion]] — sibling hub; the orphan-honest framing is a rebellion against type-mushy "everything qualifies" curation
- [[diamondlegendz]] — host site for the pokemon-zodiac project
- repo `docs/sketchbook.md` — narrative-first lair architect sketch
