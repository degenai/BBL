# Bulk Graph Bundler (BBL)

**A curation engine and storefront for trading card bulk.** The product is the curation: themed one-off bundles ("Discrete Lairs") drawn from the strata of cards corporate resellers ignore — commons, near-worthless rares, off-meta sets — assembled around concepts that cut across set boundaries: mechanics, flavor, art, jokes, vibes.

The thesis: bulk has near-zero exchange-value individually but rich use-value collectively when sorted with intent. Most bulk sellers move it by weight or random pack. BBL moves it by *theme* — and that theme is the labor that creates the value.

> See [`BBL-project-spec.md`](BBL-project-spec.md) for the full concept, brand voice, and political framing. See [`subagents.md`](subagents.md) for the full agent roster spec.

---

## Architecture in one diagram

```
Collectr CSV export
        │
        ▼
   ┌─────────────┐         cards/<game>/<set>/*.md  ◄── source of truth, BBL-internal
   │  csv2mdbot  │  ─────► sealed/<game>/*.md            held_for_lair, tags, bundles
   └─────────────┘         archive/  (qty=0)
        │
        ▼
   ┌──────────────┐  set-aware lookup, IP guards, qty-priority,
   │ researchbot  │  manual-review queue. Image cache in images/.
   │  ──────────  │
   │ Plan A: DeepSeek V4 vision (BLOCKED — not in API yet)
   │ Plan B: --prepare-only + bbl-researcher subagent (ACTIVE)
   └──────────────┘
        │
        ▼
   ┌─────────────────────┐
   │ lair architect ─────│──► lairs/pending/   (manifests for review)
   │ hub curator   ──────│──► _hubs/<tag>.md   (Tier 1 graph nodes)
   │ triviabot     ──────│──► card body ## Trivia
   │ wikilintbot   ──────│──► lint reports, safe auto-fixes
   └─────────────────────┘
```

---

## Milestones

### ✅ Phase 0 — Spec
- [x] BBL concept locked (`BBL-project-spec.md`)
- [x] Subagent roster + two-tier tag architecture (`subagents.md`)
- [x] HELDFORLAIR commitment-counter design
- [x] Discrete Lair manifest workflow

### ✅ Phase 1 — csv2mdbot
- [x] Collectr CSV → per-card MD graph
- [x] Singles vs sealed split with heuristic
- [x] Archive-on-zero with `archived_on:` stamp
- [x] Persistent BBL-internal field preservation across runs (`held_for_lair`, `tags_*`, `bundles`, `reference_image`)
- [x] CSV-hash skip (idempotent reruns)
- [x] Append-only run history at `reports/history.md`
- [x] **First reconciliation run (2026-05-07): 977 singles + 16 sealed.**

### 🔄 Phase 2 — researchbot (in progress)
- [x] Scryfall image lookup (MTG) with set-aware confidence flag (`high` / `low` / `none`)
- [x] PokemonTCG.io image lookup (Pokémon)
- [x] IP guardrails: `suspected_ip`, `ip_confidence`, `ip_verified` — never invent character identities
- [x] Manual-review flagging (low-confidence printings)
- [x] Local image cache mirroring `cards/` tree
- [x] qty-DESC priority
- [x] 3 hand-curated MTG vision passes as format reference (`_phase1_apply.py`)
- [x] **Plan B fallback for vision** — DeepSeek hosted API does not yet serve a multimodal model; vision pass ports to a Claude Code subagent
  - [x] `researchbot.py --prepare-only` — image fetch + cache + frontmatter stamp, no LLM call
  - [x] `apply_vision.py` — single-source-of-truth helper wrapping `update_card`
  - [x] `.claude/agents/bbl-researcher.md` — subagent definition
- [ ] Vision pass at scale across MTG inventory
- [ ] Vision pass at scale across Pokémon inventory
- [ ] Image-source strategy for Dragon Ball Super (no Scryfall equivalent)

### 🔄 Phase 3 — wikilintbot
- [x] Structural checks: missing frontmatter, qty sanity, duplicate nodes, stale `last_seen`, sealed misclassification, missing reference image
- [x] Tag-tier checks: `tier_confusion` (color-magic + composition + rarity/type tags in `tags_hub`), `format_drift` (non-kebab-case), `intra_tier_duplicates`, `cross_tier_duplicates`, `singleton_tags`, `missing_tags`
- [x] **`vocabulary_drift` (plural/singular) check REMOVED 2026-05-08.** Singular vs plural can carry distinct visual content (`sword` = one blade, `swords` = a rack); collapsing them is a synonym/semantics decision, not a string-edit one. Punted to Phase 5 janitor.
- [x] HELDFORLAIR sanity: `held_for_lair > quantity`, negative or non-numeric values
- [x] `--fix` mode for the unambiguous transforms (move filter-tier tags from `tags_hub` to `tags_filter`, resolve cross-tier duplicates, dedupe within tier). Other findings remain report-only.
- [x] Markdown report output via `--report <path>`
- [ ] Broken wikilinks check (no wikilinks in graph yet — defer until lairs exist)
- [ ] Hub registry checks: registry drift, orphan hubs, promotion candidates, vocabulary cap warnings (defer until hubs exist)
- [ ] `--review` mode: guided manual-review walkthrough for `needs_manual_review` cards

### ⏳ Phase 4 — lair architect *(blocked on vision tags)*
- [ ] Theme/concept parameter parsing → graph query
- [ ] `available = quantity - held_for_lair - committed-this-run` calculation
- [ ] Candidate-manifest generation (no double-booking)
- [ ] `lairs/pending/` review workflow
- [ ] HELDFORLAIR increment on approval, decrement on ship/dissolve

### ⏳ Phase 5 — hub curator *(blocked on vision tags)*
- [ ] Tag-frequency tally across enriched graph
- [ ] Top-N candidate proposal
- [ ] Human-in-the-loop confirmation flow (one batch at a time)
- [ ] Hub MD generation + wikilink injection
- [ ] `_hubs/_registry.md` maintenance + cap warnings (30/50)

### ⏳ Phase 6 — triviabot
- [ ] Community-source search (Reddit, EDHREC, Bulbapedia, etc.)
- [ ] Synthesis + writeback to `## Trivia` section
- [ ] Crickets fallback for cards with no signal

### Future / TBD
- [ ] Re-enable Plan A (DeepSeek V4 vision) when the API endpoint ships — drop-in via `--model` flag
- [ ] Storefront / order flow (Shopify? something simpler? indie marketplace? — open question)
- [ ] Dragon Ball Super / Yu-Gi-Oh / Lorcana / Force of Will image-source strategies
- [ ] Cat Pack assembly automation (recurring-SKU, variable contents)
- [ ] Convert `subagents.md` specs into invokable Claude Code subagents (`.claude/agents/*.md`) once each pipeline stabilizes — `bbl-researcher` is the first
- [ ] **Janitorbot** (Phase 5+) — operates on the populated tag graph, not single cards: synonym collapse (`cat`/`feline`), redundant-pair pruning, hub↔filter tier swaps when a tag's actual usage contradicts its tier. Not the same as wikilintbot — wikilintbot enforces structural rules per-card; the janitor makes whole-graph curation calls.
- [ ] Rename `researchbot.py` → something like `sourcebot.py` / `layer1bot.py` — current name is a holdover from when it was going to do vision too. Now it only sources layer-1 data (images, IP guards, set lookups). Cosmetic; do as separate clean-rename commit.

---

## Tech notes

**Stack:** Python 3 stdlib only (no PyYAML, no requests, no python-dotenv — by design, easy to deploy anywhere). Claude Code subagents for tasks that need vision / judgment.

**Inventory source:** Collectr app CSV exports. Headers include a date-suffixed `Market Price` column.

**Card image sources:**
- MTG → Scryfall (`https://api.scryfall.com`)
- Pokémon → PokemonTCG.io v2 (`https://api.pokemontcg.io/v2`)
- Dragon Ball Super → not yet wired
- Other games → not yet wired

**Vision model:** Pending DeepSeek V4 multimodal API rollout. Until then, the `bbl-researcher` Claude Code subagent runs the vision pass.

**Tag architecture:** Two-tier — `tags_hub` (Tier 1, hub-eligible, thematic, becomes graph nodes; ~30 max curated) and `tags_filter` (Tier 2, mechanical/structural, frontmatter only, never nodes). The split is the load-bearing design decision for graph quality.

**Frontmatter:** Minimal Markdown frontmatter, parsed with regex (no YAML library). BBL-internal fields are preserved across CSV reconciliations.

---

## Repo layout

```
.
├── BBL-project-spec.md           # concept, brand voice, political framing
├── subagents.md                   # full subagent roster spec
├── csv2mdbot.py                   # CSV → graph reconciler
├── researchbot.py                 # image lookup + vision dispatch  (a.k.a. "layer 1 sourcing" — rename pending)
├── bbl_queue.py                   # next-batch picker: cards truly ready for vision (3-prong check)
├── apply_vision.py                # vision-JSON → MD writer (subagent helper)
├── wikilintbot.py                 # graph linter (structural + tag tier checks)
├── .claude/
│   └── agents/
│       └── bbl-researcher.md      # vision-pass subagent
├── cards/<game>/<set>/*.md        # active card-node graph
├── sealed/<game>/*.md             # sealed-product nodes
├── archive/                       # qty=0 nodes (created on demand)
├── images/<game>/<set>/*.png      # cached reference art
├── reports/
│   ├── history.md                 # csv2mdbot run log
│   ├── scryfall_sets.json         # cached set-name → code map
│   └── vision_pending/*.json      # vision payloads awaiting apply
├── MTG-artists.md                 # artist reference notes
├── Pokemon-artists.md             # artist reference notes
└── collectrexport*.csv            # raw inventory exports
```

---

## Common operations

```powershell
# Reconcile a fresh Collectr export into the graph
python csv2mdbot.py collectrexport5_7_2026.csv

# Probe what models the DeepSeek hosted API actually serves today
python researchbot.py --list-models

# Plan B vision flow: prep cached images for the bbl-researcher subagent
python researchbot.py --prepare-only --limit 50 --game "Magic: The Gathering"

# Show the next-batch queue (cards truly ready for vision, qty-DESC)
python bbl_queue.py --with-qty --limit 25 --game "Magic: The Gathering"
python bbl_queue.py --count                          # just the integer

# Plan A vision flow (re-enable once DeepSeek V4 vision endpoint ships)
python researchbot.py --limit 25 --model deepseek-v4-pro

# Apply a vision JSON onto a card by hand
python apply_vision.py cards/path/to/card.md reports/vision_pending/card.json

# Lint the graph (report-only)
python wikilintbot.py --quiet --report reports/wikilint_$(Get-Date -Format yyyy-MM-dd).md

# Lint and apply safe auto-fixes (tier confusion, cross-tier dupes)
python wikilintbot.py --fix
```

---

## A note on the agent roster

The mix of scripts (`csv2mdbot.py`, `researchbot.py`, `apply_vision.py`, `wikilintbot.py`) and Claude Code subagents (`.claude/agents/bbl-researcher.md`, with lair architect / hub curator / triviabot still spec-only in `subagents.md`) is **deliberately not consolidated**. Each has a distinct verb and runs on a different cadence. Premature merging would freeze interfaces that are still evolving. The right consolidation, *when* it comes, is a thin top-level CLI wrapper (`bbl reconcile <csv>`, `bbl prepare`, `bbl lint --fix`) — not folding agents into each other.

The pattern that's emerging: **writers get the keys to wikilintbot; watchers do not.** csv2mdbot, bbl-researcher, and (future) hub curator self-lint after writing. Lair architect is a writer too but its specific output (`held_for_lair`) is exactly what wikilintbot's `held_for_lair_sanity` check audits from outside — separation of concerns.

---

## Status snapshot (2026-05-08, end of session)

- **977** active singles · **16** sealed products · **78** MTG cards fully enriched (was 22 at session start → **+56 this session**, ~3.5× growth in one sitting)
- **Vision queue right now:** `python bbl_queue.py --count` → **7**. Held back to leave context headroom for handoff. Next session can dispatch immediately.
- **Three parallel rounds dispatched cleanly today:** 8 + 10 + 16 + 15 = 49 subagent vision passes, all tier-clean from the bbl-researcher refusal/lint logic. One IP flagged correctly (Kiora — `suspected_ip` set, name kept out of `subject`).
- **Picker workflow proved out:** the `--limit 200`+ on `researchbot.py --prepare-only` is what unlocks meaningful queue depth — qty-DESC frontier is choked by cards where Scryfall set-name match fails first time, and deeper limits expose successful fallback matches. `bbl_queue.py` is the canonical "ready for vision" picker.
- **Wikilintbot:** 9 info-only findings graph-wide (8 singleton aggregations + 1 `wanderer's-strike` is the queue card with empty tags). 0 warns, 0 errors. The `vocabulary_drift` (singular/plural) check was **removed 2026-05-08** — semantic-synonym work is the Phase-5 janitor's job, not per-card lint.
- **Plan A (DeepSeek vision):** still text-only. Re-probe each session.
- **Plan B (subagent vision):** active and parallelizable to ~16 in flight; ~50–135 s per card depending on parallelism load.
- **Repo:** local only, branch `main`. GitHub remote (`degenai/bulk-graph-bundler`, private) still pending.

### For the next session

1. **Re-probe DeepSeek** first thing: `python researchbot.py --list-models`. If V4 vision shipped, drop `--prepare-only` and run inline with `--model <new-id>`.
2. **Drain the 7 in queue, then refill:**
   ```powershell
   python bbl_queue.py --with-qty --limit 25 --game "Magic: The Gathering"
   # ...fan out bbl-researcher subagents on those paths...
   python researchbot.py --prepare-only --limit 300 --game "Magic: The Gathering"
   python bbl_queue.py --count
   # ...repeat fan-out...
   ```
3. **Recommended next moves**, in priority order:
   - Push past 100 enriched MTG cards (currently 78) to unlock lair architect work — that's the threshold where `available = quantity - held_for_lair` queries start returning interesting candidate manifests.
   - Start Pokémon enrichment — same flow, `--game Pokemon`. Path wired, not yet exercised.
   - Dragon Ball Super image-source strategy (no Scryfall equivalent). Highest-unit game in inventory.
   - Push to GitHub once Alex creates `degenai/bulk-graph-bundler` (or installs `gh`).
   - Optional cleanup: rename `researchbot.py` → `sourcebot.py` (or similar) as a clean rename commit.
   - Optional: triage the manual-review queue (currently 47+ cards flagged `needs_manual_review: true`) — many have a cached image and a low-confidence URL. A small reviewer script could let Alex eyeball each and either approve (set `reference_image` + `art_match_confidence: high`) or reject.

### Curation rules locked in this project's memory

The next session should pull these without being asked — they're in `~/.claude/projects/.../memory/`:

- **Broad-net tag emission** (`bbl-tag-broad-net.md`) — vision pass emits 8–12 broad `tags_hub` per card; never coined compounds like `comfort-bringer` or `bro-energy`.
- **Color-magic is filter-tier** (`bbl-color-magic-is-filter.md`) — `blue-magic`, `red-magic`, etc. are combinatorial filters, never lair anchors. Wikilintbot enforces.
- **Wikilintbot before lair architect** (`bbl-wikilintbot-priority.md`) — built; lair architect comes next.
- **Session handoff** (`bbl-session-handoff.md`) — keep this snapshot fresh at every session close.
