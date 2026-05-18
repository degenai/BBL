---
type: hub
name: Rebellion
aliases:
  - rebellion
  - revolt
  - uprising
  - defiance
  - dissent
  - refusal
  - anti-establishment
tag_signals:
  - rebellion
  - defiance
  - dissent
  - refusal
  - sabotage
  - mob
  - riot
  - uprising
  - betrayal
  - escape
  - fugitive
  - conspiracy
  - mind-control-refused
  - oath-broken
  - mutiny
  - insurgent
  - partisan
  - runaway
  - hidden
  - ambush
anchored_lairs: []
brand_weight: foundational
tags:
  - layer
  - hub
---
# Rebellion

A foundational [[Bulk Graph Bundler]] hub. Not "edgy cards." Rebellion as the political verb — refusal, organized noncompliance, sabotage, the moment of *no*. The card art moment where someone steps out of formation, opens the cage, breaks the contract, sets the manor on fire.

> Rebellion is also the curation thesis of BBL itself. Buying a thoughtfully-themed bundle of bulk commons instead of chasing the most recently printed mythic IS the small rebellion. The hub is meta as well as literal.

## What This Hub Anchors

Two registers:

**Literal rebellion in card art.** Figures escaping (Satyr's Cunning leaping out of the underworld; Cautious Survivor filming the horror as evidence; the fugitive in the alley). Mass refusal scenes (Witch's Vengeance crowd; mobs with torches; the rally). Sabotage (Broken Wings in the racing set — wings literally clipped; betrayal flavor on Unlicensed Disintegration; arson scenes). Conspiracy and unmasking (Karlov Manor reveals; Coerced to Kill flipped to "but the puppet cut the strings").

**Meta-rebellion: curation as political act.** Bundles built around what the official TCG narrative *won't* tell you. Orphan-as-thesis lairs (Pokémon Zodiac's "Western Dragons orphaned" framed not as exclusion but as critique — *the dex went Western, the curator says so out loud*). Bundles deliberately built from commons and uncommons, never chase cards, with the framing that **the commons ARE the corpus** and the chase card is the lie capital tells about what's valuable.

## Tag-Cluster Signals

`rebellion`, `defiance`, `dissent`, `refusal`, `sabotage`, `mob`, `riot`, `uprising`, `betrayal`, `escape`, `fugitive`, `conspiracy`, `mutiny`, `insurgent`, `partisan`, `runaway`, `hidden`, `ambush` (when the ambushers are the people, not the monsters), `oath-broken`, `mind-control-refused`.

Also: any card where the depicted figure is *unmasking* something — a detective revealing the killer, a witness coming forward, a peasant standing up to a noble.

## Narrative Seeds (lair titles, not yet built)

- **"Cut the strings"** — figures escaping coercion, mind-control reversals, broken contracts, oath-breakers reframed as oath-keepers-to-something-better.
- **"The commons are the corpus"** — meta-rebellion lair, all commons & uncommons from MTG sets where the marketed chase was a mythic; positioning the commons as the real cultural texture.
- **"Let it burn"** — arson, sabotage, racing wings clipped, the manor burning, the rally with torches. The accelerationist subset.
- **"What the official story leaves out"** — Pokémon Zodiac orphan categories, MTG-flavor-text-contradicts-the-art moments, the negative-space stories.

## Anti-Patterns

This hub is NOT:
- "Bad guys" or "villains." A masked aristocrat conspiring against another aristocrat is NOT rebellion — that's intramural court politics. Rebellion requires a power gradient and the lower side acting.
- Aesthetic-only edginess. A goth-coded card with no thematic refusal is not rebellion, it's vibes.
- Anti-anything-for-its-own-sake. The thesis matters. *Rebellion in service of what?* If the answer is "branding," the card belongs in a different bundle.

## Design Note

This hub is **deliberately card-edge disconnected** in Obsidian's graph view. The node itself is visible — it sits in the layer-node clique linked to other layer nodes via body wikilinks like `[[rebellion]]` in character node bodies — but **no edges connect this hub to any individual card** by design, even when a card's name or art literally invokes rebellion (the wire flows via character / symbol nodes, not via hub-name-matching).

The `tag_signals` listed above are an *informational* indirection — cards with overlapping `tags_hub` are *candidates* for Rebellion lair assembly, not auto-anchored members. There is no `appears_on:` or `anchored_cards:` field on this node, and there won't be.

Why: rendering all tag-signal-matched cards as graph edges would balloon Rebellion to ~97 anchors (mostly drift — "ambush" alone matches 32 cards, most of which are monsters-in-ambush not people-in-rebellion). And more fundamentally — *cards are inventory, bundles are destructive*. When a Discrete Lair assembles, those cards leave the corpus on sale; any field pinning specific cards as canonical hub-anchors would be wrong the moment they ship. See `bbl-bundles-are-destructive-on-graph.md` (wave 81 P3 decision, 2026-05-14).

The triple-thesis (`_triple-thesis.md`) is the root crystal; hubs stand on their own as narrative thesis-anchors; bundle-by-bundle assembly does the rest. `anchored_lairs:` is the right tier of relationship — bundle-level, not card-level — and survives the inventory churn.

## See Also

- [[labor]] — sibling hub; labor is the material condition rebellion responds to
- [[chinese-zodiac]] — sibling hub; the zodiac project's gap-as-feature scholarship IS a small rebellion against type-mushy "everything qualifies" curation
- [[mutual-aid]] (in [[Alex]]'s wiki) — the constructive side of rebellion; what comes after refusal
- [[aether-rangers]] — character node; Avishkar's home Grand Prix team in *Aetherdrift*, constituted in the immediate aftermath of the Indigo Revolution. Wizards' Planeswalker's Guide describes them as a cross-generation, cross-class team of comrades bridging pre- and post-revolutionary Avishkar — the team's existence is rebellion's institutional aftermath, the political verb organized into a roster.
- repo `docs/sketchbook.md` — narrative-first lair architect sketch
- memory `bbl-narrative-first-lairs.md` — the principle that says hubs are political anchors, not aesthetic ones
