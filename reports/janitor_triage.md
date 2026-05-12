# Janitor triage

The parking lot for cleanup items that surface during enrichment but aren't worth interrupting a wave for. Each entry has:
- **What** — the specific finding
- **Where** — path or scope
- **Severity** — `block` (gates launch), `warn` (degrades quality but works), `note` (future improvement, not urgent)
- **Surfaced** — agent / pass that flagged it
- **Status** — `open`, `claimed`, `done`

Whoever runs a janitor pass works from the top down. When an item closes, move it to the closed section at the bottom (or delete; the git log preserves the history).

---

## Open — card-level data issues

- **Switch / Energy Switch mismatch** — `cards/pokemon/crown-zenith/144-159-switch.md`. Severity: `warn`. Collectr CSV says Switch no. 144 (Common, swap-active-Pokémon Trainer Item). Cached image, artist (`Toyste Beach`), and oracle_text are all Energy Switch no. 129 (Uncommon, move-basic-energy). PokemonTCG.io fuzzy match returned the wrong card. Fix: re-prep with explicit set-and-number constraint, or hand-pull the correct Switch image. Surfaced by Switch triviabot run, 2026-05-11. Status: `open`.

- **Manifest Dread color-identity mis-tag** — `cards/magic-the-gathering/duskmourn-house-of-horror/189-manifest-dread.md`. Severity: `warn`. Frontmatter `tags_filter` includes `blue-magic`, `multicolor-blue-green`, and `instant`. Scryfall ground truth: **mono-green sorcery, color identity [G], mana_cost `{1}{G}`**. The vision agent mis-read the teal-amber palette as a blue color-magic signal. Three filter tags are factually wrong. Fix: edit frontmatter to `green-magic` + `sorcery`, remove the wrong tags. **Possibly a broader pattern** — other vision-pass cards may have similar palette-vs-cost confusion. Worth a corpus-wide audit: cross-check each card's color-magic / type filter tags against its (now-captured) `oracle_text` content. Surfaced by Manifest Dread triviabot, 2026-05-11. Status: `open`.

  **Agent-spec implication:** the bbl-researcher agent currently infers color-magic from palette. Since prep-time capture stamps `oracle_text` and `mana_cost` into frontmatter, future vision passes should consult those as ground truth for color/type filter tags, not the palette. Filed as a spec-amendment candidate.

- **9 manual_review stragglers** — `cards/magic-the-gathering/{10th-edition,8th-edition,art-series-zendikar-rising,core-set-2021,modern-horizons,oath-of-the-gatewatch,promo-pack-throne-of-eldraine,promo-pack-zendikar-rising,unstable}/*.md` (full list in `reports/mtg_prep_5_11_resume.log`). Severity: `note`. Genuine edge cases — tokens, art-series, alt-art showcases, foil-only promos. Either accept they stay manual-review or build a triage UI. Surfaced 2026-05-08, still open. Status: `open`.

- **48 Pokémon manual_review stragglers** — mostly set-name mismatches between Collectr and PokemonTCG.io (Sword & Shield Base Set, Brilliant Stars, etc). Severity: `warn`. Many will likely resolve with a SET_NAME_ALIASES table extension for Pokémon. Surfaced 2026-05-11. Status: `open`.

- **no-num-*.md stragglers (~1 MTG, several Pokémon)** — Collectr exported with empty Card Number column. Severity: `note`. The go-forward fix is in researchbot (Scryfall UUID → collector_number); these few never resolved. Status: `open`.

## Open — schema / architecture

- **The Forest Remembers needs catalog assignment + schema v0.3 upgrade** — `diamondlegendz/bundle-previewer/sample-bundles/the-forest-remembers.json`. Severity: `note`. Pre-Tithe bundle with no `catalog_id`, no `art_crop_url` per card, $11.99 price, old narrative. Either: promote to Discrete Lair 002 with re-curation, or formally retire as a draft. Currently hidden from the hub by the manifest filter. Surfaced by the hub rebuild 2026-05-11. Status: `open`.

- **`bundles: ["tithe"]` sync on the 9 Tithe cards** — the cards' frontmatter `bundles:` field is still `[]`. Severity: `note`. Should be backfilled to `["tithe"]` for downstream traceability (a card → which bundle uses it). Status: `open`.

- **The List path migration** — 33 cards under `cards/magic-the-gathering/mystery-booster-cards/` are actually The List (PLST) inserts. They've been re-tagged with `set: The List` + `the_list_source_set: <CODE>` but the folder path still reads `mystery-booster-cards/`. Severity: `warn`. Storefront launch wants this fixed before going commercial. Status: `open`.

- **Stale `**Suspected IP:** ... verified: False` inline line on older triviabot-verified cards** — first observed on Tamiyo, Collector of Tales (PLST). Severity: `note`. The agent spec was updated 2026-05-11 to reconcile both the callout AND the inline line, but cards verified BEFORE that spec amendment still have the stale inline line. Janitor pass: grep for `verified: False` on cards where frontmatter says `ip_verified: true`, regex-swap. Status: `open`.

- **Vision-body inline metadata redundancy** — every vision-pass card has `**Suspected IP:** ...` as a line below the Vision callout AND the callout itself contains the same info. Severity: `note`. Cosmetic — could collapse to one or the other. Decide before any "what to render in Obsidian" pass. Status: `open`.

## Open — future-node candidates (Mr. Nodeley's wishlist)

- **Cinderella Cycle (ELD) — symbol or hub** — designer-confirmed in Rosewater's "More Odds & Ends: Throne of Eldraine" (the Mouse creature type was invented for Enchanted Carriage). Cycle members: Enchanted Carriage (in corpus ✓), Turn into a Pumpkin, Fairy Guidemother, Midnight Clock. Nodeley trigger when ≥3 cycle members are enriched. Surfaced by Enchanted Carriage triviabot.

- **WAR Uncommon Planeswalker Cycle — hub or symbol** — Rosewater-confirmed design template: hybrid cost, one ability, high loyalty for slot. Members in corpus: Angrath (#227), Kiora (#232). Other cycle members exist (Vivien #175, Kasmina #196, plus 17 more across colors). Nodeley trigger when ≥3 cycle members are enriched. Surfaced by Kiora triviabot.

- **Gatewatch's Triumph cycle (WAR) + Gatewatch's Defeat cycle (HOU)** — 5+5=10 card narrative bookend by Kieran Yanner. Triumph (WAR): Gideon, Jace ✓, Liliana, Chandra, Nissa. Defeat (HOU): same five characters. Nodeley trigger when ≥3 cycle members enriched OR when both cycles are partially present. Surfaced by Jace's Triumph triviabot.

- **Wanderer Arc (multi-set) — character or hub** — 5-card identity reveal across WAR → NEO → ONE → DSK plus Kaito Shizuki. Currently only Wanderer's Strike (WAR #38) in corpus. Defer until ≥2 arc cards present. Surfaced by Wanderer's Strike triviabot.

- **Sanosuke Sakuma — artist node** — Larvitar's illustrator, also designed SWSH in-game trainer-class characters: Worker, Backpacker, Office Lady, Doctor, Artist, Police Officer, Poke Kid. Cross-medium portfolio, direct hit on the labor hub. Direct future-bundle anchor for any "Galarian Working-Class" Pokémon lair. **Hold until enough of her TCG cards land in inventory to make the artist node load-bearing.** Surfaced by Larvitar triviabot.

- **Liliana Strikes Back / Bolas Falls cluster** — Despark ✓ + Topple the Statue ✓ + (pending: God-Eternal Oketra, God-Eternal Bontu, Liliana Dreadhorde General, The Elderspell, Awakening of Vitu-Ghazi). Story-spotlight cluster. Nodeley trigger when ≥4 cluster members enriched, or Edgelord trigger when any pair surfaces. Surfaced by Despark + Topple triviabots.

- **Saint/Heretic Church of Dusk pair** — Vito ✓ + (pending: Elenda the Dusk Rose). When Elenda enters inventory, immediate Edgelord 1:1 candidate. Surfaced by Vito triviabot.

## Open — parent-only Cloudflare fetch backlog

When a triviabot subagent reports it fell through to WebSearch because tier 2 Puppeteer was permission-denied, the parent (me / Alex) can run the real Puppeteer fetch on demand. Workflow: append URL + context here; I batch-fetch via `node scripts/puppeteer-fetch/fetch.js <URL>` periodically and inject the content back to the relevant card via Edit.

(Empty for now — agents have been working around it via WebSearch snippets adequately. Populate when a specific card's trivia is starved for primary-source content.)

## Open — subagent-runtime notes

- **Subagent Bash is permission-gated** — apply_vision.py and any `node scripts/...` calls auto-deny in subagent runtime. Parent applies JSONs and runs Puppeteer. Documented in `bbl-researcher.md` and `bbl-triviabot.md` agent specs. Stays here as a reminder for future agent design.

- **MTG Wiki Fandom + Bulbapedia are Cloudflare-walled even with curl+browser-UA.** Tier 2 (Puppeteer, parent-only) clears the wall. Subagents fall through to WebSearch. Documented in agent specs.

## Closed

(none yet — log items here with their resolution sha when they're done)
