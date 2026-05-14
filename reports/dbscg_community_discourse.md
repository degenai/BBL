# DBSCG Community Discourse on Full-Res Card Images — Report

_Investigation date: 2026-05-13. Time-boxed ~30 min. Research-only._

## TL;DR

Bandai's image policy is **structurally restrictive across all their TCGs** — but DBSCG is the only one of the big three Bandai card games (One Piece, Digimon, DBSCG) that **never developed a community-built full-res API**. The legacy DBSCG (2017-2024) was renamed "Masters" in 2024 alongside the Fusion World launch; it is still officially supported but community energy has visibly pivoted to Fusion World, where the only credible "API" (`api-dbscg-fw`) and the most active database (`dragonball.gg`) live. **No high-res community scan archive for legacy DBSCG was found.** The 260x363 ceiling appears to be the realistic terminal state unless Alex (or someone) builds one. The art IS out there in retail/scanned form, but it is not aggregated.

## Findings

### Community sentiment

Reddit indexing for r/DragonballSuperTCG / r/DBSCG turned up effectively no surfaced threads on image-archive complaints — searches for "high resolution," "scryfall equivalent," "image rip / scan," and "card database" returned zero direct community threads from Reddit indexed by Google. This is itself a signal: either the discourse lives on Discord (which is non-indexable without accounts) or the community is small enough that the complaint never became load-bearing.

- **Steam Workshop, "Dragon Ball Super TCG All cards from Cross Worlds up to Colossal Warfare"** (`https://steamcommunity.com/sharedfiles/filedetails/?id=1324525524`) — the mod author has acknowledged on the Workshop description that "the company is making high resolution images of cards less and less available" and ended up using **lower-resolution images with watermarks** because high-quality player scans were unfindable at scale. This is the closest thing to a primary-source confirmation of Bandai's deliberate downgrade strategy that surfaced.
- **Kanzenshuu DBSCG forum thread** (`https://www.kanzenshuu.com/forum/viewtopic.php?t=48445`) — appeared in results but no extracted content; Kanzenshuu is the long-running Dragon Ball discussion forum, so any image-archive complaints would likely live here rather than Reddit.
- **DBS Card Game Discord** (`https://discord.com/invite/dragon-ball-super-card-game-325124744145797123`) — the official DBSCG Discord exists and is large; full discourse is gated behind sign-in and cannot be indexed via web search.

### Bandai's policy / behavior

- **No DMCA history surfaced.** Searches for Bandai DMCAs against card-image archives returned zero relevant hits. The only Bandai DMCA activity in the search corpus was the 2014-era takedown of Durante's Dark Souls modding tool (DSFix) — unrelated. The absence of DMCA enforcement combined with the absence of community archives suggests **Bandai doesn't need to enforce because nobody has built the thing to enforce against**. The chilling effect is structural rather than enforcement-driven.
- **Terms of Service are maximalist** across all Bandai Namco properties (Bandai Namco Holdings, Bandai Namco Entertainment America, BANDAI TCG+) — explicit prohibitions on "copying, reproducing, downloading, broadcasting, transmitting, commercially exploiting and/or distributing" any site content including images. User-generated content provisions grant Bandai a "perpetual, irrevocable, royalty-free, fully-transferable, and sub-licensable" right over anything posted. This is the standard hostile-fan-use ToS posture.
- **Bandai's own legacy treatment** — DBSCG was rebranded to "Masters" in 2024 when Fusion World launched. Critically, **the legacy game is still officially supported** — Championship 2025-2026 events exist, new product (Premium Anniversary Box 2025) is shipping. So this is not a fully-orphaned game; it's a continuing line that got de-emphasized in marketing while Fusion World gets the spotlight. The official image-serving infrastructure at `dbs-cardgame.com/asia/cardlist/` and `dbs-cardgame.com/us-en/` is still operational, still serving the same 260x363 thumbnails.

### Bandai cross-game image comparison (the load-bearing finding)

| Bandai game | Community API exists? | Image quality available | Notes |
|---|---|---|---|
| **One Piece TCG** (2022-present) | YES — **OPTCG API** (`optcgapi.com`) free, full coverage OP-01 through OP-15+ | Higher-res than DBSCG; pulls from official Bandai image IDs | Community-built; image URLs are direct pointers to official assets |
| **Digimon TCG** (2020-present) | YES — **DigimonCard.io API** (15 req/10s rate limit, full DB) | "High-quality images" per app reviews; explicitly fan-built scraper of official Bandai sources | Most mature of the three; also has Digimon Card Dev, niamu/digimon-card-game on GitHub |
| **DBSCG / Masters** (2017-present) | **NO** — only `api-dbscg-fw` exists, which is **Fusion World only** | 260x363 thumbnails ceiling | Legacy Masters has no equivalent API surface |
| **DBSCG Fusion World** (2024-present) | Partial — `api-dbscg-fw` (Node/Express, GitHub) + `dragonball.gg` | Image quality unverified; UI is more modern than legacy DBSCG | All community energy is here, not Masters |

This is the meaningful pattern. **Bandai's restrictive policy is identical across all three games, but only DBSCG failed to grow a Scryfall-class community archive.** That's likely because:
1. One Piece and Digimon got their community-API momentum during the post-2020 TCG boom with newer dev cultures
2. DBSCG launched in 2017 before that ecosystem matured, and by 2024 when it could have caught up, the player base was being split/pulled to Fusion World

### Dead / non-existent community projects

- **DeckPlanet** — **NOT dead.** Search results confirm it is currently active at `deckplanet.net` and `dbs-deckplanet.com`, supporting DBS Masters, DBS Fusion World, Gundam Card Game, Alpha Clash, and more. v70 update was shipped. Has an active Patreon and YouTube channel. The prior investigator's "GCS bucket stopped updating mid-2023" claim was not corroborated in this pass — DeckPlanet appears to have **pivoted toward Fusion World coverage** rather than died. Whether their legacy DBSCG/Masters card database is still being maintained at parity with new sets is the open question, and would require direct site inspection (blocked by WebFetch permissions in this pass).
- **Karuto's DBSCG database** — **No evidence found.** Search for "Karuto" + DBSCG returned no matches. May have been an old Discord-only project that never had a public web presence, or the name is misremembered.
- **Any "DBSAPI" / "DBS-TCG-API" GitHub project for legacy DBSCG** — **None exists.** The only GitHub API project is `teoisnotdead/api-dbscg-fw`, explicitly for Fusion World. `amandagrice/dbscg-maker` is a custom-card maker, not a scan archive. `orouet/DBSCG-Rules` is rules text only.
- **`dbscg.tools`** — exists ("Advanced Search and Deck builder"), but content not extractable in this pass; appears to be a community deck builder pulling from official 260px sources.
- **`dragonball.gg`** — active, well-built, but **Fusion World only by self-description**. Has card DB, meta tier list, builder, collection sync. Does not cover legacy Masters.
- **CCG Trader** (`ccgtrader.net`) — has a legacy DBSCG section, but it's an old-school retailer-aggregator, image quality almost certainly matches Bandai's 260px or worse.
- **RetroDBZccg** — covers the older Score/Panini Dragon Ball Z CCG (pre-2017), not the Bandai DBSCG. Not relevant for this corpus.

### Fusion World transition impact

The Fusion World launch in 2024 is the load-bearing event:
- It split community attention away from DBSCG/Masters at exactly the moment a community-built API could have crystallized.
- Bandai did NOT actively remove legacy DBSCG resources — the official card list at `dbs-cardgame.com/asia/cardlist/` is still live and still serves 260x363 thumbnails. But all the new community tooling (api-dbscg-fw, dragonball.gg) targets Fusion World exclusively.
- The Bandai TCG+ digital client and the Fusion World digital version (Steam, Feb 2024) are the channels Bandai actively invests in. Legacy paper Masters gets championship support but no new platform investment.
- Net effect: **legacy DBSCG is in a "supported but stagnant" state for image resources.** No one is going to build a Scryfall for it now because the active dev community is busy with Fusion World.

### The 260x363 anomaly

Bandai serves 260x363 across all their card-game websites — it's not DBSCG-specific. One Piece TCG and Digimon TCG official sites use the same thumbnail-class size. The difference is that those communities built scraper-APIs that wrap the official source and (in some cases) get higher-res via in-app channels or alternate ripping methods. The 260x363 ceiling is **Bandai-standard, not DBSCG-degraded**. So Alex's intuition that DBSCG was specifically degraded is half-right: the resolution ceiling is the same across Bandai's TCG portfolio, but DBSCG is the only one where no community workaround exists.

The "art IS out there" framing is correct in the sense that:
- The Bandai TCG+ digital app surfaces higher-res rendered cards in-client (extractable with effort)
- Tournament/marketing assets used on Bandai's blog and event posts are higher-res (one-off, not cataloged)
- Player scans exist on Twitter/Discord/Imgur for popular cards (uncataloged, scattered)
- Retailer photos (eBay, TCGplayer, Cardmarket listings) are user-uploaded scans of variable quality

But there is no aggregator. The dbzexchange ~30% partial coverage Alex already found is likely the ceiling of "credibly cataloged" high-res availability for legacy DBSCG.

### Hot-mod / fan-scan finds

- **Steam Workshop Tabletop Simulator mods** — multiple DBSCG mods exist (IDs 951613891, 1324525524, 3133475660). These embed card images in TTS-playable format. Authors have explicitly noted the high-res unavailability problem. Resolution in TTS mods is typically 350-500px to keep file sizes reasonable; not a true high-res archive but better than 260px.
- **Internet Archive** — search returned only `archive.org/details/dbscg` (a Bandai tutorial video) and `dbsengloi`. **No dedicated high-res DBSCG card scan collection on archive.org.** This is in contrast to other Bandai products where 1200DPI box/manual scans exist (Super Dragon Ball Z PS2, DBZ Super Gokuu Den SFC).
- **Imgur / Mediafire / Drive folders** — none surfaced via web search. Would require Discord access to find.
- **`gaming-archive.org`** — no relevant results.

## Comparison: MTG / Pokemon TCG / DBSCG

| Game | Publisher policy | Community API | Image quality |
|------|------------------|---------------|---------------|
| MTG | Permissive, Scryfall-encouraged | Scryfall (universal) | Scryfall scan + Wizards art-crop, 672x938 normal, 1500px+ art_crop |
| Pokemon TCG | Tolerant; PokemonTCG.io + Bulbapedia coexist | Both volunteer-built, full coverage | 734-1500px |
| One Piece TCG (Bandai) | Restrictive ToS | OPTCG API (free, full) | Higher than 260px via official-image-ID indirection |
| Digimon TCG (Bandai) | Restrictive ToS | DigimonCard.io API (rate-limited, full) | "High-quality" per reviews; community-scraped |
| **DBSCG / Masters (Bandai)** | **Restrictive ToS** | **None for legacy; api-dbscg-fw covers Fusion World only** | **260x363 universal; ~30% partial higher-res via dbzexchange** |
| DBSCG Fusion World (Bandai) | Restrictive ToS | api-dbscg-fw partial | Unverified, likely modest improvement over legacy |

## Strategic implications for BBL

1. **The partial-coverage hybrid is the realistic ceiling for now.** No credible community-archive route was missed in the prior investigation. dbzexchange ~30% + Bandai 260x363 default is the actual best-available state for legacy DBSCG / Masters cards as of mid-2026.

2. **There is no Karuto / DeckPlanet ghost archive to resurrect.** DeckPlanet is alive but pivoted to Fusion World coverage; Karuto's database does not surface anywhere indexable. Neither is a hidden source of higher-res scans.

3. **The "build it ourselves" option is real but expensive.** A community-API for legacy DBSCG would need to: (a) scrape the official Bandai card list for IDs and the 260px thumbnails as base; (b) supplement with player-scan crowdsourcing (Discord, Twitter, eBay listings) for higher-res inserts. This is structurally similar to what DigimonCard.io did, and the Bandai legal posture is identical — so the precedent that nobody got DMCA'd for Digimon is the relevant safety check. **But** the active player base is now on Fusion World, so volunteer energy for a legacy project would be hard to recruit.

4. **For BBL specifically, accept the asymmetry.** MTG cards in a Bundle get Scryfall full-res, Pokemon cards get PokemonTCG.io / Bulbapedia high-res, DBSCG cards get 260x363 thumbs with optional dbzexchange supplementation for the ~30% covered. This is not a project blocker — it just means DBSCG bundles will visually present at a lower visual fidelity tier than MTG / Pokemon bundles. Worth a one-line "image quality note" in the buyer-facing storefront if DBSCG bundles ever ship.

5. **The Bandai TCG+ in-app render path is the only credible "upgrade" route** for higher-res that hasn't been investigated. If the digital client renders cards at higher resolution (mobile/tablet displays demand it), and those rendered assets can be cached/extracted via inspection of the BANDAI TCG+ app's network traffic — that's a potential community-archive seed. Not investigated in this pass; warrants a follow-up if Alex wants to push past the 260px ceiling. ToS exposure is the same as for any Bandai-asset extraction (their ToS forbids all of it, but their DMCA enforcement has been effectively zero against community-archive projects to date).

## Sources

### Primary findings
- [Steam Workshop: Dragon Ball Super TCG All cards from Cross Worlds up to Colossal Warfare](https://steamcommunity.com/sharedfiles/filedetails/?id=1324525524) — mod author's explicit acknowledgment that Bandai is making high-res images "less and less available"
- [Steam Workshop: Dragon Ball Super Card Game (TTS mod)](https://steamcommunity.com/sharedfiles/filedetails/?id=951613891)
- [Steam Workshop: DBSCG Masters/Fusion World TS](https://steamcommunity.com/sharedfiles/filedetails/?id=3133475660)

### Bandai legal / ToS
- [Terms of Service | BANDAI TCG+](https://lp.bandai-tcg-plus.com/terms/en/)
- [Terms of Use | Bandai Namco Holdings Inc.](https://www.bandainamco.co.jp/en/terms/index.html)
- [Bandai Namco Entertainment America Terms](https://www.bandainamcoent.com/legal/terms)
- [Intellectual Property for Social Good | Bandai Namco Holdings](https://www.bandainamco.co.jp/en/sustainability/materiality/ip/index.html)

### DBSCG official infrastructure
- [Dragon Ball Super Card Game (official)](https://www.dbs-cardgame.com/)
- [DBSCG Card Search (legacy/Masters)](https://www.dbs-cardgame.com/asia/cardlist/?search=true)
- [Dragon Ball Super Card Game Fusion World (official)](https://www.dbs-cardgame.com/fw/en/)
- [Fusion World Card Database](https://www.dbs-cardgame.com/fw/en/cardlist/?search=true&category%5B0%5D=583009)
- [Dragon Ball Super Card Game is Moving to the Next Level (Fusion World announcement)](https://en.dragon-ball-official.com/news/01_2061.html)
- [Championship 2025-2026](https://www.dbs-cardgame.com/event/exhibition-event/championship2025/)

### Community sites for DBSCG / Masters / Fusion World
- [DeckPlanet (multi-game, alive)](https://www.deckplanet.net/)
- [DBS DeckPlanet card database (Masters)](https://www.deckplanet.net/dbs_masters/card-db)
- [DBS DeckPlanet card database (Fusion World)](https://www.deckplanet.net/fusion_world/card-db)
- [DBS DeckPlanet Patreon](https://www.patreon.com/dbs_deckplanet/about)
- [DragonBall.gg (Fusion World focus)](https://dragonball.gg/)
- [DBSCG Toolbox](https://dbscg.tools/)
- [CCG Trader DBSCG database](https://www.ccgtrader.net/games/dragon-ball-super-card-game/)
- [DBZ Exchange (retailer with partial high-res)](https://dbzexchange.com/)
- [Kame for Dragon Ball TCG (iOS app)](https://apps.apple.com/us/app/kame-for-dragon-ball-tcg/id6740748864)
- [Collectr (multi-TCG tracker)](https://getcollectr.com/)

### Bandai cross-game comparison (the load-bearing comparison)
- [OPTCG API home](https://www.optcgapi.com/) — One Piece community API
- [OPTCG API about](https://optcgapi.com/about/general)
- [Limitless One Piece database](https://onepiece.limitlesstcg.com/cards)
- [DigimonCard.io](https://digimoncard.io/) — Digimon community DB
- [DigimonCard.io API docs](https://digimoncard.io/api-documentation)
- [Digimon TCG API (Postman)](https://documenter.getpostman.com/view/14059948/TzecB4fH)
- [niamu/digimon-card-game GitHub (Bandai scraper)](https://github.com/niamu/digimon-card-game)
- [JustTCG API docs (added Fusion World 2025-12-15)](https://justtcg.com/docs)
- [Sabatcg: Bandai's Top 3 Card Games Sales 2017-2025](https://sabatcg.com/bandais-top-3-most-successful-card-games-sales-and-revenue-from-2017-to-2025)

### GitHub projects (DBSCG ecosystem)
- [teoisnotdead/api-dbscg-fw (Fusion World API)](https://github.com/teoisnotdead/api-dbscg-fw)
- [amandagrice/dbscg-maker (custom card maker)](https://github.com/amandagrice/dbscg-maker)
- [orouet/DBSCG-Rules](https://github.com/orouet/DBSCG-Rules)

### Discord / forum surfaces (gated, not indexable)
- [Official DBSCG Discord](https://discord.com/invite/dragon-ball-super-card-game-325124744145797123)
- [Kanzenshuu DBSCG discussion](https://www.kanzenshuu.com/forum/viewtopic.php?t=48445)

### Scryfall (MTG benchmark)
- [Scryfall card imagery API](https://scryfall.com/docs/api/images)
- [Scryfall: High resolution images](https://scryfall.com/blog/high-resolution-images-50)

### Archive.org (negative result — no DBSCG scan collection)
- [archive.org Bandai DBSCG tutorial](https://archive.org/details/dbscg) — video only, not scans
