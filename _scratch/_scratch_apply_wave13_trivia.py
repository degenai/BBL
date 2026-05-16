#!/usr/bin/env python3
"""Apply wave 13 trivia (6 cards) + 5 IP-verifications (Kabu already verified) + 6 JSON sidecars."""
import json, os, re

ROOT = r"C:\Users\alexa\Desktop\Bulk Graph Bundler"

CARDS = {
    "cards/pokemon/darkness-ablaze/163-189-kabu.md": {
        "ip_verify": True,  # callout swap still needed
        "ip_name": "Kabu (Pokémon Sword and Shield)",
        "ip_verify_note": "Confirmed via PokemonTCG.io card data (swsh3-163), Bulbapedia: Kabu, and matching Supporter card oracle text. Fire-type Gym Leader at Motostoke Stadium, originally from Hoenn.",
        "trivia_md": """
## Trivia

- **Set context** — Kabu appears in Sword & Shield — Darkness Ablaze (Sword & Shield Series, expansion 3, released August 14, 2020 in English), one of the two earliest Sword & Shield sets to introduce Gym Leader Supporter cards tied to the Galar Gym Challenge narrative [PokemonTCG.io: swsh3-163; Bulbapedia: Darkness Ablaze (TCG)].
- **Character lore** — Kabu is the Fire-type Gym Leader at Motostoke Stadium and the third Gym Leader encountered in the Galar Gym Challenge. He is canonically the only Gym Leader in Galar who is not a native — he migrated from Hoenn. In-game lore notes he once lost his Gym position before reclaiming it, and that a battle with Champion Leon reignited his competitive drive [Bulbapedia: Kabu; pokemon.com/sword-shield].
- **Design milestone** — Kabu is the first Gym Leader in Pokémon Sword and Shield to Gigantamax his Pokémon in battle, using a Gigantamax Centiskorch [Serebii.net: Sword & Shield Gyms; Game8: Kabu guide]. His card's Supporter effect — drawing 8 cards if your Active Pokémon is your only Pokémon in play — reflects a thematic push-your-luck framing consistent with his "challenge yourself to grow" character arc.
- **Illustrator** — Credited as "take" on both this Darkness Ablaze print (no. 163/189) and the four-weeks-later Champion's Path reprint (no. 55/73). Take is a Japanese illustrator credited with character design work on Pokémon Sword and Shield [PokemonTCG.io artist field confirmed across both prints].

### Related cards
- Kabu (Champion's Path, no. 55/73) — same character, same artist, same Supporter draw effect; reprint four weeks after this DAA original
- Centiskorch VMAX (Darkness Ablaze, no. 34/189) — Kabu's signature Gigantamax Pokémon, same set
- Ninetales (Darkness Ablaze) — Kabu fields Ninetales in the Gym battle; same set context
""",
        "json_path": "reports/trivia_pending/pokemon/darkness-ablaze/163-189-kabu.json",
        "json_summary": "Motostoke Fire-type Gym Leader; Hoenn-origin; first SwSh Gym Leader to Gigantamax (Centiskorch); illustrator 'take'",
    },
    "cards/pokemon/rebel-clash/047-192-galarian-darumaka.md": {
        "ip_verify": True,
        "ip_name": "Galarian Darumaka (Pokémon Sword and Shield)",
        "ip_verify_note": "Confirmed via PokemonTCG.io card data (swsh2-47), card name, Water-type mapping to Ice-type Galarian form, and exact Pokedex flavor text match (fire sac atrophy lore).",
        "trivia_md": """
## Trivia

- **Set context** — Galarian Darumaka appears in Sword & Shield — Rebel Clash (expansion 2, released May 1, 2020 in English), the same set where the Galarian regional form debuted in the TCG alongside other Galar-region variants [PokemonTCG.io: swsh2-47; Bulbapedia: Rebel Clash (TCG)].
- **Regional form lore** — The Galarian form adapts the original Unova Fire-type Darumaka (National Pokedex no. 554) into a pure Ice type. In-game lore explains the shift: Darumaka in Galar lived in snowy regions so long that their fire sac cooled off and atrophied, replaced by an organ that generates cold instead [PokemonTCG.io flavor text; Bulbapedia: Darumaka (Pokémon)].
- **Evolution and version exclusivity** — Galarian Darumaka evolves into Galarian Darmanitan via Ice Stone. Galarian Darmanitan's Zen Mode is notable as the first Ice/Fire dual-type Pokémon in the series. Galarian Darumaka is a Pokémon Sword version exclusive — not available in Shield without trading [Bulbapedia: Darumaka (Pokémon); PokemonDatabase.net: Sword/Shield exclusives].
- **Flavor text** — *"It lived in snowy areas for so long that its fire sac cooled off and atrophied. It now has an organ that generates cold instead."* `[PokemonTCG.io: swsh2-47]`

### Related cards
- Galarian Darmanitan (Rebel Clash) — evolution target via Ice Stone; same set
- Galarian Darmanitan (Sword & Shield base set or later prints) — alternate prints of the evolution line
- Darumaka (original Unova form) — the Fire-type predecessor whose regional divergence defines this form's lore
""",
        "json_path": "reports/trivia_pending/pokemon/rebel-clash/047-192-galarian-darumaka.json",
        "json_summary": "Galarian Ice variant of Unova Fire Darumaka; Sword version exclusive; evolves into Galarian Darmanitan via Ice Stone",
    },
    "cards/pokemon/rebel-clash/094-192-galarian-farfetch-d.md": {
        "ip_verify": True,
        "ip_name": "Galarian Farfetch'd (Pokémon Sword and Shield)",
        "ip_verify_note": "Confirmed via PokemonTCG.io card data (swsh2-94), card name, Fighting-type mapping to Galarian form, and exact Pokedex flavor text match (brave warriors, thick leeks).",
        "trivia_md": """
## Trivia

- **Set context** — Galarian Farfetch'd appears in Sword & Shield — Rebel Clash (expansion 2, released May 1, 2020 in English). It is classified as a Fighting-type Basic Pokémon, reflecting the Galarian form's Fighting typing as opposed to the Kanto original's Normal/Flying typing [PokemonTCG.io: swsh2-94; Bulbapedia: Rebel Clash (TCG)].
- **Regional form lore** — The Galarian form is a pure Fighting type. In-game lore frames Galarian Farfetch'd as warrior-class fighters who carry thick, tough leeks as weapons. The oversized leek is a deliberate design choice: leeks native to the United Kingdom (the real-world basis for Galar) grow significantly larger than leeks in Japan [PokéJungle: Galarian Farfetch'd and Sirfetch'd — Origin of Species].
- **Evolution mechanic** — Galarian Farfetch'd evolves into Sirfetch'd after landing exactly 3 critical hits in a single battle — one of the more unusual in-battle evolution conditions in the series. The evolution can trigger even if Galarian Farfetch'd loses the battle. On evolution, the leek splits: the leafy top becomes a shield, the stem a lance, referencing medieval weapons [Bulbapedia: Sirfetch'd; The Gamer: how to evolve Galarian Farfetch'd].
- **Flavor text** — *"The Farfetch'd of the Galar region are brave warriors, and they wield thick, tough leeks in battle."* `[PokemonTCG.io: swsh2-94]`

### Related cards
- Sirfetch'd (various Sword & Shield era prints) — evolution target, same Galarian form line
- Farfetch'd (original Kanto form, various sets) — the Normal/Flying predecessor; the contrast between forms anchors the regional-forms lore
- Leek (item card, if in TCG) — the held item that boosts critical hit ratio for the Farfetch'd line
""",
        "json_path": "reports/trivia_pending/pokemon/rebel-clash/094-192-galarian-farfetch-d.json",
        "json_summary": "Galarian Fighting variant of Kanto Normal/Flying Farfetch'd; UK-leek design citation; 3-crits-in-battle evolution to Sirfetch'd",
    },
    "cards/pokemon/darkness-ablaze/082-189-sinistea.md": {
        "ip_verify": True,
        "ip_name": "Sinistea (Pokémon Sword and Shield)",
        "ip_verify_note": "Confirmed via PokemonTCG.io card data (swsh3-82), card name, Psychic-type mapping to Ghost-type Sinistea, and exact Pokedex flavor text match (lonely spirit, cold cup of tea).",
        "trivia_md": """
## Trivia

- **Set context** — Sinistea appears in Sword & Shield — Darkness Ablaze (expansion 3, released August 14, 2020 in English) as a 30-HP Basic Psychic-type Pokémon. Ghost-types are represented as Psychic in the Sword & Shield TCG era [PokemonTCG.io: swsh3-82; Bulbapedia: Darkness Ablaze (TCG)].
- **Form variant — Phony vs. Antique** — In Pokémon Sword and Shield, Sinistea exists in two forms: Phony Form and Antique Form. Antique Form Sinistea carries a tiny stamp of authenticity on the underside of its teacup — a detail that cannot be seen in normal battle and is only visible in the Pokédex or at certain angles in Pokémon Camp. Antique Form is significantly rarer; sources estimate approximately 1% of wild Sinistea spawn as Antique Form. The only functional difference is the evolution item: Phony Form requires a Cracked Pot, Antique Form requires a Chipped Pot [Bulbapedia: Sinistea (Pokémon); GameFAQs: Pokémon Scarlet board; Pokémon Database: Sinistea].
- **Design inspiration** — The lore framing — a ghost inhabiting an antique teacup with widespread forgeries in circulation — may reference the historical practice of porcelain makers stamping their products to combat counterfeiting. The Sinistea cup is described in lore as a famous piece of antique tableware; many forgeries exist, hence the "Phony" / "Antique" split [Bulbapedia: Sinistea (Pokémon)].
- **Flavor text** — *"This Pokémon is said to have been born when a lonely spirit possessed a cold, leftover cup of tea."* `[PokemonTCG.io: swsh3-82]`

### Related cards
- Polteageist (Darkness Ablaze or later sets) — Sinistea's evolution; the Phony/Antique form split carries forward into Polteageist (same two forms, same pot-item distinction); future Nodeley candidate when Polteageist lands in corpus
- Sinistea (other prints across Sword & Shield era) — same character, form detail consistent across prints
""",
        "json_path": "reports/trivia_pending/pokemon/darkness-ablaze/082-189-sinistea.json",
        "json_summary": "Galar Ghost-type haunted teacup; Phony vs Antique Form variant (1% antique, hidden stamp); evolves into Polteageist",
    },
    "cards/pokemon/darkness-ablaze/092-189-solrock.md": {
        "ip_verify": True,
        "ip_name": "Solrock",
        "ip_verify_note": "Confirmed via PokemonTCG.io card data (swsh3-92), card name, oracle text naming Lunatone, and exact Pokedex flavor text match. Rock/Psychic Pokemon from Gen III Hoenn; Fighting-type in SWSH TCG era.",
        "trivia_md": """
## Trivia

- **Set context** — Solrock appears in Sword & Shield — Darkness Ablaze (expansion 3, released August 14, 2020 in English) as a 90-HP Basic Fighting-type Pokémon. Rock/Psychic types are mapped to Fighting in the SWSH TCG era [PokemonTCG.io: swsh3-92; Bulbapedia: Darkness Ablaze (TCG)].
- **Paired design — Solrock and Lunatone** — Solrock was designed as a matched counterpart to Lunatone, introduced together in Generation III (Hoenn). In Pokémon Ruby and Sapphire, Solrock was a Ruby-exclusive and Lunatone a Sapphire-exclusive — a version-pair mechanic expressing the sun/moon duality. Both are classified as the "Meteorite Pokémon" and are said to have emerged from a meteor strike site in Hoenn's Meteor Falls [Bulbapedia: Solrock (Pokémon); PokemonDatabase: Solrock].
- **Mechanical pair expression** — This card's Resistance Shade Ability — "If you have Lunatone in play, your opponent's Pokémon in play have no Resistance" — directly encodes the Solrock-Lunatone pair into its mechanics. The card requires its counterpart on the field to activate its primary ability, making the paired design a gameplay fact, not just a flavor note [PokemonTCG.io: swsh3-92 oracle text].
- **Flavor text** — *"When it rotates itself, it gives off light similar to the sun, thus blinding its foes."* `[PokemonTCG.io: swsh3-92]`

### Related cards
- Lunatone (any Darkness Ablaze or SWSH-era print) — Solrock's mechanical counterpart; required in play to activate the Resistance Shade Ability; future Nodeley candidate when Lunatone enters corpus
- Solrock (other prints across Ruby/Sapphire era through SWSH) — same character, earlier/later print history
""",
        "json_path": "reports/trivia_pending/pokemon/darkness-ablaze/092-189-solrock.json",
        "json_summary": "Hoenn sun/moon pair anchor (Solrock = Ruby-exclusive sun, Lunatone = Sapphire-exclusive moon); ability mechanically requires Lunatone in play",
    },
    "cards/pokemon/darkness-ablaze/108-189-deino.md": {
        "ip_verify": True,
        "ip_name": "Deino",
        "ip_verify_note": "Confirmed via PokemonTCG.io card data (swsh3-108), card name, Darkness-type mapping to Dark/Dragon type, and exact Pokedex flavor text match (bites first, commits scent to memory).",
        "trivia_md": """
## Trivia

- **Set context** — Deino appears in Sword & Shield — Darkness Ablaze (expansion 3, released August 14, 2020 in English) as a 60-HP Basic Darkness-type Pokémon, reflecting its Dark/Dragon dual typing in the games [PokemonTCG.io: swsh3-108; Bulbapedia: Darkness Ablaze (TCG)].
- **Naming convention — German numerals** — Deino, Zweilous, and Hydreigon embed the German words for one, two, and three (ein, zwei, drei) into their names, counting the number of heads in each stage: Deino (1 head), Zweilous (2 heads), Hydreigon (3 heads). This German-count design is widely recognized as one of the franchise's most elegant naming conventions [Pokemaniacal: Deino, Zweilous and Hydreigon; Bulbapedia: Zweilous (Pokémon)].
- **Pseudo-legendary line** — Hydreigon, Deino's final evolution, is Unova's pseudo-legendary with 600 base stat total. The Deino-Zweilous-Hydreigon line is the only Dark/Dragon-type evolutionary chain in the series. The evolution schedule is notably slow: Deino does not evolve until level 50, one of the latest first-stage evolution thresholds in the series [Bulbapedia: Hydreigon (Pokémon); PokemonDatabase: Hydreigon].
- **Flavor text** — *"When it encounters something, its first urge is usually to bite it. If it likes what it tastes, it will commit the associated scent to memory."* `[PokemonTCG.io: swsh3-108]`

### Related cards
- Zweilous (any Darkness Ablaze or Black/White-era print) — stage 1 evolution, two-headed, German "zwei" in name
- Hydreigon (any Darkness Ablaze or Black/White-era print) — Unova pseudo-legendary final form, three-headed, German "drei" in name; Ghetsis's signature Pokemon in Black/White
""",
        "json_path": "reports/trivia_pending/pokemon/darkness-ablaze/108-189-deino.json",
        "json_summary": "Unova Dark/Dragon hydra base; German numeral naming chain (ein/zwei/drei = 1/2/3 heads); evolves into Hydreigon (Unova pseudo-legendary)",
    },
}

for rel_path, info in CARDS.items():
    abs_md = os.path.join(ROOT, rel_path.replace("/", os.sep))
    abs_json = os.path.join(ROOT, info["json_path"].replace("/", os.sep))

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

    with open(abs_md, "r", encoding="utf-8") as f:
        body = f.read()

    body = re.sub(r'^ip_verified:\s*false\s*$', 'ip_verified: true', body, flags=re.MULTILINE)

    ip_name = info["ip_name"]
    old_callout = f"> [!warning] Suspected IP: **{ip_name}** (confidence: high, unverified)\n> Reviewer: confirm whether the depicted figure is canonically this character. If yes, set `ip_verified: true` in frontmatter. If no, clear `suspected_ip`."
    new_callout = f"> [!note] IP verified: **{ip_name}**\n> {info['ip_verify_note']}"
    if old_callout in body:
        body = body.replace(old_callout, new_callout)
        print(f"  SWAPPED callout: {rel_path}")
    else:
        print(f"  (no warning callout to swap): {rel_path}")

    # Inline metadata swap (if present)
    inline_old = f"**Suspected IP:** {ip_name} (confidence: high, verified: False)"
    inline_new = f"**Verified IP:** {ip_name} (confidence: high)"
    if inline_old in body:
        body = body.replace(inline_old, inline_new)
        print(f"  SWAPPED inline line: {rel_path}")

    if "## Trivia" not in body:
        body = body.rstrip() + "\n" + info["trivia_md"].rstrip() + "\n"
        print(f"  APPENDED trivia: {rel_path}")
    else:
        print(f"  !! TRIVIA ALREADY PRESENT: {rel_path}")

    with open(abs_md, "w", encoding="utf-8") as f:
        f.write(body)

print("DONE")
