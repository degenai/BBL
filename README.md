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

## Status snapshot (2026-05-15)

- **1,954** active card MDs · **1,658 vision-passed** (85%) · **563 trivia-passed** (29%). Wave 81 ingest +136 cards (5/14c Collectr CSV); wave 83 onboarded Lorcana as 5th game.
  - MTG: **1,007 / 1,022** vision (99%) · **161** trivia (16%) — vision essentially complete; trivia is the active frontier
  - Pokemon: **415 / 519** vision (80%) · **201** trivia (39%)
  - DBS: **215 / 218** vision (99%) · **196** trivia (90%) — near parity, most-finished game
  - Lorcana: **12 / 40** vision (30%) · **5** trivia (13%) — pipeline shipped wave 83 (LorcanaJSON bulk + 1468×2048 Ravensburger CDN)
  - Weiss: **9 / 126** vision (7%) · **0** trivia — early days
  - Force of Will: 29 cards prepped, 0 enriched — not yet scanned, low priority. Sorcery: Contested Realm sits above FoW as the next preferred onboard target (not yet ingested).
- **Active enrichment frontier:** MTG trivia backlog — 846 cards vision-passed without trivia. Bulk of next session's work.
- **Character nodes: 80** (up from 9 at wave 10). Recent commissions span DBS family/cohort nodes (vegeta, pan, son-goku, trunks, son-gohan, krillin, bardock, hercule, broly, majin-buu, son-goten, uub, wmat-tournament-announcer, machine-mutants-m2), Pokemon evolution-lines (charizard / mareep / staraptor / larvitar / caterpie / ralts / rowlet / pancham / phantump), MTG planeswalkers + factions (chandra, kiora, angrath, ral-zarek, oko, iona, phyrexia, izzet-league, theros-pantheon, zendikari-resistance), and designer-coordinated cycles (eld-cinderella-cycle, dsk-unlucky-lands-cycle, fear-of-cycle, dsk-survival-archetype, crane-school-cohort, destroyer-god-attendant-dyad).
- **Symbol nodes: 9** — orzhov-signet, disguise, eerie, manifest-dread, monarch-at-common-cmr, rooms, single-strike-emblem, suspect, survival.
- **Artist nodes: 6** — Jenn Ravenna Tran, Sanosuke Sakuma, Kagemaru Himeno, Ken Sugimori, Kirisaki, Dan Murayama Scott.
- **Foundational hubs: 4** — labor, rebellion, chinese-zodiac, stewardship. `_triple-thesis.md` is a meta-doc (root crystal), not a hub.
- **Triangles closed:** Bolas-Falls (Topple ↔ Despark ↔ Prison Realm, wave 9); second explicit triangle wave 74-78. Triple-thesis doctrine locked wave 70-73.
- **Discrete Lairs shipped:** 1 — **Discrete Lair 001: Tithe**.
- **Subagents shipped:** **5** — `bbl-researcher`, `bbl-triviabot`, `bbl-edgelord` (with Mr. Nodeley + DARK NODESLEY EX alters), `bbl-nurse-joy-md`, `bbl-bundler` (half-strength). `bbl-judge` was dropped wave 92.5 (dual-pipeline pattern retired per memory `bbl-dual-pipeline-judge-pattern`).
- **Model assignment locked:** Sonnet 4.6 for routine extraction (vision, trivia, triage, bundler); Opus 4.7 for Edgelord. "Opus is my Eva, Sonnet is the weapons."
- **Agent batching pattern: REVISED wave 81** — 1 batched agent for trivia + **single-batch vision agent (N cards sequential)** instead of 2×5. ~60-70% per-wave token reduction. Memory at `bbl-agent-batching-pattern.md`.
- **Bundles are destructive on graph (wave 81 P3 decision)** — no card-level `anchored_cards` / `thesis_cards` fields on hubs; only `anchored_lairs` (bundle-tier) survives inventory churn. Triple-thesis is the root crystal; hubs stay card-edge-disconnected by design.
- **Lorcana pipeline shipped (wave 83)** — `researchbot.py` gains `find_image_lorcana()` reading from `reports/lorcana_allcards.json` (LorcanaJSON bulk); image quality is **highest in corpus** at 1468×2048 JPEG. No art-only crop available (frame fused at design). 40 cards prepped.
- **DeepSeek vision verdict:** still NOT in public API as of 2026-05-15. Watch signal: chat.deepseek.com beta-tag drop.

### For the next session — pass-the-ball brief

**Pick up here without reconstructing anything from git log.**

**1. Wave 85 is APPLIED but UNCOMMITTED.** Power went out before commit. Prong A (3 DBS character attaches: BT4-030 → vegeta, BT4-097 → son-goku, BT3-028 → pan/son-goku/trunks triple) is already in the working tree. Prongs B/C (Lorcana villain-symbol REJECT, Aetherdrift 3 sub-threshold team candidates) already logged into `reports/janitor_triage.md`. **Next step: big commit covering waves 82-85 + Lorcana infra.** ~203 modified files in working tree.

**2. Active frontier: MTG trivia backlog.** 846 MTG cards vision-passed without trivia (1007 vision - 161 trivia). The HTTP-bound batched-trivia pattern (1 agent / N cards sequential) is the right shape; dispatch in 10-20 card batches.

**3. Next-wave Nodeley batch is queued (5 nodes, all above threshold):**
- `majin-buu` (3 anchors, BT1-047 / BT4-015 / TB2-028) — scope to Good Buu / Mr. Buu identity
- `broly` (4 anchors, all Movie 8 / 1993 non-canon Koyama Broly)
- `son-goten` (3 direct anchors + Mighty Mask dual + 3 Gotenks co-anchors)
- `uub` (3 anchors, the canonical Kid Buu reincarnation / Goku's final successor)
- `wmat-tournament-announcer` (TB2-065/066/067 designer-coordinated 3-card cycle)

Placeholder MDs for 5 of these are already untracked in working tree (broly.md, majin-buu.md, son-goten.md, uub.md, wmat-tournament-announcer.md, machine-mutants-m2.md) — verify body completeness before committing.

**4. Lorcana enrichment is the active expansion frontier on the Lorcana side.** 12 / 40 vision-passed; pipeline is hot. Cross-IP diversity means villain-archetype / mentor-archetype-tier nodes are deferred (Prong B verdict); Disney-IP-cohort character nodes trigger at 3+ same-film prints (e.g., 3+ Aladdin cards → potential Aladdin-villains node).

**5. Open Edgelord-flagged future moves (cited in prior sidecars):**
- **Aetherdrift teams** (3 sub-threshold candidates parked in triage): goblin-rocketeers, keelhaulers, champions-of-amonkhet
- **Ginyu Force cohort** — 3 anchors / 2 unique members; commission when a 3rd Force member (Guldo / Burter / Jeice) enters corpus
- **Acerola** — 1 enriched + 1 prep-stub Acerola's Mischief; commission when stub completes
- **Bolas-Falls 1:N collapse** — when Liliana + Ugin character nodes exist
- **Saint/Heretic Church of Dusk** (Vito + Elenda when she arrives); **Slobad** when a depicted Slobad print lands; **Ajani Goldmane** at second depiction; **Gideon Jura** maintained refusal pending second depiction.

**6. Janitorial backlog (carries forward):**
- 9 MTG manual-review stragglers + 48 Pokemon manual-review stragglers
- 28 colorless-mana-cost artifact cards parked for curator review in `reports/color_magic_human_review.json` (Talismans, Lockets, Diamonds, etc — color tags may be intentional faction-identity signals)
- Several `bbl_node_audit.py` refinement asks (wikilink-categorization, foundational-hub threshold exemption, cross-wiki refs)
- Stale `**Suspected IP:** verified: False` inline lines on older trivia-verified cards (cosmetic)

**7. Future onboards (deferred):** **Sorcery: Contested Realm** sits above **Force of Will** in priority — neither corpus is scanned yet. FoW has 29 prep stubs; Sorcery has 0.

**8. DeepSeek vision:** still chat-beta as of 2026-05-15. Re-probe trigger unchanged.

### The most important rules locked into project memory

These live in `~/.claude/projects/C--Users-alexa-Desktop-Bulk-Graph-Bundler/memory/` and the next Claude instance pulls them automatically. Locked-in rules to scan: vision queue 3-prong check, broad-net tags_hub (8-12 broad tags, no coined compounds), color-magic is filter-tier, singular/plural intentional (Phase-9 janitor work), anti-confab principles, bundles are narrative-first, hubs are hand-curated, bundle pricing codified, no em dash in buyer-facing copy, verify API capability by calling the API, caveman mode is novelty only, bundles are destructive on graph (wave 81), single-batch vision agent (wave 81 revision).

### What changed this session (waves 82-85, 2026-05-13 to 2026-05-15)

- **Wave 82** — Sonnet 4.6 vision diff-test on Larvitar / Frantic Strength / Manifest Dread → Sonnet ≥ Opus, ~5× cost reduction. Routine agents locked to Sonnet; Edgelord stays Opus.
- **Wave 83** — **Lorcana pipeline shipped.** `researchbot.py` gains `find_image_lorcana()` + LorcanaJSON bulk index. 40 Lorcana cards prepped from CSV; first 5 enriched in scout pass. Image quality is highest in corpus (1468×2048 JPEG). No art-crop available (frame fused at design).
- **Wave 84** — `machine-mutants-m2` Mr. Nodeley node (Giru-anchored DBS character cohort).
- **Wave 85 (in flight — applied but uncommitted)** — 3-prong Edgelord dispatch:
  - Prong A: BT4-030 At All Costs Vegeta → vegeta; BT4-097 Instant Transmission → son-goku; BT3-028 Grand Tour Spaceship → pan + son-goku + trunks (triple-attach)
  - Prong B: Lorcana villain-archetype symbol — REFUSED (cross-IP diversity, no designer-stamped Villain subtype, 4/5 villain-tag sample too thin)
  - Prong C: Aetherdrift teams (Goblin Rocketeers / Keelhaulers / Champions of Amonkhet) — REFUSED with receipts, 3 candidates parked in triage at 1-of-3 threshold
- **5-Nodeley batch queued** for next wave (majin-buu / broly / son-goten / uub / wmat-tournament-announcer); placeholder MDs already in tree, untracked.
- **survival** symbol node added (`cards/_symbols/survival.md`, untracked).
- **Anti-confab catches this session:**
  - Lorcana Prong-B scout: refused villain-archetype node on cross-IP diversity grounds (would be tag-bridge across unrelated narrative universes)
  - Aetherdrift Prong-C: refused generic 'aetherdrift-grand-prix-teams' meta-node on grounds that teams are explicit RIVALS, not allies — abstracting them would erase the canonical inter-team friction
