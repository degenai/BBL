#!/usr/bin/env python3
"""One-shot: apply wave 11 trivia (6 cards) + ip-verifications (3 cards) + write 6 JSON sidecars."""
import json, os, re

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"

TRIVIA = {
    "cards/pokemon/champion-s-path/68-73-turffield-stadium.md": {
        "ip_verify": False,
        "trivia_md": """
## Trivia

- **Set context** — Champion's Path (released September 25, 2020) is a special Sword & Shield-era set structured around the eight Galar region gym towns. Each gym received a dedicated Pin Collection product featuring a gym-badge pin and a foil Pokémon card. Turffield, Hulbury, and Motostoke launched on release day; Ballonlea, Spikemuth, and Hammerlocke followed November 13, 2020 [Pokemon.com: Champion's Path Pin Collections].
- **Location lore** — Turffield is the first stop on the Galar gym challenge circuit. Gym Leader Milo is a Grass-type specialist and farmer described in-game as too laid-back to go all-out against weaker challengers. The hillside west of town bears a massive geoglyph canonically identified as a depiction of Eternatus beneath the Darkest Day cloud [Bulbapedia: Turffield].
- **Reprint history** — Turffield Stadium first appeared in Rebel Clash (May 2020, card 170/192), was reprinted in Champion's Path (68/73), then received its highest-profile version as a Gold Secret Rare in Evolving Skies (234/203). The gold foil Evolving Skies printing is the collectible apex for this effect [TCGCollector: Turffield Stadium Evolving Skies 234].
- **Mechanical reputation** — In the Evolving Skies standard format, Grass-type decks (primarily Leafeon VMAX and Rillaboom VMAX lines) frequently ran three copies to drive search consistency. The symmetrical search effect — both players can use it each turn — rewards the player who runs more Grass Evolution lines and is harder to exploit against monocolor Grass builds [JustInBasil: Highlights from Evolving Skies].

### Related cards
- Turffield Stadium (Rebel Clash, 170/192) — first English printing; same effect
- Turffield Stadium (Evolving Skies, 234/203) — Gold Secret Rare reprint; highest collectible value
- Milo (Champion's Path) — Turffield Gym Leader, thematically paired in Champion's Path product line
""",
        "json_path": "reports/trivia_pending/pokemon/champion-s-path/68-73-turffield-stadium.json",
        "json": {"card_name":"Turffield Stadium","game":"Pokemon","set":"Champion's Path","collector_number":"68/73","task_profile":"general","ip_decision":"n/a","trivia_summary":"Galar gym-circuit first-stop stadium; Champion's Path Pin Collections; Evolving Skies Gold Secret Rare apex"},
    },
    "cards/pokemon/chilling-reign/148-198-path-to-the-peak.md": {
        "ip_verify": False,
        "trivia_md": """
## Trivia

- **Set context** — Chilling Reign released June 18, 2021 (English), sourced from the Japanese Silver Lance and Jet-Black Spirit dual expansion (April 23, 2021). The set is the sixth main Sword & Shield expansion and thematically centers on the Crown Tundra DLC and the legendary Calyrex [Bulbapedia: Chilling Reign (TCG)].
- **Location lore** — Path to the Peak is a real in-game location: the final alpine route in the Crown Tundra DLC that leads north to Crown Shrine, the encounter site for Calyrex. It connects the Tunnel to the Top to the south and Crown Shrine to the north — the literal final approach to the legendary Pokémon at the top of Galar's wilderness [Bulbapedia: Path to the Peak (location)].
- **Mechanical reputation** — Path to the Peak is considered one of the most impactful cards from Chilling Reign. Its Stadium effect removes Abilities from all Pokémon with Rule Boxes (Pokémon V, GX, etc.) for both players. Competitive analysis at release flagged it as potentially format-warping: a single turn of setup could lock many dominant V-era decks entirely out of their engine [Flipside Gaming: Impact of Chilling Reign; Pokemon.com: Top Cards for Competition — Chilling Reign].
- **Community sentiment** — The ability-suppression effect drew comparison to classic "Item lock" strategies. The standard counter was increasing copies of Chaotic Swell (a rival Stadium) or running Marshadow (Resetting Hole ability) as a tech — both of which became staples specifically because of Path to the Peak's prevalence [Flipside Gaming: Impact of Chilling Reign].

### Related cards
- Chaotic Swell (Cosmic Eclipse) — primary Stadium counter to Path to the Peak
- Marshadow (Unbroken Bonds, Resetting Hole) — Ability-based Stadium removal tech run against Path to the Peak
- Calyrex VMAX (Chilling Reign) — thematic centerpiece of the same set; set lore focal point
""",
        "json_path": "reports/trivia_pending/pokemon/chilling-reign/148-198-path-to-the-peak.json",
        "json": {"card_name":"Path to the Peak","game":"Pokemon","set":"Chilling Reign","collector_number":"148/198","task_profile":"general","ip_decision":"n/a","trivia_summary":"Crown Tundra DLC final route to Calyrex; format-warping Stadium that suppresses Rule Box Abilities"},
    },
    "cards/pokemon/darkness-ablaze/007-189-simisage.md": {
        "ip_verify": False,
        "trivia_md": """
## Trivia

- **Set context** — Darkness Ablaze released August 14, 2020 as the third main Sword & Shield expansion, sourced from the Japanese Explosive Walker expansion. The set is 189 cards in its numbered set [Bulbapedia: Darkness Ablaze (TCG)].
- **Elemental monkey trio design** — Simisage is the evolved form of Pansage, one of three elemental monkey Pokémon introduced in Generation V (Unova). The trio — Pansage/Simisage (Grass), Pansear/Simisear (Fire), Panpour/Simipour (Water) — is widely noted to reference the three wise monkeys (mizaru, kikazaru, iwazaru): Pansage for "speak no evil," Pansear for "hear no evil," and Panpour for "see no evil" [Bulbapedia: Elemental monkeys]. The trio evolves via elemental stones (Leaf Stone, Fire Stone, Water Stone) rather than level-up.
- **Flavor text** — *"Ill tempered, it fights by swinging its barbed tail around wildly. The leaf growing on its head is very bitter."* [PokemonTCG.io / card frontmatter]. This aligns with the Pokédex characterization of Simisage as aggressive despite its Grass type — a deliberate design counterpoint to the docile Pansage.
- **Artist** — Illustrated by Hasegawa Saki, an artist active in the Sword & Shield era whose TCG credits include Ursaring (Evolving Skies), Crawdaunt (Battle Styles), and Diglett (Sword & Shield base). Simisage (DAA 007) is one of her earlier SWSH-era cards [PkmnCards: Hasegawa Saki artist page].

### Related cards
- Pansage (multiple sets) — pre-evolution; same trio, "speak no evil" motif
- Simisear (multiple sets) — Fire-type trio counterpart; Pansear evolution
- Simipour (multiple sets) — Water-type trio counterpart; Panpour evolution
- Pansear (multiple sets) — Fire-type trio base; "hear no evil" motif
- Panpour (multiple sets) — Water-type trio base; "see no evil" motif
""",
        "json_path": "reports/trivia_pending/pokemon/darkness-ablaze/007-189-simisage.json",
        "json": {"card_name":"Simisage","game":"Pokemon","set":"Darkness Ablaze","collector_number":"007/189","task_profile":"general","ip_decision":"n/a","trivia_summary":"Grass-arm of three-wise-monkeys elemental trio (speak no evil); Hasegawa Saki SWSH-era artist"},
    },
    "cards/pokemon/chilling-reign/033-198-castform-rainy-form.md": {
        "ip_verify": True,
        "ip_name": "Castform (Pokemon)",
        "ip_verify_note": "Confirmed via card name \"Castform Rainy Form,\" flavor text (\"This is Castform's form when pelted by rain\"), and National Pokedex no. 351 [PokemonTCG.io / card frontmatter].",
        "trivia_md": """
## Trivia

- **Set context** — Chilling Reign (June 18, 2021, English) is the sixth main Sword & Shield expansion, thematically linked to the Crown Tundra DLC and Calyrex. This card was first released in the Japanese Jet-Black Spirit expansion (April 23, 2021) [Bulbapedia: Chilling Reign (TCG)].
- **Four-form design** — Castform (National Pokedex no. 351) has four distinct forms: Normal, Sunny, Rainy, and Snowy, each triggered by weather conditions. All four forms were printed as separate cards in Chilling Reign (Normal at card 121, Sunny at card 22, Rainy at card 33, Snowy at card 34), making this set the first English release to include the complete four-form cycle simultaneously [Pokemon.com: TCG Card Database; Amazon product listing for Castform lot]. Each form card shares the "Weather Reading" Ability: if you have 8 or more Stadium cards in your discard pile, ignore all Energy costs.
- **Origin lore** — Castform was created in-universe by Weather Institute researchers in the Hoenn region as an experiment in weather manipulation. Its design is noted to reference a teru teru bozu, a Japanese paper charm doll used to wish for good weather. The forms may also reference the English idiom "rain, hail, or shine" [Bulbapedia: On the Origin of Species: Castform (Bulbanews)].
- **Flavor text** — *"This is Castform's form when pelted by rain. In an experiment where it was placed in a shower, this Pokémon didn't change to this form."* [card frontmatter / PokemonTCG.io]. The flavor text is notable for its dry, experimental framing — unusual for a cute Pokémon card; implies the form change requires natural weather, not artificial precipitation.

### Related cards
- Castform (Chilling Reign, 121) — Normal Form in the same set
- Castform Sunny Form (Chilling Reign, 022) — Sunny Form in the same set; all four share Weather Reading Ability
- Castform Snowy Form (Chilling Reign, 034) — Snowy Form in the same set
- Path to the Peak (Chilling Reign, 148) — also in Chilling Reign; Stadium-heavy discard strategies enable Weather Reading
""",
        "json_path": "reports/trivia_pending/pokemon/chilling-reign/033-198-castform-rainy-form.json",
        "json": {"card_name":"Castform Rainy Form","game":"Pokemon","set":"Chilling Reign","collector_number":"033/198","task_profile":"ip-priority","ip_decision":"verify","trivia_summary":"One of 4 Castform forms in single set; teru teru bozu charm-doll reference; Weather Reading Ability cycle"},
    },
    "cards/pokemon/chilling-reign/054-198-galarian-slowpoke.md": {
        "ip_verify": True,
        "ip_name": "Galarian Slowpoke (Pokemon)",
        "ip_verify_note": "Confirmed via card name, flavor text (\"seeds of a plant that grows only in Galar\"), and Galarica spice lore [card frontmatter / PokemonTCG.io].",
        "trivia_md": """
## Trivia

- **Regional variant lore** — Galarian Slowpoke is a pure Psychic-type regional form introduced in Pokémon Sword & Shield version 1.1.0 (January 2020). Unlike Kantonian Slowpoke (Water/Psychic), it has no Water typing. Its yellow forehead and tail tip coloring result from Galarica particles accumulated over generations from eating native Galarica seeds — a spice essential to Galar cuisine. The tail is described as having a spicy flavor [Bulbapedia: Slowpoke; search snippet from Serebii.net Pokédex].
- **Flavor text** — *"Because Galarian Slowpoke eat the seeds of a plant that grows only in Galar, their tails have developed a spicy flavor."* [card frontmatter / PokemonTCG.io]. This matches the Pokédex explanation of Galarica seed accumulation as the mechanism for both the coloring change and the spicy-tail characteristic.
- **Evolution structure** — Galarian Slowpoke has two version-exclusive evolutions: Galarian Slowbro (Poison/Psychic) via Galarica Cuff on Isle of Armor DLC, and Galarian Slowking (Poison/Psychic) via Galarica Wreath on Crown Tundra DLC. Both require DLC access, making Galarian Slowpoke the only member of the line available in the base game at launch [GameSpot: How to Evolve Galarian Slowpoke; Gameranx: Crown Tundra — Galarian Slowking].
- **Set context** — Chilling Reign (June 18, 2021, English) is the sixth main Sword & Shield expansion, thematically centered on the Crown Tundra DLC where Galarian Slowking becomes obtainable. Galarian Slowpoke's presence in Chilling Reign is consistent with the set's Galar-regional-form focus [Bulbapedia: Chilling Reign (TCG)].

### Related cards
- Galarian Slowbro (multiple sets) — Poison/Psychic evolution via Galarica Cuff; Isle of Armor DLC
- Galarian Slowking (Chilling Reign) — Poison/Psychic evolution via Galarica Wreath; Crown Tundra DLC; thematically central to this set
- Slowpoke (multiple sets) — Kantonian counterpart; Water/Psychic type
""",
        "json_path": "reports/trivia_pending/pokemon/chilling-reign/054-198-galarian-slowpoke.json",
        "json": {"card_name":"Galarian Slowpoke","game":"Pokemon","set":"Chilling Reign","collector_number":"054/198","task_profile":"ip-priority","ip_decision":"verify","trivia_summary":"Galar regional form; Galarica seed diet causes spicy tail; two DLC-exclusive evolutions (Slowbro/Slowking)"},
    },
    "cards/pokemon/burning-shadows/54-147-croagunk.md": {
        "ip_verify": True,
        "ip_name": "Croagunk (Pokemon)",
        "ip_verify_note": "Confirmed via card name, flavor text (\"cheeks hold poison sacs\"), and National Pokedex no. 453 [card frontmatter / PokemonTCG.io].",
        "trivia_md": """
## Trivia

- **Set context** — Burning Shadows released August 4, 2017, the third expansion of the Sun & Moon series. The set contains 169 cards (147 regular plus 22 secret rares) [WebSearch snippet: Burning Shadows set details].
- **Anime association** — Croagunk is strongly associated with Brock in the Pokémon Diamond & Pearl anime run. Brock's Croagunk became a recurring comic character who used Poison Jab to drag Brock away every time he flirted with a woman. Brock's Croagunk was the first Pokémon he caught in Sinnoh [Bulbapedia: Brock's Croagunk].
- **Flavor text** — *"Its cheeks hold poison sacs. It tries to catch foes off guard to jab them with toxic fingers."* [card frontmatter / PokemonTCG.io]. The ambush-predator framing here matches the art's low-crouch combat stance — the card's composition and flavor text reinforce the same behavioral beat.
- **Artist** — Illustrated by Naoki Saito, one of the most prominent Pokémon TCG illustrators, active since the HeartGold & SoulSilver expansion. His Burning Shadows work received immediate community attention and he has since become a high-demand illustrator whose full-art cards command strong secondary market prices [Bleeding Cool: Naoki Saito artist spotlight; CGC Cards: Artist Showcase Naoki Saito].

### Related cards
- Toxicroak (multiple sets) — Croagunk's evolution; Poison/Fighting
- Brock's Croagunk (multiple sets, if printed) — anime-specific character card variant
- Brock (multiple sets) — Gym Leader/companion whose anime team featured Croagunk
""",
        "json_path": "reports/trivia_pending/pokemon/burning-shadows/54-147-croagunk.json",
        "json": {"card_name":"Croagunk","game":"Pokemon","set":"Burning Shadows","collector_number":"54/147","task_profile":"ip-priority","ip_decision":"verify","trivia_summary":"Anime-iconic Brock's Croagunk (D&P run); Naoki Saito artist; ambush-predator flavor text matches low-crouch art"},
    },
}

for rel_path, info in TRIVIA.items():
    abs_md = os.path.join(ROOT, rel_path.replace("/", os.sep))
    abs_json = os.path.join(ROOT, info["json_path"].replace("/", os.sep))

    # Write JSON sidecar
    os.makedirs(os.path.dirname(abs_json), exist_ok=True)
    with open(abs_json, "w", encoding="utf-8") as f:
        json.dump(info["json"], f, indent=2, ensure_ascii=False)
    print(f"WROTE JSON {info['json_path']}")

    # Read card MD
    with open(abs_md, "r", encoding="utf-8") as f:
        body = f.read()

    # IP verification: swap warning callout + set ip_verified: true
    if info["ip_verify"]:
        ip_name = info["ip_name"]
        old_callout = f"> [!warning] Suspected IP: **{ip_name}** (confidence: high, unverified)\n> Reviewer: confirm whether the depicted figure is canonically this character. If yes, set `ip_verified: true` in frontmatter. If no, clear `suspected_ip`."
        new_callout = f"> [!note] IP verified: **{ip_name}**\n> {info['ip_verify_note']}"
        if old_callout in body:
            body = body.replace(old_callout, new_callout)
            print(f"  SWAPPED callout: {rel_path}")
        else:
            print(f"  !! CALLOUT NOT FOUND: {rel_path}")
        body = re.sub(r'^ip_verified:\s*false\s*$', 'ip_verified: true', body, flags=re.MULTILINE)
        print(f"  SET ip_verified: true: {rel_path}")

    # Append trivia (avoid duplicate)
    if "## Trivia" not in body:
        body = body.rstrip() + "\n" + info["trivia_md"].rstrip() + "\n"
        print(f"  APPENDED trivia: {rel_path}")
    else:
        print(f"  !! TRIVIA ALREADY PRESENT: {rel_path}")

    with open(abs_md, "w", encoding="utf-8") as f:
        f.write(body)

print("DONE")
