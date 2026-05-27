# Bulk Graph Bundler (BBL)

**This is a curation project.** The goal — the whole goal, end to end — is to produce **as many unique, curated card bundles as possible** from a personal bulk inventory the rest of the market treats as weight-priced filler. Every script, agent, tag, schema choice, and pipeline decision in this repo is in service of that one outcome: more well-curated bundles.

The unit of work is the **Discrete Lair**: a one-off, named, theme-driven bundle of cards that share a concept the market doesn't see. Mechanics, flavor, art, jokes, vibes. Each bundle is its own SKU. Each tells a story. Each is the labor that creates the value.

The thesis: bulk has near-zero exchange-value individually but rich use-value collectively when sorted with intent. Most bulk sellers move it by weight or by random pack. BBL moves it by *theme* — and the theme is what we sell.

**Brand architecture (locked 2026-05-11):** BBL is the show / label. **Discrete Lair** is the catalog series. Bundles are numbered append-only. The first bundle is **Discrete Lair 001 — Tithe (the men they send)**, an anti-establishment lair anchored on the apparatus of extraction across MTG's various authority castes. Catalog numbers never get reused.

The graph (the tag network, the hub-and-filter taxonomy, the vision-pass enrichment, the symbols layer, the narrative-first lair architect) exists to make those bundles assemblable at scale. Hub tags = candidate bundle anchors. Filter tags = combinatorial narrowing dimensions. Foundational hubs are hand-curated brand-position anchors (Labor, Rebellion, Chinese Zodiac), not auto-generated frequency artifacts. The whole BBL stack is a machine for surfacing "here's a bundle people will want, here's why, and here are 10 cards that compose it."

See also:
- [`BBL-project-spec.md`](BBL-project-spec.md) — full concept, brand voice, political framing.
- [`.claude/agents/`](.claude/agents/) — live agent specs (researcher, triviabot, edgelord, nurse-joy-md, bundler). [`subagents.md`](subagents.md) is historical Plan-A roadmap, preserved for context.
- [`docs/curation-modes.md`](docs/curation-modes.md) — the *forms* a curated bundle can take.
- [`docs/sketchbook.md`](docs/sketchbook.md) — catch-all for half-baked concepts. Currently sketching: bundle-creation subagent (`bbl-bundler`), high-res source art capture, collection-timeline HTML.
- [`references/`](references/) — visual references for well-curated themed binders.

---

## Architecture in one diagram

```
Collectr CSV export
        │
        ▼
   ┌─────────────┐         cards/<game>/<set>/*.md  ◄── source of truth, BBL-internal
   │  csv2mdbot  │  ─────► sealed/<game>/*.md            held_for_lair, tags, bundles, symbols
   └─────────────┘         archive/  (qty=0)
        │                  cards/_hubs/<hub>.md   ◄── foundational concepts (hand-curated)
        ▼                  cards/_symbols/<sym>.md ◄── iconographic primitives
   ┌──────────────┐
   │ researchbot  │  set-aware lookup, IP guards, qty-priority, manual-review queue.
   │  ──────────  │  Plan A: DeepSeek vision API — confirmed NOT in public REST API (chat UI only)
   │              │  Plan B: --prepare-only + bbl-researcher subagent (ACTIVE — the pipeline)
   └──────────────┘
        │
        ▼
   ┌─────────────────────┐
   │ bbl-researcher ─────│──► card body ## Vision section (tags_hub / tags_filter / symbols)
   │ bbl-triviabot ──────│──► card body ## Trivia (canonical web research, anti-confab rules)
   │ wikilintbot   ──────│──► lint reports, safe auto-fixes (self-lint after every write)
   └─────────────────────┘
        │
        ▼
   ┌─────────────────────┐
   │ bbl-bundler (future)│──► bundles/<slug>.json (Discrete Lair NNN — narrative-first)
   └─────────────────────┘
        │
        ▼
   diamondlegendz/bundle-previewer/   ◄── HTML preview + Stripe Payment Link checkout
```

---

## Milestones

### Phase 0 — Spec
- [x] BBL concept locked (`BBL-project-spec.md`)
- [x] Subagent roster + two-tier tag architecture (`subagents.md`)
- [x] HELDFORLAIR commitment-counter design
- [x] Discrete Lair manifest workflow
- [x] **Brand architecture locked** — BBL = show/label, Discrete Lair NNN = series, numbers append-only never reused

### Phase 1 — csv2mdbot
- [x] Collectr CSV → per-card MD graph
- [x] Singles vs sealed split with heuristic
- [x] Archive-on-zero with `archived_on:` stamp
- [x] Persistent BBL-internal field preservation across runs (`held_for_lair`, `tags_*`, `bundles`, `reference_image`, `symbols`)
- [x] CSV-hash skip (idempotent reruns)
- [x] Append-only run history at `reports/history.md`
- [x] **`surgical_update_existing()`** — preserves body content (`## Vision`, `## Trivia`, `## Bundle Use`) across CSV reconciliations. Critical fix after the body-wipe bug destroyed enrichments in May 2026.
- [x] **`_is_non_card_node()`** — recognizes `type: hub` and `type: symbol` plus underscored-path rule so foundational nodes never get clobbered by CSV runs.

### Phase 2 — researchbot
- [x] Scryfall image lookup (MTG) with set-aware confidence flag (`high` / `low` / `none`)
- [x] PokemonTCG.io image lookup (Pokémon)
- [x] IP guardrails: `suspected_ip`, `ip_confidence`, `ip_verified` — never invent character identities
- [x] Manual-review flagging (low-confidence printings)
- [x] Local image cache mirroring `cards/` tree at `cards/_images/`
- [x] qty-DESC priority
- [x] **No-num-* backfill** — cards without a Collectr collector number get their number filled from Scryfall UUID via `--backfill-num` / go-forward fix in researchbot. 1 stragglers remain.
- [x] **Plan B subagent vision pipeline** — `--prepare-only` + `bbl-researcher` subagent (`.claude/agents/bbl-researcher.md`)
  - [x] `apply_vision.py` — single-source-of-truth helper wrapping `update_card`
  - [x] Anti-confab prompt v4 (hair / race / gender / weapons-from-archetype / card-frame-metadata / role-identity conflation)
- [x] **Vision pass at scale across MTG inventory** — 597 cards enriched (49% of 1221-card corpus). Queue: 0.
- [ ] Vision pass at scale across Pokémon inventory
- [ ] Image-source strategy for Dragon Ball Super (no Scryfall equivalent)

### Phase 3 — wikilintbot
- [x] Structural checks: missing frontmatter, qty sanity, duplicate nodes, stale `last_seen`, sealed misclassification, missing reference image
- [x] Tag-tier checks: `tier_confusion`, `format_drift`, `intra_tier_duplicates`, `cross_tier_duplicates`, `singleton_tags`, `missing_tags`
- [x] HELDFORLAIR sanity
- [x] `--fix` mode for unambiguous transforms
- [x] Markdown report output via `--report <path>`
- [x] **Self-lint wired into bbl-researcher** — every vision-pass write triggers a follow-up lint pass on the affected card; tier confusion gets surfaced immediately, not at end-of-sprint.
- [x] **Hub / symbol awareness** — `_is_non_card_node()` recognizes foundational nodes so they don't get treated as malformed cards
- [ ] Broken wikilinks check (no wikilinks in graph yet — defer until cross-card lair references)
- [ ] Hub registry checks (defer — hubs are hand-curated not frequency-elected, so registry-drift logic doesn't apply yet)
- [ ] `--review` mode: guided manual-review walkthrough for `needs_manual_review` cards

### Phase 4 — Lair architect *(reframed: narrative-first, not tag-frequency-first)*
- [x] **First lair shipped: Discrete Lair 001 — Tithe** (2026-05-11). 10-card bundle, 9 distinct cards (Secure the Scene ×2), $5.00 list price. Manual-curated through the workflow that will become `bbl-bundler`.
- [x] **Bundle JSON schema v0.3** at `diamondlegendz/bundle-previewer/sample-bundles/tithe.json` — catalog_id + series_label, hubs/anchors/intent tags, cards array with qty_in_bundle + market_price_usd, cohesion block, pricing block (cost_basis, DIY_alternative, narrative_premium), checkout block (Stripe Payment Link)
- [x] **Pricing model codified** — $5.00 floor, shipping buyer-paid extra, narrative_premium as visible line item so curation labor is legible
- [x] **Multi-copy support** — `qty_in_bundle > 1` when inventory has dupes; bulk-disposal lever that grows with every CSV upload
- [ ] `bbl-bundler` subagent — deterministic Python orchestration + exactly 2 LLM calls (intent_tags expansion + why_it_fits drafts); sketched in `docs/sketchbook.md`
- [ ] Theme/concept parameter parsing → graph query → candidate manifest
- [ ] `available = quantity - held_for_lair - committed-this-run` calculation
- [ ] HELDFORLAIR increment on bundle approval, decrement on ship/dissolve

### Phase 5 — Foundational hubs *(reframed: hand-curated, not auto-elected)*
- [x] **Three foundational hubs shipped** at `cards/_hubs/`: `labor.md`, `rebellion.md`, `chinese-zodiac.md` (2026-05-10)
- [x] `type: hub` frontmatter schema with tag_signals, narrative seeds, anti-patterns
- [x] Bot guards updated to recognize `type: hub` nodes (csv2mdbot, wikilintbot)
- [x] **Hubs serve as brand-position anchors, not frequency artifacts** — Alex authors them; they reflect curator judgment about what BBL is, not what the corpus accidentally clusters around
- [ ] Cross-hub linking once more bundles share themes
- [ ] Auto-elected hub *candidate* list (NOT promoted hubs) — future signal to Alex about emerging clusters worth considering as new hand-curated hubs

### Phase 6 — Symbols layer *(new — shipped 2026-05-11)*
- [x] **First symbol shipped: `orzhov-signet`** at `cards/_symbols/orzhov-signet.md` (eclipsed sun, master-medallion/slave-brand canonical Orzhov iconography)
- [x] `type: symbol` frontmatter schema with name, aliases, faction, canonical_source, confidence, appears_on, related_hubs
- [x] Cards reference symbols via `symbols: ["slug"]` frontmatter field
- [x] Bot guards updated (csv2mdbot, wikilintbot) to recognize `type: symbol` nodes
- [x] **First cross-card cohesion application:** Tithe bundle's why_it_fits prose names the Orzhov Signet on Pitiless Pontiff and cross-references it on Tithe Drinker. The symbol is "literally functional ideology" per Alex.
- [ ] Vision-pass `symbols_observed` field — bbl-researcher proposes a symbol slug when it spots known iconography; apply_vision.py cross-references the library and writes to `symbols: [...]`
- [ ] Wikilintbot bidirectional consistency check between card `symbols:` field and symbol MD `appears_on:` list
- [ ] More symbols: Boros gauntlet, Dimir cipher, Eldraine throne pattern, Theros constellation, etc.

### Phase 7 — triviabot
- [x] **Agent spec shipped** at `.claude/agents/bbl-triviabot.md` (~200 lines)
- [x] Anti-confab rules baked in: no role-identity conflation (caught in first Tithe Drinker test where the agent linked an unnamed common to a named NPC on role overlap alone)
- [x] Writes to card body `## Trivia` section, never frontmatter (frontmatter is for structured data, body is for prose)
- [x] First test run completed on the 9 Tithe-bundle cards
- [ ] Synthesis pass across the rest of the enriched corpus
- [ ] Reddit / EDHREC / Wizards-article integration for community sentiment data
- [ ] Crickets fallback for cards with no signal

### Phase 8 — Storefront / Bundle preview
- [x] **`diamondlegendz/bundle-previewer/`** — separate repo, sibling to BBL. HTML preview page renders bundle JSON into buyer-facing layout
- [x] Sectioned pricing receipt (card values / labor / DIY alternative / narrative premium)
- [x] Stripe Payment Link integration field in schema (placeholder URLs until products go live in Stripe dashboard)
- [x] anime.js v4 entrance animations, CSP-safe
- [x] **Print-shippable** — preview page is printable as bundle inclusion card; date stamped on prices
- [ ] Live Stripe products for shipped bundles
- [ ] Order routing / shipping label generation
- [ ] Multi-bundle catalog page (currently single-bundle preview)

### Future / TBD
- [ ] **Re-probe DeepSeek vision when beta tag drops from chat.deepseek.com** — currently chat-UI-only, watch signal logged. Open-source VL2/Janus weights mean it's the strongest non-OpenAI/non-Anthropic vision model available.
- [ ] Dragon Ball Super / Yu-Gi-Oh / Lorcana / Force of Will image-source strategies
- [ ] Cat Pack assembly automation (recurring-SKU, variable contents)
- [x] **Mystery Booster Cards = The List path migration** — done wave 96.8. Collectr labels PLST inserts as "Mystery Booster Cards"; 34 cards were folder-misfiled + had stale `set:` field. Migration script git-mv'd 34 MDs + 68 images to `cards/magic-the-gathering/the-list/`, patched `set:` field + image paths + body embeds, plus 12 downstream references across layer nodes, the Tithe bundle JSON, the stamping script, and 3 edge-proposal JSONs. Verified clean.
- [ ] **Janitorbot** (Phase 9+) — operates on the populated tag graph, not single cards: synonym collapse (`cat`/`feline`), redundant-pair pruning, hub↔filter tier swaps. Different from wikilintbot (per-card structural rules) — janitor makes whole-graph curation calls.
- [ ] **High-res source art** — sketched in `docs/sketchbook.md`. Current image cache is 488×680 card scans; future tier would pull artist-original art from Scryfall's `art_crop` URL or external sources for bundle hero imagery.
- [ ] Rename `researchbot.py` → `sourcebot.py` (cosmetic; current name is a holdover)

---

## Tech notes

**Stack:** Python 3 stdlib only (no PyYAML, no requests, no python-dotenv — by design, easy to deploy anywhere). Claude Code subagents for tasks that need vision / judgment.

**Inventory source:** Collectr app CSV exports. Headers include a date-suffixed `Market Price` column.

**Card image sources:**
- MTG → Scryfall (`https://api.scryfall.com`)
- Pokémon → PokemonTCG.io v2 (`https://api.pokemontcg.io/v2`)
- Dragon Ball Super → not yet wired
- Other games → not yet wired

**Vision model:** Claude (via the `bbl-researcher` subagent). DeepSeek vision was probed thoroughly in May 2026 — **confirmed NOT in the public REST API**. The chat.deepseek.com web UI uses a separate internal pipeline beta-tagged on the consumer side. 12-variant payload probe + 5 corroborating GitHub issues across unrelated SDKs all hit the same Rust deserialization error: server's message-content enum has exactly one variant declared (`text`). Watch signal: chat UI beta tag drops → re-probe the API.

**Tag architecture:** Two-tier — `tags_hub` (Tier 1, hub-eligible, thematic, becomes graph nodes) and `tags_filter` (Tier 2, mechanical/structural, frontmatter only, never nodes). The split is the load-bearing design decision for graph quality. Color-magic is filter-tier (`blue-magic` etc. NEVER in tags_hub).

**Foundational layers:** Hubs (`cards/_hubs/`) are hand-curated concepts that anchor brand position. Symbols (`cards/_symbols/`) are iconographic primitives with documented canonical meanings from the published source material. Both are first-class graph dimensions with their own MD nodes; cards reference them by slug in frontmatter.

**Buyer-facing copy rule:** No em dashes anywhere a buyer will see (bundle narrative, why_it_fits, marketing copy). Em dashes are fine in commits, memory, sketchbook, code comments, conversation. Scope: anything that reads as AI to the buyer.

**Frontmatter:** Minimal Markdown frontmatter, parsed with regex (no YAML library). BBL-internal fields are preserved across CSV reconciliations via `surgical_update_existing()` in csv2mdbot.

---

## Repo layout

```
.
├── BBL-project-spec.md                # concept, brand voice, political framing
├── subagents.md                       # full subagent roster spec
├── csv2mdbot.py                       # CSV → graph reconciler (with surgical_update_existing)
├── researchbot.py                     # image lookup + vision dispatch (rename to sourcebot pending)
├── bbl_queue.py                       # next-batch picker: 3-prong ready-for-vision check
├── apply_vision.py                    # vision-JSON → MD writer (subagent helper)
├── wikilintbot.py                     # graph linter (structural + tag tier + hub/symbol awareness)
├── bbl_review.py                      # chronological re-review queue + cursor
├── .claude/
│   └── agents/
│       ├── bbl-researcher.md          # vision-pass subagent
│       └── bbl-triviabot.md           # web-research subagent (anti-role-identity-conflation rules)
├── cards/<game>/<set>/*.md            # active card-node graph (Obsidian vault root)
├── cards/_images/<game>/<set>/*.png   # cached reference art (inside vault so embeds resolve)
├── cards/_hubs/*.md                   # foundational hubs (labor, rebellion, chinese-zodiac)
├── cards/_symbols/*.md                # iconographic primitives (orzhov-signet, ...)
├── sealed/<game>/*.md                 # sealed-product nodes
├── archive/                           # qty=0 nodes + triviabot orphans
├── reports/
│   ├── history.md                     # csv2mdbot run log
│   ├── scryfall_sets.json             # cached set-name → code map
│   ├── review_queue.txt               # chronological enrichment order (IS the prompt-version control)
│   └── vision_pending/<game>/<set>/<slug>.json   # vision payloads, set-namespaced
├── MTG-artists.md                     # artist reference notes
├── Pokemon-artists.md                 # artist reference notes
└── collectrexport*.csv                # raw inventory exports

# Sibling repo (separate, public-facing storefront preview):
../diamondlegendz/bundle-previewer/
├── index.html                         # bundle previewer page
├── app.js                             # animations, schema-aware render
└── sample-bundles/tithe.json          # Discrete Lair 001 — first bundle shipped
```

---

## Common operations

```powershell
# Reconcile a fresh Collectr export into the graph
python csv2mdbot.py collectrexport5_10_2026.csv

# Show the next-batch queue (cards truly ready for vision, qty-DESC)
python bbl_queue.py --with-qty --limit 13 --game "Magic: The Gathering"
python bbl_queue.py --count

# Plan B vision flow: prep cached images for the bbl-researcher subagent
python researchbot.py --prepare-only --limit 600 --game "Magic: The Gathering" --scryfall-sleep 1.0

# Apply a vision JSON onto a card by hand
python apply_vision.py cards/path/to/card.md reports/vision_pending/.../card.json

# Lint the graph (report-only)
python wikilintbot.py --quiet --report reports/wikilint_$(Get-Date -Format yyyy-MM-dd).md

# Lint and apply safe auto-fixes
python wikilintbot.py --fix

# Re-review queue: walk older enrichments under the latest prompt
python bbl_review.py status
python bbl_review.py next 13
python bbl_review.py advance 13
python bbl_review.py rewind all

# Re-probe DeepSeek (still text-only as of 2026-05-11)
python researchbot.py --list-models
```

---

## Findings & lessons (durable across sessions)

These survive the rolling status snapshot — load-bearing facts the next session shouldn't have to rediscover.

**On the picker / queue:**
- `csv2mdbot` writes an empty placeholder `reference_image:` line on every card from day one. Any "ready for vision" check that reads only frontmatter without verifying the path on disk will over-count by ~500×. The 3-prong filter in `bbl_queue.py` (non-empty path + on-disk + empty `tags_hub` + not `needs_manual_review`) is the canonical answer.
- `--limit 600` on `researchbot.py --prepare-only` is the magic number for refilling. Deeper limits expose successful fallback-name matches and produce queues of 50+ ready cards.

**On researchbot's idempotency:**
- Re-running `--prepare-only` can flap a card between `prepared` and `manual_review` if Scryfall returns a different best-match on the second pass. The bbl-researcher refusal logic catches this downstream, but the bug remains: `--prepare-only` should skip cards already showing `art_match_confidence: high` AND `os.path.exists(reference_image)`.

**On the IP guardrail:**
- `bbl-researcher` correctly populates `suspected_ip` for in-universe MTG planeswalkers without putting their names in `subject`. 20 cards currently carry IP flags. Verification is downstream and triviabot's responsibility.

**On prompt versioning without metadata:**
- The bbl-researcher prompt is at v4 (anti-confab + role-identity-conflation rules). We deliberately do NOT stamp `prompt_version: N` into card frontmatter. Instead, **the order of cards in `reports/review_queue.txt` IS the version control** — earlier cards = older prompt era. `bbl_review.py` manages a cursor that tracks "everything before this index has been re-reviewed under the current prompt."

**On Obsidian image embeds:**
- The vault is rooted at `cards/`. Anything outside is invisible to Obsidian's resolver. The image cache lives at `cards/_images/<game>/<set>/<slug>.png`. PNGs aren't graphed (only `.md` files become nodes), so the card-only graph constraint is preserved. The underscore prefix sorts visually distinct from card-game directories. Same convention for `_hubs/` and `_symbols/` — foundational nodes outside the card namespace.

**On the body-wipe bug (csv2mdbot, fixed):**
- csv2mdbot was unconditionally re-rendering each card MD on every CSV reconciliation, destroying `## Vision`, `## Trivia`, `## Bundle Use` sections and any non-CSV frontmatter fields. Fixed via `surgical_update_existing()` which only touches CSV-managed fields and leaves body + BBL-internal fields alone. Bodies restored from git history (commit dcfea4d). **Lesson:** never re-render existing nodes; always merge.

**On synonym overlap (Phase-9 janitor's homework):**
- The graph has confirmed synonym pairs surfacing: `cat`/`feline`, `book`/`tome`, `flight`/`flying`, `weapon`/`weapons`. NOT a bug — they reflect honest description of different cards' content. Synonym/redundancy resolution is the future janitorbot's job.

**On hub-tag density:**
- At 22 enriched cards, ~53 hub tags appeared in 2+ cards. At 597 enriched, **945 hub tags shared by 2+** (2112 unique). Bridge density grew super-linear in card count. Lair architect activation threshold is well past.

**On parallel fan-out:**
- The `bbl-researcher` subagent runs 50–135 s per card. Up to 16 in flight verified clean. The refusal logic is robust — agents will not write tags from a wrong-printing image.

**On bundles as narrative-first, not tag-first:**
- Bundles are narrative → tags, not tags → narrative. The title does the persuasion work. Brand voice is anti-establishment / labor / curation-as-rebellion, not "themed boosters." Tithe's title ("the men they send") locks the thesis before any card is named.

**On hubs as hand-curated, not frequency-elected:**
- Hubs are foundational concepts Alex authors. They reflect curator judgment about what BBL stands for, not what the corpus accidentally clusters around. "Labor > solidarity" because hub names need *zing*, not generic-left signifiers. Auto-elected frequency lists are useful as candidate signals but never as promotion sources.

**On symbols as functional ideology:**
- The Orzhov Signet's master-medallion/slave-brand duality is "literally functional ideology" — the same icon meaning opposite things depending on the manner of its bearing. Symbols layer captures this kind of canonical iconographic load. Highest-leverage bundle copy device for cohesion.

**On the DeepSeek vision API:**
- Confirmed NOT in public REST API as of 2026-05-11. 12 payload variants probed, all schema-rejected. 5 corroborating GitHub issues across unrelated SDKs. The chat.deepseek.com UI uses a separate internal pipeline. Re-probe trigger: chat UI drops the beta tag from vision. Until then BBL stays on Claude vision + manual chat-paste workflow.

---

## A note on the agent roster

The mix of scripts (`csv2mdbot.py`, `researchbot.py`, `apply_vision.py`, `wikilintbot.py`) and Claude Code subagents (`.claude/agents/bbl-researcher.md`, `.claude/agents/bbl-triviabot.md`, with `bbl-bundler` sketched) is **deliberately not consolidated**. Each has a distinct verb and runs on a different cadence. Premature merging would freeze interfaces that are still evolving. The right consolidation, *when* it comes, is a thin top-level CLI wrapper (`bbl reconcile <csv>`, `bbl prepare`, `bbl lint --fix`, `bbl bundle <theme>`) — not folding agents into each other.

The pattern: **writers get the keys to wikilintbot; watchers do not.** csv2mdbot, bbl-researcher, and (future) bbl-bundler self-lint after writing. Wikilintbot audits from outside.

---

## Status snapshot (2026-05-27)

- **3,032** active card MDs · **2,474 vision-passed** (82%, by `## Vision` body section) · **1,314 trivia-passed** (43%). Corpus grew +172 cards this session via Collectr CSV intake.
  - MTG: **1,460 cards** · **1,238 vision** (85%) · **711 trivia** (49%) — trivia frontier alive; vision % nudged down from set-expansion
  - Pokemon: **1,070 cards** · **830 vision** (78%) · **250 trivia** — both runways active
  - DBS: **241 / 241** vision · **241** trivia — 100%, finished game
  - Final Fantasy TCG: **64 / 64** vision · **60** trivia — vision-complete
  - Lorcana: **40 / 40** vision · **40** trivia — 100% complete
  - Weiss-Schwarz: **61 / 157** vision (39%) · **12** trivia — early
  - Force of Will: **29** prepped, **0** enriched — low priority
- **Active enrichment frontier:** MTG trivia (~527 vision-passed without trivia) and Pokemon (~240 await vision, ~580 await trivia). Cadence this session: 3–12 vision + 3–12 trivia + 1 Edgelord + 1 CBG per wave (waves 203–213 since last snapshot; wave 213 was a full-swarm 8-agent close).
- **Character nodes: 116** · **Symbol nodes: 11** (constellation, wave 207) · **Artist nodes: 15** (zoltan-boros wave 209, forrest-imel wave 210, daarken wave 211 — densest-art-cluster discipline now load-bearing) · **Hubs: 6** (labor, rebellion, stewardship, chinese-zodiac, tsukumogami, `_triple-thesis.md` meta-doc).
- **Mr. Nodeley pantheon expansion** — Erebos (wave 203) + Heliod (wave 204) + Belzenlok (wave 212) + thallid-lineage (wave 213) joined the character layer. Three pantheon sub-nodes spec-amendment-compliant: WebFetch-verified designer-source citations captured in their commission sidecars per the 2d22fcb6 spec (CBG-009 + CBG-012 + CBG-016 anti-pattern prophylaxis).
- **Discrete Lairs shipped:** 1 — **Discrete Lair 001: Tithe**.
- **Subagents shipped:** **5** — `bbl-researcher`, `bbl-triviabot` (extended this session with **orphan-mirror task profile** under Opus override), `bbl-edgelord` (with Mr. Nodeley + DARK NODESLEY EX alters; **3-sided edge discipline encoded this session**), `bbl-nurse-joy-md`, `bbl-bundler` (half-strength).
- **The Orphanage — FULLY CLOSED (2026-05-25):** corpus-wide one-sided cohort-edge cleanup architecture. `bbl_orphan_count.py` is the manifest+richness-tier counter. **556 → 0 orphans across 9 sweeps + pilot + 3 augments + 1 Mr. Nodeley node-creation — 100%.** First time the corpus is fully wired at the orphan-edge level. Wave-195 surfaced a systematic wikilink-scope-shift failure mode (3 regressions in sweep #9 batch A — `[[rebellion]]` propagation, snipped-edge resurrection, sibling-cross-link generation); spec amended + memory written (`bbl-wikilink-scope-shift`); rule held cleanly across remaining 23 dispatches.
- **Model assignment:** Sonnet 4.6 default; Opus 4.7 for Edgelord AND for triviabot `task: orphan-mirror` (high-stakes prose-mirror work where hallucination cost is asymmetric).
- **Bundles are destructive on graph (wave 81 P3 decision)** — no card-level `anchored_cards` / `thesis_cards` fields on hubs; only `anchored_lairs` (bundle-tier) survives inventory churn. Hubs stay card-edge-disconnected by design.
- **DeepSeek vision verdict:** still NOT in public API. Watch signal: chat.deepseek.com beta-tag drop.

### For the next session — pass-the-ball brief

**Pick up here without reconstructing anything from git log.**

**1. Working tree clean except 2 stray PNGs at root.** Last 5 commits: `54c2658a` (wave 213 full swarm, 12v + 12t + thallid-lineage + CBG round 7), `38933991` (wave 212 + belzenlok node), `4b570142` (CSV intake + csv2mdbot token-collision fix), `a45c6255` (wave 211 + daarken node), `2d22fcb6` (Mr. Nodeley WebFetch spec amendment). Big session: 11 waves shipped (203–213), 1 source-side bug fix (csv2mdbot token-collision), 4 new layer nodes (3 artists + erebos + heliod + belzenlok + thallid-lineage + constellation symbol), 1 wiki-side push (Matt-mirror frame + ai-economics + secondary-crystal pages + index.md retirement).

**2. THE BUG OF THE WEEK — csv2mdbot token-collision (fix shipped in `4b570142`):** Collectr CSV exports include token rows that share collector-number space with parent-set cards (CMR-8 Anointer of Valor ↔ CMR-8 Elf Warrior Token, M21-6 Baneslayer Angel ↔ M21-6 Demon Token). The bug aggregated them to one key, wrongly archived 7 cards over ~1 week (Baneslayer M21-6, 5 others wave-211, Ignite the Beacon WAR-18 from 4 days earlier). Fix: `unique_key()` now includes `COL_NAME` + new `--allow-archive` guard (default = list zero-candidates, require human re-run with the flag). Memory: `bbl-csv2mdbot-token-collision`. **Next CSV ingests need `--allow-archive` to actually archive; without the flag, csv2mdbot lists candidates only.**

**3. CBG-007 / CBG round 7 catch worth surfacing now:** `liliana-vess.md` line 62 four-demon-arc paragraph has FOUR stacked canon-falsifiable errors (CBG-022). Wrong contract chronology, wrong Griselbrand context, wrong Razaketh killer (corpus says Bolas; canonical Wizards "Feast" 2017-06-14 says Liliana with necromancy-raised Luxa crocodiles), wrong Bolas-binding timing. Fix-diff sidecar at `reports/cbg_fix_diffs/CBG-022.json` is the highest-density single paragraph rigor-catch in seven CBG dispatches. Next-pass priority.

**4. CBG fix-diff queue staged but NOT yet applied (14 sidecars):** CBG-011 through CBG-024 sit in `reports/cbg_fix_diffs/`. CBG-001 through CBG-010 are CLOSED. The fix-diff workflow is empirically validated — apply-cost dropped from "re-walk diagnosis" to "git apply + verify." Next session should plan an integration round: apply the 14 sidecars in batch, mark triage entries done, commit. Standard pattern is "run 1-2 waves, then 1 integration round, then resume."

**5. Mr. Nodeley WebFetch spec amendment (commit `2d22fcb6`) has fired 3 clean waves running.** Daarken (wave 211), Belzenlok (wave 212), thallid-lineage (wave 213) all commissioned with WebFetch-or-Puppeteer-verified designer-source receipts captured in their sidecars. The anti-pattern that surfaced as CBG-009 / CBG-012 / CBG-016 (fabricated Rosewater/Stoddard verbatim phrases imported from card trivia into layer-node bodies) is now PROPHYLACTICALLY blocked at commission time. Old corpus drift remains — that's what the CBG fix-diff queue is for.

**6. Two big rule-outs from wave 213 worth carrying forward:**
- Dog Umbra (MH3-22) is NOT a Dog creature subtype; it's an Enchantment-Aura with "Dog" only in the name. m21-dog-tribal cohort does NOT get this expansion. Triviabot caught it.
- Bespoke Battlewagon (MH3-52) is SOLO Boros, not Boros-Szikszai duo. Wave-209 sidecar flagged it for the gabor-szikszai.md future node — that flag was wrong; do not include Bespoke Battlewagon in a future Szikszai node's appears_on.

**7. Staged Sonnet work (Sonnet-shape, NOT Edgelord/Mr. Nodeley):**
- 3 belzenlok attaches pending: Whisper Blood Liturgist DOM-111, Soul Salvage DOM-104, Final Parting DOM-93 (all trivia-passed wave 212)
- 3 thallid-lineage future-attaches pending trivia: Tukatongue Thallid MM2-167, Sarpadian Simulacrum MH3-135, Fungal Infection DOM-94
- liliana-vess.md `appears_on:` extension with Final Parting (per wave-212 trivia handoff)
- Athreos sub-node when N=2 → N=3 (no progress this session)
- Snapping Voidcraw + Twisted Riddlekeeper + Coatl + Wumpus symmetric Connections bullets
- gabor-szikszai.md artist node (4 solo + 2 duo credits per wave-209 stage; but verify each via Scryfall artist field per CBG-024 discipline — Bespoke Battlewagon is OUT)
- Rambunctious Mutt 30.md line 86 upstream Rosewater-fabrication trivia cleanup (CBG-009 upstream)

**2. One active frontier: normal enrichment.** Orphanage stays closed. Wave shape: 3–5 vision + 3–5 trivia + 1 Edgelord per `bbl-agent-batching-pattern`. Priority queues:
- MTG trivia: ~531 cards vision-passed but no trivia — biggest frontier.
- Pokemon: ~198 await vision, ~578 await trivia.
- IP-verification queue: any `suspected_ip + ip_verified: false` cards via `bbl_trivia_queue.py --ip-priority`.

**3. Wave-201 sidecar staged a deferred Sonnet-override task — high priority.** Per `wave201-eldrazi-bfz-subtype-typology-confab-correction.json` next_pass_suggestions (mode-2 narrow-scope, parent-shaped):
- **BFZ Eldrazi 4-card attach to `[[eldrazi]]` cohort:** BFZ 54 Adverse Conditions + 55 Benthic Infiltrator + 56 Cryptic Cruiser + 58 Eldrazi Skyspawner. All four now vision + trivia complete. Standard three-sided attach (frontmatter `characters:` block-form + card body `## Connections` bullet + node `appears_on:` + auto-gen `## Appears on` block). Body-substrate is primed: wave-201 typology fix corrected the Drone/Processor creature-subtype vs Scion/Spawn token-only distinction + added the Ingest→Processor BFZ-block feeding-loop framing. Connections bullets can correctly slot: Benthic Infiltrator + Eldrazi Skyspawner as Drone-tier (Benthic-as-Ingest-source, Skyspawner-as-Scion-generator), Cryptic Cruiser as Processor-tier (closing Ingest-loop with exile-consumption), Adverse Conditions as Devoid-instant-creating-Scion-token. Body roster counter moves 16 → 20; stale BFZ-coverage caveat at lines 140-141 ("Eldrazi Skyspawner remains canonical Eldrazi anchor not yet in inventory") needs deletion in same pass.
- **Snapping Voidcraw + Twisted Riddlekeeper + Hope-Ender Coatl + Wumpus Aberration symmetric Connections bullets** — bundle with above. Mechanical wikilink-discipline: each bullet cites the other three by name+type in backticks (NOT wikilinks — sibling-cohort within-node references, per `bbl-wikilink-scope-shift` Potion sub-rule 5).

**4. Mr. Nodeley wave-202 staged 3 next-wave Sonnet attaches:**
- **Alpine Watchdog (M21-3)** → `[[m21-dog-tribal]]` once vision + trivia complete. Currently pre-enrichment per Edgelord refusal note.
- **Future-watch: `m21-cat-tribal`** parallel node candidate when 3+ M21 cat cards trivia-pass with Rosewater-article-citation parity.
- **Future-watch: `m21-shrine-cycle`** node candidate when 3+ Sanctum cards enrich.

**5. Carried-forward watches (still cold):**
- **Vivi Opus III 3-017L / Opus XXVIII 28-016L** — if either lands in a future CSV pull, attach to `[[ff9-zidane-party]]` (NOT to a new per-character vivi node) unless Vivi-printing density reaches 4+ across distinct Opus sets per node's caveats.
- **son-gohan Discrete Lair candidate** — 7 trivia-passed aspects / 8 corpus prints / qty 18; bundle commission-ready when the labor-credit-erasure thesis stack gets a customer.
- **mogg-fanatic-lineage** still 2/4 corpus per wave-196/200/201 entries; future-watch for Mogg Fanatic / Goblin Grenade / Mogg War Marshal entering corpus to trigger chain or symbol-tier promotion.

**4. Wave-195 rule is now load-bearing**:
- `.claude/agents/bbl-triviabot.md` `## Task profile: orphan-mirror` has the EXACTLY-ONE-WIKILINK rule + 3 named failure modes (hub-inheritance, snipped-edge-resurrection, sibling-cohort-propagation). Applies to any future orphan-mirror run and to bundler when it goes live.
- Memory: `bbl-wikilink-scope-shift` documents the broader scope-shift discipline. Applies to any agent that quotes precedent from one graph layer into a smaller-scope output (cohort → card, hub → bundle, etc.). Adversarial audit step: `git diff` for `\[\[` matches outside the expected slug before every commit involving precedent-quoting agents.

**5. Open triage items (`reports/janitor_triage.md`):**
- **`vision-passed` tag drift** — corpus has 2,386 cards with `## Vision` body section but only 1,670 with `vision-passed` tag. ~716-card discrepancy. Tag-add sweep OR audit which-came-first. Not blocking; `## Vision` body count is canonical.
- **Duskmourn `mana_cost` set-wide sweep** — CONFIRMED systemic; route to `bbl-nurse-joy-md` for full DSK backfill.
- **fear-of-cycle node-body refresh** — denominator needs 14→20 (whole Duskmourn family, DSK + DSC); 6 roster rows to add.
- **DSK-98 Fear of the Dark** — rarity contradiction (card says `C`, node says rare).
- ~~**9 prior-session leftover files in working tree (3 sessions running)**~~ — CLEARED 2026-05-26 via wave-201+202 catch-up flush commit (`2aee4776`). All landed as `review_bad` / "find this image" annotations for later image-source-upgrade triage.
- **elemental-monkey-trio** — Takao Unno designer-attribution conflict, needs a primary source.

**6. Process notes:**
- Caveman SessionStart hook may fire — RETIRED for BBL per `bbl-caveman-novelty-only`; work in normal mode.
- RPC council (`~/.claude/wiki/nodes/RPC.md`) is a protocol Alex runs — ideological lenses (Žižek, Christman, McKenna, Parenti…), not BBL agent-personas.
- Pre-commit recap discipline holds — recap in conversation BEFORE commit, get greenlight, then push.
- Mr. Nodeley Option-C pattern (this session) — when dispatched with a binary judgment, sometimes the right answer is a third option discovered via corpus walk. Vivi-ornitier dispatch posed (A) create per-character node OR (B) strip pointer; Mr. Nodeley found 3 unwired FF9 cards + 2 broken sibling wikilinks and created a per-Category cohort instead. Trust the agent to refuse the binary when the corpus shape demands it.

**7. Future onboards (deferred):** Sorcery: Contested Realm > Force of Will. Neither corpus is scanned. FoW has 29 prep stubs; Sorcery has 0.

### The most important rules locked into project memory

These live in `~/.claude/projects/C--Users-alexa-Desktop-Bulk-Graph-Bundler/memory/` and the next Claude instance pulls them automatically. Locked-in rules to scan: vision queue 3-prong check, broad-net tags_hub (8-12 broad tags, no coined compounds), color-magic is filter-tier, singular/plural intentional (Phase-9 janitor work), anti-confab principles, bundles are narrative-first, hubs are hand-curated, bundle pricing codified, no em dash in buyer-facing copy, verify API capability by calling the API, caveman mode is novelty only, bundles are destructive on graph (wave 81), single-batch vision agent (wave 81 revision), commit-msg temp-file trap, yaml flatten quote wrap.

### What changed this session (waves 184–193 + Orphanage architecture + 9 sweep waves + 4-leftover cleanup, 2026-05-24 to 2026-05-25)

**Sweep #9 + 4-leftover cleanup (final Orphanage push, 2026-05-25):**
- **Sweep #9 batch A (`8198070a`)** — 18 cohorts / 39 cards. User-flagged audit caught 3 wikilink-scope-shift regressions: `[[rebellion]]` propagated from cohort bundle-template note into Turn-into-a-Pumpkin card bullet; staraptor DAA-145 ↔ DAA-147 mirror edge resurrected after explicit wave-120 Edgelord dissolution; breloom DRI-005 ↔ DRI-006 sibling edge added against cohort body's explicit prohibition. Fixed in-place + spec amended (bbl-triviabot.md gets wave-195 EXACTLY-ONE-WIKILINK rule with 3 named failure modes) + memory `bbl-wikilink-scope-shift` saved.
- **Sweep #9 batch B (`f427346b`)** — 18 cohorts / 32 cards across 4 phases for cross-cohort overlap-card file-conflict sequencing (alola-kahunas touches 119-olivia + 193-guzma-hala alone first, then alola-elite-four + team-skull + jace-beleren parallel, then war-gatewatch-triumph-cycle alone). Wave-195 rule held cleanly — 0 wikilink drift across all 18 dispatches.
- **4-leftover cleanup (`48257b73`)** — valgavoth detector-quirk wikilink normalized; larvitar LOT-114 stub bullet; son-gohan cohort augmented with Childhood / Cell-as-genetic-template aspect (7th aspect, BT2-075 closed); vivi-ornitier dispatched to Mr. Nodeley as binary (create node OR strip pointer), agent walked corpus and chose Option C — found 3 unwired FF9 cards (Garnet EX, Freya, Artemicion), created `cards/_characters/ff9-zidane-party.md` per FFTCG per-Category cohort precedent, fixed 2 broken `[[vivi-ornitier]]` wikilinks in ff6-returners-party, then orphan-mirror pass closed the 4 new orphans node-creation surfaced.
- **Final orphan count: 0** (high 0 / medium 0 / low 0 / missing-node 0). 556 → 0 cumulative across 9 sweeps + 3 augments + 1 Mr. Nodeley node-creation.



**Normal enrichment (waves 184–193, 10 waves):**
- ~50 vision + ~50 trivia across the run. New character node: `richard-kane-ferguson` artist node (closed wave-39 staged trigger via Wither and Bloom MH3-111 third credit). New symbol node: `energy-counter` (renamed from `energy` for mechanic-faithful disambiguation; legacy alias retained).
- Vision flagged + triviabot verified multiple IP cards (Mowu, Tamiyo, Davriel, Rellor, Pineco, Maushold, Cottonee, Ludicolo, Gliscor) and refuted others (Marchesa-agent-not-Marchesa, Witherbloom-mage-not-Dina, Mira-not-Goku-fires-Dark-Kamehameha).
- Edgelord ran 1:1 mirrors, cohort attaches, and 1 wave-16-stale-flag cleanup (Honor the God-Pharaoh → nicol-bolas with frontmatter cascade).
- Nurse Joy ran a DSK mana_cost diagnosis; 9 cards backfilled via scratch script.

**Critical bug fixes this session:**
- **YAML quote-wrap bug** — `researchbot._flatten_for_frontmatter()` was JSON-escaping value content without an outer YAML quote wrap, producing malformed `flavor_text: \"X\"` lines. Source-fixed + 431-card corpus sweep applied. Memory `bbl-yaml-flatten-quote-wrap` saved.
- **Commit-msg temp-file trap** — `git add -A` was staging in-tree scratch files before `rm` fired; 2 cleanup commits + `*.tmp` gitignore + memory `bbl-commit-msg-temp-file-trap`.
- **`update_frontmatter_field` BLOCK_LIST_FIELDS bug recurrence** — 88-card sweep (was 25 first time); source-fixed.
- **parse_frontmatter quote-stripping bug** — fixed in 3 copies (researchbot, bbl_queue, csv2mdbot).
- **Prep starvation pattern** — `DEFAULT_LIMIT = None` + `has_ref` priority in sort key; bulk-1-of-each new cards no longer starved.

**Orphanage architecture (built + executed this session):**
- `bbl_orphan_count.py` — Python orchestrator with per-cohort richness assessment.
- `bbl-triviabot` extended with `task: orphan-mirror` profile (Opus override, no web research, per-card refusal allowed, EXPLICIT NON-REFUSAL CONDITION).
- `bbl-edgelord` step 6 extended with "For card→character (cohort) edges" three-sided discipline (prevents new orphans).
- **8 sweep waves + pilot + 2 augments:** dsk-toy-horror pilot (3), sweep #1 son-goku (29+3 cross), Trunks augment (2), sweep #2 (4 cohorts/68), sweep #3 (6 cohorts/71 with spec-sharpening retry mid-sweep), sweep #4 (5 cohorts/45 + 1 refusal triggered son-gohan augment task), sweep #5 (10 cohorts/62), sweep #6 (13 cohorts/66), sweep #7 (15 cohorts/60), sweep #8 (15 cohorts/50). **Cumulative: 556 → 75 orphans (86% closed).**
- **2 cohort-augment edge cases surfaced honestly via refusal mode:**
  - Trunks BT4-023 Iron Vow → Wrath-of-the-Dragon film-canon archetype slot (RESOLVED).
  - Son-Gohan BT2-075 Supreme DNA → Childhood / Android-Cell Saga base-form slot (PENDING — task #12).
- **1 broken pointer surfaced:** `8-016h-vivi → vivi-ornitier` (PENDING — task #10).

**Other graph-shape work:**
- Tsukumogami hub authored last session (carried into this snapshot for continuity).
- 200+ spurious schema-citation wikilinks corrected via sweep (evolution-line cluster).
- Memory saves: `bbl-yaml-flatten-quote-wrap`, `bbl-commit-msg-temp-file-trap`, plus session-handoff state.
