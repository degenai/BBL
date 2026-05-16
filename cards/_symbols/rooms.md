---
type: symbol
name: Rooms (mechanic)
aliases:
  - rooms
  - room
  - room-mechanic
  - room-card
  - room-enchantment
  - split-room
  - door-mechanic
  - unlock-this-door
faction: ~
universe: "Magic: The Gathering / Duskmourn (DSK, 2024-09-27)"
canonical_source: "Wizards of the Coast — Mark Rosewater's Top of the Duskmourning Part 1 and Part 2 (2024-09); MTG Wiki — Room; Scryfall — type:room / oracletext:'unlock this door'"
confidence: canonical
appears_on:
  - magic-the-gathering/duskmourn-house-of-horror/34-surgical-suite-hospital-room
  - magic-the-gathering/duskmourn-house-of-horror/43-bottomless-pool-locker-room
  - magic-the-gathering/duskmourn-house-of-horror/181-greenhouse-rickety-gazebo
  - magic-the-gathering/duskmourn-house-of-horror/190-moldering-gym-weight-room
  - magic-the-gathering/duskmourn-house-of-horror/235-smoky-lounge-misty-salon
related_hubs: []
related_characters:
  - valgavoth
---

# Rooms (mechanic)

The iconographic-and-rules-text primitive of the **Room** card type introduced in *Duskmourn: House of Horror* (DSK, 2024-09-27) as one of the set's signature mechanics (alongside Manifest Dread, Eerie, Survival, and Delirium-as-returning-subtheme). Rooms are a designer-coordinated split-card variant: each Room card carries two halves (two "doors") on the same physical card, and the player may cast either half as an enchantment whose half-state unlocks on the battlefield. Once unlocked, the controller may later pay the second half's mana cost as a sorcery to unlock that door too, doubling the card's enchantment effects. The marker is a first-class graph-relevant mechanical primitive parallel to [[suspect]], [[disguise]], and [[manifest-dread]]: a designer-coordinated cohort identifier that crosses multiple cards in a set, marks them as members of a designer-stated thematic program, and provides the canonical iconographic anchor for any bundle assembled around the program.

Unlike Manifest Dread / Suspect / Disguise — which are pure mechanical-keyword primitives with no visual signature on the card art — **Rooms are a hybrid primitive**: they carry both a mechanical signature (the split-card layout, the "unlock this door" rules text) AND a visual signature (the two-panel split-art rendering, one panel per door, depicting two adjacent or transformed interior spaces in the Duskmourn manor-as-plane). The visual signature alone is enough to identify a Room card from card-art-only inspection.

## The functional ideology

The Rooms mechanic is the canonical-by-printing mark for the DSK **labyrinth-as-mechanic layer**. Per Mark Rosewater's "Top of the Duskmourning" articles (Part 1 and Part 2, September 2024) and the canonical MTG Wiki Room page, Rooms were designed to render the Duskmourn plane's central conceit — the entire setting is the inside of a haunted house large enough to be its own world — at the card-design level. Each Room card is *literally* a room in the House, and the controller's gameplay choice of *which door to unlock first* maps the in-fiction experience of walking through the labyrinth and choosing which threshold to cross. The two halves of each Room are art-directed as adjacent interior spaces (Surgical Suite + Hospital Room, Bottomless Pool + Locker Room, Smoky Lounge + Misty Salon) or as before/after transformations of the same space (Greenhouse + Rickety Gazebo, Moldering Gym + Weight Room), letting the card's visual rendering tell the *progression* story even before the player engages the rules text.

The cohort's most BBL-relevant property is its **direct dual-coding of architectural-progression horror as combat-rules**. Where Eerie renders the *house breathing* (enchantment-trigger pings, see the future [[eerie]] node), and Survival renders the *trapped-and-watching* state, and Manifest Dread renders the *summoning of the unknown*, Rooms render the *the corridor unfolding ahead* as a split-enchantment whose second half is itself a future game state the controller can choose to pay into. The mechanic's narrative read is the survivor opening one door, finding another, and deciding when to open the next.

For any BBL bundle on DSK mechanical cohesion, the architectural-horror register, or the manor-as-plane thesis, the Rooms mechanic is the highest-leverage iconographic-mechanical anchor available in the *Duskmourn* slice of the corpus. Bundle prose that names the mechanic by name earns lore-aware buyer credibility AND lets Wizards' actual designer-coordinated cohort work do the thesis work — Rooms are *literally* the rules-text rendering of the house unfolding around you, and the storefront copy can lean on that without inventing the angle.

## Where it appears

Confirmed in corpus (5 anchors — well past the ≥3 single-strike-emblem precedent threshold, and equal to the [[manifest-dread]] anchor count):

- **Surgical Suite // Hospital Room** (DSK-34, uncommon WU, John Avon art) — `{1}{W}{U}` Room. The Surgical Suite half returns a low-mana-value creature card from your graveyard to the battlefield on door-unlock; the Hospital Room half draws cards. Two adjacent interior medical-horror spaces — the operating theater and the recovery ward — render the Duskmourn medical-grotesque visual register.
- **Bottomless Pool // Locker Room** (DSK-43, uncommon U, Wisnu Tan art) — `{1}{U}` Room. The Bottomless Pool half bounces a creature on door-unlock; the Locker Room half is a tempo-piece. Two adjacent interior pool-locker-complex spaces — the bottomless deep-end and the changing room beside it — render the *summer-camp-horror water* visual register.
- **Greenhouse // Rickety Gazebo** (DSK-181, uncommon G, John Di Giovanni art) — `{1}{G}{G}` / `{2}{G}{G}` Room. The Greenhouse half adds mana-fixing to your lands on door-unlock; the Rickety Gazebo half is the before/after transformation: the same space as Greenhouse but ruined and overgrown. The two halves render the *time-as-decay* visual register with a vine-overgrown abandoned-conservatory aesthetic.
- **Moldering Gym // Weight Room** (DSK-190, common G, Helge C. Balzer art) — `{2}{G}` Room. The Moldering Gym half is a basic-land ramp on door-unlock; the Weight Room half triggers Manifest Dread on door-unlock AND adds three +1/+1 counters to the resulting face-down 2/2. The card co-anchors on both this node and the [[manifest-dread]] node — the canonical *Room-mechanic-meets-Manifest-Dread* dual-symbol case. The two halves render an abandoned-gym-overrun-with-vegetation transformation in horror register.
- **Smoky Lounge // Misty Salon** (DSK-235, uncommon UR, Marco Gorlei art) — `{R}{U}` / `{2}{R}{U}` Room. The Smoky Lounge half adds `{R}{R}` mana usable only for Room spells / unlocking doors during your first main phase; the Misty Salon half is a tempo-piece. Two adjacent interior manor spaces — the warm-red trophy lounge and the cold-blue moonlit library — render the *temperature-coded-manor-interior* visual register, with stag-skull mounts tying both halves to the same hunter aesthetic.

Strong candidates pending corpus enrichment for vision / trivia (textual sources confirm the type on these):

- **Ghostly Keybearer** (DSK-61) — a creature whose combat-damage trigger *unlocks a locked door of up to one target Room you control*. NOT a Room itself, but a Room-mechanic interaction card; would not enter `appears_on:` for this node (which is reserved for Room-type cards), but the [[eerie]] / future Room-interactions cross-edge applies.
- **Keys to the House** (DSK-251) — an artifact whose triggered ability lets the controller unlock Rooms cheaper. NOT a Room itself; same treatment as Ghostly Keybearer.
- Other DSK cards bearing the Room subtype on Enchantment. MTG Wiki's Room page lists roughly 15-18 distinct Room printings across DSK (the mechanic is one of the set's structural-keyword design devices, spanning common-through-mythic rarity).

The corpus may accumulate further Room-type cards as DSK enrichment continues; the symbol-node anchor is sized to grow.

## Caveats

- **Rooms are paired with — but distinct from — Eerie, Manifest Dread, Survival, and Delirium.** The DSK signature mechanics were designed as an interlocking suite per Rosewater's preview articles. Rooms render the *labyrinth* (split-card enchantment doors); [[eerie]] renders the *house breathing* (enchantment-trigger pings — and Eerie *requires Rooms exist* to trigger, making the two mechanics structurally interdependent); Survival renders the *trapped-and-watching* state (still-tapped-during-second-main-phase triggers); [[manifest-dread]] renders the *summoning of the unknown* (top-of-library reveal + mill + face-down deploy); Delirium (returning from Shadows over Innistrad) renders the *graveyard-as-deck-condition* that Manifest Dread feeds. Each warrants its own future symbol-layer node when corpus accumulates ≥3 anchors per mechanic — current Rooms coverage clears the threshold; Eerie coverage is at 5 corpus members and is the strongest immediate sibling-node candidate (commissioned alongside this one); Survival coverage is at 6 corpus members; Manifest Dread is already a symbol-layer node.
- **The Room *card-type* and the *split-enchantment double-door creature-state* are co-extensive but conceptually distinct.** The Room subtype is a Wizards-canonical card-type designation visible in the printed `type_line` ("Enchantment — Room"); the split-card-with-two-doors deployment is the gameplay state the affected card occupies on the battlefield. Both predicates pick out the same set of cards in current MTG canon, but the **card-type is the symbol-layer anchor** that the BBL graph hosts at the `_symbols/` level. State-tracking is captured in card oracle_text ("When you unlock this door"-containing strings); card-type membership is captured here.
- **Rooms are a Duskmourn design innovation, not a returning mechanic.** Per Rosewater's preview articles and MTG Wiki's Room page, the split-card-as-progressive-enchantment design space was prototyped for DSK and had no direct precedent (split cards previously came from Invasion-block Aftermath cards, Modal Double-Faced Cards, and classic Apocalypse split cards, none of which used the progressive-unlock pattern). The mechanic is canonical for the DSK-and-reprints window; future MTG sets may reintroduce Rooms as a returning mechanic, but as of 2026-05-14 no such revival has been announced. The hybrid visual + mechanical signature makes Rooms more distinctive than the pure-keyword DSK mechanics (Manifest Dread, Eerie, Survival), and Wizards' mechanic-recycling pattern suggests Rooms are a strong candidate for return given how memorable the split-card art rendering is.
- **Rooms ARE iconographically visible on the card-art level** — unlike [[suspect]], [[disguise]], and [[manifest-dread]] (all pure mechanical-keyword primitives with no card-art signature), Rooms carry a *visual signature* (the two-panel split-art rendering, one panel per door). This makes Rooms a **hybrid primitive** — both visual AND mechanical. The two-panel rendering can be identified from card art alone before any rules-text reading; the controller's choice of which door to unlock first is a separate mechanical state. This places Rooms structurally between [[orzhov-signet]] / [[single-strike-emblem]] (pure visual primitives) and [[suspect]] / [[disguise]] / [[manifest-dread]] (pure mechanical primitives) in the symbol-layer taxonomy. The node-type predicate is *first-class graph-relevant designer-coordinated cohort primitive*, regardless of whether the primitive is visual-only, mechanical-only, or hybrid.
- **The [[valgavoth]] character-node is the natural cross-edge.** The Duskmourn plane *is* Valgavoth's House, and every Room card depicts a chamber within that House. The Rooms mechanic at the rules-text level renders Valgavoth's labyrinth-as-trap cosmology — each unlocked door commits the player deeper into the demon's domain. The `related_characters: [valgavoth]` frontmatter field on this node encodes the cross-edge; the Valgavoth node may want a reciprocal `related_symbols: [rooms]` update as a downstream sync task.

## Sources

- **Wizards of the Coast — Mark Rosewater, "Top of the Duskmourning" Part 1 and Part 2** (`https://magic.wizards.com/en/news/making-magic`, September 2024) — primary first-party source for the Rooms mechanic's design history, the split-card-as-progressive-enchantment design space, and the five-mechanic DSK suite.
- **MTG Wiki — Room (mechanic)** (`https://mtg.fandom.com/wiki/Room`) — primary mechanic page; documents the Room subtype, the door-unlock rules, the full DSK Room roster, and the Eerie + Room interaction.
- **MTG Wiki — Duskmourn: House of Horror** — set page; documents the five-mechanic suite (Rooms, Eerie, Survival, Manifest Dread, Delirium-returning) as the set's design program.
- **Scryfall** — `type:room` returns the canonical DSK Room roster; `oracletext:"unlock this door"` returns the cards with the Rooms-specific door-unlock trigger.
- `cards/magic-the-gathering/duskmourn-house-of-horror/190-moldering-gym-weight-room.md` — in-corpus vision entry documenting the Room-mechanic-plus-Manifest-Dread dual-symbol interaction.
- `cards/magic-the-gathering/duskmourn-house-of-horror/235-smoky-lounge-misty-salon.md` — in-corpus vision entry documenting the temperature-coded-manor-interior visual register.

## Appears on

<!-- auto-generated from appears_on; do not edit by hand -->

- [[34-surgical-suite-hospital-room]]
- [[43-bottomless-pool-locker-room]]
- [[181-greenhouse-rickety-gazebo]]
- [[190-moldering-gym-weight-room]]
- [[235-smoky-lounge-misty-salon]]
## See also

- [[manifest-dread]] — sibling symbol node from DSK; structural precedent. The Rooms + Manifest Dread pair completes two of the five DSK signature mechanics. Co-anchors on **Moldering Gym // Weight Room** (DSK-190), which carries both the Room card-type and triggers Manifest Dread on door-unlock — the canonical *Room-mechanic-meets-Manifest-Dread* dual-symbol case.
- [[eerie]] — sibling symbol node from DSK (commissioned in same pass); structurally interdependent with Rooms (Eerie triggers when *you fully unlock a Room*, making the Eerie mechanic literally require Rooms to exist on the battlefield to fire). Many DSK cards play both nodes simultaneously at the deck-construction level.
- [[suspect]] — sibling symbol node from MTG/MKM; structural precedent for designer-coordinated mechanical-keyword primitives. Distinction: Suspect is pure mechanical-keyword; Rooms are hybrid (visual + mechanical).
- [[disguise]] — sibling symbol node from MTG/MKM (commissioned in same pass); structural precedent. Distinction: Disguise is pure mechanical-keyword; Rooms are hybrid.
- [[orzhov-signet]] — sibling symbol node from MTG/Ravnica; structural precedent for visual primitives. Distinction: Orzhov Signet is a pure visual primitive; Rooms are hybrid (visual + mechanical).
- [[single-strike-emblem]] — sibling symbol node from Pokemon/Galar; structural precedent. Distinction: Single Strike Emblem is a pure visual primitive on Pokemon TCG cards; Rooms are a hybrid primitive on MTG DSK cards.
- [[valgavoth]] — sibling DSK character node; the set-defining antagonist whose plane this mechanic embodies at the architectural level. Every Room card is literally a chamber within Valgavoth's House.
- [[Bulk Graph Bundler]] — the project this symbol enriches.
- Future DSK Discrete Lair candidate — 5 Rooms corpus anchors + 7 Manifest Dread anchors + 5 Eerie anchors + 6 Survival candidates + the [[valgavoth]] anchor form an extraordinarily substantial bundle-cohesion stack for a Duskmourn-architecture-of-horror lair anchored on the House's interior rendering. The five-mechanic suite makes the bundle thesis the set design itself.
