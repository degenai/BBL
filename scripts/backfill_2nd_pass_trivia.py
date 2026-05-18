#!/usr/bin/env python3
"""Backfill 2nd-pass trivia bullets to card MDs.

Some agents in the 24-agent wave had Write/Edit permission and appended
their own findings directly; others returned text-only outputs. This
script does a single uniform append pass for cards still missing 2nd-
pass content. Each card gets a ## Trivia (second pass) section with
curated bullets distilled from the agent output captured in
reports/trivia_second_pass_deltas.md.

Idempotent: skips cards that already have a 2nd-pass section.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Per-card 2nd-pass bullets, curated from the agent transcripts.
# Markers in each bullet match the grep-detection in the gate check
# above so subsequent runs are idempotent.
DATA = {
    # ---- DRONE ----
    "cards/magic-the-gathering/commander-legends/348-workshop-assistant.md": """\

## Trivia (second pass)

- **Kaladesh's "Aether Cycle" caste system** — Kaladesh worldbuilding divides society into a five-stage cycle: Inspire / Innovate / **Build** / Liberate / Reclaim. The Build phase is the labor layer: "hardworking manufacturers build the device, infuse it with aether, and repair and maintain it throughout its lifetime." Dwarves are Kaladesh's designated Build-phase caste — "tireless workers" who treat their constructs "as though they were their children." Workshop Assistant sits inside the maintenance economy as a Build-phase instrument. `[Wizards: Planeswalker's Guide to Kaladesh, 2016]`
- **Countless Gears guild specialty** — One of Kaladesh's inventor societies, the Countless Gears, specializes in "the smallest automatons and thopters found on Kaladesh." Workshop Assistant's spider-form fits their product profile exactly. `[Wizards: Planeswalker's Guide to Kaladesh]`
- **Junk Diver infinite combo at common rarity** — Workshop Assistant + Junk Diver + a sacrifice outlet (Blasting Station, Ashnod's Altar) = infinite ETB/LTB/death triggers or infinite colorless mana. Both pieces are common, making the combo Pauper-relevant. Commander Spellbook documents 25+ combo lines built around Workshop Assistant. `[CommanderSpellbook.com; EDH-Combos.com]`
- **Commander Legends reprint philosophy** — Mark Rosewater articulated the design shift: Set Design moved away from "big splashy" rare reprints, instead "using the reprints at lower rarities to reprint cards that helped make those themes work together." Workshop Assistant — utility common gluing artifact-sacrifice themes at common rarity — is exactly the profile this philosophy targeted. `[Wizards: "Your Wish Is My Commander Legends, Part 2," Mark Rosewater, 2020]`
- **Artist: Victor Adame Minguez (correction)** — All three printings (KLD, CMR, KLR) share the same illustration by Minguez — identical Scryfall illustration IDs confirm no art variant exists across printings. Works in oils on MDF board after transitioning from digital as the MTG originals market grew. ~163 MTG illustrations by 2026. His 2021 sale of the Grist, the Hunger Tide original set a personal record at $35,000. `[Hipsters of the Coast 2021, 2022; Gatherer]`
- **KLR is Arena-only** — Kaladesh Remastered is digital-only (no paper copies). Scryfall `games` field confirms `["arena"]`. `[Scryfall API]`
""",

    "cards/final-fantasy-tcg/opus-viii/8-008c-golem.md": """\

## Trivia (second pass)

- **Artist Yasuhisa Izumisawa was a Magic player** — Per his own account in the official FFTCG Illustration Showcase Interview (May 2019): *"For a while, I was obsessed with Magic: The Gathering. A lot of money and long nights went into playing that game."* The artist behind the FFCC cards in Opus VIII was himself a dedicated MTG player — a biographical loop that closes in 2025 when Wizards licensed Final Fantasy IP for *Universes Beyond: Final Fantasy*, the highest-grossing MTG set ever released. `[Square Enix FFTCG Illustration Showcase Interview no. 7, May 21 2019 — eu.finalfantasy.com/topics/70]`
- **Izumisawa career arc** — Career Square Enix internal artist. Pixel art on Xenogears → monster design on SaGa Frontier 2 → weapon/gadget design on Final Fantasy IX → monster design and textures on Final Fantasy X → main character designer on the FFCC series. His Opus VIII card illustrations were his first finished single-illustration card work; he noted it "took a while" compared to his usual rough game-design reference sheet output. `[Square Enix Interview no. 7, 2019]`
- **Source game commercial profile** — *Final Fantasy Crystal Chronicles: Echoes of Time* (2009) sold approximately 570,000 units worldwide. First-week Japan: 101,718 DS / 21,721 Wii. Metacritic: 75/100 DS, 64/100 Wii. Its modest profile makes FFTCG's Opus VIII showcase treatment (dedicated artist interview, original commissioned art) a curatorial affection play, not a market-demand response. `[Wikipedia: FFCC: Echoes of Time; VGChartz]`
- **Golem variants in source game** — Tiered enemy type in FFCC:EoT: base Golem, Bolt Golem (median), Magic Golem (strongest, casts spells), Grappler Golem (Graveyard / Forest / Tower dungeons). The 8-008C art's simplified geometric silhouette — squat body, mask face, single circular eye, no elemental markers — corresponds to the base Golem tier. `[Final Fantasy Wiki: Golem (Crystal Chronicles)]`
- **Prior FFTCG Golem** — Golem (1-106C, Opus I, 2016) is an Earth-element Backup-type common from the original Fire/Earth Starter Deck, drawing from the broader FF bestiary. The 8-008C is the SECOND distinct Golem common in Opus history: different source game, different card type, different artist, same creature name across eight sets. `[Collector's Cache: 1-106C]`
- **MTG x FF crossover context (2025)** — *Universes Beyond: Final Fantasy* (released June 13 2025) generated ~$200M in revenue on day one and contributed to 23% YoY player growth for Magic. FFTCG itself was NOT retired: Set 28 (*Dreamlike Oceans*) is scheduled for March 2026. Square Enix and Wizards now coexist in the market; the IP was licensed, not absorbed. `[Game Rant; Star City Games: Magic Grows 23%]`
""",

    "cards/weiss-schwarz/hatsune-miku-project-diva-f/pd-s22-e027-rr-hatsune-miku-factory-tyrant.md": """\

## Trivia (second pass)

- **cosMo@BousouP credited as the module's costume designer**, not only its composer — atypical for Project DIVA, where SEGA normally handles module design in-house. The black peaked cap with teal stripe, CD brooch at the neckline, and cogwheel-framed twin-tail cuffs all carry his design credit. `[Project DIVA Wiki: Factory Tyrant, via WebSearch snippet]`
- **cosMo biography** — Born 1986 Tokyo. Primary occupation: animator. Music production began 2007, influenced by BEMANI rhythm games (GuitarFreaks, DrumMania). Niconico nickname: "High-Speed Development Miku Master" (compositions typically exceed 200 bpm). "Sadistic.Music∞Factory" is his 56th original Vocaloid work. `[Vocaloid Wiki: cosMo]`
- **Western release driven by SEGA Twitter campaign** — June 2013 PlayStation Blog post asking fans to like/share for a western PS3 release got 25,000+ likes / 15,000+ shares in three days. Project DIVA F PS3 hit US August 27 2013; Weiss Schwarz English PD/S22 arrived three months later (Nov 2013). `[PlayStation Blog, June 2013]`
- **Sales / reception** — PD F PS Vita Japan opened #1 with 158,607 first-week copies; ~390K shipped by April 2013. SEGA devs publicly acknowledged budget "may have been too big" — outsold by Persona 4: Golden in the same window. `[SEGAbits, 2012]`
- **Long commercial tail** — Factory Tyrant module released as SEGA Super Premium (SPM) arcade-prize figure in March 2017 (240mm); added to Project DIVA Arcade Future Tone May 28 2015 — three years past the original game. Japanese title: "Wagamama Koubachou" (literally "Selfish Plant Manager"). `[MyFigureCollection.net]`
- **Song still culturally active** — Original Niconico upload (Aug 27 2012) ~592K views per Vocaloid Rankings tracker; 2021 V4X YouTube remake crossed 1M views. `[Vocaloid Rankings; VocaDB]`
""",

    "cards/magic-the-gathering/modern-horizons-3/130-phyrexian-ironworks.md": """\

## Trivia (second pass)

- **Slobad's full body-horror arc** — Memnarch amputated his limbs and wired him into the spark-transfer machine for FIVE YEARS; Slobad was the involuntary architect of the device meant to strip Mirrodin's inhabitants of their sparks. When fired, the spark transferred to him; he sacrificed it to resurrect all who had died. Later killed by panicked goblins, body sank into the plane's core, compleated by New Phyrexia, reshaped his Phyrexian form to resemble his late friend Bosh. `[MTG Wiki: Slobad]`
- **Naming lineage** — "Phyrexian Ironworks" structurally echoes Krark-Clan Ironworks (Fifth Dawn, 2004) — the Mirrodin-block artifact named after the Krark Clan, one of Mirrodin's goblin clans (Slobad's people). The faction+Ironworks naming pattern reads as machine compleated. `[Scryfall: Krark-Clan Ironworks 5DN 134]`
- **Artist Mathias Kollros** — Illustrated exactly two cards in MH3: Petrifying Meddler (Eldrazi) and Phyrexian Ironworks — one from each of the set's major artifact-creature factions. RTR 2012 debut; 173+ MTG cards. ArtStation handle: guterrez. `[Scryfall: artist query]`
- **Commander niche** — Highest deck inclusion is energy commanders (Pia Nalaar, Chief Mechanic at 24%; Liberty Prime, Recharged at 17%), NOT Phyrexian tribal — energy-artifact crossover niche despite the faction name. `[EDHREC card page]`
- **MH3 energy revival context** — MaRo's "Expanding Your Horizons: Energy" (June 2024) frames Energy as "a second-tier Modern deck that designers hoped to give a boost." The Phyrexian Oil counter sub-theme also connects to post-March of the Machine residue. `[Wizards of the Coast: Expanding Your Horizons]`
""",

    "cards/magic-the-gathering/magic-2015-m15/239-will-forged-golem.md": """\

## Trivia (second pass)

- **Jason Felix plagiarism + Wizards suspension (2021)** — Felix illustrated 137+ MTG cards. In April 2021 he publicly admitted that the Strixhaven Mystical Archive printing of Crux of Fate incorporated — without permission — elements of Kitt Lapeña's 2016 Nicol Bolas fan painting and Raymond Swanland's Ugin, the Spirit Dragon card art. Wizards suspended future work; he agreed to compensate both artists. Finished outstanding commissions by June 2021 and has not been contracted by Wizards since. `[Hipsters of the Coast 2021-04; Wizards: Statement on Crux of Fate 2021-03-30]`
- **M15 guest-DESIGNER context (correction)** — M15's innovation was 15 *guest game designers* (not artists): Markus "Notch" Persson, Rob Pardo, George Fan, and others. Will-Forged Golem carries no guest credit — standard Wizards team design. The set is the first core set to feature named outside-creator attribution at all. `[Kotaku 2014; Engadget 2014-04-19]`
- **Convoke rules change in M15** — When Convoke debuted in Ravnica: City of Guilds (2005) it was a cost-REDUCTION ability. M15 changed it to an alternative-cost payment. M15 also expanded the mechanic beyond Selesnya green-white to all five colors and artifacts. Will-Forged Golem is one of only two artifact Convoke cards in the set (22 Convoke cards total in M15). `[Draftsim: Convoke History; Gatherer M15 Convoke filter]`
- **Sam Stoddard design article** — "Developing Convoking" (Wizards of the Coast, July 25 2014) — the design team intentionally held Convoke back from intervening sets to make it M15's signature mechanic. `[magic.wizards.com/.../developing-convoking-2014-07-25]`
- **Convoke is "deciduous"** — Rosewater confirmed on Blogatog (June 29 2024): available to design teams in any set where it fits, not expected in every set. Convoke history: Ravnica (2005), Future Sight, M15, Guilds of Ravnica, Modern Horizons, Modern Horizons 3. `[Commander's Herald 2024]`
""",

    "cards/magic-the-gathering/war-of-the-spark/240-iron-bully.md": """\

## Trivia (second pass)

- **Reprinted in Double Masters (correction)** — Iron Bully was reprinted in 2XM (August 2020) as no. 262, same artist, same flavor text — first pass said "first and only printing"; that was wrong. `[Scryfall: 2XM 262]`
- **Commander Grozdan is a real named character** — Boros minotaur, Ordruun bloodline, stationed at Kamen Fortress, assigned to suppress Rakdos activity under Aurelia's command per the Guildmasters' Guide to Ravnica (2018 WotC/D&D sourcebook). First pass called him a "minor NPC" — wrong. The sourcebook predates WAR; Grozdan was canon when WAR was written. The flavor line's comedic register is consistent with Boros doctrine-over-deliberation ethos. `[Ravnica Campaign Setting Wiki; Guildmasters' Guide to Ravnica]`
- **WAR colorless-common artifact-creature trio** — Iron Bully (240, Aaron Miller), Prismite (242, Alayna Danner), Saheeli's Silverwing (243, Daniel Ljunggren). Three cards, three artists, contiguous collector numbers. Iron Bully is the only one with a pump trigger on entry. `[Scryfall: WAR card search]`
- **Aaron Miller — career depth** — Theros 2013 debut with Chained to the Rocks (a Prometheus-referenced piece). 164 unique MTG illustrations by 2026. Multiple Spectrum: The Best in Fantastic Art inclusions; GenCon Best in Show 2013, Juror's Choice 2010. Built a custom MTG token line via Kickstarter (2020) — 18 original foil tokens. `[Hipsters of the Coast 2020; aaronbmiller.com]`
""",

    "cards/magic-the-gathering/battlebond/249-yotian-soldier.md": """\

## Trivia (second pass)

- **Same artist as Skullclamp** — Luca Zontini's Mirrodin-era work includes both Yotian Soldier (a humble 1/4 vigilance defensive filler) and Skullclamp (Darksteel, 2004) — one of the most infamously broken artifacts ever printed, banned in Standard, Legacy, Extended, and Modern within months of release. The same illustrator produced Magic's most defensively modest common and its most aggressively banned equipment in the same block era. Zontini's first MTG credit was Mercadian Masques (1999); his last is Battlebond (2018) — a 19-year run with the game. `[Scryfall: artist:"Luca Zontini" full prints list]`
- **Christopher Rush's deeper legacy** — The original Antiquities artist is best known for Black Lotus, but Rush also designed the five mana symbols (the pip icons on every Magic card) and co-designed the game's logo with Jesper Myrfors. Wizards' 2016 obituary quotes Matt Tabak: "It's a fitting tribute that he remains part of every card we print." Rush died February 10 2016 at age 50. Every Yotian Soldier printed after that date still carries his mana symbols. `[Wizards: Christopher Rush obituary, 2016-02-11]`
- **Brothers' War (2022) design context** — Mark Rosewater confirmed in "Odds and Ends: The Brothers' War" that Yotian Soldier was explicitly considered for a BRO main-set reprint: "We did explore several reprints, including Sage of Lat-Nam, the Urza lands, and numerous artifacts like Yotian Soldier and Ornithopter" — but cut because the set received a retro artifact bonus sheet. BRO instead introduced four new Yotian-named cards: Yotian Frontliner, Yotian Medic (Queen Kayla bin-Kroog flavor), Yotian Dissident, Yotian Tactician. The 1994 common spawned a four-card lore family 28 years later. `[Wizards: Odds and Ends: The Brothers' War]`
""",

    "cards/pokemon/vivid-voltage/151-185-drone-rotom.md": """\

## Trivia (second pass)

- **Pulseman design lineage** — Rotom's core concept (a ghost possessing electrical devices) is widely cited as a design reference to Pulseman (Game Freak / Sega, 1994), also directed by Sugimori. Pulseman transforms into a ball of plasma and enters electrical conduits; the red-spike headpiece and electricity-as-possession mechanic are the most-cited parallels. Volt Tackle (Pikachu's Gen IV move) derives from Pulseman's "Volteccer." `[PokeCommunity Daily; Pulseman Wikipedia]`
- **Per-form designer breakdown** — Base Rotom by Ken Sugimori. Battling forms: Heat by Lee HyunJung, Fan by Motofumi Fujiwara, Mow by Yusuke Ohmura, Wash by Hiroki Fuchino, Frost by Hironobu Yoshida. No separate designer credit recorded for the non-battling Drone form. `[Bulbapedia designer list; nintendo.fandom.com/wiki/Rotom]`
- **JN115 / 1,200th anime episode** — "Curtain Up! Fight the Fights!" (Pokemon Ultimate Journeys, 2022) — the 1,200th episode of the Pokemon animated series. Five Drone Rotom fly over Wyndon Stadium expelling colored smoke trails that form the World Coronation Series logo in the sky, opening the Masters Eight Tournament (Ash, Iris, Alain, Diantha, Lance, Steven Stone, Cynthia, Leon). `[Bulbapedia JN115]`
- **Artist: 5ban Graphics** — 3D CG studio embedded within Creatures Inc. (co-holder of the Pokemon IP alongside Game Freak and Nintendo). Active in Pokemon TCG since Black & White era (Japanese debut Dec 2010); 1,700+ cards by Sword & Shield era. Defines the visual identity of most Pokemon V, VMAX, and full-art GX cards. Community reception polarized — PokeBeach forum threads describe early modeling as "belonging in the early 2000s." `[Serebii.net 5ban Graphics card dex]`
- **Competitive TCG assessment** — Minimal constructed play in SwSh format; no top Limitless decklists. Pojo.com ranked Vivid Voltage no. 31 (December 2020) — niche control tool with bluff element (opponent can decline reveal, forfeiting peek) but too slow for aggressive metas. Marginal upgrade over Hand Scope. `[Pojo.com VV review]`
- **Sister card: Rotom Phone** (Champion's Path 064/073, Ryo Ueda) — same SwSh era Item card with Rotom inhabiting a device. Effect category opposite: look at top 5 of your deck vs. force opponent hand reveal. Twin axes of TCG information advantage. `[Bulbapedia Rotom Phone]`
""",

    "cards/magic-the-gathering/modern-horizons-3/150-eldrazi-repurposer.md": """\

## Trivia (second pass)

- **Rosewater Blogatog on Spawn vs Scion design choice** — "1/1 scions were better for the more normal set where the creature matters more, and 0/1 spawns were better for the higher powered set where the cost discount and the mana ability were more exciting." MH3 deliberately reverted to Spawn from BFZ's Scion. Eldrazi Repurposer's double-trigger (cast + death) makes it a premier Spawn engine in exactly the high-powered environment Rosewater names. `[Blogatog: markrosewater.tumblr.com/post/770577990721667072]`
- **General Tazri's full arc** — Three card printings across a decade. General Tazri (Oath of the Gatewatch, 2016) — 5-color Ally commander who led the allied resistance against Ulamog and was instrumental in the recapture of Sea Gate. Tazri, Beacon of Unity (Zendikar Rising, 2020) — the same figure as General-Commander overseeing Sea Gate's post-Eldrazi rebuilding. Tazri, Stalwart Survivor (March of the Machine: The Aftermath, 2023) — defended Zendikar during the Phyrexian invasion. That MH3 (2024) still attributes flavor to her "allied commander" rank frames the quote as a soldier's long institutional memory of the enemy. `[Scryfall lore:tazri]`
- **Pauper format impact** — After MH3's June 2024 release, Gruul Eldrazi / Gruul Ponza became a defining Pauper archetype. The archetype leverages Spawn tokens for mana ramp and land denial; Repurposer's 3/3 body with guaranteed double-Spawn trigger is core. Gruul Eldrazi achieved 5-0 in MTGO Pauper League no. 8217 (July 2024) and Top 4 at Copa Rio Pauper (June 2024). `[MTGDecks.net]`
- **Daren Bader** — Debuted with Tempest (1997); 193 unique art credits across 68 sets by 2024 — one of the game's longest-tenured illustrators. Most prominent individual cards: Akroma, Angel of Fury; Finale of Devastation (WAR 2019); Enduring Ideal (SOK 2005). Works predominantly in traditional media — oils and acrylics on illustration board. `[Gatherer; Scryfall a:"Daren Bader"]`
""",

    "cards/magic-the-gathering/throne-of-eldraine/221-henge-walker.md": """\

## Trivia (second pass)

- **Titus Lunter detained by ICE, August 2018** — At Seattle-Tacoma International Airport alongside fellow WotC-contracted European artists Anna Steinbauer and Magali Villeneuve. All three were traveling to Wizards of the Coast headquarters in Renton, WA for a D&D concept art push. ICE permanently revoked all three artists' ESTA visa waivers; they were deported after being held overnight. Wizards of the Coast made no public statement. `[Hipsters of the Coast: "WotC-Affiliated Artists Anna Steinbauer, Magali Villeneuve, and Titus Lunter Detained by ICE in Seattle," August 2018]`
- **Lunter's full ELD batch** — 6 cards in Throne of Eldraine: Charmed Sleep, Witch's Vengeance, Wildwood Tracker, Henge Walker, Prophet of the Peak, and Castle Locthwain. Castle Locthwain (the black-aligned Castle cycle land) is his high-value hit from the set — EDHREC rank 733, ~$3.58 today. Lunter is Dutch and has been illustrating for Magic since Khans of Tarkir (2014), specializing in environmental concept art. `[Scryfall: a:"Titus Lunter" set:eld; Hipsters of the Coast 2018]`
- **Garenbrig built before humans** — The Great Henge and Castle Garenbrig were constructed by giants before humans rose to power on Eldraine. The court's animating virtue is Strength. King Yorvo (a Giant Noble) rules. "Larger giants with stone skin tend to be kinder to small folk, using their strength to help those in need," sometimes becoming Garenbrig knights. The Henge functions as more than monument: at certain dates, aligned calendar-stone monoliths cast shadows that open a magical gate to the depths of the Wilds. Moving the monoliths into alignment is itself considered worthy of earning a Garenbrig knighthood. `[Wizards: Planeswalker's Guide to Eldraine, October 2019]`
- **Yorvo, Lord of Garenbrig** (ELD 185, art by Zack Stella) — the named ruler of the court Henge Walker inhabits. Legendary Creature — Giant Noble, costing {G}{G}{G}, entering with four +1/+1 counters and growing whenever another green creature enters. EDHREC rank 8,916. His triple-green cost is a direct mechanical expression of Adamant / Garenbrig-Strength. `[Scryfall: Yorvo, Lord of Garenbrig]`
- **~1,000x price gap** — The Great Henge sits at $63.89 nonfoil as of May 2026 (Scryfall). First reprint Commander Masters (CMM 294, August 2023); reprint supply has not suppressed demand. Henge Walker sits at $0.06 nonfoil — approximately a thousand-x gap between the landmark and the creature it animates. `[Scryfall: prices fields, May 2026]`
- **Wilds of Eldraine (2023) extends the Garenbrig thread** — In the 2023 set's narrative, the protagonist twins travel to Castle Garenbrig to request King Yorvo's permission to use the Great Henge as a portal to the Wilds — the first story-spotlight activation of the Henge as a transportation device. Henge Walker's flavor text carries a second register against this: the Henge is both animator of constructs and literal gateway. `[mtg.cardsrealm.com: Eldraine lore primer, 2023]`
""",

    # ---- TITHE ----
    "cards/magic-the-gathering/throne-of-eldraine/109-wicked-guardian.md": """\

## Trivia (second pass)

- **"Wicked" as ELD villain-naming convention** — A deliberate design signal for fairy-tale antagonists. Wicked Guardian (the cruel-stepmother figure) and Wicked Wolf (Three Little Pigs) are the two cards carrying it. Jay Annelli's CoolStuffInc Flavor Gems piece (2019-10-01) names the full Cinderella cycle explicitly and places Wicked Guardian as the custodian figure. `[CoolStuffInc: Flavor Gems of ELD]`
- **Locthwain court lore** — Human Noble places her in Locthwain's social architecture. The Wizards Planeswalker's Guide describes Locthwain's Persistence virtue as enacted through "persistent efforts at serving the queen" — the nobility-exploiting-servant dynamic in the card art is canon to the court's internal logic. `[Wizards: Planeswalker's Guide to Eldraine]`
- **Noble subtype history** — Noble was reintroduced in ELD after retirement in the Grand Creature Type Update; 20 older creatures gained the subtype retroactively. Wicked Guardian is part of the inaugural new-print Noble wave. `[MTG Wiki: Noble subtype]`
- **ELD Draft ranking** — Star City Games rated it the 3rd-best black common (behind Bake into a Pie and Reave Soul), with a noted steep drop-off after the top tier. `[SCG ELD Draft Review]`
- **Matt Stewart — artist profile** — Three-time Chesley Award winner. 245+ MTG card credits across the game. Parsons-trained; Tolkien-influenced personal work. Oil-on-gessobord medium for ELD. `[Gatherer artist search]`
""",

    "cards/magic-the-gathering/war-of-the-spark/81-charity-extractor.md": """\

## Trivia (second pass)

- **Art brief vs. final painting** — AD Dawn Murin's brief specified a knight on horseback holding an offering plate with a gold coin necklace. Matt Stewart departed substantially: no horse, no offering plate; the keys and locked strongbox were his own additions — included to underline how seriously the templar takes collection. `[Hipsters of the Coast: "Behind the Front Lines," Donny Caltrider, 2019-04-18]`
- **Reference sourcing for a common** — For this $0.05 card Stewart posed in full armor himself, sourced horse-armor photographs from the Wallace Collection in London, used a Christmas ornament to nail the Orzhov gold tone, and photographed the Palace of Westminster for the background architecture. `[Hipsters of the Coast, 2019-04-18]`
- **Same artist, same set: $35,000 sale** — In the same release Stewart's Nicol Bolas, God-Pharaoh mythic-edition oil (24" x 30") sold for $35,000 — possibly the highest commission for any single piece in WAR. A common and a $35k centerpiece, same artist, same release date. `[Hipsters of the Coast: Nicol Bolas sale, 2019]`
- **WAR's only two black lifelink commons** — Banehound (1/1 haste, {B}) and Charity Extractor (1/5, {3}{B}). Opposite design poles within the same keyword slot — one aggressive one-drop, one defensive wall. `[Scryfall: WAR black lifelink common search]`
- **EDH commander placement** — Top shells: Sidar Jabari of Zhalfir (WUB Knight tribal with eminence — Charity Extractor's knight body feeds the hand-cycling without needing to attack profitably) and Karlov of the Ghost Council (lifelink trigger every combat fuels Karlov's +1/+1 counter engine). `[EDHREC card page]`
- **WAR Limited evaluation** — The format was heavily shaped by planeswalker density: creatures needed evasion to threaten planeswalkers. A 1/5 with no evasion cannot attack planeswalkers usefully — widely considered underdraftable. `[Hipsters: WAR Common Review; MTG Arena Zone WAR Limited Guide]`
""",

    "cards/magic-the-gathering/ravnica-allegiance/194-pitiless-pontiff.md": """\

## Trivia (second pass)

- **"Pontiff" is a NAMED institutional rank** — not generic ecclesiastical flavor. Sits between the advokist/ministrant class and the Obzedat ghost council in the Orzhov hierarchy. A pontiff commands a staff of 2d6 ministrants with attendant knights and syndics, has access to servitor thrulls, and holds the privilege of direct communication with the Obzedat. The card depicts an office, not an improvised title. `[World Anvil: Orzhov Syndicate Ranks; EDHREC: Historically Speaking — The Orzhov Syndicate]`
- **Cathedral backdrop is Orzhova** — Also known as "Cathedral Opulent" or "Church of Deals" — the Orzhov guildhall on the western edge of Tenth District Plaza. Soaring ceilings and oversized marble statues of bishops, enforcer angels, and ghosts make every visitor feel physically small. Below the church is a bejeweled catacomb housing the mummified bodies of the Obzedat, lined with pre-Guildpact protection magic old enough to be outside the law. Robed "Gray Sisters" perform all menial labor. `[MTG Wiki: Orzhova]`
- **Yongjae Choi — double Orzhov commission in RNA** — Choi illustrated both Pitiless Pontiff and Kaya, Orzhov Usurper in the same set: the guild's vampire enforcement rank and its incoming planeswalker ruler, by the same hand, in one release. His Ravnica-block footprint also includes Lazav, the Multifarious (GRN mythic, Dimir) and Faerie Duelist (RNA common). He sells a print of the Pitiless Pontiff art on INPRNT. `[Scryfall: a:"Yongjae Choi" e:rna; INPRNT gallery]`
- **RNA's political moment** — Pitiless Pontiff entered print at the exact story beat when Teysa Karlov (Grand Envoy and highest-ranking living mortal in the guild, an advokist not a pontiff) was attempting to overthrow the Obzedat with Boros knight Tajic. She was foiled and stripped of her offices. The pontiff tier (enforcement layer between living mortals and ghost council) was the institutional structure holding during the failed coup. RNA's narrative closes with the Obzedat purged by Kaya. `[MTG Wiki: Teysa Karlov; EDHREC Historically Speaking]`
- **Preview source** — Limited Resources podcast (Patreon post, 2019-01-03) — MTG's longest-running draft-strategy podcast. No Wizards story spotlight (`story_spotlight: false` per Scryfall). No named Pitiless Pontiff character appears in any RNA story chapter. `[Scryfall preview metadata]`
""",

    "cards/magic-the-gathering/ravnica-allegiance/192-mortify.md": """\

## Trivia (second pass)

- **Five distinct flavor texts across 29 printings**:
  - **GPT (Glen Angus 2006)**: visceral prose poem, no speaker
  - **DDK era (Nils Hamm 2013-2018)**: Sorin quip — *"Many who cross Sorin's path come down with a sudden and fatal case of being-in-the-way-of-a-millennia-old-vampire."*
  - **RNA / ONC / DMC / MOC (Anthony Palumbo)**: Hilgur, Orzhov euthanist text
  - **Foundations Starter (Nils Hamm 2024)**: generic high fantasy — *"The queen sent her champion to defeat the necromancer threat. His helmet was returned the next day, warped and stained with blood."*
  - **SCH 21 promo (Andreia Ugrai 2023)**: NO flavor text — a sixth distinct artist beyond first pass
- **Astarion's Thirst Secret Lair** — D&D 50th Anniversary Superdrop, August 27 2024. Bartek Fedyczak, inverted borderless frame. Five-card vampire suite containing an Exquisite Blood + Sanguine Bond infinite combo. Mortify is the suite's removal piece. Flavor: *"Can you feel death's cold grip?"* `[Commander's Herald 2024]`
- **Crossover flavor substance** — LotR Commander printing (Ilker Yildiz) pulls Sam Gamgee cooking rabbits ("Of Herbs and Stewed Rabbit," TTT Book IV Ch4) — domesticity mapped onto a kill spell. FFVI surgefoil (Thanh Tuan) quotes an anonymous Imperial soldier watching Espers extracted into Magicite — directly the game's extraction/destruction narrative. `[Scryfall print history]`
- **"Orzhov euthanist" formally defined** — The Guildmaster's Guide to Ravnica (2018 WotC/D&D sourcebook) defines euthanist as an Orzhov enforcer role: "an assassin euphemistically called a euthanist who brings speedy ends to lives deemed to have gone on too long." The role was coined in Guildpact (2006), codified in GGtR (2018), and reused on RNA (2019) — 13-year canon arc. `[Guildmaster's Guide to Ravnica]`
""",

    "cards/magic-the-gathering/dragon-s-maze/109-tithe-drinker.md": """\

## Trivia (second pass)

- **Extort mechanic origin** — Designed by Shawn Main outside the Gatecrash team during devign. The original cost was 1 generic mana; development changed it to {W/B} hybrid. MaRo drafted 14 extort cards to convince skeptics. `[Wizards: "Gatecrashing the Party Part 3"; "Designing for Orzhov"]`
- **Extort color identity ruling** — {W/B} appears in REMINDER TEXT only; mono-colored extort cards (Blind Obedience) are legal in mono-black Commander. Rules discourse specific to the mechanic. `[Magic Judges Blog; MTGSalvation Rulings]`
- **Reprint history** — Commander 2017 (no. 200, "Vampiric Bloodlust" precon) and The List (PLST C17-200). The C17 vampire-tribal shell explains the EDH inclusion data. `[Scryfall prints search]`
- **Maniak's only Orzhov-watermark card** — Tithe Drinker is the ONLY card with an Orzhov watermark in Slawomir Maniak's 222+ card MTG catalog. All his other vampire work is Innistrad-plane. `[Scryfall: a:"Slawomir Maniak" e:rna OR e:gpt OR e:dgm]`
- **Dragon's Maze reception + Pauper exception** — Set widely called one of the weakest ever; prerelease attendance ~50% down from Gatecrash. MTGSalvation Pauper set review called Tithe Drinker "the best [common] in this set." `[MTGSalvation Pauper review thread]`
- **Dragon's Maze narrative** — The set centers the implicit Maze race; Orzhov's named champion was Teysa Karlov. The depicted vampire on Tithe Drinker is unnamed/generic, not Teysa. Jace became the Living Guildpact at the set's conclusion. `[MTGSalvation Player's Guide; MTG Wiki: Dragon's Maze]`
""",

    "cards/magic-the-gathering/ravnica-allegiance/190-lawmage-s-binding.md": """\

## Trivia (second pass)

- **Azorius three-column hierarchy** — Lawmages belong to the Lyev column. Azorius Senate structure: Jelenn / Lyev / Sova columns, with triangle-crest encoding on apparel. `[MTG Wiki: Azorius Senate]`
- **Pacifism lineage correction** — Pacifism's earliest printing is Mirage (October 1996, no. 32) — NOT Alpha 1993 as the first-pass brief suggested. 42 total printings to date. `[Scryfall: MIR no. 32]`
- **Temporal Isolation footnote precision** — The Hipsters "Designs of RNA" article specifically names Temporal Isolation (Time Spiral) as the disqualified near-precedent — structural footgun distinction (can't remove from combat) explained at length. `[Hipsters of the Coast: "Designs of RNA," 2019-01]`
- **Detain-to-permanent-aura trajectory** — Detain (RTR 2012 keyword) → Lawmage's Binding (RNA 2019 enchantment). Same functional clause ("can't attack or block, activated abilities can't be activated"), different permanence — keyword temporary effect translated to permanent aura. `[MTG Wiki: Detain]`
- **Jumpstart Rainbow deck** — Full 20-card deck contents confirmed. Lawmage's Binding is the deck's SOLE creature lockdown. `[Wizards: Jumpstart Decklists 2020-06-18; Scryfall JMP 453]`
""",

    "cards/magic-the-gathering/modern-horizons-3/31-indebted-spirit.md": """\

## Trivia (second pass)

- **MH3 as draft-innovation set** — 528 cards, released June 14 2024. Bypasses Standard; injects directly into Modern. Combines over 70 keyword abilities. Bestow returning alongside Afterlife on the same card is a direct product of the mechanic-showcase philosophy. `[Scryfall set metadata]`
- **Bestow + Rosewater's favorite mechanic confession** — Bestow debuted in Theros (September 2013), with only rare reappearances (Commander 2018) in 11 years before MH3. When a fan noted its return, Rosewater responded on Blogatog: *"Bestow is my favorite mechanic from OG Theros."* Storm Scale 6-7. `[Blogatog post 752578620798730240, 2024]`
- **Afterlife mechanic framing (Wizards official)** — Debuted as the Orzhov guild mechanic in Ravnica Allegiance (January 2019). The official mechanics article: *"Just because someone's mortal form has diminished into disuse, the spirit within may be free to serve."* `[Wizards: Ravnica Allegiance Mechanics, 2019]`
- **THE FIRST CARD ever to carry both Bestow AND Afterlife** — `[Cross-reference: Scryfall search for both keywords on one card returns exactly Indebted Spirit]`
- **Draftsim called it out** — *"Bestowing Indebted Spirit looks absolutely silly. For 3 mana, you get a +1/+1 aura, a 1/1 creature and two 1/1 fliers thanks to afterlife."* EDHREC rank 7,972 confirms it as a draft-role uncommon rather than a Commander staple. `[Draftsim: MH3 Limited Set Review]`
- **Artist L.A. Draws** — therealola.artstation.com. Confirmed credits: Blood Artist (Innistrad Remastered), Whirling Quicksand, Demonic Contract, Hate Mirage, The Phasing of Zhalfir, Telling Time. No Hipsters of the Coast profile found as of 2026-05. `[ArtStation; artofmtg.com]`
""",

    "cards/magic-the-gathering/modern-horizons-3/21-charitable-levy.md": """\

## Trivia (second pass)

- **"Collection counter" is corpus-unique** — Full Scryfall oracle search for enchantments bearing "collection counter" returns EXACTLY ONE result: Charitable Levy. Named counters prevent cross-card bookkeeping confusion; here the name reads as a thematic label for the tithe-collection process itself. `[Scryfall API oracle search, 2026-05]`
- **Noncreature-spell-tax lineage** — Glowrider (Legions, 2003-02-03) was the identically-worded Rare creature ancestor. Thalia, Guardian of Thraben (Dark Ascension, 2012) became the canonical staple form. Charitable Levy is the FIRST ENCHANTMENT in this lineage to impose the tax and carry a built-in self-destruct threshold — applies the tax exactly three times before converting itself into card advantage and a Plains tutor. `[Scryfall: Glowrider oracle_id; Thalia oracle_id]`
- **Vs. Smothering Tithe** — Architecturally distinct: Smothering Tithe (RNA 2019) taxes opponent card draws, generates Treasure tokens indefinitely, never self-terminates. Charitable Levy taxes all players' noncreature spells, counts its own triggers toward a fixed exit threshold, liquidates as cantrip + land tutor. Both white enchantment taxation, opposite philosophies — infinite accumulator vs. self-liquidating tempo speed-bump. `[Scryfall: both cards]`
- **WotC ruling 2024-06-07** — The triggered ability resolves before the taxed spell and fires even if the triggering spell is countered — the collection counter advances regardless of whether the spell resolves. `[Scryfall rulings API]`
- **EDH adoption** — 19,480 Commander decks per EDHREC (Scryfall rank 6,766) as of 2026-05 — substantial inclusion for an uncommon in a Modern-targeted set. Commander's Herald budget review: *"a tax piece that replaces itself and ramps you... it taxes your own spells, but if you can play creatures until it cracks, it is nothing but upside."* `[EDHREC; Commander's Herald: MH3 Set Review — Budget]`
- **Eli Minaya — debut context** — Approached by AD Zack Stella in 2021. MTG debut Dominaria United (2022): Love Song of Night and Day, Cosmic Epiphany. Primary background: science fiction/fantasy novel cover illustration (Tor Books, Amazon Publishing). Self-described dream commission: "a set of lands with really abstract and textured takes on Swamps and Plains." 36 Gatherer credits by MH3. `[Star City Games: SCG 2022 interview; Gatherer]`
""",

    "cards/magic-the-gathering/throne-of-eldraine/95-malevolent-noble.md": """\

## Trivia (second pass)

- **Source tale: Bluebeard (Perrault, 1697)** — TV Tropes classifies this card explicitly under "The Bluebeard" trope as an "Adaptational Heroism" variant: the noble applies Bluebeard's lure-then-kill structure to witches rather than wives, using the witches' own appetite for children's bones as the lure. Evil-vs-evil dynamic characteristic of Eldraine's fractured fairy-tale register. `[TV Tropes: The Bluebeard]`
- **Bait works because ELD canon makes witches predatory toward children** — The Wizards Planeswalker's Guide to Eldraine (2019-10-31) describes ELD witches as "shadowy human warlocks that reside in the wilds, so disconnected from the rest of humanity that most consider them to be fair folk" who "take great joy in their evil deeds" and are known for stealing children and poisoning towns. The Noble's promise of "fresh children's bones" is credible IN-fiction precisely because Wizards canon made the witches' child-appetite explicit. `[Wizards: Planeswalker's Guide to Eldraine]`
- **Rosewater's exact quote on adding Noble in ELD** — *"The game just has a lot of people whose job it is to rule over others, and it felt weird not to have a class that covered that. Throne of Eldraine was full of kings and queens, princes and princesses, so it seemed like the right time to finally add Noble."* `[Wizards: More Odds & Ends: Throne of Eldraine, Rosewater, 2019-10-21]`
""",

    "cards/magic-the-gathering/throne-of-eldraine/86-eye-collector.md": """\

## Trivia (second pass)

- **Rankle's dual design source** — In MaRo's November 2019 ELD vision-design handoff article, Rankle is described as both "Deal-Making Imp — a nod to Rumpelstiltskin" AND the plane's Puck figure from A Midsummer Night's Dream. Eye Collector's tribute mechanic sits squarely in the Rumpelstiltskin extraction vein. `[Wizards: Throne of Eldraine Vision Design Handoff Part 2, 2019]`
- **Rankle's extended-lore arc** — Rankle does not appear as a creature card in Wilds of Eldraine (Sept 2023); his WOE presence is the spell Rankle's Prank (WOE 102, flavor: "The louder they scream, the harder he laughs."). His creature-card return came in March of the Machine (April 2023) as Rankle and Torbran (MOM 252). The Wizards story "The Adventures of Rankle, Master of Love" covers this arc — no mention of named eye-collectors or servants. `[Scryfall; Wizards story]`
- **6-year reprint gap** — Eye Collector received its first reprint in Foundations Jumpstart (J25, 2025), card no. 439 — six years after ELD. Rankle has been reprinted in Commander Masters, OTC, and as an Arena Alchemy variant. Over 1,000 Commander decks run Rankle as general (rank 1,294) — mythic demand drove reprints while the common courier waited. `[Scryfall prints history]`
- **Uriah Voth** — 67 Gatherer credits as of 2026. ELD credits: Eye Collector and Bramblefort Fink (ELD 311). No Hipsters artist profile found. `[Gatherer artist search]`
- **Pauper / PDH legal** — 1-mana 1/1 flyer with on-hit mill fits Pauper UB Faeries shells and PDH mill lists. `[Scryfall legalities]`
""",

    "cards/magic-the-gathering/core-set-2021/35-secure-the-scene.md": """\

## Trivia (second pass)

- **Sole printing** — Scryfall confirms `reprint: false`, single result in the oracle prints search. M21 is the first and only printing. No Ravnica predecessor card exists; the Azorius flavor is tonal borrowing, not a port. `[Scryfall API]`
- **Judith as color-anomalous flavor speaker** — Among the ~15 cards Judith the Scourge Diva is quoted on across MTG history, nearly all carry Rakdos color identity (R, B, or BR). Secure the Scene (mono-W) appears to be the ONLY outlier — the joke lands because she is the maximally wrong guild-voice to be commenting on an Azorius arrest. `[Scryfall ft:Judith card list]`
- **Azorius visual canon source** — *Plane Shift: Ravnica* (WotC official D&D supplement, 2018) canonically describes Azorius magic as "blue or golden runes floating and glowing in the air in circular patterns or shimmering azure barriers." The luminous bindings in Boros's art are the official house visual for Azorius enforcement spells. `[Plane Shift: Ravnica, WotC 2018]`
- **Boros-Szikszai solo-career context** — Zoltan Boros and Gabor Szikszai's partnership ran 1986–2010; Zoltan relocated to New York at dissolution. This 2020 card is a decade-into-solo commission. Both artists still co-sign convention cards. `[boros-szikszai.com; DV Media interview]`
""",
}


def append_section(path: Path, content: str) -> bool:
    """Append content to file. Returns True if appended, False if skipped (marker present)."""
    text = path.read_text(encoding="utf-8")
    if "## Trivia (second pass)" in text:
        return False
    # Ensure clean newline boundary
    if not text.endswith("\n"):
        text += "\n"
    text += content
    path.write_text(text, encoding="utf-8")
    return True


def main():
    appended = []
    skipped = []
    missing = []
    for rel, content in DATA.items():
        path = REPO / rel
        if not path.exists():
            missing.append(rel)
            continue
        if append_section(path, content):
            appended.append(rel)
        else:
            skipped.append(rel)

    print(f"appended: {len(appended)}")
    for r in appended:
        print(f"  + {r}")
    print(f"skipped (already had 2nd pass): {len(skipped)}")
    for r in skipped:
        print(f"  · {r}")
    if missing:
        print(f"MISSING: {len(missing)}")
        for r in missing:
            print(f"  ! {r}")


if __name__ == "__main__":
    main()
