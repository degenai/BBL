# Cardmarket API Investigation — DBSCG Image Access

_Investigated: 2026-05-13_

## TL;DR

Cardmarket's API does expose image URLs (relative paths, ~1-hour signed TTL) and DBSCG is a confirmed supported game on the marketplace. However, **Cardmarket is not currently accepting new API applications**, access is gated to professional sellers only via manual approval, and no public pricing tier exists — making this a dead end for our use case in the near term. The better alternative is TCGAPIs.com, which covers DBSCG among 80+ games with high-res images and a paid subscription starting at ~$9.99/mo.

---

## API Capabilities

- **Image URL exposure:** Yes — the Product entity (API 2.0) includes an `image` field containing a relative path, e.g. `./img/cards/Born_of_the_Gods/springleaf_drum.jpg`. This resolves to a full Cardmarket CDN URL. The URL is **signed and valid for 1 hour only** — not suitable for long-term caching or our prep-time canonical capture pattern.
  - Source: [API 2.0 Product Entity docs](https://api.cardmarket.com/ws/documentation/API_2.0:Entities:Product)

- **Image resolution:** **Unknown — not documented publicly.** The Cardmarket web UI shows card scans (seller-uploaded scans, not publisher art) that vary in quality and dimensions per listing. There is no stated minimum resolution in the API docs, and no specification found in any SDK README or third-party source. The API image path points to Cardmarket's own CDN rather than publisher-sourced art. Given that content is seller-scan-derived, consistency is not guaranteed. Resolution is likely comparable to typical scan uploads (commonly 600–1000px range) but this is unverified.

- **DBSCG coverage:** **Yes.** Cardmarket has a dedicated Dragon Ball Super storefront at `cardmarket.com/en/DragonBallSuper` with expansions listed and singles actively traded. The game is a first-class category, not a niche add-on.
  - Source: [Cardmarket DBS storefront](https://www.cardmarket.com/en/DragonBallSuper), [Expansions list](https://www.cardmarket.com/en/DragonBallSuper/Expansions)

- **OAuth complexity:** OAuth 1.0a, four-token model (app token + app secret + access token + access token secret). Multiple SDKs (PHP, Python pymkm, .NET) implement it, so the pattern is well-understood. Setup complexity is **medium** — not trivial but not novel. The actual blocker is getting credentials at all (see Pricing/Access below).
  - Source: [Auth Overview](https://api.cardmarket.com/ws/documentation/API:Auth_Overview), [pymkm Python wrapper](https://github.com/andli/pymkm)

- **Rate limits:** **600 requests per minute**, HTTP 503 "Slow Down" on breach. Stock export endpoint has a separate cap of 100 different users per 23-hour window. No stated daily cap found.
  - Source: Cardmarket API docs (via search synthesis)

---

## Pricing / Access

- **Free tier:** None documented. No public tiered pricing exists at all.
- **Seller account requirement:** API access is **restricted to professional sellers on Cardmarket** — you must be an active seller with an approved "Dedicated App" credential.
- **Application status:** **Cardmarket is not currently accepting new API applications.** This is explicitly stated in their help center as of the time of this investigation.
  - Source: [help.cardmarket.com/en/cardmarket-api](https://help.cardmarket.com/en/cardmarket-api), [Auth Overview](https://api.cardmarket.com/ws/documentation/API:Auth_Overview)
- **Workaround services:** Third-party aggregators (RapidAPI's "CardMarket API TCG" listing, Apify scrapers) resell Cardmarket data, but these are unofficial, scraper-based, and violate Cardmarket ToS. Not suitable for production.

---

## Comparison

| API | Free? | Image res | DBSCG | Setup |
|-----|-------|-----------|-------|-------|
| Scryfall | Yes | 734px+ (high-res available) | n/a (MTG only) | None — no key needed |
| PokemonTCG.io + Bulbapedia | Yes | 734–1500px | n/a (Pokemon only) | No key needed for basic; key for higher rate limits |
| Cardmarket (official) | No — seller-gated | Unknown (seller scans, inconsistent) | Yes (full catalog) | Hard — applications closed |
| TCGPlayer Partner API | No — **closed to new developers** | ~200–500px (CDN thumbnails; varies) | Yes (CategoryId 27) | Hard — waitlist/closed |
| TCGAPIs.com | Free tier (100 req/day) | "High-res, hotlinkable, multiple resolutions" (specific px unconfirmed) | Yes (80+ games including DBS) | Easy — self-serve API key |

Notes on TCGAPIs.com pricing:
- Free: 100 req/day
- Paid starts at ~$9.99/mo (exact tier unclear — the $9.99 figure is from a related service, tcgapi.dev, which is distinct from TCGAPIs.com; TCGAPIs.com pricing was not publicly confirmed in search results)
- Commercial license included at Pro ($49.99/mo) and Business ($99.99/mo) tiers for tcgapi.dev; TCGAPIs.com may differ

---

## Strategic Verdict

**Cardmarket API is not pursuable right now — applications are closed, access is seller-gated, and image resolution is unverified and scan-derived rather than publisher-art.**

Even if access opened, the 1-hour signed URL TTL is architecturally incompatible with our prep-time canonical capture pattern (we stamp image_url into frontmatter once, read locally downstream; a TTL'd URL breaks that on the second use).

**Recommended next step: probe TCGAPIs.com.** It covers DBSCG, claims high-res hotlinkable images, and offers a self-serve free tier with no gating. Per the BBL verification rule — call the API before reporting capability as a finding. Run a probe call against their endpoint for a known DBSCG card and measure the actual image dimensions returned before committing to any subscription.

TCGPlayer is also closed to new developers; skip it.

---

## Implementation Effort Estimate (Cardmarket, hypothetical if access opened)

- OAuth 1.0a wiring: ~80–100 LoC (pymkm pattern exists as reference)
- Endpoint integration into `researchbot.py` (game-type routing, product lookup by name+set, image URL extraction): ~60–80 LoC
- TTL problem: incompatible with our canonical capture pattern — would require real-time fetch on every research run rather than prep-time stamp; adds ~1 API call per card per enrichment run, not a one-time cost
- Net assessment: **medium implementation lift, but architecturally unsuitable** due to TTL, and moot while applications are closed

For TCGAPIs.com (if probe confirms resolution): ~40–60 LoC to add a DBSCG routing branch in `researchbot.py` analogous to the existing PokemonTCG.io branch. Self-serve key means zero auth-setup overhead.

---

## Sources

- [Cardmarket API 2.0 Main Page](https://api.cardmarket.com/ws/documentation/API_2.0:Main_Page)
- [Cardmarket API 2.0 Product Entity](https://api.cardmarket.com/ws/documentation/API_2.0:Entities:Product)
- [Cardmarket Auth Overview](https://api.cardmarket.com/ws/documentation/API:Auth_Overview)
- [Cardmarket Help — API page](https://help.cardmarket.com/en/cardmarket-api)
- [Cardmarket DBS storefront](https://www.cardmarket.com/en/DragonBallSuper)
- [Cardmonitor/cardmarket-api PHP SDK](https://github.com/Cardmonitor/cardmarket-api)
- [andli/pymkm Python wrapper](https://github.com/andli/pymkm)
- [pyotty/cardmarket-.net-SDK](https://github.com/pyotty/cardmarket-.net-SDK)
- [TCGAPIs.com](https://tcgapis.com/)
- [TCGPlayer developer hub](https://developer.tcgplayer.com/)
- [tcgapi.dev pricing](https://tcgapi.dev/pricing/)
