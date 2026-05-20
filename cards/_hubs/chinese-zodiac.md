---
type: hub
name: Chinese Zodiac
aliases:
  - chinese-zodiac
  - zodiac
  - wuxing
  - shengxiao
  - lunar-zodiac
  - china-zodiac
tag_signals:
  - rat
  - ox
  - tiger
  - rabbit
  - dragon
  - snake
  - horse
  - goat
  - sheep
  - ram
  - monkey
  - rooster
  - chicken
  - dog
  - pig
  - boar
  - wood-element
  - fire-element
  - earth-element
  - metal-element
  - water-element
  - lunar-new-year
  - agrarian
anchored_lairs: []
brand_weight: foundational
linked_project: pokemon-zodiac
canonical_source: "diamondlegendz pokemon-zodiac project (Alex + Andy) — https://diamondlegendz.com/pokemon-zodiac/ ; local repo Diamondlegendz/pokemon-zodiac/app.js encodes the functional-agrarian China-max ruleset R1-R9 and the full DATA grid (12 zodiac slots x 6 columns: 5 Wuxing elements + Aura = 72 cells)"
tags:
  - layer
  - hub
---
# Chinese Zodiac

A foundational `Bulk Graph Bundler` hub. The Wuxing × shengxiao (Chinese zodiac) grid as a curatorial framework. Foundationally tied to the [[diamondlegendz]] [[pokemon-zodiac]] project, which already encodes the **functional-agrarian China-max ruleset** — twelve zodiac slots × six columns (five Wuxing elements + an Aura column), seventy-two cells, ~27 honestly open. The grid is the rubric. BBL supplies cards.

> The zodiac framework reads bulk through a lens that's defensibly cultural-design-history rather than "themed boosters." It's curation-as-scholarship: each cell either fills cleanly or stays honestly open, and the gaps themselves are content.

## Canonical Ruleset Reference (2026-05-19)

The authoritative ruleset and grid data now live in `Diamondlegendz/pokemon-zodiac/app.js` (see `canonical_source` in frontmatter). That file encodes **nine rules across three tiers** — R1-R4 Chinese-tradition translation, R5-R8 project rubrics, and **R9 the market-acceptance test**: when The Pokemon Company ships a Pokemon under official zodiac/Wuxing framing (Year-of-X TCG product, Pokemon Center merchandise, Lunar New Year events) and the AAPI community does not object, the placement is ratified. R9 overrides the Tier 3 fauna exclusions but never the R5 element rules — Wuxing element constraints are structural, not cultural.

R9 post-dates the strict-orphan descriptions in the Animal-slot criteria below. Under R9 the **Dragon** row restores Western heraldic dragons and kaiju (TPC shipped Charizard EX for Year of the Dragon 2024 Taiwan/HK) and the **Dog** row restores wolves / foxes / hellhounds (TPC Year of the Dog 2018 precedent). The grid is also 6 columns wide, not 5 — the sixth **Aura** column holds element-orphaned Pokemon (pure Electric / Dark / Ghost / Psychic) that carry a TPC-ratified zodiac identity (Pikachu Rat, Mareep Goat, Mightyena Dog, Spoink Pig). Reconciling the strict-orphan prose below against the live R9 ruleset is a pending Edgelord task.

## What This Hub Anchors

Card art depicting any of the twelve zodiac animals under the functional-agrarian criteria, plus the five Wuxing elements where they map onto TCG type-honest mechanics, plus the sixth Aura column for element-orphaned but TPC-zodiac-ratified figures.

**Animal-slot criteria** (from [[pokemon-zodiac]], applies equally to MTG/other; R9 restorations folded in):
- 鼠 Rat (BROAD): any rodent — rat, mouse, squirrel, hamster, beaver, agrarian pest. R9 extends to market-readable borderline silhouettes (pangolin/armadillo) when TPC bundles them under Year-of-Rat framing.
- 牛 Ox (BROAD): all bovines — cattle, water buffalo, yak, wild ox. R9 admits American bison (野牛 in modern Mandarin) when TPC ships it as a Year-of-Ox pick.
- 虎 Tiger (STRICT): actual tigers only. Lions stay orphaned — and R9 agrees, TPC declined to ship lions for Year of the Tiger 2022. Both strict rule and market test concur; row stays fully open.
- 兔 Rabbit (BROAD): lagomorphs — rabbits and hares. Long ears beat digger silhouette.
- 龍 Dragon: Chinese loong + carp-dragon is the strict reading, but R9 **restores** Western heraldic dragons and kaiju — TPC shipped Charizard EX as the Year of the Dragon 2024 Taiwan/HK flagship. The cultural-design observation that the dex over-indexes Western dragons is preserved as scholarship, not used to orphan cells.
- 蛇 Snake (STRICT): legless reptiles. Eels are 鳗 (fish, not snake). R9 admits sea-serpent visual coding when TPC bundles it (2025 Year of the Snake shipped Gorebyss/Huntail).
- 馬 Horse (STRICT): horses specifically. Donkeys included via line-as-unit; zebras orphaned.
- 羊 Goat (BROAD): horned ruminants — goat, sheep, ram interchangeably.
- 猴 Monkey (BROAD): any primate.
- 雞 Rooster (STRICT): chicken specifically. Other birds (duck, goose, eagle) have separate characters and stay orphaned.
- 狗 Dog: domestic dogs is the strict reading, but R9 **restores** wolves, foxes, and hellhounds — TPC bundled Poochyena / Eevee / Growlithe as Year of the Dog 2018 spawns. Vulpix-Ninetales stays orphan: kitsune is Japanese 狐仙 sacred-category, an R9-blocking cross-cultural objection.
- 豬 Pig (BROAD): suids broadly — wild boar and domestic pig.

**Element criteria** (TCG-type-honest, MTG colors equivalent):
- 木 Wood: Forest / Green / Grass-type
- 火 Fire: Mountain / Red / Fire-type
- 土 Earth: Plains-as-mundane, Wastes, Ground/Rock/Normal-as-mundane. R5 extension: terrestrial-habitat Poison-types (cobras, skunks, sludge) are chthonic and read Earth.
- 金 Metal: Artifact / Steel-type (Steel only — Wuxing has no Air, so Electric does NOT map here)
- 水 Water: Island / Blue / Ice / Water-type

**Aura column** (the sixth): element-orphaned figures — pure Electric, Dark, Ghost, Psychic, Fairy, Flying, Fighting — that carry a TPC-ratified zodiac identity under R9 (Pikachu Rat, Mareep Goat, Mightyena Dog, Spoink Pig, Dragonite Dragon). R9 ratifies the animal-fit; R5 still orphans the element. The Aura cell records the zodiac aura without claiming a Wuxing home.

## Tag-Cluster Signals

Any animal-slot tag from the list above + element-typing in `tags_filter`. The MD frontmatter `collector_number` and `set` give the printing context; `name` gives the lore framing; `tags_hub` gives the figurative content. Cross-reference all three.

## Narrative Seeds (lair titles, not yet built)

These are `anchored_lairs`-tier candidates — bundle-level narrative seeds, not card-edge attachments. Cell counts and groupings below are verified against the live DATA grid in the `canonical_source` app.js.

- **"China-max Zodiac Set"** — bulk Pokémon commons filling the ~45 cells the grid currently rates with cluster depth ≥ 1, in one bundle. Ships with the pokemon-zodiac poster as the persuasion device. The narrative is the framework itself, already written.
- **"Wood Element"** (or any single element column) — a single-column set at a lower price point. Repeat for Fire/Earth/Metal/Water; the Aura column can ship as its own "off the Wuxing grid" oddity set.
- **"The Deep Four"** — the four genuine depth-5 cells, the densest clusters in the grid: Earth Rat (Skwovet / Drilbur / Sandshrew / Rattata), Earth Ox (Terrakion / Tauros / Bouffalant / Miltank), Earth Dragon (Drampa / Tyranitar / Garchomp / Flygon), and Aura Dragon (the six-line Dratini-through-Kommo-o pseudo-dragon stack). Earth carries three of the four — the agrarian element runs deepest, which is itself the thesis.
- **"Swords of Justice"** — Cobalion + Terrakion + Virizion + Keldeo. The trio tag spans **four cells across three rows**: Terrakion sits in Earth Ox, Virizion in Wood Goat, Cobalion in Metal Goat, Keldeo in Water Horse. Tiny, sharp, complete — a designer-confirmed in-game grouping that cross-stitches three zodiac slots, which is the cohesion premium.
- **"Sim Monkey Trio"** — Simisage + Simisear + Simipour, the elemental monkey trio filling Wood / Fire / Water of the Monkey row in synchrony. A clean three-cell single-row mini-bundle; the trio is a designer-confirmed cycle (Gen V elemental monkeys).
- **"What doesn't fit"** — an orphan-as-thesis lair drawn from the post-R9 Tier 3 footnotes: domestic cats (Great Race myth, TPC declined), most birds (one-bird Rooster slot), Vulpix-Ninetales (kitsune, R9-blocked by cross-cultural objection). The genuine structural orphans — not the R9-restored fauna — become the bundle's interpretive copy.
- **"MTG Zodiac"** — same framework applied to MTG cards. The grid auto-builds from existing tags; under R9 the dragon row widens (Western heraldic dragons are restored, not orphaned), so MTG's dragon-heavy inventory becomes an asset rather than a drift problem.

## Why This Hub Earns Foundational Status

It's the only hub that comes with a *pre-built rubric*. [[labor]] and [[rebellion]] are conceptual lenses Alex writes lairs through. Chinese Zodiac is also that, but additionally it's a 72-cell grid (12 slots × 6 columns) with hard rules — the nine-rule R1-R9 ruleset — already published at diamondlegendz. That makes it the cleanest first BBL-native bundle application — narrative pre-written, sourcing well-defined, even the poster artwork exists. The other two hubs require Alex to author each narrative from scratch.

## Anti-Patterns

This hub is NOT:
- **Type-mushy inclusion without TPC ratification.** The ruleset is two-gated: an animal must pass the functional-agrarian slot criterion AND clear either a Wuxing element (R5) or the Aura column. R9 *restores* Western dragons, wolves, and foxes — but only because TPC shipped them under official Year-of-X framing with no AAPI-community objection. The anti-pattern is not the fauna; it is admitting a card to a cell on vibes ("close enough, makes the grid look full") with no element home and no publisher ratification. Lions stay orphaned because both the strict rule and the market test agree TPC declined to ship them. The discipline is the *evidence requirement*, not blanket exclusion.
- R5 element rules bent for convenience. R9 is a Tier-3 override — it ratifies animal-fit, never the element. Pure Electric / Dark / Ghost / Psychic stay element-orphaned even when TPC bundles them; they land the Aura column, not a Wuxing cell. A card does not "become" Metal because the grid has a Metal gap to fill.
- Vietnamese / other regional zodiac variants. The [[pokemon-zodiac]] project is China-max for cultural-and-commercial alignment (AAPI diaspora collectors are predominantly Chinese tradition, TPC drops Year-of-Dragon Charizard never Year-of-Cat). BBL follows the same line.
- A purely aesthetic "animals" hub. The zodiac framework is mythological / agrarian / cosmological. A bundle of cute cats doesn't fit; a bundle of agrarian-rat-pest cards does.

## Design Note

This hub is **deliberately card-edge disconnected** in Obsidian's graph view. The node itself is visible — it sits in the layer-node clique linked to other layer nodes via body wikilinks — but **no edges connect this hub to any individual card** by design, even when a card depicts one of the twelve zodiac animals directly (the wire flows via character / symbol nodes, not via hub-name-matching).

The `tag_signals` listed above are an *informational* indirection — cards with overlapping `tags_hub` are *candidates* for Chinese Zodiac lair assembly under the functional-agrarian criteria, not auto-anchored members. There is no `appears_on:` or `anchored_cards:` field on this node, and there won't be.

Why: rendering all tag-signal-matched cards as graph edges would balloon Chinese Zodiac to ~115 anchors (mostly drift — "dragon" alone matches 39 MTG cards, and even though R9 now *restores* Western heraldic dragons to the Dragon row, a tag-match still does not equal a cell-fill; a card must clear the two-gate slot+element test, not merely carry the tag). The auto-render would directly contradict the rubric's two-gated scholarship. And more fundamentally — *cards are inventory, bundles are destructive*. When a Discrete Lair assembles, those cards leave the corpus on sale; any field pinning specific cards as canonical hub-anchors would be wrong the moment they ship. See `bbl-bundles-are-destructive-on-graph.md` (wave 81 P3 decision, 2026-05-14).

The triple-thesis ([[_triple-thesis]]) is the root crystal; hubs stand on their own as narrative thesis-anchors; bundle-by-bundle assembly does the rest. `anchored_lairs:` is the right tier of relationship — bundle-level, not card-level — and survives the inventory churn.

## See Also

- [[pokemon-zodiac]] — the scholarly project this hub leans on; the rubric, ruleset, poster, and orphan footnotes already exist there
- [[labor]] — sibling hub; the zodiac is a peasant cosmology, all animal slots are agrarian-functional
- [[rebellion]] — sibling hub; the orphan-honest framing is a rebellion against type-mushy "everything qualifies" curation
- [[diamondlegendz]] — host site for the pokemon-zodiac project
- repo `docs/sketchbook.md` — narrative-first lair architect sketch
