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
- [x] Tag-tier checks: `tier_confusion` (color-magic + composition + rarity/type tags in `tags_hub`), `format_drift` (non-kebab-case), `intra_tier_duplicates`, `cross_tier_duplicates`, `vocabulary_drift` (plural/singular pairs), `singleton_tags`, `missing_tags`
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
├── researchbot.py                 # image lookup + vision dispatch
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
python researchbot.py --prepare-only --limit 25 --game "Magic: The Gathering"

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

## Status snapshot (2026-05-08)

- **977** active singles · **16** sealed products · **22** cards fully enriched (top-22 by quantity in MTG)
- **Hub-tag bridges:** 53 tags shared by 2+ cards. Top: `forest` 5x, `comic-relief` 5x, `moss` 5x, `fairy-tale` 4x, `guardian` 4x, `service-worker` 4x, `labor` 3x.
- **Wikilintbot:** report-only on most checks, auto-fix on tier_confusion + cross_tier_duplicates + intra_tier_duplicates. First pass: 26 findings → 23 auto-fixed → 3 remain (2 info aggregations + 1 vocab judgment). 0 errors graph-wide.
- **Plan A (DeepSeek vision):** still blocked — hosted API serves only `deepseek-v4-pro` and `deepseek-v4-flash`, both text-only. Re-probe with `python researchbot.py --list-models` to check.
- **Plan B (Claude Code subagent + inline vision):** active. bbl-researcher subagent definition includes self-lint step.
- **Repo:** local only, on branch `main` — GitHub remote (`degenai/bulk-graph-bundler`, private) pending Alex's move.

### For the next session

Last commit before handoff is on `main`. To pick up cleanly:

1. **Restart Claude Code** so `.claude/agents/bbl-researcher.md` registers as an invokable subagent type. Once registered, the vision flow is parallelizable — main session can fan out `Agent(subagent_type="bbl-researcher")` calls instead of doing vision inline.
2. **Re-probe DeepSeek** in case V4 vision rolled out: `python researchbot.py --list-models`. If a vision-capable model ID appears, drop `--prepare-only` and run with `--model <new-id>` instead of using the subagent path.
3. **Recommended next moves**, roughly in priority order:
   - Continue MTG enrichment in batches of ~25 via `python researchbot.py --prepare-only --limit 25 --game "Magic: The Gathering"` then bbl-researcher on each prepared card. Batch sizes can grow as the rule-set settles.
   - Start Pokémon enrichment — same flow, `--game Pokemon`. Path is wired but not yet exercised at scale.
   - Build a Dragon Ball Super image-source strategy (no Scryfall equivalent — needs DBS card resource scraping or manual URL paste). DBS has the most units in inventory, so this unlocks a lot.
   - Push to GitHub once Alex creates the empty repo at `degenai/bulk-graph-bundler` (or installs `gh` CLI).
   - Build lair architect once enough cards have hub tags (~100 cards is roughly the threshold where `available = quantity - held_for_lair` queries return interesting candidate manifests).

### Curation rules locked in this project's memory

The next session should pull these without being asked — they're in `~/.claude/projects/.../memory/`:

- **Broad-net tag emission** (`bbl-tag-broad-net.md`) — vision pass emits 8–12 broad `tags_hub` per card; never coined compounds like `comfort-bringer` or `bro-energy`.
- **Color-magic is filter-tier** (`bbl-color-magic-is-filter.md`) — `blue-magic`, `red-magic`, etc. are combinatorial filters, never lair anchors. Wikilintbot enforces.
- **Wikilintbot before lair architect** (`bbl-wikilintbot-priority.md`) — built; lair architect comes next.
- **Session handoff** (`bbl-session-handoff.md`) — keep this snapshot fresh at every session close.
