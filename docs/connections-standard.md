---
type: doctrine
name: Connections-section standard
brand_weight: foundational
status: locked-2026-05-14
---

# Connections-section standard

`## Connections` is the corpus's richest edge-enrichment surface. One bullet per edge. Each bullet carries: a wikilink to a real graph node, a one-or-two-sentence canonical reading of why the edge exists, and bracketed source citations. That's the whole job.

Across waves 64–73 the format drifted — citation punctuation varied (`[Scryfall: ...]` vs `` `[Scryfall: ...]` ``), opening-phrase conventions diverged across card-card vs card-hub vs card-symbol attaches, and prose length stretched from one sentence to three-hundred-word paragraphs. This document locks the format so future Edgelord runs and the eventual connections-renderer parse the same shape everywhere.

The standard is a *floor*, not a ceiling. Brand-voice density and canonical-evidence weight remain Edgelord's call. The format is what holds across cards.

## Canonical template

```markdown
## Connections

- [[<target-node-stem>]] — <edge-type opener>. <Canonical reading: what the edge IS, what evidence supports it, what graph-axis it sits on.> `[<Source 1>]` `[<Source 2>]`
```

Required elements:

1. **Section header** is always literally `## Connections`. No suffix, no parenthetical, no per-edge sub-header.
2. **Bullet marker** is `-`. One bullet per edge. Multiple edges on one card = multiple bullets, one per target.
3. **Wikilink first.** `[[<target-node-stem>]]` is always the first content of the bullet. The stem matches the target MD's filename-without-extension (e.g. `[[26-prison-realm]]`, `[[orzhov-signet]]`, `[[mareep-line]]`). Obsidian resolves against the `cards/` vault root regardless of which subdirectory the linking card lives in.
4. **Em-dash separator** (` — `) between the wikilink and the prose. Space-dash-space.
5. **Opener** is a noun phrase or short labeled clause naming the edge-type. Ends in a period. (See "Opener conventions" below.)
6. **Canonical reading** is one or two sentences. Names what the edge IS in canon, cites the load-bearing evidence inline. No more than two sentences. If the reading needs more than two sentences, you're writing a Trivia entry, not a Connections bullet.
7. **Citations trail.** Backticked bracketed source-strings at the end, space-separated: `` `[Source A]` `[Source B]` ``. Two to four citations is the typical range. One is acceptable when the canon is single-source; zero is never acceptable — refuse the edge if you can't cite it.

## Opener conventions

The opener names the edge-type in the same vocabulary the Edgelord agent spec enumerates. Pick the closest match; do not invent new categories.

- **Named-character identity** — `Same character across [N] [set / printings / form].`
- **Story-spotlight pair / chain** — `Paired story-spotlight beats of [arc].` or `Sequential story-spotlight beats in [arc].`
- **Symbol-on-art** — `[Symbol name] [carrier-noun].` (e.g. `Orzhov Signet on throne backing.`)
- **Designer-coordinated cycle / cohort** — `Designer-coordinated [cycle / cohort / sequence] within [set].`
- **Evolution-line / kinship pair** — `Same-line evolution mirror.` or `[Stage-X]-to-[Stage-Y] adjacency.`
- **Mechanical interlock** — `Oracle-text mechanical dependency:` (use the colon form when the canonical evidence IS the oracle text)
- **Hub / symbol / character roster attach** (1:N) — `[Node name] roster card.` or `[Node name] member.`
- **Triangle / cycle anchor** — `[Set / arc] [cycle name], [verb / axis-label] anchor.` (e.g. `Battle for Zendikar triple-thesis cycle, rebellion-verb anchor.`)

If the edge doesn't fit any of these openers cleanly, the edge is probably weak. Refuse rather than invent a new opener category.

## Citation format

- **Backticked bracketed strings**, space-separated, at the tail of the second sentence: `` `[Scryfall: oracle_text]` `[MTG Wiki: Manifest dread]` ``.
- The backticks are not optional. They give the citation visual weight in raw markdown and they reserve the option for the future connections-renderer to format citations distinctly.
- Inside the brackets, lead with the **source name** (Scryfall, MTG Wiki, Bulbapedia, PokemonTCG.io, EDHREC, Dragon Ball Wiki, a designer-article title), then a colon-and-specifier when the source has internal anchors (`Scryfall: oracle_text`, `MTG Wiki: War of the Spark Story Spotlights`, `Wizards: Top of the Duskmourning Part 1`).
- **Wikilinks-as-citations are permitted ONLY for meta-hub anchors** like `` `[[_triple-thesis]]` `` where the wikilink IS the canonical-evidence pointer. Do not cite ordinary nodes via wikilink — wikilinks belong in the bullet body, citations belong in the trail.
- **Path-style citations** (`[cards/_symbols/orzhov-signet.md]`) are deprecated. Cite the source-of-truth, not the BBL file derived from it.

## Mutual-mirror cases (triangle / chain)

When three or more cards mutually reference each other (the Battle for Zendikar triple-thesis triangle, the War of the Spark Bolas-Falls story-spotlight triangle), **each card carries N-1 bullets in its `## Connections` section**, one per sibling. The bullets are written from this card's POV — opener-and-reading describe what THIS card is, then how it relates to that sibling.

Do not collapse the triangle into one bullet per card. Each pair is its own edge; each gets its own bullet; each is traversable from either endpoint.

The opener convention for triangle members is:

```
[Set / arc] [cycle name], [this-card's-axis-label] anchor.
```

Followed by the canonical reading of this card's axis-position, then how the sibling occupies the adjacent position, then the cycle-citation in the trail. See the BFZ triangle example below.

## Worked examples

### 1:1 mirror — Pokemon evolution adjacency

```markdown
## Connections

- [[048-198-flaaffy]] — Same-line evolution mirror, Chilling Reign 047/048 within-set adjacency. Mareep is the Johto Electric chain's base stage (Pokedex no. 179, evolves to Flaaffy at level 15); the within-set adjacent collector numbers are designer-coordinated cohort placement encoding the wool-to-electrification cost-of-power progression visible across the two illustrations. `[PokemonTCG.io: swsh6-47 + swsh6-48 evolvesTo / evolvesFrom]` `[Bulbapedia: Mareep (Pokemon)]`
```

### 3-way mutual triangle — BFZ thesis cycle

```markdown
## Connections

- [[152-reckless-cohort]] — Battle for Zendikar triple-thesis cycle, stewardship-verb anchor. This card depicts the white-magic protector-tier among Zendikar's ruins (lifelink-pump mechanics for the resistance, "I can give you strength" flavor encoding care-without-coercion). Reckless Cohort occupies the rebellion-verb position (Sea Gate survivor, Ally-resistance mechanics) — the *resistance refuses* face that this *steward holds the ground* face is paired against. `[Scryfall: oracle_text + flavor_text on Serene Steward]` `[[_triple-thesis]]`
- [[129-kozilek-s-sentinel]] — Battle for Zendikar triple-thesis cycle, stewardship-verb anchor. Kozilek's Sentinel occupies the labor-verb position (Eldrazi drone-caste pressing through Zendikar's tunnels; Devoid mechanically encoding mana-identity-stripping as the cosmological-scale extraction) — the *apparatus consumes* face that this *steward holds the ground* face is the counterpose to. Together with Reckless Cohort the three cards form the corpus's first 3-card MTG cycle hitting all three thesis-verbs simultaneously. `[Scryfall: oracle_text + flavor_text]` `[[_triple-thesis]]`
```

(The other two cards in the triangle carry the same two-bullet pattern, each written from their own POV. Three cards × two bullets each = six bullets total across the triangle.)

### 1:N attach — card to hub / symbol / character

```markdown
## Connections

- [[orzhov-signet]] — Orzhov Signet on jewelry. The four-pronged eclipsed-sun device set in the locket's heart-pendant is the canonical master's-medallion form of the signet (Commander 2011 *Orzhov Signet* artifact flavor: "If it's carried on a medallion, its bearer is a master"); the flavor speaker on this card, Milana the Orzhov prelate, is wearing the institutional power-mark as a status object. `[Scryfall: Orzhov Signet (CMD 2011) flavor text]` `[MTG Wiki: Orzhov Syndicate]`
```

## When NOT to write a Connections section

`## Connections` exists for **load-bearing graph edges**. Do not write a Connections section when:

- The connection is a shared tag (`forest`, `armor`, `mountain`). Tag-bridges live in `tags_hub`, not in Connections.
- The connection is shared color identity, rarity, release-year, or other meta-trivia.
- The connection is a same-artist credit *without* thematic intent. (Same artist + designer-coordinated cycle = valid; same artist alone = not.)
- The candidate edge is to a node that doesn't yet exist. Either propose the node (Mr. Nodeley) or wait — do not write a placeholder bullet to a node that may never be created.
- The card has no enriched vision pass yet. Connections sit on top of Vision and Trivia, not in place of them.

Refusal with receipts is the antidote. A card with zero `## Connections` bullets is fine; a card with thin or invented bullets is technical debt.

## Candidate retrofits (existing Connections that don't conform)

Surfaced in the 2026-05-14 standardization survey. Apply in future curator passes; not this pass.

**Citation-format retrofits** (un-backticked or inline-bracketed citations should be migrated to backticked bracketed form):

- `cards/magic-the-gathering/war-of-the-spark/35-topple-the-statue.md` — citations are bracketed but not backticked.
- `cards/magic-the-gathering/war-of-the-spark/26-prison-realm.md` — same; bracketed without backticks.
- `cards/magic-the-gathering/war-of-the-spark/190-despark.md` — same.
- `cards/magic-the-gathering/battle-for-zendikar/46-serene-steward.md` — uses `Citations: [...]` trailing-prose form; convert to backticked trail.
- `cards/magic-the-gathering/battle-for-zendikar/129-kozilek-s-sentinel.md` — same.
- `cards/magic-the-gathering/battle-for-zendikar/152-reckless-cohort.md` — same.
- `cards/magic-the-gathering/ravnica-allegiance/236-orzhov-locket.md` — uses `[cards/_symbols/orzhov-signet.md]` path-style citation; should cite the canonical source (Commander 2011 Orzhov Signet flavor) instead, retain `[[orzhov-signet]]` wikilink only in body.
- `cards/magic-the-gathering/duskmourn-house-of-horror/189-manifest-dread.md` — citations bracketed but not backticked.
- `cards/magic-the-gathering/duskmourn-house-of-horror/190-moldering-gym-weight-room.md` — same.
- `cards/pokemon/burning-shadows/40-147-pikachu.md` — uses inline bracketed citations with `[[labor]]` wikilink mixed into the trail; split body wikilinks from trail citations.
- `cards/pokemon/darkness-ablaze/086-189-larvitar.md` — single trailing `[...]` block without backticks.
- `cards/pokemon/chilling-reign/047-198-mareep.md` — same; single trailing block.
- `cards/pokemon/darkness-ablaze/092-189-solrock.md` — backticked but inconsistent.

**Prose-length retrofits** (Connections bullets that exceed the two-sentence ceiling and should be trimmed):

- `cards/pokemon/chilling-reign/047-198-mareep.md` — single bullet runs ~270 words; trim to two sentences with the surplus reading moved into `## Trivia` if any of it is load-bearing canon.
- `cards/pokemon/darkness-ablaze/086-189-larvitar.md` — single bullet ~210 words; same treatment.
- `cards/pokemon/darkness-ablaze/092-189-solrock.md` — ~190 words; same treatment.

**Opener-convention retrofits** (Connections bullets whose opener doesn't match the canonical opener list):

- None surfaced as outright violations in the sampled cards, but the BFZ-triangle openers ("Battle for Zendikar triple-thesis cycle, stewardship-verb anchor") are now codified as the canonical form for triangle/cycle anchors. Future cycle work uses this opener verbatim.

**Mirror-completeness retrofits** (cards whose Connections sections are orphaned mirrors — bullet on one side, missing on the other):

- `cards/magic-the-gathering/zendikar-rising/63-jace-mirror-mage.md` — has an empty `## Connections` section (header only, no bullets). Either populate or remove the header. Removing is preferred when no edge is currently warranted; a present-but-empty section is technical debt.

Total retrofit surface: ~15 cards. Recommend Edgelord-enlightened passes targeting one retrofit-cluster per wave (story-spotlight cluster, Pokemon evolution-mirror cluster, etc.) rather than a single mass-retrofit run.

## See also

- `bbl-edgelord` agent spec — the agent that writes `## Connections` sections
- `cards/_hubs/_triple-thesis.md` — meta-hub whose triangle structure produces the triangle-shaped Connections case
- memory `bbl-edgelord-target-enriched-not-random.md` — Edgelord wave-targeting rule
- memory `bbl-museum-curation-framing.md` — refusal-with-receipts as the disposition behind the standard
