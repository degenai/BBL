# Weiss Schwarz Vision Strategy — Findings

Investigation date: 2026-05-14. Corpus: 126 cards across 9 anime/franchise sets.

## TL;DR

Bushiroad's official English cardlist (`en.ws-tcg.com`) is the canonical image source for all 126 Weiss Schwarz cards. The site serves PNGs at ~400×558px (100–560KB each) — well above the DBSCG 260×363 baseline and comparable to PokemonTCG.io. Image paths are **not uniformly derivable from collector number alone** for all sets (one anomaly: BD/WE35 uses product-specific folder paths). The implementation strategy is a **per-card HTML search scrape** against the Bushiroad EN search endpoint, which returns the image path in the server-rendered HTML for every English-edition card tested. No auth, no Cloudflare, no JS execution required.

---

## Tested Sources

### Bushiroad EN — `en.ws-tcg.com` (PRIMARY)

- **Search endpoint:** `https://en.ws-tcg.com/cardlist/searchresults/?keyword={COLLECTOR_NUMBER_URL_ENCODED}`
- **Response type:** Server-rendered HTML, HTTP 200
- **Image path embedded in HTML as:** `<div class="image"><img src="/wordpress/wp-content/images/cardimages/{PRODUCT_FOLDER}/{SET}_{NUM}.png" ...></div>`
- **CDN base:** `https://en.ws-tcg.com/wordpress/wp-content/images/cardimages/`
- **Zero-result detection:** HTML contains `<p class="c-search__no-post">No cards were found.</p>` and `Search Results<span>0</span>items.`
- **UA required:** Browser User-Agent (any modern UA works; no Referer header needed)
- **Cloudflare:** Not present on this domain. HTTP 200 with plain browser UA.

**Resolution confirmed per set:**

| Set | Collector Number | Path pattern | Dimensions | File size |
|-----|-----------------|--------------|------------|-----------|
| Attack on Titan (AOT/S35) | AOT/S35-E024 C | `a/aot_s35/AOT_S35_E024.png` | 400×558 px | 455 KB |
| Hatsune Miku (PD/S22) | PD/S22-E092 C | `p/pd_s22/PD_S22_E092.png` | 400×558 px | 425 KB |
| Magia Record (MR/W80) | MR/W80-E040 U | `m/mr_w80/MR_W80_E040.png` | 400×558 px | 558 KB |
| Mob Psycho 100 (MOB/SX02) | MOB/SX02-100 CR | `m/mob_sx02/MOB_SX02_100.png` | 558×400 px* | 186 KB |
| Seven Deadly Sins (SDS/SX03) | SDS/SX03-034 U | `s/sds_sx03/SDS_SX03_034.png` | 350×489 px | 491 KB |
| Bang Dream/PPR (BD/WE35) | BD/WE35-E20 C | `GBP21/PPR/WE35_E20.png` | 399×558 px | 459 KB |

*MOB/SX02-100 is the "100%" event card — landscape format, same pixel area as portrait cards.

**Collector number suffix handling:** Lowercase letter suffixes (E084a, E094c, E075b) are preserved exactly as-is in the filename. SP/S/R variants also appear as suffixes (E001SP, E001S — separate images for special prints).

**Path formula for "standard" sets (AOT/S35, PD/S22, MR/W80, MOB/SX02, SDS/SX03):**
```
collector_number = "AOT/S35-E024 C"
slug = collector_number.split(' ')[0]  # strip rarity: "AOT/S35-E024"
parts = slug.replace('/', '_').replace('-', '_').lower()  # "aot_s35_e024"
prefix = parts[:parts.index('_')]  # "aot"  (first letter for subfolder)
# Result: a/aot_s35/AOT_S35_E024.png
```

**BD/WE35 is the anomaly:** the path uses non-standard product folders (`GBP21/PPR/` for E01-E20+, `BD5TH/` for PE-prefixed promotional cards). The folder cannot be derived from the collector number — it reflects Bushiroad's internal product release organization. **The search endpoint resolves this correctly for every card; the formula approach fails for BD/WE35.**

**Recommended implementation:** Use search endpoint universally (not direct CDN formula), parse `<img src="...">` inside `<div class="image">`, then construct absolute URL from the extracted path.

---

### Bushiroad JP — `ws-tcg.com`

- Tested: HTTP 200, serves JP-edition cardlist
- JP collector numbers (no `E` prefix, e.g., AOT/S35-024) return results on the JP site
- **EN-edition cards (E-prefix) return zero results on the JP site**
- JP image CDN does NOT serve EN card images (`https://ws-tcg.com/wordpress/wp-content/images/cardimages/a/aot_s35/AOT_S35_E024.png` → HTTP 404)
- **Conclusion:** JP site is a separate product catalog. Not applicable to our EN-edition corpus.

---

### HeartoftheCards.com — `heartofthecards.com`

- **Status:** HTTP 200, functional
- **Coverage:** Translation database, not an image database
- Card images use hash-based IDs: `/hg-hotc-thumbs/{hash}a.jpg`
- ID is not derivable from collector number
- Thumbnail size: 11KB JPEG — roughly 106px wide (constrained by CSS `max-width:106px`), likely ~100–150px actual dimensions
- No larger image available at the per-card page; all images are the same hash-based thumbnails
- **Verdict:** Not viable as an image source. HotC's value is translation text, not card scans.

---

### EncoreDecks — `encoredecks.com`

- **Status:** HTTP 200, React SPA (JavaScript-rendered)
- Card-specific URL patterns tried: `/api/card/AOT/S35-E024`, `/api/series/S35/cards`, `/api/series/S35/page/1`, `/api/cards?setid=S35`, `/api/en/set/S35/cards` — all return 404 or the "Page Could Not Be Found" SPA shell
- The SPA requires JavaScript execution to render card data; curl-with-UA returns the HTML shell only (no card data)
- **Verdict:** Requires Puppeteer to access. Per `bbl-subagent-runtime-workarounds`, Puppeteer is PARENT-only. Not viable for subagent use. Skip.

---

### WSdb — `wsdb.xyz`

- **Status:** HTTP 404 — domain is gone. Defunct.

---

### Cardrush JP — `cardrush.jp`

- **Status:** HTTP 200 on root, but no Weiss Schwarz product category
- `/product-list/category/ws` → 404
- `/product/search?keyword=AOT/S35` → 404
- Cardrush focuses on Yu-Gi-Oh and other card games; WS is not in their catalog
- **Verdict:** Not applicable.

---

### TCGplayer — `tcgplayer.com`

- Search API probed: `POST https://mp-search-api.tcgplayer.com/v1/search/request` with `productLineName: ["weiss-schwarz"]` and `number: ["AOT/S35-E024"]`
- **Returns 0 results.** TCGplayer indexes WS but their `number` field format likely uses the JP numbering or different format. Not pursued further given Bushiroad EN already covers the corpus.
- **Verdict:** Not viable as primary or fallback.

---

### Fandom wikis per anime (Attack on Titan wiki, Madoka wiki, etc.)

- Not deeply probed. These wikis host show character art and lore content, not card scans.
- Fandom's MediaWiki API (`api.php`) is no longer publicly exposed per the DBSCG investigation findings.
- Static CDN URLs require per-card filename discovery (human-edited, inconsistent).
- **Verdict:** Skip. Same conclusion as DBSCG investigation.

---

## Recommended Primary Source

**Bushiroad EN search endpoint + image CDN: `https://en.ws-tcg.com/cardlist/searchresults/?keyword={ENCODED_COLLECTOR_NUMBER}`**

Reasoning:
- **Publisher-served, canonical, no auth, no Cloudflare, no JS execution**
- 400×558px PNG (or 350×489 for SDS/SX03) — well above DBSCG's 260×363 baseline
- Confirmed HTTP 200 on all 6 active sets in the corpus (AOT/S35, PD/S22, MR/W80, MOB/SX02, SDS/SX03, BD/WE35)
- The keyword search by collector number is a reliable per-card lookup that handles all product-folder variations
- Zero-result signal is clean and parseable from HTML (`"No cards were found."`)
- Cards with lowercase suffix in number (E084a, E094c) work correctly
- Portrait and landscape card formats both work (MOB/SX02-100 is landscape)

**Coverage estimate for the 126-card corpus:**

| Set | Cards in corpus | Active directory | Expected coverage |
|-----|----------------|-----------------|-------------------|
| AOT/S35 (Attack on Titan) | ~14 | Yes | ~100% (tested E024, E064, E072, E092, E094c) |
| PD/S22 (Hatsune Miku) | ~46 | Yes | ~100% (tested E092, E084a, E075b, E074a/b) |
| MR/W80 (Magia Record) | ~21 | Yes | ~100% (tested E040, E099, E028) |
| MOB/SX02 (Mob Psycho 100) | ~41 | Yes | ~100% (tested SX02-100, SX02-098) |
| SDS/SX03 (Seven Deadly Sins) | 2 | Yes | 100% (tested SX03-034, SX03-080) |
| BD/WE35 (Bang Dream/PPR) | 1 | Yes | 100% (tested WE35-E20) |
| CCS (Cardcaptor Sakura) | 0 | Empty dir | N/A — no cards yet |
| RAG (Rent-A-Girlfriend) | 0 | Empty dir | N/A — no cards yet |

CCS/RAG directories exist but have zero cards. When they arrive, CCS/WX01 images are confirmed on the EN site (`c/ccs_wx01/CCS_WX01_001.png`). RAG (not yet probed) will likely follow the same pattern.

---

## Recommended Fallback

**None required at first iteration.** If a search returns "No cards were found" (possible for very recent sets not yet in Bushiroad's EN database, or if a JP-edition card slips through), flag to `reports/janitor_triage.md`.

If fallback eventually needed and quality matters: the JP Bushiroad site (`ws-tcg.com`) serves JP-edition card images. Since JP and EN editions share the same art (different text frames only), the JP image could substitute — but this requires a separate set-code mapping (JP uses different set codes for the same franchise, e.g., AOT/S35 JP numbering without E-prefix). Not worth wiring until there's an actual miss.

---

## Implementation Sketch

Mirror the existing `find_image_dbs` / `find_image_pokemontcg` pattern:

```python
WS_SEARCH_BASE = "https://en.ws-tcg.com/cardlist/searchresults/"
WS_CDN_BASE    = "https://en.ws-tcg.com"

def find_image_ws(card_name: str, set_name: str = "",
                  collector_number: str = ""
                  ) -> tuple[str | None, str, str, str, str, str, str]:
    """Returns (url, confidence, number, artist, art_crop_url='',
    flavor_text='', oracle_text='').

    Strategy: keyword-search Bushiroad EN by collector number, parse the
    first <div class="image"><img src="..."> from the HTML, construct
    absolute image URL. Falls back to None on zero-result or HTTP error.

    Note: 'artist', 'flavor_text', 'oracle_text' are NOT available from
    this source — defer to triviabot.
    """
    if not collector_number:
        return None, "none", "", "", "", "", ""

    # Strip rarity suffix ("AOT/S35-E024 C" -> "AOT/S35-E024")
    number_clean = collector_number.split(" ")[0]

    import urllib.request, urllib.parse, re
    params = urllib.parse.urlencode({"keyword": number_clean})
    url = f"{WS_SEARCH_BASE}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
    except Exception:
        return None, "none", "", "", "", "", ""

    # Zero-result detection
    if "No cards were found" in html:
        return None, "none", "", "", "", "", ""

    # Extract first card image path from rendered HTML
    m = re.search(r'<div class="image"><img src="(/wordpress/wp-content/images/cardimages/[^"]+\.png)"', html)
    if not m:
        return None, "none", "", "", "", "", ""

    image_url = WS_CDN_BASE + m.group(1)
    return image_url, "high", number_clean, "", "", "", ""
```

**Wire in `find_reference_image` dispatch:**
```python
GAME_STRATEGY = {
    ...
    "Weiss Schwarz": "ws",
}

if strat == "ws":
    return find_image_ws(card_name, set_name, collector_number=...)
```

**Effort estimate:** ~50 LoC in `researchbot.py`, no new script files, no new dependencies. Per-card cost: 1 GET request against Bushiroad EN (HTML ~177KB per response). Rate-limiting: Bushiroad EN has no documented rate limit, but a 0.5–1s sleep between cards is courteous given the HTML parse overhead. The DeepSeek vision call cost dominates anyway.

**What this does NOT capture** (same as DBSCG):
- `artist` — not exposed via URL or HTML without additional parsing
- `flavor_text` / `oracle_text` — not on this page; triviabot territory
- `art_crop_url` — Bushiroad serves full card frames, no art-only crop

---

## Per-Card URL Formula (Discovered)

**Two-step process:**

1. Fetch search page:
   ```
   GET https://en.ws-tcg.com/cardlist/searchresults/?keyword={COLLECTOR_NUMBER_STRIP_RARITY}
   User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...
   ```

2. Extract image path from HTML regex:
   ```
   <div class="image"><img src="(/wordpress/wp-content/images/cardimages/[^"]+\.png)"
   ```
   Prepend `https://en.ws-tcg.com` to construct full URL.

**Examples verified working:**

| Collector number (frontmatter) | Search keyword | Image URL |
|-------------------------------|----------------|-----------|
| AOT/S35-E024 C | AOT/S35-E024 | `en.ws-tcg.com/wordpress/wp-content/images/cardimages/a/aot_s35/AOT_S35_E024.png` |
| PD/S22-E092 C | PD/S22-E092 | `en.ws-tcg.com/wordpress/wp-content/images/cardimages/p/pd_s22/PD_S22_E092.png` |
| PD/S22-E084a U | PD/S22-E084a | `en.ws-tcg.com/wordpress/wp-content/images/cardimages/p/pd_s22/PD_S22_E084a.png` |
| AOT/S35-E094c C | AOT/S35-E094c | `en.ws-tcg.com/wordpress/wp-content/images/cardimages/a/aot_s35/AOT_S35_E094c.png` |
| MR/W80-E040 U | MR/W80-E040 | `en.ws-tcg.com/wordpress/wp-content/images/cardimages/m/mr_w80/MR_W80_E040.png` |
| MOB/SX02-100 CR | MOB/SX02-100 | `en.ws-tcg.com/wordpress/wp-content/images/cardimages/m/mob_sx02/MOB_SX02_100.png` |
| SDS/SX03-034 U | SDS/SX03-034 | `en.ws-tcg.com/wordpress/wp-content/images/cardimages/s/sds_sx03/SDS_SX03_034.png` |
| BD/WE35-E20 C | BD/WE35-E20 | `en.ws-tcg.com/wordpress/wp-content/images/cardimages/GBP21/PPR/WE35_E20.png` |

---

## Coverage Estimate Across the 9 Sets

| Set | Cards in corpus | Expected image coverage | Probe result |
|-----|----------------|------------------------|--------------|
| Attack on Titan (AOT/S35) | ~14 | ~100% | 5 cards tested, all hit |
| Hatsune Miku PD/S22 | ~46 | ~100% | 5 cards tested incl. letter-suffix variants |
| Magia Record (MR/W80) | ~21 | ~100% | 3 cards tested, all hit |
| Mob Psycho 100 (MOB/SX02) | ~41 | ~100% | 2 cards tested, all hit |
| Seven Deadly Sins (SDS/SX03) | 2 | 100% | Both cards confirmed |
| Bang Dream/PPR (BD/WE35) | 1 | 100% | 1 card confirmed (non-standard path) |
| Cardcaptor Sakura Clear Card | 0 | N/A | Site confirmed serving CCS/WX01 set |
| Rent-A-Girlfriend | 0 | N/A | Not probed; expected to work (same site) |

**Overall estimate: ~100% of the 126 cards currently in corpus are resolvable.** The only theoretical miss is cards from sets Bushiroad EN hasn't published (unlikely for our corpus — all 6 active sets are confirmed on the site).

---

## Risks / Gotchas

- **BD/WE35 path is non-standard.** The product-folder path (`GBP21/PPR/` and `BD5TH/`) cannot be derived from the collector number. The search-based approach handles this correctly — do NOT attempt a direct CDN formula shortcut for this set.

- **Collector number format normalization required.** Frontmatter stores `"BD/WE35-E20 C"` (includes rarity suffix after space). Strip everything after the first space before using as the search keyword. Failure to strip will likely still return results (the site searches by substring), but may return multiple cards. Strip to be clean.

- **Letter-suffix case sensitivity.** The image filename preserves lowercase (E084a, E094c). The keyword search is case-insensitive so `PD/S22-E084A` finds the card, but the extracted image URL has the lowercase filename. No normalization needed on this dimension — just use the URL as returned.

- **SP / S variant cards.** Cards with SP (special), S (signed), or R suffix in the image filename are separate images from the base card. The search for `PD/S22-E001` may return both `PD_S22_E001.png` and `PD_S22_E001SP.png`. The regex grabs the FIRST match. Spot-check: the first result in search HTML is consistently the base card variant. If our corpus holds variant cards, their frontmatter collector numbers may need to include the suffix (e.g., `PD/S22-E001 SP`) — verify before wiring.

- **JP vs EN edition.** Our corpus holds EN-edition cards (E-prefix in number). Bushiroad EN only serves EN cards. If a future CSV import brings JP-edition WS cards (no E-prefix, different numbering), the EN site will return zero results. Flag to janitor_triage — don't silently fail.

- **HTML response size is ~177KB per search.** This is the full cardlist page wrapper even for a single-card keyword. For a batch of 126 cards, that's ~22MB of HTML to parse. Acceptable given HTTP is not the bottleneck (DeepSeek vision API is). If it becomes a concern, the regex parse is fast (no DOM parsing needed).

- **No Referer header required.** Tested without Referer — HTTP 200 on all probes. Bushiroad EN has no hotlink protection on the cardlist image CDN as of this investigation.

- **Resolution variance by set.** AOT/S35, PD/S22, MR/W80, BD/WE35 consistently measure 400×558. SDS/SX03 measured 350×489. MOB/SX02 measured 558×400 (landscape). All are materially above the DBSCG 260×363 floor and should yield usable vision tags.

- **WSdb is gone.** wsdb.xyz returns HTTP 404. Do not reference in implementation docs.
