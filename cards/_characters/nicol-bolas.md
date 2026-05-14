---
type: character
name: Nicol Bolas
aliases: [nicol-bolas, bolas, the-elder-dragon, god-pharaoh, dragon-god, the-forever-serpent]
universe: "Magic: The Gathering / Multiverse"
faction: ~
species: Elder Dragon (formerly planeswalker; de-sparked post-War of the Spark)
canonical_source: "MTG Wiki — Nicol Bolas; Wizards of the Coast story archive; War of the Spark novel (Greg Weisman, 2019)"
confidence: canonical
appears_on:
  - magic-the-gathering/war-of-the-spark/26-prison-realm
  - magic-the-gathering/war-of-the-spark/35-topple-the-statue
  - magic-the-gathering/war-of-the-spark/190-despark
related_hubs: [rebellion]
related_symbols: []
ip_resolution_for: nicol-bolas
---

# Nicol Bolas

The elder dragon planeswalker who served as Magic: The Gathering's primary multiversal antagonist for roughly two and a half decades of Wizards of the Coast story output, from his introduction in Time Spiral (2006) through his climactic defeat in War of the Spark (2019). Twin of Ugin. Architect of the Mending-era Conflux. God-Pharaoh of Amonkhet. The most-storylined villain in the game's history; the canonical anchor of any narrative beat involving the elder dragon brood, the Amonkhet zombification arc, or the planeswalker-harvest plot that drove the entire 2017–2019 story block.

## What this node anchors

Card art that depicts Bolas himself — in flesh, in monumentalization, or in the moment of his defeat — plus cards whose narrative beat *centers* him as the off-frame antagonist (his statues, his Eternals, his Elderspell, his prison). The character is large enough that he splits into substantively different aspects across his printings, and the BBL graph can edge those aspects together through this anchor node rather than card-to-card.

**Aspects in the corpus (current):**

- **War of the Spark — Bolas-Falls cluster** — three story-spotlight cards depicting adjacent beats of his defeat:
  - **Topple the Statue** (WAR-35, common, Sidharth Chaturvedi art) — Vitu-Ghazi fells the Ravnican Bolas statue; flavor text names him; Act 2 morale rally.
  - **Despark** (WAR-190, uncommon, Slawomir Maniak art) — Liliana, freed from his contract, commands the corrupted God-Eternals Oketra and Bontu against him; Act 3 turning beat.
  - **Prison Realm** (WAR-26, uncommon, Daarken art) — Bolas imprisoned in the Meditation Plane (renamed the Prison Realm post-WAR) under Ugin's containment; Act 3 coda. Flavor text names him.

All three carry Scryfall's `story_spotlight: true` flag, depict the same character at adjacent narrative beats, and were art-directed as part of the same set's twenty-seven-card story-spotlight cycle.

## Canonical sources

- **MTG Wiki — Nicol Bolas** (`https://mtg.fandom.com/wiki/Nicol_Bolas`) — full character page; primary reference for biography, story arcs, planar travels, and the WAR conclusion.
- **MTG Wiki — Meditation Plane** (`https://mtg.fandom.com/wiki/Meditation_Plane`) — confirms the Meditation Plane was renamed the Prison Realm after WAR and is Bolas's eternal containment under Ugin.
- **MTG Wiki — War of the Spark** — set page; primary reference for the Bolas-Falls narrative cluster and the seven-card Act 2 story-spotlight cycle (Pledge of Unity, Rally of Wings, Awakening of Vitu-Ghazi, Topple the Statue, Enter the God-Eternals, Spark Harvest, The Elderspell, Deliver Unto Evil).
- **War of the Spark: Ravnica** (Greg Weisman, Del Rey 2019) — official tie-in novel; canonical prose source for the defeat sequence depicted across the spotlight cards.
- **Wizards of the Coast — magic.wizards.com story archive** (`https://magic.wizards.com/en/news/story`) — official story posts across the Bolas arc; primary for Amonkhet, Hour of Devastation, Ixalan, Dominaria, and War of the Spark beats.
- **Scryfall** — `is:storyspotlight set:war` returns the 27-card WAR story-spotlight cycle including all three Bolas-Falls cards; designer-confirmed cluster membership rests on this flag.

## Caveats

- This node is the character. The **set-level event** (the War of the Spark itself) and the **place** (the Meditation Plane / Prison Realm) are separate-but-related concepts. If a future pass needs to anchor non-Bolas WAR story-spotlights — e.g. the Gatewatch Triumph cycle, the Ravnican guild beats — they should attach to a sibling node (event or hub), not here.
- Bolas's twin Ugin is a distinct character with overlapping iconography (horns, draconic, magic-binding). When Prison Realm depicts Bolas with Ugin's containment magic around him, the depicted figure is Bolas, but the *mechanism* is Ugin's — both characters are graph-relevant. A future Ugin character node would edge to Prison Realm as the jailer side of the same beat.
- His Liliana-handled defeat in Despark depicts Liliana foregrounded with Bolas implied off-frame (the God-Eternals she commands are the visible apparatus). The card belongs to this character anchor because the *narrative subject* is Bolas's defeat, not Liliana's victory — the flavor text and story-spotlight tag confirm. A future Liliana character node would also edge to Despark as the protagonist-of-the-act side.

## See also

- [[rebellion]] — the BBL hub most thematically compatible with the Bolas-Falls cluster; the toppling of a tyrant-god rendered in stone, the slave-mage turning on her master, the imprisonment of the architect of multiversal harvest. The hub's "Let it burn" and "Cut the strings" narrative seeds both index here.
- [[Bulk Graph Bundler]] — the project this character node serves.
