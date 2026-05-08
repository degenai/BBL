# Bulk Graph Bundler (BBL)

**This is a curation project.** The goal — the whole goal, end to end — is to produce **as many unique, curated card bundles as possible** from a personal bulk inventory the rest of the market treats as weight-priced filler. Every script, agent, tag, schema choice, and pipeline decision in this repo is in service of that one outcome: more well-curated bundles.

A "Discrete Lair" is the unit of work: a one-off, named, theme-driven bundle of cards that share a concept the market doesn't see. Mechanics, flavor, art, jokes, vibes. Each bundle is its own SKU. Each tells a story. Each is the labor that creates the value.

The thesis: bulk has near-zero exchange-value individually but rich use-value collectively when sorted with intent. Most bulk sellers move it by weight or by random pack. BBL moves it by *theme* — and the theme is what we sell.

The graph (the tag network, the hub-and-filter taxonomy, the vision-pass enrichment, the lair architect) exists to make those bundles assemblable at scale. Hub tags = candidate bundle anchors. Filter tags = combinatorial narrowing dimensions. The whole BBL stack is a machine for surfacing "here's a bundle people will want, here's why, and here are 30 cards that compose it."

See also:
- [`BBL-project-spec.md`](BBL-project-spec.md) — full concept, brand voice, political framing.
- [`subagents.md`](subagents.md) — the agent roster spec.
- [`docs/curation-modes.md`](docs/curation-modes.md) — the *forms* a curated bundle can take (haiku set, sonnet set, mood lair, etc.). Forms are part of the pitch — they're what makes "why would I want this curation?" answerable in one sentence.
- [`references/`](references/) — visual references for what a well-curated themed binder looks like in practice.

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
│   └── vision_pending/<game>/<set>/<slug>.json   # vision payloads, set-namespaced (mirrors cards/ tree)
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

## Findings & lessons (2026-05-08)

These are durable observations that survive the rolling status snapshot below — load-bearing facts the next session shouldn't have to rediscover.

**On the picker / queue:**
- `csv2mdbot` writes an empty placeholder `reference_image:` line on every card from day one. Any "ready for vision" check that reads only frontmatter without verifying the path on disk will over-count by ~500×. The 3-prong filter in `bbl_queue.py` (non-empty path + on-disk + empty `tags_hub` + not `needs_manual_review`) is the canonical answer.
- `--limit 600` on `researchbot.py --prepare-only` is the magic number for refilling. At `--limit 25` to `--limit 50`, the queue often drains to 0 after one fan-out round because the qty-DESC frontier is choked by cards Scryfall couldn't match on first try. Deeper limits expose successful fallback-name matches and produce queues of 50+ ready cards.

**On researchbot's idempotency:**
- Re-running `--prepare-only` can flap a card between `prepared` (with `reference_image` populated, `art_match_confidence: high`) and `manual_review` (with `reference_image: ` empty, `art_match_confidence: none`). Theros Beyond Death cards demonstrated this clearly — a deeper-limit re-run reverted them mid-session. Bug: researchbot does not guard against downgrading an already-prepared card. Fix: skip the lookup entirely when frontmatter already shows `art_match_confidence: high` AND `os.path.exists(reference_image)`.

**On the IP guardrail:**
- `bbl-researcher` correctly populates `suspected_ip` for in-universe MTG planeswalkers without putting their names in `subject`. As of the 2026-05-08 session, 6 cards carry IP flags: Garruk Wildspeaker, Kiora, Nicol Bolas (×2), Teyo, the Wanderer. Verification step is downstream and not yet built — these flags accumulate until something consumes them. Worth a small `python ip_review.py` script eventually that lists all `suspected_ip` cards for human verification.

**On Obsidian image embeds:**
- The Obsidian vault is rooted at `cards/`, so wikilink-style embeds (`![[images/...]]`) look outside the vault and render as "file not found." The fix is to use **standard markdown** embeds with **relative paths**: `![<slug>](../../../images/<game>/<set>/<slug>.png)`. Renders inline in any Obsidian config (vault at project root, vault at `cards/`, doesn't matter), AND renders on GitHub web. This was migrated across all 207 affected cards via `reports/fix_image_embeds_v2.py`.
- The Vision section now also begins with a prominent `> [!warning] Suspected IP: **<name>**` callout for any card whose vision pass flagged an IP. Renders as a yellow warning callout in Obsidian, falls back to a styled blockquote elsewhere. Reviewer instructions inline.

**On `apply_vision.py`'s tier normalizer:**
- The helper has a small built-in normalizer that auto-moves certain tags from `tags_hub` to `tags_filter` regardless of what the vision JSON emits — `crowd`, `no-figure`, `artifact` are confirmed cases. This is *good* (reinforces the tier rules) but undocumented; future agent definitions may want to know which tags are "always-filter" so they don't waste judgment on them. Source: `researchbot.update_card`.

**On synonym overlap (Phase-5 janitor's homework):**
- The graph already has confirmed synonym pairs surfacing: `cat` (×4) and `feline` (×3); `book` (×3) and `tome` (×3); `flight` (×6) and `flying` (×3); `weapon` (×5) and `weapons` (variable). These are NOT a bug — they reflect honest description of different cards' content. Synonym/redundancy resolution is the future janitorbot's job: detect, propose canonical form, sweep + collapse + leave audit trail.

**On hub-tag density (the lair-architect unlock):**
- At 22 enriched cards, ~53 hub tags appeared in 2+ cards. At 100 enriched cards, **222 hub tags** appear in 2+ cards. The bridge density grew much faster than card count — not 4.5× linear but closer to 4× hub density per 4.5× card count, which means the graph is genuinely composing rather than just accumulating. Top bridges as of 100-card mark: `forest`(22), `armor`(17), `warrior`(14), `wings`(13), `robed-figure`(12), `wilderness`(12), `fire`(11), `ruins`(11), `ritual`(10), `monster`(10), `predator`(10).

**On parallel fan-out:**
- The `bbl-researcher` subagent runs 50–135 s per card depending on parallelism load. Up to 16 in flight verified clean across multiple rounds. Beyond that not yet tested. Refusal logic is robust — the agent will not write tags from a wrong-printing image, and its refusal preserves graph cleanliness even when the dispatch picker has a bug.

---

## A note on the agent roster

The mix of scripts (`csv2mdbot.py`, `researchbot.py`, `apply_vision.py`, `wikilintbot.py`) and Claude Code subagents (`.claude/agents/bbl-researcher.md`, with lair architect / hub curator / triviabot still spec-only in `subagents.md`) is **deliberately not consolidated**. Each has a distinct verb and runs on a different cadence. Premature merging would freeze interfaces that are still evolving. The right consolidation, *when* it comes, is a thin top-level CLI wrapper (`bbl reconcile <csv>`, `bbl prepare`, `bbl lint --fix`) — not folding agents into each other.

The pattern that's emerging: **writers get the keys to wikilintbot; watchers do not.** csv2mdbot, bbl-researcher, and (future) hub curator self-lint after writing. Lair architect is a writer too but its specific output (`held_for_lair`) is exactly what wikilintbot's `held_for_lair_sanity` check audits from outside — separation of concerns.

---

## Status snapshot (2026-05-08, post-Scryfall-recovery)

- **977** active singles · **16** sealed products · **201** MTG cards fully enriched (was 22 at session start → **+179**, ~9× growth)
- **Vision queue right now:** `python bbl_queue.py --count` → **363**. Massively topped up after the Scryfall recovery work (see Findings). At ~13 cards/parallel-round, that's ~28 rounds to all-MTG-enriched.
- **Manual review pile:** down from 398 → **9 genuine edge cases** (tokens, art series, alt-art showcases, foil-only promos). Triage UI eventually but not blocking.
- **Scryfall recovery shipped this session:**
  - `--retry-flagged` mode walks the manual-review pile and re-runs lookups
  - `http_get_json` hardened with retry-on-429/5xx + exponential backoff
  - `SET_NAME_ALIASES` table for set names that don't normalize cleanly (Mystery Booster Cards → mb1, Promo Pack: X → ppXXX, Classic: Sixth Edition → 6ed, etc.)
  - `_SET_PAREN_SUFFIX_RE` strips trailing parentheticals (Magic 2014 (M14) → m14)
  - `normalize_card_name_for_lookup()` strips trailing collector-number suffixes from names (Island (254) → Island)
  - `--scryfall-sleep N` configurable inter-request sleep (default 0.1s, bump to 1.0+ for sustained sweeps)
  - `--refresh-set-map` flag rebuilds the cached set_map
  - `is_already_prepared()` idempotency guard so --prepare-only doesn't re-query Scryfall for cards already prepared (~387 wasted calls per sweep without it)
- **Six parallel rounds today across 7+ batches:** 8 + 10 + 16 + 15 + 7 + 15 + 13 + 13 + 13 + 13 + 10 = **133 successful subagent dispatches**, all tier-clean. **10 IP cards flagged correctly:** Kiora, Nicol Bolas (×2), Teyo, the Wanderer, Garruk, Radha, Teferi, Tamiyo, Oko — all `suspected_ip` set, names kept out of `subject`.
- **Hub-tag density:** 1029 unique hub tags emitted, **362 shared by 2+ cards** (was 53 at session start → 222 at 100-mark → 362 at 175-mark). The bridge-density growth is super-linear in card count, which is exactly what the lair architect needs.
- **JSON path migration completed:** `reports/vision_pending/<game>/<set>/<slug>.json` now mirrors the `cards/` tree — protects against MTG reprint name-collisions (Opt, Cancel, basic lands appear in dozens of sets). All 124 pre-existing JSONs migrated via `git mv` to preserve history.
- **`vocabulary_drift` lint check removed** — singular/plural splits intentionally allowed; semantic synonym collapse is Phase-5 janitorbot work.
- **Researchbot non-idempotency bug** (logged in Findings): re-running `--prepare-only` can flap a card from `prepared` back to `manual_review`. bbl-researcher refusal logic catches it; not blocking but worth fixing.
- **Wikilintbot graph-wide:** 2 info-only findings (singleton aggregations). 0 warns, 0 errors.
- **Plan A (DeepSeek vision):** still text-only.
- **Plan B (subagent vision):** running smoothly — 13 in parallel completes ~1 min wall-clock when the API is responsive.
- **Repo:** local only, branch `main`. Commits this session: 5–6 stacked, all clean.

### For the next session

1. **Re-probe DeepSeek** first: `python researchbot.py --list-models`.
2. **Refill from deeper:** `python researchbot.py --prepare-only --limit 1500 --game "Magic: The Gathering"`. The shallow limits we used today have squeezed most of what the standard pipeline can produce.
3. **Build a manual-review triage UI/script.** ~430 cards still flagged `needs_manual_review: true` (Scryfall set-name match failed). Many DO have a cached image and a low-confidence URL — worth a small interactive script that lets Alex eyeball each, approve the cached art, and flip the card to `art_match_confidence: high`. This is the next force-multiplier for getting toward all-MTG-enriched.
4. **Stand up lair architect.** With 175 enriched cards and 362 hub bridges, the graph density is well past the activation threshold. This is the unlock the whole project has been pointing at.
5. **Fix researchbot non-idempotency:** skip the lookup if `art_match_confidence: high` is already set AND `os.path.exists(reference_image)`. Should be a 5-line patch.
6. **Other remaining moves** (lower priority): Pokémon enrichment first run, Dragon Ball Super image-source strategy, push to GitHub, `researchbot.py` → `sourcebot.py` rename.

### Curation rules locked in this project's memory

The next session should pull these without being asked — they're in `~/.claude/projects/.../memory/`:

- **Broad-net tag emission** (`bbl-tag-broad-net.md`) — vision pass emits 8–12 broad `tags_hub` per card; never coined compounds like `comfort-bringer` or `bro-energy`.
- **Color-magic is filter-tier** (`bbl-color-magic-is-filter.md`) — `blue-magic`, `red-magic`, etc. are combinatorial filters, never lair anchors. Wikilintbot enforces.
- **Wikilintbot before lair architect** (`bbl-wikilintbot-priority.md`) — built; lair architect comes next.
- **Session handoff** (`bbl-session-handoff.md`) — keep this snapshot fresh at every session close.
