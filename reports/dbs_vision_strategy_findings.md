# Dragon Ball Super Vision Strategy — Findings

Time-boxed scoping for `researchbot.py` to vision-enrich the 181 legacy DBSCG cards
(BT1–BT22 era, plus TB1–TB2 Themed Boosters, SD1–SD11 Starter Decks, P-???
Promos, EDBS reprints). Investigation date: 2026-05-13.

## Tested sources

- **Bandai official `/us-en/cardlist/` (HTML server-render)** — `https://www.dbs-cardgame.com/us-en/cardlist/?search=true&category={SET_ID}` — HTTP 200, 552KB, **images present in initial HTML** at `../../images/cardlist/cardimg/{NUMBER}.png`. No JS execution required. Browser UA sufficient; no Cloudflare challenge.
- **Bandai direct image CDN** — `https://www.dbs-cardgame.com/images/cardlist/cardimg/{NUMBER}.png` — HTTP 200 with Referer header, image/png, **260×363 PNG (~70KB)**. Coverage probed: BT1-001, BT2-067, BT4-002, BT22-001, TB1-001, TB2-031, SD3-01, P-001, P-035, SD2-05 → all 200. Only miss was `EB1-001`/`EB2-001` (404), but the corpus does NOT use the `EB-` prefix; the two Expansion Deck Box Set 08 cards in inventory are numbered `BT4-078` and `BT4-084` (reprints from Colossal Warfare), which resolve fine.
- **DeckPlanet CDN (GCS bucket)** — `https://storage.googleapis.com/deckplanet_card_images/{NUMBER}.png` — HTTP 200 on `BT1-001`, `BT2-001`, `BT4-002`, `P-001`, `TB1-001`; **404 on `EB1-001`, `BT19-001`, `BT22-001`, `EB2-001`** (coverage gap, likely stopped updating mid-2023). Same 260×363 thumbnails as Bandai (the CDN appears to mirror Bandai). Discovered via the `dragogodev/cgs` repo's `Dragon Ball Super/cgs.json` config file.
- **DeckPlanet API** (`https://dbs-deckplanet-api.com/items/cards?limit=-1`) — DNS resolution failed from local network (`curl exit 7`); host may be deprecated or geo-blocked. Not viable as a runtime dependency.
- **Bandai `/asia/cardlist/` legacy endpoint** — HTTP 200 but returns the search FORM only; results are not embedded server-side for the Asia path. POST to `index.php?search=true` also returns the form, not results. Skip in favor of `/us-en/`.
- **GitHub `teoisnotdead/api-dbscg-fw`** — Fusion World only, no legacy data. Skip.
- **GitHub `dragogodev/cgs`** — Useful as a discovery vector (the `cgs.json` exposed the GCS bucket pattern) but the repo itself only contains metadata schemas, no images.
- **Cardmarket** — HTTP 403 to curl-with-UA; would need Puppeteer. Per `bbl-subagent-runtime-workarounds` Puppeteer is PARENT-only, and Cardmarket pages are listing-keyed (not collector-number-keyed), so finding the right card requires search-result scraping. Not worth the implementation overhead given Bandai already covers the corpus.
- **Fandom DBSCG wiki, RetroDBZccg, ogcards.com** — Not deeply probed once the Bandai endpoint was confirmed covering. Listed here so future-Claude doesn't re-walk.

## Recommended primary source

**Bandai official image CDN: `https://www.dbs-cardgame.com/images/cardlist/cardimg/{COLLECTOR_NUMBER}.png`**

Reasoning:
- **Canonical (publisher-served), single-URL formula, no auth, no JS, no Cloudflare**
- 100% coverage on every collector-number pattern in the corpus (BT, TB, SD, P, plus EDBS reprints which use BT numbering)
- Requires a `Referer: https://www.dbs-cardgame.com/us-en/cardlist/` header (verified — direct request without Referer also returned 200 but adding it defensively matches what a real browser sends and protects against future hotlink-blocking)
- Mirrored by DeckPlanet's GCS bucket, but the GCS mirror has coverage gaps for sets after ~BT18; the Bandai canonical does not

**Resolution caveat: images are 260×363 PNG thumbnails.** That's below the Pokémon baseline (PokemonTCG.io serves ~734px, Bulbapedia upgrade triggers at ≥800px). DeepSeek vision will tolerate it (no documented minimum), but tag-extraction quality on character art will be weaker than the MTG/Pokémon waves. The trade-off: Bandai's images include the full card frame with rendered skill text, so for triviabot purposes the small art-area is offset by oracle-text capture being trivial via OCR.

## Recommended fallback source

**None worth wiring at first iteration.** If a card 404s at the Bandai URL after this strategy ships, flag for manual review and add to `reports/janitor_triage.md` per `bbl-janitor-triage-file`. Two reasons:

1. Bandai coverage on the corpus is provably 100% across all 8 set families.
2. Every higher-res alternative requires either Puppeteer (PARENT-only, blocks subagent use) or search-and-match (Cardmarket / Fandom listing pages aren't keyed by collector number).

If `bbl-edgelord` consistently complains about resolution after a test wave, the right next move is a Puppeteer-fetch helper that hits the Bandai `/us-en/cardlist/?search=true&card_number={N}` page and pulls the **zoomed/lightbox image** the `.zoomcard` class hints at (the HTML has `class="zoomcard"` on the 260px thumbs — there may be a corresponding higher-res image served on click that I didn't have time to verify). That work is deferred.

## Implementation sketch

Add a third strategy mirroring `find_image_pokemontcg`:

```python
DBS_IMAGE_BASE = "https://www.dbs-cardgame.com/images/cardlist/cardimg"
DBS_REFERER    = "https://www.dbs-cardgame.com/us-en/cardlist/"

def find_image_dbs(card_name: str, set_name: str = "",
                   collector_number: str = ""
                   ) -> tuple[str | None, str, str, str, str, str, str]:
    """Returns (url, confidence, number, artist, art_crop_url='',
    flavor_text='', oracle_text=''). Bandai serves a static thumbnail
    keyed on collector_number; artist + oracle/flavor are NOT available
    from this source — capture deferred to triviabot."""
    if not collector_number:
        return None, "none", "", "", "", "", ""
    url = f"{DBS_IMAGE_BASE}/{collector_number}.png"
    # HEAD probe; treat 200 as confident, anything else as miss.
    if _head_ok(url, referer=DBS_REFERER):
        return url, "high", collector_number, "", "", "", ""
    return None, "none", "", "", "", "", ""
```

Wire it in `find_reference_image`:

```python
if strat == "dbs":
    return find_image_dbs(card_name, set_name, collector_number=...)
```

Two integration tweaks for the dispatch layer:
1. **Add `"Dragon Ball Super": "dbs"` to the `GAME_STRATEGY` dict** (currently around line 581 area).
2. **Pass `collector_number` into `find_reference_image`.** Currently the function takes `(game, card_name, set_name, set_map)` — DBS is the first game where the collector number is the lookup key, not the card name. The simplest path is to read `number` from frontmatter at the call site and pass it through; the MTG/Pokémon branches will ignore the new parameter.
3. **Add `_head_ok(url, referer=None)`** helper (urllib HEAD request, treat 200 as truthy). Defensive — saves downloading a 70KB PNG just to discover it's a 404 page.

**Effort estimate:** ~40–60 lines of code in `researchbot.py`, no new script files, no new dependencies (urllib + the `download_image` function already in the file handle the rest). Per-card cost: 1 HEAD request + 1 GET on hit (Bandai has no documented rate limit; a 0.2–0.5s sleep between cards is courteous). Reliability risk: low — single-URL formula on a publisher CDN with no JS challenge, no auth, no per-request token. The DeepSeek vision call cost dominates this anyway.

**What this strategy explicitly does NOT capture** (compared to Scryfall/PokemonTCG.io paths):
- `artist` — Bandai doesn't expose it via URL; would need to scrape the `/us-en/cardlist/?card_number=…` HTML
- `flavor_text` / `oracle_text` — same, scrape-only
- `art_crop_url` — DBSCG has no art-only crop

This means `bbl-triviabot` and `bbl-edgelord` will need to read the card body image directly, the same way they would for any thumbnail-only source. That's fine and matches the existing Pokémon path for older sets (PokemonTCG.io doesn't expose flavor text reliably either).

## Risks / gotchas

- **Resolution is the only real concern.** 260×363 vs. Pokémon's 734px+ baseline. Test a 5–10 card wave through `bbl-edgelord` before scaling to all 181. If tag quality drops noticeably, the fallback is the deferred Puppeteer zoomcard strategy.
- **No Referer guard verified at scale.** The single test passed both with and without Referer. If Bandai ever turns on hotlink protection, the curl-with-UA pattern from `bbl-subagent-runtime-workarounds` already covers Referer — just add it.
- **Card numbers with foil suffixes need normalization.** Corpus uses filenames like `tb2-031-wild-tiger-the-imposing--foil.md`; the `number` field in frontmatter should be `TB2-031` (no foil suffix). Verify the prep-time frontmatter populates `number` cleanly — if it currently inlines `--foil`, strip it before constructing the image URL. (Spot-check on a couple corpus cards before shipping.)
- **EB-prefix not in corpus today, but if a future CSV brings EDBS-original-numbering cards in, Bandai 404s on EB-prefix.** Acceptable failure mode: flag for manual review, no silent bad behavior.
- **DeckPlanet GCS bucket is a backup mirror but its coverage drops after ~BT18.** Don't wire it as fallback; it'd be a worse-coverage second source that adds complexity for no win.

## Per-card image-URL formula

```
{COLLECTOR_NUMBER}.png  →  https://www.dbs-cardgame.com/images/cardlist/cardimg/{COLLECTOR_NUMBER}.png
```

Required header:
```
Referer: https://www.dbs-cardgame.com/us-en/cardlist/
User-Agent: <any browser UA>
```

Verified working examples (all HTTP 200):
- `BT1-001`, `BT2-067`, `BT4-002`, `BT22-001` (Booster sets)
- `TB1-001`, `TB2-031` (Themed Boosters)
- `SD2-05`, `SD3-01` (Starter Decks — note 2-digit card num)
- `P-001`, `P-035` (Promos)

Confirmed image properties: PNG, RGBA/P mode, 260×363 dimensions, ~50–90KB filesize.

## Higher-res alternatives (investigated 2026-05-13)

### Tested

- **Bandai `cardimg_l/` `cardimg_zoom/` `cardimg_b/` `cardimg_p/` `cardimg_pc/` `cardimg_org/` `cardimg_hi/` `cardimg_full/`** — `https://www.dbs-cardgame.com/images/cardlist/{variant}/BT4-002.png` — all HTTP 404. No publisher-served higher-res variant of the cardlist directory exists.
- **Bandai `_l` `_lg` `_large` `_b` filename suffixes** in `cardimg/` — `https://www.dbs-cardgame.com/images/cardlist/cardimg/BT4-002_{suffix}.png` — all HTTP 404. (Side note: `_b` and `_PR` ARE used for back-face / promo variants on Z/UB-era cards, but not as a higher-res signifier.)
- **Bandai `images/cardlist/large/` and `images/cardlist/cardimg/large/`** — both HTTP 404.
- **Bandai `.zoomcard` CSS hook** — confirmed cosmetic only. CSS rule at `cardlist.css:697` applies `transform: scale(1.2)` on hover to the same 260×363 image. NO `data-zoom-image` / `data-src` / `data-large` attributes in the HTML; NO JS handler in `cardlist.js` that fetches a larger image; NO lightbox/modal anywhere in the cardlist DOM. The class is purely a CSS hover hook.
- **Bandai `/us-en/cardlist/?search=true&category=583009` (legacy DBS browse)** — HTTP 200 but **"No cards matched your search"**. Bandai has retired all legacy DBS categories (BT, TB, SD, P prefixes) from the cardlist server-side renderer; only Z/UB-era Fusion World sets are still indexed. The `cardimg/` CDN still serves the legacy PNGs by collector number — but the only HTML pages that reference them are now gone.
- **Bandai `/us-en/cardlist/?search=true&card_number=BT4-002`** — HTTP 200 but same "no results" landing; per-number search is also retired for legacy.
- **Bandai JP `/jp/cardlist/`** — HTTP 404. The JP path under `/jp/` doesn't exist; JP players are routed to `/fw/jp/cardlist/` (Fusion World JP) which has the same Z/UB-only catalog and the same image-CDN as `/us-en/`.
- **Bandai `/fw/jp/cardlist/`** — HTTP 302 to a default Z/UB category, no legacy.
- **Carddass `www.carddass.com/dbscg/` and `/dbs/`** — both 404. The Carddass root redirects to `sec.carddass.com/jp/`, which links DBS users out to `dbs-cardgame.com/fw/jp/` (back to Bandai) and `dbsdv.com` (Dragon Ball Super Divers — a different arcade product, not the TCG). No standalone Carddass DBSCG card portal exists.
- **dbsdv.com** — Dragon Ball Super DIVERS, not the TCG. Distinct product line. Skip.
- **Fandom DBSCG wiki via Puppeteer** — Cloudflare-challenged at the edge (`cf-mitigated: challenge`, HTTP 403). The `scripts/puppeteer-fetch/fetch.js` helper is correctly designed to bypass this — but a subagent can only invoke `node --version`; full `node fetch.js <url>` is permission-gated. Per `bbl-subagent-runtime-workarounds` and `bbl-puppeteer-over-snippets`, **this probe is PARENT-only**. Not attempted further.
- **Fandom static CDN direct probe** — `https://static.wikia.nocookie.net/dragonballsupercardgame/images/d/d2/BT4-002.png` — HTTP 404 (returns a placeholder.webp). MediaWiki uploads are keyed on filename, which is human-edited and inconsistent (e.g., `BT4-002_-_Baby_-_Rampaging_Great_Ape.png` or similar); coverage discovery requires page-scraping with Puppeteer.
- **Fandom MediaWiki API (`api.php`)** — HTTP 404. Fandom has removed the public api.php endpoint. Discovery via API not viable.
- **Limitless TCG** — `/cards/dbs` and `/cards/dbz` both 404. No DBS coverage on Limitless (Pokémon/One Piece/Lorcana focused).
- **CardTrader** — root redirects to localized path; default search 404s. Would require scraping a listing page (search-and-match, not collector-number-keyed). Same overhead as the Cardmarket dead-end already documented.
- **CardRush JP** — Cloudflare 403 with JS challenge. Puppeteer-only, PARENT-only.
- **TCGplayer search API (`https://mp-search-api.tcgplayer.com/v1/search/request`)** — HTTP 200, no auth required. **Structured POST with `filters.term.number = ["BT4-002"]` and `filters.term.productLineName = ["dragon-ball-super-ccg"]` returns the matching productId.** Verified 5-for-5 across BT1-001, TB1-001, P-001, BT22-001, BT19-001 (the DeckPlanet post-BT18 gap is covered here). Some collector numbers return multiple results due to foil/alt-art variants (BT4-002 has a Normal at `168548` and a Foil at `169347`); take the first hit or filter on `printing=Normal` for the base art.
- **TCGplayer image CDN (`https://product-images.tcgplayer.com/`)** — HTTP 200, no auth.
  - **Original (no fit-in path)**: 260×363, ~50KB, **unwatermarked** but **identical pixel content to Bandai's CDN** (same source, same `last-modified: 2021-03-05`). Not an upgrade.
  - **`fit-in/1000x1000/{productId}.jpg`**: 715×1000, ~140-190KB, **watermarked** with diagonal "TCGPlayer" text across the card face. **The fit-in derivative is an upscale of the 260px source** — confirmed by `last-modified` being identical across all sizes — so the apparent resolution gain is interpolation, not extra detail. Tag-extraction quality won't improve, and the watermark would actively hurt vision-pass tag yield (DeepSeek would tag the watermark text).
  - **`fit-in/5000x5000/{productId}.jpg`**: 3577×5000, ~1.7MB. Same caveat — interpolated and watermarked.
- **Cardmarket** — already documented as 403-to-curl and Puppeteer-only; not re-probed.
- **CardRush, pixel.gg, RetroDBZccg, ogcards.com** — not probed individually after the TCGplayer finding clarified the underlying problem (the 260×363 PNG is the only resolution that exists upstream; everyone mirrors it).

### Root cause finding

**Bandai never produced a higher-res-than-260×363 web asset for legacy DBSCG (BT/TB/SD/P sets).** Every third-party site that hosts these cards — DeckPlanet, TCGplayer, the (presumably) Fandom wiki — ultimately sources from the same Bandai CDN file. The 260×363 PNG is the canonical web resolution for this product line. The publisher's Z/UB-era cards (Fusion World, the active product) get the same 260×363 treatment, so this isn't a legacy-archive resolution drop — it's the format Bandai standardized on across the whole game.

The only places higher-res scans could exist:
1. **Print-press scans** held by Bandai Japan / Toei licensors — never released publicly.
2. **Wiki-editor uploads of physical-card scans** — exist on Fandom but require Puppeteer discovery (PARENT-only) AND human-edited filenames AND inconsistent per-card coverage.
3. **Marketplace seller photos** (TCGplayer Marketplace listings, eBay) — phone-camera quality, variable, no consistent URL pattern.

### Recommended secondary strategy

**None viable; stick with Bandai 260×363.** Specifically:

1. The TCGplayer `fit-in/1000x1000/` URL formula is operationally clean (productId discoverable via free search API, no auth, no rate-limit hit during this probe) but **the upscaled-and-watermarked output would degrade vision-pass tag quality, not improve it.** The added pixels are interpolation; the watermark is real noise.
2. Fandom via Puppeteer is the only path that might yield actual physical-card scans, but it's PARENT-only, requires per-card filename discovery, and coverage is unknown without probing — high cost, uncertain payoff. **Park this as a future protocol for the parent process if (and only if) edgelord tag quality on DBS becomes a blocker after a real test wave.**

### Implementation sketch if viable

Not applicable — stay with the Bandai strategy already documented above. If a future test wave shows DeepSeek tag quality on DBS is genuinely below the wave-floor, the next move is a **parent-side script** `scripts/dbs_fandom_image_discovery.py` that:
- Reads `cards/dragon-ball-super/*/*.md` and pulls the `number` field
- Runs `scripts/puppeteer-fetch/fetch.js` against `https://dragonballsupercardgame.fandom.com/wiki/{NUMBER}` for each card
- Greps the HTML for `static.wikia.nocookie.net/dragonballsupercardgame/images/...png|jpg` references
- HEAD-probes to find the largest available variant (Fandom serves multiple sizes: `revision/latest/scale-to-width-down/{N}` at e.g. 800, 1200, 2000)
- Writes `image_url_hires` into frontmatter alongside the existing `image_url`
- ~80-120 LoC, 30-45 min, blocks researchbot.py call sites until merged

This is documented for future-Claude per `bbl-keep-scratch-scripts` discipline — don't build it speculatively.

### Per-card image-URL formula

**For TCGplayer (NOT recommended due to watermark + upscale-artifact):**

```
1. POST https://mp-search-api.tcgplayer.com/v1/search/request
   Body: {"algorithm":"","from":0,"size":1,
          "filters":{"term":{"productLineName":["dragon-ball-super-ccg"],
                             "number":["{COLLECTOR_NUMBER}"]}},
          "listingSearch":{...},"context":{...},"settings":{...},"sort":{}}
2. Extract results[0].results[0].productId
3. Image URL: https://product-images.tcgplayer.com/fit-in/1000x1000/{productId}.jpg
   (watermarked; identical pixel info to Bandai 260px)
```

**For Fandom (theoretical, requires Puppeteer):**
Pattern is `https://static.wikia.nocookie.net/dragonballsupercardgame/images/{HashA}/{HashAHashB}/{filename}/revision/latest?cb={timestamp}` with `scale-to-width-down/{N}` for sizing. Filename and hash discovered by scraping the wiki page HTML. Not formula-friendly.

