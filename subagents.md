# BBL Subagents Registry

> **⚠ This doc is historical (Plan A) — see live agent specs in `.claude/agents/`.**
>
> Originally a roadmap for a DeepSeek-hosted vision pipeline. That plan was deprecated wave ~10 once Claude Code subagents matured enough to handle the vision pass at quality. Live specs:
> - **Vision pass** → `.claude/agents/bbl-researcher.md` (Sonnet 4.6, replaces the DeepSeek vision-call code that lived in `researchbot.py` until wave 92.5)
> - **Trivia pass** → `.claude/agents/bbl-triviabot.md` (Sonnet 4.6)
> - **Topology / edges / new nodes** → `.claude/agents/bbl-edgelord.md` (Opus 4.7, with Mr. Nodeley alter)
> - **Triage diagnoses** → `.claude/agents/bbl-nurse-joy-md.md` (Sonnet 4.6)
>
> The watch signal for re-introducing Plan A: `python researchbot.py --list-models` — when a DeepSeek vision model appears without "beta" tagging, hosted vision becomes a viable alternative path. Memory: `bbl-deepseek-vision-watch`.
>
> The sections below are preserved as the original architectural spec (tag architecture, schema rules, etc.) since most of that still holds; only the Plan-A DeepSeek-specific copy is stale.

Roster of specialized agents the Bulk Graph Bundler project needs. Specs only — implementation TBD.

**Migration plan:** once specs are locked and a first-pass implementation works, these get converted into actual Claude Code subagents (`.claude/agents/*.md` definitions) so they're invokable from any session in the project. Spec-first, code-second, agent-third.

**Knowledge investment philosophy:** the vision pass and trivia pass run **once per unique card, not per copy held**. A node with quantity 12 costs the same to enrich as a node with quantity 1. The graph is the long-term asset — pay the cost once, query forever.

---

## Tag Architecture (load-bearing decision)

Two-tier tag system. Same data model, different graph treatment.

### Tier 1 — Hub-eligible tags (graph nodes, ~30 max curated)

Thematically rich tags that cross-cut games and sets and would make for compelling Discrete Lairs. Each gets an MD hub at `_hubs/<tag>.md` and becomes a node in the Obsidian graph view. Cards with the tag wikilink to the hub.

Examples: `cat`, `sunset`, `pie`, `service-worker`, `cozy`, `gothic`, `fire`, `forest`, `villain`, `comic-relief`, `labor` (← powers socialist Discrete Lairs).

These hubs are the cool thematic backbone the graph displays. Curated vocabulary, not auto-promoted.

### Tier 2 — Filter-only tags (frontmatter only, never nodes)

Mechanical / structural / compositional tags. Indexable, searchable, queryable by lair architect. Never get an MD hub. Never appear as graph nodes.

Examples: `faces-left`, `faces-right`, `2-figures`, `3-figures`, `solo-portrait`, `mid-shot`, `lifegain`, `mill`, `rare`, `common`, `uncommon`, `holo`, `non-holo`.

These are the "Option H" tags — useful for filtering but kept out of the graph to avoid clutter.

### Why this split

The graph is for *fun* — it should display the aesthetic/thematic bridges, not the mechanical taxonomy. Mechanical tags do real work for queries; they just don't earn a node. Trait-ness (cat-ness, sunset-ness, labor-ness) is informative bridging; structural-ness (faces-left, 2-figures) is metadata. Different jobs, different graph treatment.

### Frontmatter schema

```yaml
tags_hub: [cat, cozy, forest]            # tier 1, become wikilinks in card body
tags_filter: [faces-left, 2-figures, mid-shot, lifegain]  # tier 2, frontmatter only
```

Researchbot generates both. Hub Curator (below) decides which tier 1 tags get promoted to actual hub MDs.

---

## csv2mdbot

**Purpose:** Convert a fresh singles inventory CSV into a graph of per-card MD pages. Reconcile against existing graph. Archive zeroed-out nodes.

### Inputs
- A fresh CSV export of current singles inventory. **Source format: Collectr app export.** Confirmed columns:
  `Portfolio Name, Category, Set, Product Name, Card Number, Rarity, Variance, Grade, Card Condition, Average Cost Paid, Quantity, Market Price (As of YYYY-MM-DD), Price Override, Watchlist, Date Added, Notes`
  - `Category` = game (MTG, Pokémon, Dragon Ball Super, etc.) — no ambiguity needed.
  - `Variance` = Normal / foil treatment / parallels.
  - `Market Price` column header includes the snapshot date — capture it.
- The existing card-node graph (directory of MD files for previously-recorded cards).

### Actions
1. **Create / update card nodes** — for each unique card in CSV, ensure an MD page exists. New cards get created from template; existing cards get quantity + changed fields updated.
2. **Diff against graph** — any card-node present in the graph but absent from the new CSV is treated as implied traded or sold. Set quantity to 0; preserve the file.
3. **Archive zeroed nodes** — any node whose quantity is 0 gets moved to an `archive/` folder. Wikilinks from bundles still resolve.

### Output
- Updated card-node directory.
- `archive/` directory of zeroed nodes.
- Short run report: created / updated / zeroed / archived counts.

### Per-card MD template (draft)
```markdown
---
name: {{Card Name}}
set: {{Set Code}}
collector_number: {{N}}
foil: {{true|false}}
condition: {{NM|LP|MP|HP|DMG}}
quantity: {{N}}
held_for_lair: 0
last_seen: {{YYYY-MM-DD}}
game: {{mtg|pokemon|yugioh|lorcana|fow|...}}
---

# {{Card Name}} ({{Set Code}})

Bundles: {{wikilinks}}
Tags: {{filled in by researchbot}}
Reference image: {{filled in by researchbot}}
Notes:
```

**`held_for_lair` (a.k.a. HELDFORLAIR) — commitment counter.** Tracks how many copies of this card are committed to *approved* Discrete Lairs that haven't shipped yet. Incremented on lair approval, decremented when the lair ships (or is dissolved). Treated as untouchable inventory by the lair architect.

**csv2mdbot must preserve `held_for_lair` across CSV reconciliations** — it's not in the CSV export, it's BBL-internal state. Don't overwrite it.

### Open questions
- Unique key — proposed: `Category + Set + Card Number + Variance + Grade + Card Condition`. Confirm whether condition splits into separate nodes or aggregates.
- File naming — `Lightning Bolt (LEA).md` vs slug-based?
- Should implied sold/traded deltas append to a ledger MD for sales history?
- Capture `Average Cost Paid` and `Market Price` snapshot history per node, or single latest only?

---

## researchbot

**Purpose:** Flesh out card-node MDs created by csv2mdbot. Each card gets a reference image and a structured set of vision-model-derived characteristics so the graph becomes queryable by what's actually *in* the art, not just metadata.

**Vision model: DeepSeek V4 (confirmed native multimodal, released 2026-04-24).**

- **Default model: `deepseek-v4-pro`** (1.6T total / 49B active params). Pro gets used for essentially all card analysis — Alex wants the model to have a fair shot at the art and won't bottom-feed on capability to save pennies. Cost is reassessed after a few topups, not pre-optimized.
  - `deepseek-v4-flash` (284B / 13B active) reserved only for genuinely dumb tasks (e.g., bulk format normalization, plain-text reformatting) where vision quality doesn't matter. Card art analysis is never a flash task.
- Both support 1M context and dual Thinking / Non-Thinking modes. Use Thinking for IP verification reasoning and ambiguous art; Non-Thinking acceptable for clear-cut tagging.
- API is OpenAI-ChatCompletions and Anthropic-API compatible — drop-in with existing SDK clients.
- Image input: public URL, base64-encoded string, or file upload. Formats: JPEG, PNG, WEBP.
- Key in `.env.local` as `DEEPSEEK_API_KEY`. Base URL: `https://api.deepseek.com` (keep base, just swap model ID).
- Pricing: per-million-token rates published in DeepSeek docs (chart image — fetch + record before launch). Add a few dollars at a time per Alex's budget cadence.

**Cost shape:** vision pass runs once per unique card-node, never per copy. A 12-copy node costs the same to enrich as a 1-copy node. Re-runs only happen on schema changes or model upgrades.

### Inputs
- A card-node MD (or batch of them) lacking image / tags.

### Processing order
**Prioritize by descending `quantity`.** A node with 12 copies has 12x the chance of appearing in future Discrete Lairs than a singleton — its tags pay back faster. Default sort: `quantity DESC, then last_seen DESC`. Singletons get enriched eventually; they're just at the back of the line.

### Actions

1. **Find reference photo** — pull a clean canonical image of the card (Scryfall API for MTG, PokémonTCG API / Bulbapedia for Pokémon, equivalents for other games). NEVER a photo of the user's physical copy — a canonical reference so the model can read art and characteristics reliably.

   **Set-aware lookup with confidence flag.** Different printings of the same card name often have completely different art (reprints, Universes Beyond crossovers, special editions). Researchbot must:
   - Try a **set-specific** lookup first (Scryfall: `?fuzzy=<name>&set=<code>`; PokémonTCG: `name:"X" set.name:"Y"`).
   - On hit: `art_match_confidence: high`. Proceed to vision pass.
   - On miss: fall back to fuzzy-without-set. If that returns *something*: `art_match_confidence: low`. **Defer to text-only conservative tagging** — do not run the vision pass on possibly-wrong-printing art. Set `needs_manual_review: true` with a reason.
   - On total miss: `art_match_confidence: none`. Set `needs_manual_review: true`.
   - When deferring: optionally try grabbing both the set-specific *and* fallback images, note that they differ, and let manual reviewer pick the right one. (v2 behavior — initial implementation just defers.)

2. **Run DeepSeek vision pass** on the reference image + card text. Emit structured fields:

   **Subject**
   - `subject` — what's depicted (character, creature, object, scene)
   - `subject_known_ip` — true/false. If the card depicts a recognizable IP character (Goku, Batman, Pikachu, etc.), mark true.
   - `suspected_ip` — name + confidence (`low | med | high`). Used when subject *looks* like a known character but the card name doesn't say so. Example: card titled "Yum Tacos!" depicting Goku — mark `suspected_ip: Goku, confidence: high` and trigger verification.
   - `ip_verified` — true/false. Set true only after online lookup of card name + game confirms identity. **Never commit a hard ID without verification.**
   - `description` — full visual description if no IP, or as supplement.

   **Composition / framing**
   - `facing` — which way subject is facing (left, right, forward, away, three-quarter)
   - `composition` — close-up, mid-shot, wide, scene
   - `mode` — portrait, action, narrative scene, abstract
   - `figure_count` — solo, duo, group, crowd, none

   **Background / foreground**
   - `foreground` — short description
   - `foreground_palette` — dominant colors
   - `background` — short description
   - `background_palette` — dominant colors

   **Setting / environment**
   - `setting` — forest, urban, desert, ocean, mountain, indoor, dungeon, space, void, etc.
   - `architecture` — if any (gothic, ruined, modern, organic, none)
   - `time_of_day` — dawn, day, sunset, twilight, night, magic hour, indeterminate
   - `weather` — rain, snow, fog, fire, smoke, calm, clear, storm, etc.

   **Atmosphere**
   - `mood` — cozy, grim, comedic, sublime, horror, action, peaceful, etc.
   - `genre_cues` — fantasy, sci-fi, anime, photoreal, cartoon, woodcut, watercolor, etc.
   - `lighting` — harsh, soft, backlit, rim, ambient, chiaroscuro

   **Details / objects**
   - `objects` — list of notable objects in the art (sword, book, pie, taco, banner, throne, etc.)
   - `animals_creatures` — any animals or creatures present (cat, dragon, bird, etc.)
   - `food_drink` — any food or drink visible (critical for *Things That Are Pies* and similar)
   - `clothing_style` — medieval, futuristic, casual, formal, armor, naked, etc.
   - `iconography` — runes, sigils, religious symbols, faction marks, brands
   - `emotion` — facial expression / body language read of subject

   **Tag emission (two-tier — see Tag Architecture section)**
   - `tags_hub` — flat list of *thematically rich* tags this card qualifies for. These are candidates for becoming Tier 1 hub nodes. Researchbot does NOT decide which tags get hubs — it just nominates from the universe of thematic concepts present. Examples for a sunset/cat card: `[sunset, cat, cozy, forest]`.
   - `tags_filter` — flat list of *mechanical / structural / compositional* tags. Always Tier 2, never become nodes. Examples: `[faces-left, 2-figures, mid-shot, lifegain, common]`.
   - The line between hub-eligible and filter-only is: "would I curate a Discrete Lair around this concept?" — sunset yes, lifegain no, labor yes, mid-shot no.

3. **IP verification subroutine** — when `suspected_ip` is set with confidence ≥ low:
   - Search card name + game online (official wikis, Scryfall, Bulbapedia, fan wikis).
   - Confirm identity from authoritative source.
   - On confirmation: set `subject_known_ip: true`, `ip_verified: true`, fill `subject` with the character name.
   - On no confirmation: keep `suspected_ip` field, leave `ip_verified: false`, and **do not commit a name in `subject`** — describe instead.
   - **Hard rule: never invent or guess a character identity.** Crossover cards (MTG Universes Beyond, Pokémon collabs, DBS character variants) are the high-risk zone — flag explicitly.

4. **Write back to MD** — store image link/path + all structured fields in frontmatter or a dedicated `## Vision` body section.

### Output
- Card-node MD updated in-place with reference image + full vision pass.

### Open questions
- Image storage — link to remote URL, or download local copy to `images/`?
- Controlled vocabulary vs. free-form for tags? Probably hybrid: structured fields use controlled vocab, free `tags` list is open.
- Batch size per run / DeepSeek rate limits / cost per card pass.
- Re-run policy — when the model improves, do we re-pass the whole graph?
- Locking down the exact DeepSeek model ID (V4 vs VL2 vs newer).

---

## lair architect

**Purpose:** Take target parameters, query the card graph, and output candidate **Discrete Lair** manifests (proposed themed bundles).

A **Discrete Lair** is the curated bundle output — a set of cards assembled around a concept. Name is a deliberate riff on Wizards' *Secret Lair* drop product. Where Secret Lair is corporate, opaque, FOMO-driven, and high-end, a Discrete Lair is small, transparent, indie-curated, and lives in the bulk strata. "Discrete" both as in *separate / individual* and as in *modest / unflashy* — the opposite of Secret Lair's whole vibe.

### Inputs
- Target params, e.g.:
  - Theme / concept (free text — "things that are pies", "sunset art", "service workers")
  - Card count (or count range)
  - Game filter (mtg only, cross-game, etc.)
  - Price ceiling / value target
  - Required must-include or must-exclude cards
  - Tag filters (positive and negative)

### Actions
1. **Parse params** into a graph query (tag matches, metadata filters).
2. **Compute availability per card** — `available = quantity - held_for_lair - (copies already used in other manifests in this run, including pending ones already on disk)`. Only cards with `available > 0` are eligible. **This is the rule that prevents one copy of a card from being committed to five different lairs.**
3. **Walk the graph** — find available candidate cards matching the theme via tags, art, mechanic, flavor.
4. **Score candidates** — relevance to theme, variety, charm, fit with bundle size.
5. **Assemble candidate manifests** — produce 1–N proposed lair compositions for review, never double-booking a card across them.

### Output
- One or more candidate Discrete Lair manifest MDs written to `lairs/pending/` for human review. Each manifest lists the included cards (wikilinked), the theme, the rationale, and projected total card count / price.
- Nothing is finalized until Alex approves. On approval the manifest moves to `lairs/approved/` and **`held_for_lair` is incremented by 1 on each card-node in the manifest**. On rejection it moves to `lairs/rejected/` with a brief reason logged for theme tuning (no `held_for_lair` change).
- When an approved lair ships (or is dissolved), `held_for_lair` decrements and `quantity` decrements (on ship) accordingly.
- The agent never auto-deletes a manifest — review is the gate.

### Open questions
- How many candidate manifests per run by default?
- Quantity decrement timing — at approval, or at fulfillment/sale?
- Auto-archive rejected manifests after N days, or keep indefinitely?

---

## hub curator

**Purpose:** Decide which `tags_hub` tags graduate to actual Tier 1 hub MDs. The gatekeeper between researchbot's free nomination and the graph's curated node set.

Pattern matches **lair architect** rather than the bots: requires human-in-the-loop confirmation, exercises taste, maintains a registry. Not a mechanical pipeline.

### Inputs
- The full graph after researchbot has tagged a meaningful slice (target: a few hundred enriched cards minimum).
- The current hub vocabulary registry (`_hubs/_registry.md` — list of tags currently promoted to hubs).
- A target hub count (default: 30).

### Actions

1. **Tally** — count `tags_hub` frequency across the enriched graph. Drop tags with too few cards (< 5) — not enough mass for a hub.
2. **Propose** — surface the top ~30 candidates by frequency × thematic strength, plus any "boutique" picks (rare-but-strong concepts like `labor` or `pie`).
3. **Confirm with Alex, one batch at a time** — present candidates with sample card lists. Alex approves, rejects, or holds each. **Never auto-promotes.**
4. **Promote approved tags** — for each:
   - Create `_hubs/<tag>.md` with frontmatter (`type: hub`, `tag: <tag>`) and a Dataview query body listing all cards with that tag.
   - Inject `[[<tag>]]` wikilinks into the bodies of cards carrying the tag (so the graph view draws edges).
   - Append to `_hubs/_registry.md`.
5. **Warn at thresholds** — if the registry hits 30, warn before adding more. If it hits 50, hard-stop and require explicit override. **Combinatorial bloat is the explicit failure mode to prevent.**

### Output
- New hub MDs under `_hubs/`.
- Updated card MDs (with hub wikilinks injected).
- Updated `_hubs/_registry.md`.

### Hub MD template (draft)
```markdown
---
type: hub
tag: cat
---

# Cat

Cards in inventory with the `cat` tag.

```dataview
LIST FROM "cards"
WHERE contains(tags_hub, "cat")
SORT quantity DESC
```
```

### Open questions
- Approval batch size — one tag at a time, or 5-tag batches?
- Demotion flow — if a hub stops being interesting (low card count after archiving), how is it retired?
- Should hub MDs include curator notes / lair history (lairs that drew from this tag)?

---

## triviabot

**Purpose:** Web-search a card for community signal — lore, jokes, format relevance, infamous moments, fan affection — and add the notable bits to the card node. If the community has nothing to say, report **crickets**.

Distinct from researchbot: researchbot reads the card itself (art, text, mechanics). Triviabot reads what *people have said about* the card.

### Inputs
- A card-node MD (or batch).

### Actions
1. **Search community sources** — Reddit (r/magicTCG, r/spikes, r/EDH, r/pkmntcg, etc.), EDHREC writeups, Scryfall card comments, MTGGoldfish/ChannelFireball articles, Bulbapedia trivia sections, YouTube card-specific videos, TCGplayer infinite, blog posts.
2. **Synthesize** — pull out the genuinely interesting bits: format moments, deck archetypes the card defined, fan nicknames, art controversies, lore connections, memes.
3. **Write back to MD** — append a `## Trivia` section with sourced one-liners.
4. **Crickets fallback** — if signal is thin (no meaningful results across sources), write `## Trivia\n\nCrickets.` and move on. Does not pad with filler.

### Output
- Card-node MD updated with trivia section or explicit `Crickets.` marker.

### Open questions
- Threshold for "crickets" — zero hits, or below some signal floor?
- Cite sources inline, or just summarize?
- Re-run cadence — trivia ages, especially around new format shifts.

---

## wikilintbot

**Purpose:** Keep the BBL graph clean. Scans the whole card-node + bundle + lair MD set and reports structural issues. Optional auto-fix for safe ones.

Modeled on the wikilint suite in Alex's global wiki (`~/.claude/wiki/scripts/lint/suite`) — same protocol-over-subagent philosophy: prefer fast deterministic checks where possible, only invoke an LLM for judgment calls.

### Checks

**Structural**
- **Broken wikilinks** — `[[Card Name]]` pointing at a node that doesn't exist.
- **Orphans** — card nodes not referenced by any bundle or lair.
- **Unlinked mentions** — card name appears as plain text in a bundle/lair MD where a wikilink would resolve.
- **Missing frontmatter fields** — quantity, set, game, etc. per the template.
- **Missing reference image** — researchbot didn't run or failed.
- **Duplicate nodes** — same unique key resolved to two files.
- **Stale `last_seen`** — card not seen in CSV for N runs (configurable).
- **Quantity sanity** — node in `cards/` with quantity 0 (should be archived); node in `archive/` with quantity > 0 (should be reactivated).
- **Sealed misclassification** — node in `cards/` whose frontmatter has empty `collector_number` AND empty `rarity` (heuristic for sealed). Flag for re-routing.

**Tag linting (load-bearing for graph quality)**
- **Missing tags** — both `tags_hub` and `tags_filter` empty after researchbot has had a chance to run.
- **Tier confusion** — mechanical tags (`faces-left`, `2-figures`, `lifegain`, `mid-shot`, etc.) appearing in `tags_hub`, or thematic tags (`cat`, `sunset`, `cozy`, `pie`) appearing in `tags_filter`. Suggest tier swap.
- **Vocabulary drift** — same concept spelled differently across nodes (`cat` vs `cats`, `sunset` vs `sunsets`, `faces-left` vs `faces_left` vs `facing-left`, `Cat` vs `cat`). Surface plural/singular and casing inconsistencies; propose a canonical form.
- **Format drift** — kebab-case vs snake_case vs space-separated within same tag pool. Pick one (kebab-case) and flag deviations.
- **Duplicates within a card** — same tag appearing twice in `tags_hub` or `tags_filter`.
- **Cross-tier duplicates** — tag appearing in both `tags_hub` and `tags_filter` on same card. Pick one tier.
- **Singleton tags** — tag used by only one card across whole graph. Either typo, or too specific to be useful — flag for review.
- **Generic-only tags** — bare color or vague mood tags without modifier (`red`, `dark`, `cool`) that are too unspecific to bridge meaningfully.

**Hub registry**
- **Hub registry drift** — a `_hubs/<tag>.md` exists but `_hubs/_registry.md` doesn't list it (or vice versa).
- **Orphan hub** — a hub MD with no cards currently carrying that tag (candidate for retirement).
- **Promotion candidates** — a tag in `tags_hub` appears on N+ cards across multiple games but isn't yet a promoted hub. Surface to hub curator.
- **Hub vocabulary cap** — registry over 30 entries (warn) or over 50 (error).
- **Hub wikilink missing** — a card carrying a promoted hub tag should have `[[<tag>]]` in its body. Missing wikilink = graph edge missing. Auto-fixable.

**Lair / inventory consistency**
- **HELDFORLAIR sanity** — `held_for_lair > quantity` is impossible (over-committed). `held_for_lair` should also equal the count of approved lairs that reference this card; mismatch = drift between manifests and node state.

### Manual review walkthrough mode

When invoked with `--review` (or its skill-style equivalent), wikilintbot enters **guided manual review mode**:

1. **Build the queue** — find all cards with `needs_manual_review: true`, sort by quantity DESC.
2. **Walk Alex through them one at a time.** For each card:
   - Show: card name, game, set, qty, the `manual_review_reason` field, the current reference image (if any), and any provisional tags.
   - Offer actions:
     - **(R) Re-fetch** — try a different image lookup strategy (alternate set code, manual URL paste).
     - **(A) Accept current** — confirm the existing image is good despite the warning; clear `needs_manual_review`, set `art_match_confidence: high`.
     - **(D) Describe-only** — keep card un-illustrated; mark with text-only conservative tags Alex types in.
     - **(S) Skip** — leave for next session.
     - **(X) Exclude permanently** — flag the card as "no useful image source"; never re-flag.
3. **Resume support** — review state persisted between sessions (which cards Alex has already actioned).
4. **Output** — updated card frontmatter, cleared review flags where resolved, summary of the session at the end.

This is the bridge between researchbot's automated work and Alex's curatorial judgment. Wikilintbot is the only agent that surfaces the queue interactively.

### Output
- Lint report MD: issues grouped by check, file paths, suggested fixes.
- Optional `--fix` flag for safe auto-corrections (relocate quantity-0 to archive, add missing wikilinks where unambiguous).

### Open questions
- Run on demand, on every csv2mdbot pass, or scheduled?
- Which checks are safe to auto-fix vs. report-only?
- Should orphan card nodes be flagged or just inventoried (a card not in a lair yet isn't broken — it's available)?
