# TTS DBSCG Mod Investigation — Findings

## TL;DR

The mod is real and actively maintained: Steam Workshop ID 1699347294 is "Dragon Ball Super Card Game - Scripted + ALL CARDS HD (Every set, constantly updated)", a fork of 3vo's scripted table with 5,000+ cards where "almost all" have been upgraded to higher-resolution images. Exact pixel dimensions are unconfirmed by community sources but Bandai's 260×363 is the floor — TTS's 4096px sheet limit is the ceiling. Acquisition requires TTS (~$20) to load and cache the mod locally before any extraction tool can pull the images; a Steam-account-free JSON-level workaround exists via steamworkshopdownloader.io + ttsunhoster but has a critical bag-unpacking limitation. **Viability: conditional yes — worth the $20 if TTS is treated as a one-time imaging session tool, not a gaming purchase.**

---

## Mod metadata

- **Title:** Dragon Ball Super Card Game - Scripted + ALL CARDS HD (Every set, constantly updated)
- **Steam Workshop ID:** 1699347294
- **URL:** https://steamcommunity.com/sharedfiles/filedetails/?id=1699347294
- **Author:** Fork of 3vo's scripted table (original table author = 3vo; fork maintainer identity not confirmed in indexed sources)
- **Subscriber count:** Not confirmed via search — Steam Workshop page not fetchable without live browser. Community references consistently describe it as the primary maintained DBSCG mod.
- **Last updated:** Not confirmed from indexed sources; mod description states "constantly updated" with cards added "within days of REVEAL not release" via automation.
- **File size:** Not disclosed in indexed sources.
- **Companion site:** https://sites.google.com/view/dbstts

---

## Image resolution claims

- The mod description states it contains "every single card in HD with no low-res sample cards."
- A second indexed description snippet states "almost all of the cards have been updated with higher resolution images." The "almost all" language suggests the upgrade was iterative, not complete from the start — likely reflecting ongoing maintenance as new sets are added.
- No community comment or mod page excerpt in indexed search results states a specific pixel dimension (e.g., "750×1046" or "867×1210").
- **Verified or unverified:** Unverified at pixel level. The HD claim is consistent across multiple indexed snippets of the mod description and companion site. Given TTS's 4096px sheet maximum and that the images beat Bandai's 260×363 CDN, the likely range is 400–800px wide per card face. **Cannot confirm without loading the mod or extracting a sample image URL from the JSON.**

---

## Image hosting

- **Where images live:** Unknown from external research. TTS mods reference image URLs embedded in their JSON save files. Common hosts for TTS mods are Steam Cloud (steamuserimages-a.akamaihd.net), Imgur, and Discord CDNs. For a large, actively maintained mod of 5,000+ cards, Steam Cloud is the most likely primary host — Imgur and Discord CDNs have reliability and rate-limit issues at this scale.
- **Accessible without TTS ownership:** Conditionally yes. The mod's JSON file can be obtained via steamworkshopdownloader.io (no Steam account required, no TTS purchase required — it downloads the raw Workshop file). Once you have the JSON, you can extract all image URLs from it manually or with ttsunhoster/tts_save. **However:** cards stored inside "bags" (the mod uses bags to reduce load time per its description) are NOT pre-loaded — TTS only caches bag contents when the bag is physically opened in-game. This means a JSON-only extraction would miss any cards that were inside bags and hadn't been spawned yet.
- **The bag problem is the critical unknown.** If images for all 5,000+ cards are referenced in the top-level JSON (even inside bag object definitions), they're extractable without loading. If the bag objects only reference sub-JSON files that download on-demand, the full image set requires TTS + a session where every bag is opened.

---

## Coverage estimate

- **Number of cards claimed:** 5,000+ (companion site and mod description both state this)
- **Sets covered:** "Every Masters set" per the mod title; the companion site confirms Masters (BT01–BT25+) coverage. Fusion World (FW) coverage is unclear for this specific mod — a separate, newer mod (ID 3133475660, "Dragon Ball Super Card Game Masters/Fusion World TS") explicitly covers both.
- **Missing sets:** Fusion World may be in the newer sister mod rather than 1699347294. Special sets, promos, and regional exclusives unknown.
- **Sister mod:** ID 3133475660 — "Dragon Ball Super Card Game Masters/Fusion World TS" — appears to be the current maintained successor covering both game lines. Subscriber count not confirmed but it appears in search results alongside 1699347294 as the top two DBSCG TTS results. Claims 5,500+ cards importable via DeckPlanet integration.

---

## ttsbackup tooling

There are multiple tools in this space — the "ttsbackup npm" in the original lead is actually `stefankendall/ttsbackup` (npm), while the more robust Python tool is `eigengrau/tts-backup`. A third option, `ttsunhoster`, is specifically suited for the extraction use case here.

### stefankendall/ttsbackup (npm)
- **npm URL:** https://www.npmjs.com/package/ttsbackup
- **GitHub:** https://github.com/stefankendall/ttsbackup
- **License:** MIT
- **Install:** `npm install -g ttsbackup`
- **Steam-login requirement:** Requires TTS installed. Reads `WorkshopFileInfos.json` from the TTS mods directory — meaning TTS must be installed and the mod subscribed to. Cannot operate on a raw JSON file obtained externally.
- **Workflow:** Subscribe to mod → open TTS to cache assets → run `ttsbackup` → select mod from list → specify save location → outputs rehosted backup mod.

### eigengrau/tts-backup (Python — more complete)
- **GitHub:** https://github.com/eigengrau/tts-backup
- **License:** Available (repo exists, license file confirmed)
- **Install:** `pip install` from source distribution
- **Steam-login requirement:** Yes effectively — requires locally cached content in `~/Documents/My Games/Tabletop Simulator/`. All mod assets must have been cached by TTS before backup. The bag-unpacking limitation applies: cards in bags are only cached when the bag is opened in-game.
- **Estimated runtime:** Not found in indexed sources. For 5,000+ card images at typical sizes, initial TTS caching is the bottleneck (network-bound, likely 1–3 hours depending on connection and server load). The backup/extraction step itself would be fast once assets are local.

### theFroh/ttsunhoster (Python — best for JSON-first extraction)
- **GitHub:** https://github.com/theFroh/ttsunhoster
- **Purpose:** Takes a Workshop mod `.json` file, extracts all image/model URLs, downloads to local `Images/` and `Models/` folders. Does NOT require TTS installation.
- **Usage:** `unhoster.py [--output OUTPUT] json_input [json_input ...]`
- **Steam-login requirement:** No — but requires obtaining the mod's JSON file first. JSON can be retrieved via steamworkshopdownloader.io without Steam ownership.
- **Critical limitation:** The bag problem (see above). Cards stored only as bag-level object references that link to sub-JSONs will not be captured.
- **Estimated runtime:** Multiple simultaneous downloads; likely 30 minutes to 2 hours for 5,000+ card images depending on host server speed and image sizes.

### Recommended path (if pursuing without TTS purchase)
1. Pull the mod JSON from steamworkshopdownloader.io using ID 1699347294
2. Run ttsunhoster against it, check the image count in the output `Images/` folder
3. If image count is near 5,000 — the bag problem is a non-issue and TTS ownership is unnecessary
4. If image count is much lower (e.g., <500) — bags contain sub-JSONs and TTS purchase is required

This test costs nothing and can be done before spending $20.

---

## Alternative TTS mods

| ID | Title | Notes |
|----|-------|-------|
| 3133475660 | Dragon Ball Super Card Game Masters/Fusion World TS | Newer (2024+), covers both Masters + Fusion World, 5,500+ cards, DeckPlanet integration, actively maintained. Likely the better extraction target. |
| 951613891 | Dragon Ball Super Card Game | Older base mod (3vo's original scripted table); lower card count, predecessor to 1699347294. |
| 2085829112 | Dragon Ball Super TCG | Separate mod, coverage unknown from search results. |
| 1324525524 | Dragon Ball Super TCG All cards from Cross Worlds up to Colossal Warfare | Older partial coverage (Cross Worlds through Colossal Warfare only), likely abandoned. |
| 1552795176 | Dragon Ball Super Card Game FR | French-language variant. |

**Recommendation:** Target 3133475660 (Masters/Fusion World TS) as the primary extraction target alongside 1699347294 — 3133475660 appears newer and covers Fusion World which 1699347294 may not.

---

## Cost breakdown

- **TTS Steam purchase:** ~$20 one-time (currently ~$19.99 USD; goes on sale frequently for ~$5–10)
- **Free pre-test:** Pull JSON via steamworkshopdownloader.io → run ttsunhoster → count images. No cost, ~30 min. This determines if TTS purchase is even required.
- **If TTS required:** Install TTS, subscribe to both mods, open every bag in-game (laborious), run eigengrau/tts-backup or ttsunhoster. Time estimate: 3–6 hours total session work.
- **ttsbackup setup friction:** Low (npm install or pip install, well-documented)
- **Total acquisition friction:** Low-medium. The free pre-test path is the smart first move.

---

## Legal posture

Consistent with the torrent investigation findings. Bandai has no DMCA enforcement history against fan-made TTS mods or card image archives. Steam Workshop ToS frames mod content as derivative under publisher copyright, but personal-use archiving of images from Workshop mods falls into the same long-tolerated gray zone as screen-capturing card scans. The TTS modding community has operated this extraction workflow publicly for years without documented enforcement action. Same low-risk posture as the prior investigation's verdict.

---

## Verdict

**Pursue — but run the free pre-test first.**

Step 1: Download the mod JSON (ID 1699347294 and/or 3133475660) from steamworkshopdownloader.io at zero cost. Run ttsunhoster. Check the image count.

- If images are near 5,000 — you have the full corpus, no TTS purchase needed. Extract, sort, done.
- If images are sparse — bags contain sub-JSONs. Buy TTS on the next sale (~$5–10), run a caching session, extract.

The $20 TTS purchase is reasonable even at full price as a one-time imaging tool, but there's a real chance the free path gets you everything. Do not spend the $20 before running the pre-test.

The resolution claim ("HD, no low-res sample cards") is credible based on consistent mod description language but unverified at pixel level. The dbzexchange hybrid covers 30% of corpus at 867×1210; TTS images are likely in the 500–800px width range — meaningful upgrade over Bandai's 260×363 for thumbnail work, but may or may not beat dbzexchange on the 30% overlap. Sample first before committing to a full extraction session.
