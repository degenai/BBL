# Sketchbook — forming ideas

Catch-all for half-baked concepts, future work, and "wouldn't it be cool if" notes. Things land here before they're ready to be specs, scripts, or features. Promote out into proper docs (or commit work) when they crystallize.

---

## Collection timeline HTML

**The idea:** the git commit log of this repo IS a story — when each card got enriched, what prompts were active, when bugs got fixed, what insights surfaced. Render that as an HTML page: a scrolling visual timeline of the curation work itself.

**Why it matters:** BBL's whole thesis is *curation IS the labor IS the value*. Most of that labor lives in commit messages and git history right now. Visualizing the timeline makes the labor *visible* in a way buyers, collaborators, and Alex's future self can browse. It's the same logic as the Misty binder reference — the labor needs to be legible to be sellable.

**What to render** (rough):
- One row / card / cluster per enrichment commit, chronologically.
- Each row: commit subject, date, count of cards enriched in that commit, any IP flags, notable lair-bridge candidates surfaced in the message body.
- Color/icon for: enrichments, prompt-version changes, refactors, bug fixes, feature additions (queue helper, retry mode, embed migration, etc.).
- Maybe a running counter at the top: "Day 1 → 22 enriched. Day 2 → 175. Day 3 → 344. ..."
- Optional: thumbnail strip of the cards that landed in each batch (pulls from `cards/_images/<game>/<set>/<slug>.png`).
- Highlight inflection points: the Scryfall recovery (398 flagged → 9), the prompt v2 / v3 cuts, the haiku-mode insight, the embed-format fix.

**Implementation notes** (when we get there):
- Pure static HTML + JS — no server. Drop into `reports/timeline.html` or `docs/timeline/index.html`.
- Build script reads `git log --reverse --format=%H|%ai|%s|%b -- cards/` and emits the timeline data as a JSON blob inline.
- Could leverage Tailwind via CDN for quick styling, or just hand-rolled CSS.
- Filterable by commit-type (enrichment / prompt-change / fix / feature).
- Self-update: a `bbl_timeline.py` script regenerates the HTML from current git log. Run after each session.
- Optional later: deploy to GitHub Pages once the repo goes public.

**Why this lives in sketchbook, not as a milestone:** because it's a *showcase artifact*, not a pipeline component. The pipeline produces curated bundles; the timeline narrates *how the curation happened*. Different audience, different cadence (built once near the end, regenerated occasionally).

---

## Flavor / oracle text capture

**The idea:** Scryfall returns `flavor_text` and `oracle_text` on the same payload `find_image_scryfall` (`researchbot.py:313`) already hits for `image_uris`. Zero extra API calls would be needed to capture them. Both belong in card frontmatter eventually.

**Why it matters:**
- `flavor_text` often names the figure ("Teferi watched the Bolas Citadel rise...") — would help disambiguate the growing pile of `suspected_ip` flags (Nissa, Liliana, Ral, Chandra, Jace…) without needing a separate web lookup
- `oracle_text` is queryable for mechanical lair themes ("lifegain" / "sacrifice" / "graveyard"-oriented Discrete Lairs)
- triviabot will eventually want both fields as starting context before going out to Reddit/EDHREC

**Status:** deferred 2026-05-10 — surfaced mid-batch by a bbl-researcher subagent that noticed `card_text: (not provided)` in `VISION_USER_TEMPLATE`. Alex's call: cool, canonical, not mission-critical, can be backfilled "in a dumb way later."

**Implementation notes** (when we get there):
- Two phases — **capture** first, **consumption** later. Don't conflate them.
- Capture-only phase: one-shot script that re-hits Scryfall per already-enriched card, patches `flavor_text:` / `oracle_text:` / optionally `type_line:` / `keywords:` into frontmatter, doesn't touch vision tags. Idempotent on re-run. Safe to drop mid-corpus because it doesn't change downstream behavior.
- Consumption phase (later, separately): decide whether `flavor_text` should feed into the bbl-researcher vision system prompt. Risk: re-introduces the confab failure mode v4 was hardened against (Divine Arrow / Spark Harvest / Nahiri's Stoneblades all successfully refused to name characters mentioned in flavor text but not in art). If we add it as input, the anti-confab rules need retesting — probably want explicit prompt language like "flavor text is context, NOT a license to name what isn't in the image."
- Going-forward wiring on `researchbot.py --prepare-only` should land alongside or after the backfill, not before — keeps the corpus consistent.

**Why this lives in sketchbook:** capture is trivial work but its consequence (vision-prompt consumption) is an architectural decision worth deliberating, not slipping into a sprint.

---

## Archive folder as triviabot knowledge store

**The idea:** generalize `archive/` from its current narrow use ("cards that dropped to qty=0 — sold, traded, or bundled") to also hold orphan knowledge nodes that triviabot creates during research.

When triviabot researches Nissa's Triumph (suspected_ip flag from vision), it'll pull EDHREC trivia, Reddit sentiment, lore. In that process it learns relevant info about Nissa, Vital Force / Nissa, Worldwaker — planeswalkers we don't own. Instead of throwing that info away, write an `archive/magic-the-gathering/<set>/<num>-<slug>.md` for each, with the trivia attached and a flag like `source: triviabot-orphan`.

**Why this is good:**
- The folder semantics already generalize cleanly — `archive/` is "knowledge nodes for cards not currently in inventory," and the reason (we sold them vs we never had them) is just a frontmatter flag away.
- More graph nodes per concept = better hub-curator signal on which tags are real anchors.
- Triviabot's marginal cost: a scrape that mentions 5 cards costs the same whether we save 1 or 5 nodes.
- Cleanly handles the "returning from archive" case: when a future CSV includes that card for real, csv2mdbot's existing archive-return path moves the MD into `cards/`, preserves the body, surgical-update writes the CSV-managed fields. Already works.

**Coordination needed when implementing triviabot:**
- archive/ MDs need `source` (or similar) flag distinguishing `triviabot-orphan` from `bundled` / `sold` / etc.
- Lair architect's `available = quantity - held_for_lair - committed-this-run` query filters orphan cards out automatically since they have `quantity: 0`. No change needed.
- Hub curator queries should *include* archive entries — they're real graph data for tag-promotion votes.
- Storefront / inventory views must continue hiding archive entries (already implicit via `quantity > 0`).

**Status:** future work, parked here while triviabot itself is unbuilt. When it lands, archive-write behavior should be in scope from day one.

---

## (more to come)

This file is intentionally append-only for now. Add new "wouldn't it be cool" concepts below as they form. When something graduates from idea to in-progress work, move it into the README's milestones section or its own dedicated doc.
