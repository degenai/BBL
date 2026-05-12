# Bulk Graph Bundler (BBL)

**This is a curation project.** The goal — the whole goal, end to end — is to produce **as many unique, curated card bundles as possible** from a personal bulk inventory the rest of the market treats as weight-priced filler. Every script, agent, tag, schema choice, and pipeline decision in this repo is in service of that one outcome: more well-curated bundles.

The unit of work is the **Discrete Lair**: a one-off, named, theme-driven bundle of cards that share a concept the market doesn't see. Mechanics, flavor, art, jokes, vibes. Each bundle is its own SKU. Each tells a story. Each is the labor that creates the value.

The thesis: bulk has near-zero exchange-value individually but rich use-value collectively when sorted with intent. Most bulk sellers move it by weight or by random pack. BBL moves it by *theme* — and the theme is what we sell.

**Brand architecture (locked 2026-05-11):** BBL is the show / label. **Discrete Lair** is the catalog series. Bundles are numbered append-only. The first bundle is **Discrete Lair 001 — Tithe (the men they send)**, an anti-establishment lair anchored on the apparatus of extraction across MTG's various authority castes. Catalog numbers never get reused.

The graph (the tag network, the hub-and-filter taxonomy, the vision-pass enrichment, the symbols layer, the narrative-first lair architect) exists to make those bundles assemblable at scale. Hub tags = candidate bundle anchors. Filter tags = combinatorial narrowing dimensions. Foundational hubs are hand-curated brand-position anchors (Labor, Rebellion, Chinese Zodiac), not auto-generated frequency artifacts. The whole BBL stack is a machine for surfacing "here's a bundle people will want, here's why, and here are 10 cards that compose it."

See also:
- [`BBL-project-spec.md`](BBL-project-spec.md) — full concept, brand voice, political framing.
- [`subagents.md`](subagents.md) — the agent roster spec.
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
- [ ] **Mystery Booster Cards = The List path migration** — Collectr labels The List (PLST) inserts as "Mystery Booster Cards"; affected 33 cards have been re-tagged with `set: The List` + `the_list_source_set: <ORIG_CODE>` but folder path still says `mystery-booster-cards/`. Holistic janitor pass needed before launch.
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

## Status snapshot (2026-05-12)

- **1,523** active card MDs · **666** enriched (43% of corpus) · vision queue refilled by 5/12 CSV ingest (+80 cards)
  - MTG: 641 / 784 enriched (82%)
  - Pokemon: 25 / 408 enriched (6%) — Galar Gym Leader cluster is the active Pokemon-side thread
- **Character nodes:** **9** — nicol-bolas, fear-of-cycle (5 corpus members), endriders, aether-rangers, jace-beleren, tamiyo, orzhov-syndicate (6 corpus members), azorius-senate, **galar-gym-challenge** (8 corpus members — Allister, Bea, Leon, Nessa, Opal, Melony, Kabu, Milo). Pokemon-side institutional anchor for the apparatus-of-spectacle / labor-as-televised-competition thesis.
- **Symbols:** **1** — `orzhov-signet`, now 4 corpus members (Pitiless Pontiff, Tithe Drinker, Orzhov Locket, Orzhov Guildgate — worn / mounted / stamped at three scales)
- **Artists:** **2** — Jenn Ravenna Tran, Sanosuke Sakuma
- **Foundational hubs:** 3 — `labor`, `rebellion`, `chinese-zodiac`
- **Bolas-Falls triangle:** closed (Topple ↔ Despark ↔ Prison Realm story-spotlight triangle complete; future enlightenment flagged when Liliana + Ugin nodes arrive — refactor 3 mirror legs into 1:N stack on nicol-bolas)
- **Discrete Lairs shipped:** 1 — **Discrete Lair 001: Tithe** (extensible to 5-card via Orzhov Locket + Guildgate signet addition)
- **Subagents shipped:** **5** — `bbl-researcher`, `bbl-triviabot`, `bbl-edgelord` (with Mr. Nodeley + DARK NODESLEY EX alters), `bbl-nurse-joy-md`, `bbl-judge`. Sketched: `bbl-bundler`.
- **Model assignment locked:** Sonnet 4.6 for routine extraction (vision, trivia, triage); Opus 4.7 for graph-spanning judgment (Edgelord, Judge). "Opus is my Eva, Sonnet is the weapons."
- **Dual-pipeline + Judge pattern: DROPPED** — single-Opus-Edgelord is standard; no Judge unless explicit dual-pipeline dispatch
- **Agent batching pattern: LOCKED** (wave 10) — 1 batched agent for trivia (HTTP-bound, serial barely costs wall-clock), 2-3 micro-batched agents × 2-3 cards each for vision (LLM-bound, preserve parallel). ~50-70% per-wave token reduction. Memory at `bbl-agent-batching-pattern.md`.
- **DeepSeek vision verdict:** still NOT in public API as of 2026-05-12. Watch signal: chat.deepseek.com beta-tag drop.

### For the next session — pass-the-ball brief

**Pick up here without reconstructing anything from git log.**

**1. Active enrichment loop is HOT.** Wave 10 ended cleanly. Next wave should use the **new batching pattern** locked in `bbl-agent-batching-pattern.md`:
- **Trivia: 1 batched agent for N cards sequential** (HTTP-bound, serial barely costs wall-clock)
- **Vision: 2-3 micro-batched agents × 2-3 cards each** (LLM-bound, preserve parallel)
- Edgelord stays single-Opus, sequential when multiple
- Wave 10 demo: 4 dispatches for 15 cards (vs old way ~15 dispatches). Same volume, ~57% fewer dispatches.

**2. Wave 10 Phase 2 incomplete.** E1 (Edgelord wave-10 follow-up) hit a 529 server overload during dispatch and was held by user. E2 (fresh look) never dispatched. **Pick up by re-dispatching E1** on the unlucky-lands 10-card cycle scan (Raucous Carnival DSK-266 is anchor, designer-coordinated 13-life triskaidekaphobia cycle per trivia). If 3+ corpus members, Nodeley node-proposal for `cards/_characters/dsk-unlucky-lands-cycle.md`.

**3. galar-gym-challenge cluster is most-active Pokemon-side node** (8 corpus members). Leon arrived 5/12 — node body extended, vision/trivia pending on Leon (Vivid Voltage 154 holofoil). Bea/Opal/Nessa/Milo all got trivia wave 10 — `take` Game Freak designer chain triple-attested → quadruple-attested.

**4. Open Edgelord-flagged future moves (cited in prior sidecars):**
- **Bolas-Falls 1:N collapse** — when Liliana + Ugin character nodes exist, refactor the Topple/Despark/Prison Realm triangle into a 1:N stack on nicol-bolas. N²→N edge cost.
- **Speed Demons DFT↔DSC cross-set bridge** — Ooze Patrol flavor canonically names Valgavoth's race team. Waiting for a DSC corpus member to mirror to.
- **Razorkin faction node** — Hordecaller (DSK-152) is the only corpus member; Needlehead + Ripchain not in inventory. Trigger: 3+ in corpus.
- **Norin character node** — Norin Swift Survivalist (DSK-297) flagged suspected_ip "Norin the Wary" (legacy MTG); triviabot work pending.
- **dsk-room-cycle Nodeley** — 2 corpus members (Smoky Lounge + Moldering Gym). Trigger: 3rd Room card.
- **Saw-references cluster** — Trial of Agony (DSK-159) is the lone Saw-homage card; Saw / Let's Play A Game / Lord of Pain not in corpus.
- **HIJIKI OKA real-world brand integration** — surfaced via Opal trivia (real Galar textile sponsor on her uniform). Parallel to Macro Cosmos but no macro-cosmos node yet.

**5. Janitorial backlog (mostly carried over):**
- 9 manual-review cards (Marnie holofoil `art_match_confidence: low` triage)
- Mystery Booster Cards = The List folder path migration (deferred to holistic janitor pass)
- `bundles: ["tithe"]` sync on Tithe-anchored cards' frontmatter (currently empty)
- Vision-pass agent occasionally over-conservative on color-magic tags when oracle_text omits mana cost (Norin/Keybearer/Domination in wave 10) — fixable in lint pass via mana_cost field

**6. DeepSeek vision:** still chat-beta. Re-probe trigger unchanged.

### The most important rules locked into project memory

These live in `~/.claude/projects/C--Users-alexa-Desktop-Bulk-Graph-Bundler/memory/` and the next Claude instance pulls them automatically:

- **Vision queue uses 3-prong check, never frontmatter alone** — `bbl_queue.py` is the picker.
- **Broad-net tags_hub** — 8–12 broad tags per card, never coined compounds.
- **Color-magic is filter-tier** — `blue-magic` etc. NEVER in `tags_hub`.
- **Singular/plural is intentional** — synonym collapse is Phase-9 janitor work.
- **Update README status snapshot at session close** — Alex has session-close anxiety, the snapshot is the load-bearing artifact.
- **Anti-confab principles** — under-specify rather than guess; no role-noun-imports-default-weapon; no card-frame-metadata reads; no role-identity-from-role-overlap conflation.
- **Bundles are narrative-first** — title does the persuasion work, brand voice is anti-establishment / labor / curation-as-rebellion.
- **Hubs are hand-curated** — foundational concepts authored by Alex, never auto-promoted from frequency.
- **Bundle pricing codified** — $5 floor, shipping buyer-paid extra, narrative_premium as visible line item.
- **No em dash in buyer-facing copy** — em dashes fine in commits/memory/sketchbook, scope is buyer-facing only.
- **Verify API capability by calling the API** — research agents citing AI-influencer blogs are unreliable; probe before reporting.
- **Caveman mode is novelty only** — drop to verbose when explaining workflow or when Alex says "I'm lost."

### What changed this session (2026-05-12)

- **Wave 8 (6 vision + 6 trivia + 2 Edgelords)** — galar-gym-challenge character node landed (3 → 7 corpus members across waves)
- **Wave 9 (6 vision + 6 trivia + 2 Edgelords)** — Bolas-Falls triangle closed (Topple ↔ Despark ↔ Prison Realm); orzhov-signet symbol node extended 2→4 + orzhov-syndicate character node 4→6 (Orzhov Locket + Guildgate as medallion + architectural-scale signet appearances — three-scale read: worn / mounted / stamped)
- **Wave 10 — new batching pattern debuted** (9 vision + 6 trivia + 2 Edgelords scoped, E2 incomplete due to 529): 4 dispatches for 15 cards; Leon arrival completes Galar Supporter 5-cycle (galar-gym-challenge node now 8 members)
- **Agents:** `bbl-edgelord` with Mr. Nodeley (node-proposals) + DARK NODESLEY EX (node-dissolutions) alters; `bbl-nurse-joy-md` (triage diagnoses); `bbl-judge` (dual-pipeline comparator, DROPPED operationally)
- **Layers built:** `cards/_artists/` (Jenn Ravenna Tran, Sanosuke Sakuma); `cards/_characters/` expanded from 0 to 9 nodes
- **Agent batching pattern locked** at `memory/bbl-agent-batching-pattern.md` — 1 trivia agent + 2-3 micro-batched vision agents; ~50-70% per-wave token reduction; applied wave 10
- **Sonnet/Opus model assignment locked** at `memory/bbl-sonnet-for-routine-agents.md` — Sonnet for routine extraction, Opus for graph-spanning judgment, Edgelord locked to Opus via frontmatter after Sonnet visibility limit discovery (Sonnet snapshot saw 390 vs Opus 728 enriched count)
- **Dual-pipeline + Judge pattern dropped** — single Opus Edgelord is standard; Judge only for explicit dual-pipeline dispatch (rare)
- **Sequential Edgelord pattern** — when batching multiple Edgelords in one wave, run sequential (not parallel) to avoid MD-write race conditions
- **csv2mdbot hub-protection guard** — frontmatter `type:` check + `_`-dir guard prevents zero/archive of layer nodes (hubs/symbols/artists/characters)
- **Anti-confab catches this session:**
  - Manifest Dread blue-magic palette-confab → "color-magic from oracle_text not palette" rule baked into bbl-researcher spec
  - Aether Rangers Edgelord stale-input artifact → "sequential, not parallel" Edgelord rule
  - Diversion Specialist "Duskmourn Survivor" creature-type → actually Human Warrior (triviabot caught)
  - Razorkin faction-wide carnival framing → REFUTED (per-card art choice only, no Wizards Planeswalker's Guide support)
  - Trial of Agony "Trial of cycle" → REFUTED (lone in DSK per Scryfall set search; Saw-homage cluster instead)
  - Smoky Lounge / Moldering Gym stag-skull sibling reading → REFUTED (different artists, different art content; the wave-8 vision agent confabbed shared iconography that doesn't exist)
- **Edgelord triangle topology** — Bolas-Falls (Topple/Despark/Prison Realm) is the corpus's first closed-triangle structural shape
