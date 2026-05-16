#!/usr/bin/env python3
"""Apply wave 12 trivia (6 cards) + 6 IP-verifications + 6 JSON sidecars."""
import json, os, re

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"

CARDS = {
    "cards/pokemon/vivid-voltage/154-185-leon--holofoil.md": {
        "ip_name": "Leon (Pokémon Sword and Shield)",
        "ip_verify_note": "Confirmed via Bulbapedia character page, Pokémon.com official Galar character profile, and Sword & Shield primary game canon. Figure's purple cape, wide-brimmed cap, dark skin, and champion's stadium pose match Leon's canonical visual signature exactly.",
        "trivia_md": """
## Trivia

- **Set context** — Vivid Voltage (SWSH4) was released November 13, 2020 and contains 185 cards plus secret rares. It is the fourth main expansion of the Sword & Shield series and was the first set to introduce Amazing Rare cards to the English game [Bulbapedia: Vivid Voltage (TCG)].
- **IP verification** — Leon is the undefeated Galar Champion and older brother of Hop, having won his first-ever Gym Challenge at age 10 without a single defeat, endorsed by Chairman Rose of Macro Cosmos. He is recognizable by his iconic flowing cape and wide-brimmed cap [Bulbapedia: Leon].
- **Galar Gym Challenge cycle** — This card is the apex of the Vivid Voltage 5-Supporter Galar Gym Leader cycle: Allister (no. 146), Bea (no. 147), Leon (no. 154), Nessa (no. 157), and Opal (no. 158), all illustrated by Ken Sugimori. Leon as Champion is the institutional endpoint of the same apparatus these five Gym Leaders feed [Bulbapedia: Vivid Voltage (TCG); pokemon.com TCG Database swsh4/154].
- **Mechanical note** — Leon's Supporter effect adds 30 damage to your Pokemon's attacks for one turn (before Weakness/Resistance). At release this was flagged as a "1-2 of" playable in ADP, Eternatus VMAX, and PikaRom decks; it is currently not legal in Standard (D Regulation Mark rotated out) but remains legal in Expanded [Limitless TCG VIV/154].
- **Corporate-spectacle anchor** — Leon's in-game ascent was directly sponsored by Chairman Rose of the Macro Cosmos conglomerate. Bulbapedia confirms Rose's endorsement letter launched Leon's Championship run — the same conglomerate that organized the Galar League as a televised stadium-cup spectacle. The Champion-Cup format at Wyndon Stadium exists specifically to make Dynamax battles broadcastable at scale. This card depicts the apex product of Macro Cosmos's sports-spectacle apparatus [Bulbapedia: Leon; Bulbapedia: Galar League].

### Related cards
- Bea (Vivid Voltage, no. 147) — same Galar Gym Leader Supporter cycle, Sword-version counterpart to Allister at Stow-on-Side
- Nessa (Vivid Voltage, no. 157) — same Vivid Voltage Galar cycle, Hulbury Water-type Gym Leader
- Opal (Vivid Voltage, no. 158) — same Vivid Voltage Galar cycle, Ballonlea Fairy-type Gym Leader
- Allister (Vivid Voltage, no. 146) — same cycle; corpus already enriched, wired to galar-gym-challenge
- Chairman Rose / Macro Cosmos — no TCG card in current corpus; Leon's canonical endorser and the Galar League's corporate operator
""",
        "json_path": "reports/trivia_pending/pokemon/vivid-voltage/154-185-leon--holofoil.json",
        "json_summary": "Galar champion completing the 5-Supporter Vivid Voltage cycle; Macro Cosmos / Chairman Rose corporate-spectacle apex",
    },
    "cards/pokemon/cosmic-eclipse/208-236-will.md": {
        "ip_name": "Will (Pokémon Gold and Silver)",
        "ip_verify_note": "Confirmed via Bulbapedia character page (Will), Bulbapedia card page (Will — Cosmic Eclipse 208), and pokemon.com TCG Database (sm12/208). Will's domino mask, flowing light-colored hair, and theatrical one-hand-raised pose are his canonical visual signature across game and card appearances.",
        "trivia_md": """
## Trivia

- **Set context** — Cosmic Eclipse (SM12) was released November 1, 2019 in English, making it the twelfth and final main expansion of the Sun & Moon series. The set introduced TAG TEAM Supporter cards (pairs of two trainers on one card) for the first time in the English game [Bulbapedia: Cosmic Eclipse (TCG)].
- **IP verification** — Will is the first member of the Johto Elite Four in Pokemon Gold and Silver, specializing in Psychic-type Pokemon. He wears a domino mask covering the upper half of his face and has distinctive light-colored hair across his various game appearances. Bulbapedia's card page confirms this card's illustrated figure is Will, with artwork by Ken Sugimori [Bulbapedia: Will (Cosmic Eclipse 208)].
- **Japanese origin** — Will's Cosmic Eclipse card was first released in the Japanese Dream League subset (September 6, 2019) before its English debut in Cosmic Eclipse on November 1, 2019. Dream League was the Japanese set that introduced the Johto Elite Four as individual Supporter cards [Bulbapedia: Will (Cosmic Eclipse 208); loosepacks.com Japanese Dream League].
- **Johto Elite Four cohort** — Will's four Johto Elite Four peers are Will (Psychic), Koga (Poison, returning from Kanto gym leader status in Gen 1/2), Bruno (Fighting), and Karen (Dark), with Lance as Champion. If the corpus acquires Karen, Koga, or Bruno cards from SM-era sets, a Johto Elite Four cohort node would be viable [Bulbapedia: Elite Four; Serebii: Gold & Silver Elite Four].
- **Mechanical note** — Will's effect lets the player choose heads or tails for the first coin flip in any chain of coin flips that turn. This removes the single highest-variance outcome from multi-flip attacks, providing a soft luck-manipulation effect [pokemon.com TCG Database sm12/208].

### Related cards
- Karen (Cosmic Eclipse) — Johto Elite Four Dark-type member; same Dream League Japanese origin; potential future cohort node peer
- Koga (any set featuring Johto/Kanto crossover content) — Johto Elite Four Poison-type; Gen 1 Fuchsia Gym Leader elevated to E4
- Bruno (any set) — Johto Elite Four Fighting-type member
- Lance (Dragon-type Champion) — Johto Champion who appears on various sets; the apex of Will's elite gauntlet
""",
        "json_path": "reports/trivia_pending/pokemon/cosmic-eclipse/208-236-will.json",
        "json_summary": "First Johto Elite Four member in corpus; Psychic-type masked trainer; Dream League Japanese origin; cohort-node future trigger when ≥2 more land",
    },
    "cards/pokemon/burning-shadows/40-147-pikachu.md": {
        "ip_name": "Pikachu (Pokémon)",
        "ip_verify_note": "Confirmed via Bulbapedia, Pokemon.com, and Serebii. Pikachu is National Pokedex no. 025, the franchise mascot since 1996, with an unambiguous visual signature (yellow body, red cheek pouches, lightning-bolt tail). This card's depicted figure matches exactly.",
        "trivia_md": """
## Trivia

- **Set context** — Burning Shadows (SM3) was released August 4, 2017 in English as the third main expansion of the Sun & Moon series. The set's thematic focus is Ho-Oh and Necrozma, framed by Team Skull's presence in the Alola region: "Fiery Battles and Deep Shadows!" The set contains 169 cards including secret rares [Bulbapedia: Burning Shadows (TCG)].
- **IP verification** — Pikachu is National Pokedex no. 025, an Electric-type Mouse Pokemon introduced in Generation I (Pokemon Red and Blue, 1996). It has served as the franchise mascot since the original games and appears in virtually every Pokemon property [Bulbapedia: Pikachu (Pokemon); pokemon.com Pokedex].
- **Flavor text — labor-extraction subtext** — The flavor text on this card reads: *"A plan was recently announced to gather many Pikachu and make an electric power plant."* This language is strikingly industrial: Pikachu are treated not as individual creatures but as an aggregate energy source to be harvested at scale. The flavor text is sourced directly from the card [PokemonTCG card frontmatter; pokemasters.net, tcgcollector.com]. This framing — many Pikachu, one power plant — recurs across several Pokedex entries in the mainline games and is the most explicit resource-extraction register in any Pikachu TCG card in the current corpus.
- **Artist** — This card was illustrated by Saya Tsuruta, a TCG illustrator with multiple Pikachu-family card credits. The card art shows Pikachu mid-leap against a radiating lightning field — a kinetic, void-background composition typical of Tsuruta's approach to Electric-type creatures [card frontmatter artist field].
- **Franchise presence** — Pikachu has appeared on more Pokemon TCG cards than any other species. Its iconic status means Pikachu cards trend toward collector demand above their in-game utility: the Burning Shadows common Pikachu (no. 40/147) is valued above most commons in the set at approximately $0.70 market price despite having no competitive-tier attack output [card frontmatter market_price field; TCGPlayer market data].

### Related cards
- Raichu (any set) — Pikachu's Stage 1 evolution; the power-scale escalation of the same labor-energy framing
- Pikachu and Zekrom-GX (Team Up, SM9) — TAG TEAM partner card representing the industrial-electricity angle at GX tier
- Dedenne-GX (Unbroken Bonds) — electric rodent parallel; broadly treated as a mechanical successor to Pikachu in Lightning-type decks
""",
        "json_path": "reports/trivia_pending/pokemon/burning-shadows/40-147-pikachu.json",
        "json_summary": "Labor-extraction flavor text 'gather many Pikachu and make an electric power plant'; corpus's strongest Pikachu labor-angle anchor",
    },
    "cards/pokemon/burning-shadows/12-147-pansage.md": {
        "ip_name": "Pansage (Pokemon)",
        "ip_verify_note": "Confirmed via Bulbapedia character page (Pansage — Pokemon), Bulbapedia card page (Pansage — Burning Shadows 12), and the Elemental monkeys group article. Pansage's distinctive cream body, bipedal stance, and leafy head tuft are unambiguous species identifiers.",
        "trivia_md": """
## Trivia

- **Set context** — Burning Shadows (SM3) was released August 4, 2017 as the third main expansion of the Sun & Moon series. Despite being an Alola-era set, it includes a range of Unova-origin Pokemon like Pansage — the Sun & Moon series drew broadly from the National Pokedex rather than restricting to Generation VII species [Bulbapedia: Burning Shadows (TCG)].
- **Three wise monkeys design origin** — Pansage and its Elemental Monkey trio companions (Pansear and Panpour) are based on the Japanese proverb of the three wise monkeys: "see no evil, hear no evil, speak no evil." In the official Ken Sugimori pose art, **Pansage represents "speak no evil"** (Iwazaru — covering the mouth), Pansear represents "hear no evil" (Kikazaru — covering the ears), and Panpour represents "see no evil" (Mizaru — covering the eyes). This attribution is documented on Bulbapedia's Elemental monkeys group page [Bulbapedia: Elemental monkeys].
- **Flavor text — healing gesture** — The flavor text reads: *"It shares the leaf on its head with weary-looking Pokémon. These leaves are known to relieve stress."* This maps Pansage's "speak no evil" design register — docility, sharing, soothing — directly onto a healing mechanic: the leaf-sharing gesture softens the wise-monkey archetype into an act of mutual care [card frontmatter flavor_text field].
- **Artist** — This card was illustrated by Shigenori Negishi, a TCG illustrator based in Chigasaki City with 155+ Pokemon TCG card credits. Negishi is documented on Bulbapedia's illustrator page and the artofpkm.com illustrator directory [Bulbapedia: Shigenori Negishi; artofpkm.com/illustrators/65].
- **Elemental Monkey trio cohort status** — Pansage, Pansear (corpus pending), and Panpour are Gen 5 (Unova) Pokemon introduced in Pokemon Black and White. Simisage, Simisear (Darkness Ablaze 027, corpus: 2 copies), and Simipour are their evolutions via elemental stones. With Pansage (BUS-12) and Simisear (DAA-027) both now in corpus, and the trio anchored at [[elemental-monkey-trio]], the corpus holds 2 of 6 trio members; Pansear, Panpour, Simisage, and Simipour are out-of-corpus [Bulbapedia: Elemental monkeys; card frontmatter characters field].

### Related cards
- Simisage (any set) — Pansage's evolution via Leaf Stone; same "speak no evil" design register at evolved tier
- Pansear (any set) — Elemental Monkey trio companion, "hear no evil," fire-type
- Panpour (any set) — Elemental Monkey trio companion, "see no evil," water-type
- Simisear (Darkness Ablaze, no. 027/189) — already in corpus; fire-type evolved member of same trio node
""",
        "json_path": "reports/trivia_pending/pokemon/burning-shadows/12-147-pansage.json",
        "json_summary": "Grass-arm 'speak no evil' base form of elemental-monkey-trio; Shigenori Negishi artist; leaf-sharing-relieves-stress healing flavor",
    },
    "cards/pokemon/darkness-ablaze/027-189-simisear.md": {
        "ip_name": "Simisear (Pokemon)",
        "ip_verify_note": "Confirmed via Bulbapedia (Elemental monkeys), Bulbapedia card page (Simisear — Darkness Ablaze 027), and pokemon.com TCG Database (swsh3/27). Simisear's flame tufts on head and tail, cream face, and reddish-orange body are unambiguous species identifiers.",
        "trivia_md": """
## Trivia

- **Set context** — Darkness Ablaze (SWSH3) was released August 14, 2020 as the third main expansion of the Sword & Shield series. The set contains 201 cards and is thematically organized around Eternatus — "A Brilliant Flame on the Darkest Day!" Despite the SWSH-era setting, Simisear is a Gen 5 (Unova) Pokemon included as part of the set's broad National Pokedex draw [Bulbapedia: Darkness Ablaze (TCG)].
- **Three wise monkeys design chain — hear no evil** — Simisear is the evolution of Pansear, the fire-type member of the Elemental Monkey trio. Per Bulbapedia's Elemental monkeys group page, Pansear (and by extension Simisear) corresponds to "hear no evil" (Kikazaru) in the three wise monkeys proverb design chain. The "hear no evil" position maps onto Simisear's large, prominent ears and its characterization as an excitable creature that "gets hot" when excited [Bulbapedia: Elemental monkeys; Bulbapedia: Pansear (Pokemon)].
- **Flavor text — sweets and excitement** — The flavor text reads: *"When it gets excited, embers rise from its head and tail and it gets hot. For some reason, it loves sweets."* The "loves sweets" detail is widely noted in Pokemon fan communities as an oddity — no in-game explanation is provided for the sweet tooth, making it one of those Pokedex entries that functions as pure character texture [card frontmatter flavor_text field].
- **Artist** — This card was illustrated by the artist known as "0313," a TCG illustrator whose pseudonymous credit appears on multiple Pokemon TCG cards. The cozy, warm indoor setting on this card — soft reds and oranges against a light background — represents 0313's tendency toward intimate, domestic framing for creature subjects [card frontmatter artist field; tcgcollector.com: Simisear Darkness Ablaze 027/189].
- **Elemental Monkey trio corpus status** — Simisear is a Stage 1 evolution (from Pansear via Fire Stone). With Pansage (BUS-12) and Simisear (DAA-027) in corpus and both wired to [[elemental-monkey-trio]], the corpus now holds the grass unevolved and fire evolved members of the trio. Pansear (fire unevolved), Panpour (water unevolved), Simisage (grass evolved), and Simipour (water evolved) remain out-of-corpus [card frontmatter characters field].

### Related cards
- Pansear (any set) — Simisear's pre-evolution; fire unevolved member of the Elemental Monkey trio
- Simisage (any set) — grass evolved member of the trio; Pansage's evolution
- Simipour (any set) — water evolved member of the trio; Panpour's evolution
- Pansage (Burning Shadows, no. 12/147) — already in corpus; grass unevolved member of same trio node
""",
        "json_path": "reports/trivia_pending/pokemon/darkness-ablaze/027-189-simisear.json",
        "json_summary": "Fire-arm 'hear no evil' evolved form of elemental-monkey-trio; '0313' artist; loves-sweets flavor",
    },
    "cards/pokemon/burning-shadows/19-147-charmeleon.md": {
        "ip_name": "Charmeleon (Pokémon)",
        "ip_verify_note": "Confirmed via Bulbapedia, Serebii, and pokemon.com Pokedex. Charmeleon is National Pokedex no. 005, Stage 1 of the Charmander-Charmeleon-Charizard line. Orange body, cream underbelly, flame-tipped tail, and bipedal clawed stance are unambiguous species identifiers.",
        "trivia_md": """
## Trivia

- **Set context** — Burning Shadows (SM3) was released August 4, 2017 as the third main expansion of the Sun & Moon series. The set's thematic focus is Ho-Oh and Necrozma in the Alola setting; Charizard-GX was one of the set's headlining GX cards, making this Charmeleon (no. 19/147) a pre-evolution of the set's marquee GX Pokemon [Bulbapedia: Burning Shadows (TCG)].
- **IP verification** — Charmeleon is National Pokedex no. 005, a Fire-type Stage 1 Pokemon in the Charmander evolutionary line. It evolves from Charmander at level 16 and into Charizard at level 36. Charizard gained the additional Flying type on final evolution, making the line one of only two original Kanto starters to change type mid-evolution [Serebii: Pokedex 005; pokemondb.net: Charmeleon].
- **Flavor text** — The flavor text on this card reads: *"It lashes about with its tail to knock down its foe. It then tears up the fallen opponent with sharp claws."* This is consistent with Charmeleon's in-game characterization as aggressive and combative — Bulbapedia's Charmeleon page notes the species "becomes uncontrollable" during battle and will scratch even its own trainer if it is displeased [card frontmatter flavor_text field; Bulbapedia: Charmeleon (Pokemon)].
- **Artist** — This card was illustrated by kawayoo, a TCG illustrator credited on multiple Pokemon cards. The geometric teal-and-blue-green angular background on this card is a recognizable kawayoo compositional choice, contrasting the warm orange of the creature against cool geometric planes [card frontmatter artist field].
- **Charizard-line cohort threshold** — The corpus currently holds 2 Charmeleon cards: Burning Shadows no. 19/147 and Vivid Voltage no. 024/185. The Mr. Nodeley threshold for a Charizard-line cohort node is 3 cards. One additional Charizard-line acquisition (Charmander, Charmeleon, or Charizard from any set) would trigger the cohort node [TCGCollector: Charmeleon VIV-024/185; Serebii TCG Cardex 005].

### Related cards
- Charmeleon (Vivid Voltage, no. 024/185) — second Charmeleon in corpus; different set, same evolutionary stage; illustrated by Satoshi Nakai
- Charmander (any set) — Charmeleon's pre-evolution; National Pokedex no. 004
- Charizard-GX (Burning Shadows) — same set's headlining GX Pokemon; the evolutionary apex of this card's line
- Charizard (Vivid Voltage, no. 025/185) — available in the same set as the second Charmeleon; would complete a within-VIV evolutionary sequence
""",
        "json_path": "reports/trivia_pending/pokemon/burning-shadows/19-147-charmeleon.json",
        "json_summary": "Charizard line middle stage; 2/3 cohort-node threshold; kawayoo geometric-background artist; combative flavor text",
    },
}

for rel_path, info in CARDS.items():
    abs_md = os.path.join(ROOT, rel_path.replace("/", os.sep))
    abs_json = os.path.join(ROOT, info["json_path"].replace("/", os.sep))

    # Write JSON sidecar
    os.makedirs(os.path.dirname(abs_json), exist_ok=True)
    sidecar = {
        "card_path": rel_path,
        "ip_name": info["ip_name"],
        "ip_verified": True,
        "summary": info["json_summary"],
    }
    with open(abs_json, "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=2, ensure_ascii=False)
    print(f"WROTE JSON {info['json_path']}")

    # Read card MD
    with open(abs_md, "r", encoding="utf-8") as f:
        body = f.read()

    # Set ip_verified: true
    body = re.sub(r'^ip_verified:\s*false\s*$', 'ip_verified: true', body, flags=re.MULTILINE)

    # Swap warning callout for verified note
    ip_name = info["ip_name"]
    old_callout = f"> [!warning] Suspected IP: **{ip_name}** (confidence: high, unverified)\n> Reviewer: confirm whether the depicted figure is canonically this character. If yes, set `ip_verified: true` in frontmatter. If no, clear `suspected_ip`."
    new_callout = f"> [!note] IP verified: **{ip_name}**\n> {info['ip_verify_note']}"
    if old_callout in body:
        body = body.replace(old_callout, new_callout)
        print(f"  SWAPPED callout: {rel_path}")
    else:
        print(f"  !! CALLOUT NOT FOUND: {rel_path}")

    # Swap inline metadata line (if present)
    inline_old = f"**Suspected IP:** {ip_name} (confidence: high, verified: False)"
    inline_new = f"**Verified IP:** {ip_name} (confidence: high)"
    if inline_old in body:
        body = body.replace(inline_old, inline_new)
        print(f"  SWAPPED inline line: {rel_path}")

    # Append trivia
    if "## Trivia" not in body:
        body = body.rstrip() + "\n" + info["trivia_md"].rstrip() + "\n"
        print(f"  APPENDED trivia: {rel_path}")
    else:
        print(f"  !! TRIVIA ALREADY PRESENT: {rel_path}")

    with open(abs_md, "w", encoding="utf-8") as f:
        f.write(body)

print("DONE")
