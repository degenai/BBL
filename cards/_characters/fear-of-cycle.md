---
type: character
name: Fear-of cycle (Duskmourn phobia-Nightmares)
aliases: [fear-of-cycle, fear-of, duskmourn-phobia-cycle, duskmourn-nightmares, phobia-cycle]
universe: Magic: The Gathering / Duskmourn (DSK, 2024-09-27)
faction: ~
species: cycle of Enchantment Creature — Nightmare cards
canonical_source: "MTG Wiki — Duskmourn: House of Horror (set page, Cycles section); Scryfall set DSK (name prefix `Fear of` returns the cycle members); per-card oracle text and type-line confirmation"
confidence: canonical
appears_on:
  - magic-the-gathering/duskmourn-house-of-horror/9-fear-of-abduction
  - magic-the-gathering/duskmourn-house-of-horror/55-fear-of-failed-tests
  - magic-the-gathering/duskmourn-house-of-horror/56-fear-of-falling
  - magic-the-gathering/duskmourn-house-of-horror/134-fear-of-being-hunted
  - magic-the-gathering/duskmourn-house-of-horror/135-fear-of-burning-alive
related_hubs: []
related_symbols: []
---

# Fear-of cycle (Duskmourn phobia-Nightmares)

A Duskmourn: House of Horror design cycle of Enchantment Creature — Nightmare cards whose names all begin with "Fear of..." Each card personifies a specific phobia as a stalking, embodied creature: the rabbit-skulled predator that is the fear of being hunted, the burning skull-cluster demon that is the fear of burning alive, the towering abductor-figure that is the fear of abduction, and so on. The cycle is the most direct mechanical expression of the set's "phobias as monsters" Vision Design Handoff thesis (suspense-over-shock, Freddy/Jason-type unkillable antagonists rendered as the dread itself rather than its source).

## What this node anchors

Card art and rules text that name a specific phobia as a Nightmare creature. The unifying frame across the cycle is twofold: (a) the naming convention "Fear of <verb-phrase or noun-phrase>" enforced uniformly across all cycle members, (b) the Enchantment Creature — Nightmare type-line shared by every member, marking each card as both an embodied creature and the abstract psychic state it personifies.

**Cards in our corpus pointing here (current):**

- **Fear of Abduction** (DSK-9, uncommon, Fernando Falcone art) — white Nightmare with Flying; enters and exiles a target creature an opponent controls; leaves and the exiled cards return to their owner's hand. The phobia personified is the loved-one-vanished trope of slasher and abduction-horror cinema.
- **Fear of Failed Tests** (DSK-55, uncommon, Jana Heidersdorf art) — blue Nightmare whose combat damage to a player draws that many cards. Flavor text is Zimone Wola muttering the recurring student-anxiety dream in her sleep — the phobia is the anxiety-dream of academic exposure.
- **Fear of Falling** (DSK-56, uncommon, Maxime Minard art) — blue Nightmare with Flying; on attack, target blocker loses -2/-0 and flying. Flavor text: *"It had been months since Jakob had started falling but only a few weeks since he'd run out of breath to scream."* The phobia is endless plummet rendered as a flying creature that *takes* flight from its victims.
- **Fear of Being Hunted** (DSK-134, uncommon, Maxime Minard art) — red Nightmare with Haste; must be blocked if able. Flavor text: *"It makes no effort to hide itself, savoring its prey's rising panic as the sound of its clacking skull grows closer and closer."* The phobia is the unhideable stalker; the art is a skeletal rabbit-skulled predator amid sprung mousetraps.
- **Fear of Burning Alive** (DSK-135, uncommon, J.P. Targete art) — red Nightmare; enters and deals 4 damage to each opponent; with Delirium active, repeats its damage to a target creature whenever a source you control deals noncombat damage to an opponent. The art is a charred quadrupedal demon with a screaming-skull-cluster fused to its flank — the phobia is incineration carrying its victims with it.

## Canonical sources

- **MTG Wiki — Duskmourn: House of Horror** — set page; Cycles section documents the "Fear of..." uncommon Nightmare cycle alongside the set's other cycles (Rooms, Survival creatures, manifest dread enablers).
- **Scryfall** — set DSK; the search `s:dsk name:"Fear of"` returns the cycle members and confirms shared Enchantment Creature — Nightmare type-line across them.
- **Wizards: Duskmourn Vision Design Handoff** (cited in Horrid Vigor DSK-184 trivia via WebSearch snippet) — names "phobias as antagonists" and Freddy/Jason-type unkillable antagonists as the design register the cycle inhabits.
- **Scryfall per-card pages** for DSK-9, DSK-55, DSK-56, DSK-134, DSK-135 — primary source for oracle_text, type_line, flavor_text strings cited above.

## Caveats

- The Fear-of cycle is a collective design device, not an individual named character. Modeled as a character-layer node because the layer already accepts collective named entities (cf. Endriders precedent: "Modeled here as a `character` node because the character layer already accepts collective named entities"). A future `_cycles/` layer could re-home this entry if the corpus accumulates enough designer-confirmed flavor cycles to warrant the split — the Cinderella cycle in Throne of Eldraine and the Survivor cycle in Duskmourn itself are the obvious next candidates. For now, single layer, same precedent.
- **Cycle members canonical at the DSK-set scope but not yet in BBL inventory.** The Fear of Burning Alive (DSK-135) trivia pass canonicalized the full DSK Fear-of cycle roster against Scryfall's per-card pages. The canonical roster spans all five colors plus a UB multicolor capstone, totaling ten members. Five members are in the corpus and pointered to this node (see `appears_on:`); five members are Scryfall-confirmed but not yet acquired and will attach to this node when they land via a future Collectr CSV upload:
  - **Fear of Surveillance** (DSK-11, white) — second white slot in the cycle alongside Fear of Abduction.
  - **Fear of Isolation** (DSK-58, blue) — third blue slot alongside Failed Tests and Falling.
  - **Fear of the Dark** (DSK-98, black) — the cycle's sole black slot. Independently corroborated by the Say Its Name (DSK-197) trivia: same artist (Sam Wolfe Connelly), same Conte medium, part of Connelly's Duskmourn cluster, flagged "not in current inventory."
  - **Fear of Missing Out** (DSK-136, red) — completes the 134-135-136 red block alongside Being Hunted and Burning Alive.
  - **Fear of Infinity** (DSK-214, UB multicolor) — the cycle's multicolor capstone.

  The full canonical cycle is thus five colors plus a UB capstone, with multiple members in W (2: Abduction, Surveillance), U (3: Failed Tests, Falling, Isolation), B (1: the Dark), R (3: Being Hunted, Burning Alive, Missing Out), and UB (1: Infinity). Alchemy: Duskmourn and DSK Commander follow-on printings are not surveyed in this pass; if those product lines added further Fear-of cards, those are out of scope until the corpus or a follow-up trivia pass surfaces them.
- The cycle's color distribution across the BBL corpus (as of 2026-05-12) is white (1: Abduction), blue (2: Failed Tests, Falling), red (2: Being Hunted, Burning Alive). The corpus is missing one of two white slots, one of three blue slots, the single black slot, one of three red slots, and the UB capstone — five acquisitions away from full canonical cycle coverage.
- The "Fear of" naming convention is the load-bearing connection across the cycle, not the Nightmare creature type alone. Other Duskmourn Nightmare-typed cards exist (Twitching Doll, Hauntwoods Shrieker, etc.) that are not part of the Fear-of cycle — these are Nightmare-typed creatures within the set's broader horror flavor, not phobia-personifications named with the "Fear of" prefix. Membership predicates on the name pattern, not the creature type. The two layers correlate but are not co-extensive.

## See also

- [[rebellion]] — the BBL hub most thematically near-but-not-coextensive with this cycle. A "phobia personified as monster" lair could anchor on the meta-rebellion thesis (the unkillable monster as the unrepayable debt, the slasher-as-systemic-collapse, the survivor refusing to play the script the cycle hands them). The hub edge is potential, not yet load-bearing — when the three vision-stub Fear-of cards are enriched and the triviabot identifies specific flavor-text moments of refusal-against-the-phobia, this edge may activate.
- [[Bulk Graph Bundler]] — the project this character node serves.
