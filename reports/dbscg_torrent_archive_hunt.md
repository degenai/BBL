# DBSCG High-Res Archive Hunt -- Findings

## TL;DR

No single community-preserved torrent or Internet Archive dump of all DBSCG Masters card images was found. The most actionable path is the TTS "ALL CARDS HD" mod (Steam Workshop ID 1699347294) combined with the DeckPlanet GCS CDN (`storage.googleapis.com/deckplanet_card_images/{cardId}.png`), both of which cover every Masters set. TCGAPIs remains the cleanest paid option if local ownership is deprioritized.

---

## Promising Leads (viable acquisition paths)

### TTS "Scripted + ALL CARDS HD" -- Every Set, Constantly Updated
- **URL:** https://steamcommunity.com/sharedfiles/filedetails/?id=1699347294
- **Companion site:** https://sites.google.com/view/dbstts
- **Scope:** Every Masters set (5,000+ cards); explicitly self-described as "no more playing with low-res sample cards, all in HD"
- **Resolution:** Not confirmed by pixel count in public-indexed content, but TTS card sheets can go to 4096px wide; the mod author specifically sourced higher-res images than Bandai's 260px CDN serves
- **Live status:** Actively maintained as of searches in May 2026; companion YouTube channel (@DBSTS) active
- **Acquisition path:** TTS Workshop mod files embed images as URLs (typically stored on Imgur, Dropbox, or a private CDN). The `ttsbackup` npm tool (`github.com/stefankendall/ttsbackup`) can download the mod's manifest and spider all image URLs locally. This gives you the full image corpus without touching a torrent.
- **Friction:** Requires owning TTS (~$20 on Steam); then running ttsbackup against mod ID 1699347294. Fully legal under Steam Workshop ToS. Images are Bandai's IP but the community redistribution is unenforced (confirmed per `dbscg_community_discourse.md`).

### DeckPlanet GCS CDN (Free, public, no auth)
- **CDN URL pattern:** `https://storage.googleapis.com/deckplanet_card_images/{card_number}.png`
- **Source:** Confirmed from `dragogodev/cgs` cgs.json config (`github.com/dragogodev/cgs`) -- the Card Game Simulator project points to this bucket for DBSCG Masters images
- **API:** `https://dbs-deckplanet-api.com/items/cards?limit=-1` returns full card list with `card_number` identifiers; iterate and pull each image
- **Coverage:** DeckPlanet covers Masters (dbs-deckplanet.com / deckplanet.net/dbs_masters); they are an active community platform as of May 2026 with Patreon and Discord
- **Resolution:** Unknown pixel dimensions without a live probe, but this is a modern (2022-2026) community platform explicitly built for display use; likely substantially above Bandai's 260px
- **Friction:** Zero dollars, zero sign-up. Script the API dump: GET `/items/cards?limit=-1`, collect all `card_number` values, mass-download the GCS URLs. This is the cleanest free path.
- **Risk:** GCS bucket is publicly listed but not officially blessed; if Bandai ever requested takedown it would disappear. Also resolution is unconfirmed -- needs a probe call before committing to a full download.

### OCTGN Image Pack Infrastructure (hi-izuru.org)
- **Distribution pages:**
  - https://cosmoascse.weebly.com/dbs-card-game-octgn-image-packs.html -- "Download all sets" link documented; appears to offer per-set or all-sets bulk download
  - https://keyshor.weebly.com/dragon-ball-super-octgn-image-packs.html -- per-set OCTGN image packs for Dragon Ball Super
  - http://www.hi-izuru.org/OCTGN -- primary host for OCTGN image packs (multiple TCGs)
- **Resolution:** OCTGN image packs are typically card-face PNGs at whatever resolution the community sourced. Pre-Bandai-downgrade packs may contain 500-800px+ images. Post-downgrade packs may have mix. Resolution unconfirmed without browsing the actual pack files.
- **Live status:** hi-izuru.org was referenced in multiple community threads as the canonical host; live status unconfirmed (site predates Bandai's image downgrade era). Weebly pages confirmed indexed.
- **Coverage:** Set-by-set; the weebly pages document individual set packs + a bulk "all sets" option. Coverage extent across all BT sets is unconfirmed.
- **Friction:** Medium -- navigate the distribution pages, verify links are live, download. Likely older and may stop at a certain set if the OCTGN community abandoned DBSCG support.

### TCGAPIs (Paid -- $7/month Hobby tier)
- **URL:** https://tcgapis.com/
- **Scope:** Dragon Ball Super is explicitly listed among 80+ TCGs covered
- **Resolution:** "Hotlinkable image URLs in multiple resolutions for every card and every printing -- alt arts, full arts, borderless, promos" (confirmed from their marketing copy)
- **Coverage:** Described as universal -- every printing, every variant
- **Live status:** Active SaaS product as of May 2026
- **Friction:** $7/month subscription; cancel after bulk download. Requires agreeing to ToS, which may prohibit bulk download for local storage. Check ToS before subscribing.
- **Note:** This is the coverage guarantee option. If DeckPlanet CDN has gaps, TCGAPIs fills them.

---

## Verified Internet Archive Collections

None found specific to DBSCG Masters card images.

- `archive.org/details/dbscg` -- Bandai's 2017 tutorial application (software, not card images)
- `archive.org/details/dbscg-fw-launcher-...` -- Fusion World launcher executable (software)
- `archive.org/details/zteamdbs` -- Content type unclear from search snippets; may be video/manga, not card images
- `archive.org/details/dbsengloi` -- Appears to be Dragon Ball Super episode video files

The Pokemon TCG and Yu-Gi-Oh card image archives that exist on Archive.org have no confirmed DBSCG analog. This is a gap in preservation community coverage.

---

## GitHub Repos with Image Hoards

### dragogodev/cgs
- **URL:** https://github.com/dragogodev/cgs
- **Role:** Card Game Simulator data repo; includes Dragon Ball Super Masters + Fusion World cgs.json configs
- **Image posture:** Does NOT host images; instead, `cgs.json` points to `storage.googleapis.com/deckplanet_card_images/{cardId}.png` as the live CDN. This is the authoritative pointer to where community images live.
- **Last updated:** Active as of prior investigation
- **License:** None stated; community project

### zz1000zz/OCTGN_DBS
- **URL:** https://github.com/zz1000zz/OCTGN_DBS
- **Role:** OCTGN patch / plugin for DBSCG; likely contains image pack references or a set-manifest for hi-izuru.org image packs
- **Image posture:** Game plugin, not an image hoard. Would need inspection to confirm whether it bundles any images or only references external packs.
- **Resolution:** Not confirmed

### PatrickPierce/bandai-scraper
- **URL:** https://github.com/PatrickPierce/bandai-scraper
- **Role:** Web scraper for Bandai TCG sites; currently documented as One Piece only, but the architecture is Bandai-generic and could be adapted for DBSCG
- **Image posture:** Scraper tool, not a hoard. Could be adapted to pull from dbs-cardgame.com if Bandai's CDN exposes higher-res URLs not previously found. Low likelihood given Bandai's deliberate downgrade.

### amandagrice/dbscg-maker
- **URL:** https://github.com/amandagrice/dbscg-maker
- **Role:** Custom card builder app; not an image archive. Dead end for this purpose.

---

## TTS Workshop Mods with Embedded Images

### "Dragon Ball Super Card Game - Scripted + ALL CARDS HD (Every set, constantly updated)"
- **URL:** https://steamcommunity.com/sharedfiles/filedetails/?id=1699347294
- **Subscriber count:** Not confirmed from search snippets (Steam blocks indexing of subscriber counts)
- **Last updated:** Actively maintained as of May 2026 per search results
- **Image resolution:** Claimed HD; TTS supports up to 4096px sheet width; actual per-card dimensions depend on how the author tiled the deck sheets. Likely 400-800px per card face based on TTS community norms ("about 500x720 is a good size").
- **Coverage:** Every Masters set + continuously updated
- **Image acquisition:** Use `ttsbackup` tool to download the mod's asset manifest and spider all remote image URLs to local storage. The mod JSON lives in your TTS cache after subscribing; ttsbackup then re-hosts them locally.

### "Dragon Ball Super Card Game Masters/Fusion World TS"
- **URL:** https://steamcommunity.com/sharedfiles/filedetails/?id=3133475660
- **Notes:** Newer mod covering both Masters and Fusion World; HD status unconfirmed but mentioned in the same search results cluster as the HD mod

### "Dragon Ball Super CCG Sets 1 & 2"
- **URL:** https://steamcommunity.com/sharedfiles/filedetails/?id=1168301242
- **Notes:** Older, limited to sets 1-2; images taken directly from the official website at time of creation (pre-downgrade era); may be higher res than what Bandai now serves. Limited coverage.

---

## Dead Ends Documented

- **Torrent indexes (TPB, 1337x, Nyaa, RuTracker):** No DBSCG card image archive torrent surfaced in any search. Nyaa returns only Dragon Ball Super anime/manga content. RuTracker returned nothing relevant. This vector is likely empty -- the DBSCG community never consolidated a torrent dump the way Magic and Pokemon communities have.
- **Internet Archive dedicated image collection:** Does not exist. Only software (tutorial app, FW launcher) is preserved there.
- **Reddit/MediaFire/MEGA direct links:** No threads confirmed with live image dump links. The community discourse indicates such links existed in 2018-2022 era but are not indexable or have rotted.
- **CCG GAMEZ scanner:** Has a Dragon Ball Z CCG section (game ID 126), not confirmed for DBSCG Masters. Likely covers only pre-2017 DBZ CCG.
- **dragogodev/cgs images hosted in-repo:** Repo contains only JSON configs, no image files. All images are remote CDN.
- **PatrickPierce/bandai-scraper for DBSCG:** Explicitly One Piece only at time of search; not adapted for DBSCG.
- **TTS image extraction as standalone archive:** TTS mod images are spread across external URLs (Imgur, Dropbox, etc.) referenced in the mod JSON -- they are not a self-contained archive. They only become local via a tool like ttsbackup.

---

## Recommended Acquisition Order

1. **Probe DeckPlanet GCS CDN first.** Hit `https://dbs-deckplanet-api.com/items/cards?limit=3`, grab a few `card_number` values, and fetch `https://storage.googleapis.com/deckplanet_card_images/{card_number}.png` for each. Measure the pixel dimensions. If resolution is 500px+ this is the free, scriptable, complete solution. Write a small loop against the full `/items/cards?limit=-1` response and batch-download the whole corpus. Zero cost, zero sign-up, entirely community-legitimate.

2. **TTS ALL CARDS HD mod as resolution validator + gap-filler.** Subscribe to mod 1699347294 in TTS, run ttsbackup, and compare a sample of the resulting images against the DeckPlanet GCS images. Whichever is higher-res wins for that card. The TTS mod may have sourced older higher-res Bandai images that predate the deliberate downgrade. The ttsbackup tool lets you own them locally. Friction: $20 TTS purchase if not already owned.

3. **OCTGN hi-izuru.org pack archive.** Visit hi-izuru.org/OCTGN, check whether DBS packs are still served, check file sizes (a full-set OCTGN pack at 500px/card for a 200-card set is roughly 20-40MB). Download any sets missing from the DeckPlanet corpus. This is likely incomplete for newer sets (post-2021) since OCTGN's DBSCG community was not keeping pace with new releases.

4. **TCGAPIs Hobby tier ($7/month) as the coverage guarantee.** If DeckPlanet + TTS leave gaps (especially promo cards, campaign cards, alternate arts, Japanese-only variants), TCGAPIs is the only confirmed source offering universal coverage at multiple resolutions. Subscribe for one month, bulk-download via their API, cancel. Before subscribing, read their ToS specifically for bulk download clauses.

---

## Legal Posture Notes

- **Bandai DMCA history:** Confirmed nil per `dbscg_community_discourse.md`. One Piece TCG and Digimon TCG community APIs operate openly under the same Bandai publisher without enforcement action. DBSCG community resources carry equivalent low risk.
- **DeckPlanet GCS CDN:** Publicly accessible URLs, community-hosted database. No login required. Risk: bucket could be taken down if Bandai objects, which is unprecedented in their history with community sites.
- **TTS mod content / ttsbackup:** Steam Workshop ToS permits personal use downloads. ttsbackup is a published npm package specifically designed for this workflow. The images themselves are Bandai IP but the redistribution-to-self pattern is analogous to the long-tolerated MTG/Pokemon mod ecosystem.
- **OCTGN image packs:** Long-standing community distribution vector for card games; multiple TCG publishers including Wizards of the Coast have tacitly allowed OCTGN image packs for years. DBSCG is lower-profile than MTG.
- **TCGAPIs:** Licensed SaaS; legally cleanest paid option. Hotlinking is their designed use case; bulk local download may conflict with their ToS -- verify before doing it.
- **No torrent archive exists to evaluate** for legal posture -- this vector is not a live option.
