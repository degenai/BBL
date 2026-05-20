# Sketchbook — forming ideas

Catch-all for half-baked concepts, future work, and "wouldn't it be cool if" notes. Things land here before they're ready to be specs, scripts, or features. Promote out into proper docs (or commit work) when they crystallize.

---

## Thumbnail composer (anti-slop A/B workflow)

**The idea (Alex 2026-05-11):** bundle thumbnails for storefront / catalog grid / social preview should NEVER be straight AI-generated. That reads as cheap and slop-y to anyone who recognizes the aesthetic, which is everyone now. Instead: AI assists *composition*, not generation. Library of real assets, programmatic combinatorial layouts, flashcard A/B picker for Alex to choose the winner.

**Visual grammar (the asset library):**
- **Transparent cutouts of "our" faces** — Alex, Sarah, possibly Babycakes the cat. Sourced from real photos with bg removed. Expression library: deadpan, raised eyebrow, knowing glance, wide-eyed shock. The Erik Hoffstad / Internet Comment Etiquette aesthetic — clickbait conventions used unironically to sell something real.
- **Red arrows** — the universal "look at this" indicator. Multiple angles, sizes, line weights. Memetic; reads as parody-of-Bandcamp / parody-of-YouTube-thumbnail.
- **Game brand logos** — MTG logo, Pokémon logo, the wordmarks themselves. Provides instant "this is about THAT trading card" recognition before the buyer has read a word.
- **Set logos / symbols** — set-specific. Throne of Eldraine crown, War of the Spark thorn, Ravnica guild marks. Sourced from Scryfall set-icon SVGs (which are public and consistent). Pulled per-bundle based on which sets the cards in the lair span.
- **DISCRETE LAIR #NNN badge** — generated from a template per bundle. Matches the catalog-line "BBL · Discrete Lair NNN" branding from the previewer. Bold, geometric, single-color, sticker-shape.
- **Card art crops** — the actual art_crop images from the bundle. Featured prominently (one or two cards as visual anchor) rather than the full bundle.

**The workflow:**
1. **Library curation** — one-time setup. Build `assets/thumbnail-library/{faces,arrows,logos,set-icons,badges}/` with PNG/SVG. Each asset has a small JSON sidecar (`alex-deadpan.png` + `alex-deadpan.json` with metadata: vibe tags, size, recommended pairings).
2. **Programmatic composition** — per bundle: a Python script reads the bundle JSON, picks N variations of (background card-art + 1-2 face cutouts + 1-2 red arrows + game logo + set icon(s) + LAIR badge), composes via PIL or similar, emits N candidate thumbnails to `bundles/<slug>/thumbnails/cand-N.png`.
3. **Flashcard A/B picker** — small HTML page (or built into the bundle previewer): shows pairs of candidate thumbnails, Alex clicks the winner, the loser drops out, tournament-style. Final winner gets stamped as `bundles/<slug>/thumbnail.png` and referenced in the bundle JSON.
4. **Optional ranking variant** — show 10 at a time, Alex sorts by drag, top one wins. Lower friction for "all candidates are bad, regenerate" scenarios.

**Why this matters:**
- AI thumbnails read as slop. Slop kills trust. Trust is the only thing BBL has that the Reddit-grade bulk seller doesn't.
- The composition step is real labor that's *visible* to the buyer when they look at the thumbnail. Faces > stock art. Red arrows > generic frame. Game logo > "Magic: The Gathering" in 14pt Helvetica.
- The A/B flashcard step keeps Alex's judgment in the loop. Composition is mechanical, curation is human.
- The aesthetic is anti-establishment by referencing internet-clickbait grammar without surrendering to it. Same energy as the brand voice across the rest of BBL.

**Open questions when this gets built:**
- Where do face cutouts live (private repo? local-only?) — privacy boundary
- How many candidate thumbnails per bundle? (Suggest 8–12 to keep tournament short)
- Does the composer reuse anime.js v4 animations or does it produce static PNGs? (Static for thumbnail; animated preview is the existing previewer page's job)
- Does this need a dedicated agent (`bbl-thumbnailer`?) or is it pure Python orchestration like csv2mdbot?

**Probably:** pure Python composition + HTML A/B picker, no LLM in the loop except for "given the bundle's narrative + intent tags, suggest 3 face expressions and 1 LAIR-badge color that fit the mood." That single LLM call decides asset *flavor*; deterministic Python does the *combinatorics*. Same shape as the bundler design: ≤2 LLM calls per task, deterministic everywhere else.

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

## Narrative-first lair architect

**The pivot** (2026-05-10): until this point the implicit lair-architect spec was
*find dense tag intersections in the graph → label the cluster → ship.* Alex
flipped it. The flow is **narrative → tag**, not tag → narrative. A bundle is
not its tag cluster; it's a thesis with cards as evidence.

> "We will naturally want to gravitate towards certain themes that fit our
> brand, anti establishment, enjoyment of personal curation as rebellion from
> chasing the most recently printed chase card. A celebration of labor and
> societal critique can be strong narratives to wrap bundles around. Tie a
> bundle not to just a set of tags but to a unique narrative."

This separates BBL from Secret Lair (Wizards' product). Secret Lair sells
themed boosters — random aesthetic groupings, "here are 5 cats." BBL sells
zines with cards stapled in — the writing is the labor; the cards are
substantiation.

**Brand voice anchors** (the kinds of narratives that fit):
- Labor critique (`labor`, `exhaustion`, `servant`, `drudgery`, `tax-collector`, `vow`)
- Class struggle in disguise (Karlov Manor murder mystery = class violence in evening wear; tax-collector + servant + scrubbing scene as ambient unfreedom)
- Anti-establishment / anti-FOMO (curation-as-rebellion against the chase-card treadmill)
- Anti-colonial / nature-reclaims-civilization (overgrown ruins, broken golden spear in vines, empire ends)
- Solidarity / collective action (crowd scenes, rallying cries, mass refusal)
- Personal-political (Alex's politics legible without being preachy — show, don't lecture)

**Example narrative seeds** the existing corpus would already support:
- **"Sleep when you're dead"** — Mind Rot (inventor slumped at workbench, M21 art), Wicked Guardian (servant scrubbing for nobility, ToE), Charity Extractor (armored tax-collector, MKM), Cabal Therapy, Deafening Silence (stitched-mouth vow-monks, ToE). Spine: `labor` + `exhaustion` + `servant` + `drudgery` + `vow`.
- **"The forest remembers"** — Bala Ged Recovery, Return to Nature (broken golden spear in undergrowth), War of the Spark Forest #262 (Ravnica reclaimed by green), the "overgrown ruins" cluster. Spine: `forest` + `ruins` + `moss` + `vines` + `overgrowth` + `nature-reclaims-civilization`. The "Forest" oversized cluster from co-occurrence analysis decomposes here.
- **"Workers of the world, untap"** — Witch's Vengeance (crowd), Inspire Awe (rallying cry), Crush Dissent (negative-space framing — what the bundle is against). Spine: `crowd` + `mob` + `villagers` + `ritual` + `rallying-cry` + `oppression`.
- **"What the manor doesn't tell you"** — Loxodon Eavesdropper, Coerced to Kill (showcase), Deadly Complication (showcase), Topiary Panther, Culvert Ambusher — Karlov Manor reread as class-violence-in-costume. Spine: `noir` + `crime-scene` + `investigation` + `manor` + class anxiety read into the mystery genre.

**The titles ARE poems.** "Sleep when you're dead" or "The forest remembers"
or "Workers of the world, untap" do the entire persuasion work on the
storefront listing. The buyer reads the title alone and knows if they're the
buyer for it. That's the bar for a BBL bundle title.

**Architecture sketch** (three routes, none picked as of 2026-05-10):

1. **Manual / Alex-authored.** Alex writes the narrative phrase AND a hand-curated set of intent tags. Lair architect just runs the matching math (find cards whose tags overlap the intent set, rank by overlap density, filter for visual/mood cohesion). Highest fidelity, slowest scale, doesn't help discovery.
2. **LLM-mediated.** Alex writes narrative phrase only. LLM expands to ~10-15 candidate hub tags. Matcher finds best card subset. Most discovery, lowest precision, risks drifting from brand voice if LLM hallucinates "this is what labor-themed art looks like" away from Alex's actual aesthetic.
3. **Hybrid** (probably the right default). Alex writes narrative + 3-5 anchor tags (the load-bearing ones). LLM expands the rest of the intent set. Matcher does the rest. Locks brand voice in Alex's hands; lets matcher cast a wider-than-Alex-would-bother net.

**Matching math** (when we get there) — pseudocode:
```
def find_bundle(narrative, anchor_tags, intent_tags, n=5..15):
    # intent_tags = anchor_tags + LLM-expanded set
    candidates = []
    for card in inventory_where_quantity_gt_held_for_lair:
        overlap = len(set(card.tags_hub) & set(intent_tags))
        if overlap >= 2:  # at least 2 intent tags must hit
            candidates.append((overlap, card))
    candidates.sort(reverse=True)
    # cohesion pass: ensure mood/setting/palette don't fight each other
    return filter_for_visual_cohesion(candidates[:n*3])[:n]
```

**Why filter for cohesion after density:** a bundle of 10 cards all tagged
`labor` but spanning Greek-myth + Innistrad-gothic + Eldraine-fairytale +
Aetherdrift-racing would feel incoherent even though every card hits the
narrative. The visual register has to lock too. `mood` + `setting` +
`time_of_day` + palette fields in frontmatter are exactly the tier_filter
data the cohesion pass would use.

**Status:** lair architect itself isn't built yet. This sketch parks the
brand thesis and the architecture direction so when it gets built it starts
narrative-first by default, not tag-first.

---

## Bundle Previewer + bundle JSON schema

**Status (2026-05-11):** scaffold landed at `diamondlegendz/bundle-previewer/`.
HTML/JS/CSS playground, CSP-safe, anime.js v4 from the facets vendor. Renders
a single bundle JSON into a hero (catalog-line + hub badges + title + subtitle
+ narrative) + anchor-tag chips + card grid (image + name + matched tags +
why_it_fits + per-card pricing + multi-copy pill) + cohesion panel + sectioned
pricing receipt with Stripe checkout button + metadata footer. Default loads
`sample-bundles/tithe.json` (Discrete Lair 001).

**Why on Diamond Legendz, not BBL:** DL is the html/js/css playground per
project conventions; BBL stays Python-only. Eventual buyer-facing variant
can fork off the dev one with the file-picker and JSON-debug surfaces
stripped out.

### Bundle JSON schema (v0.3)

Locked in 2026-05-11. Adds the `checkout` block (Stripe Payment Link URL) to
v0.2. Earlier history: v0.1 had narrative + cards; v0.2 added `pricing` block
+ per-card market price.

When the `bbl-bundler` agent lands, this is its emit contract.

```json
{
  "schema_version": "0.3",
  "series_label": "BBL",
  "catalog_id": "Discrete Lair 001",
  "title": "Tithe",
  "subtitle": "the men they send",
  "narrative": "Long-form prose paragraph that does the persuasion work. Reads as the bundle's marketing copy. NOT a tag-cluster description, a thesis.",
  "hubs": ["labor"],
  "anchor_tags": ["labor", "exhaustion", "servant", "drudgery"],
  "intent_tags": ["labor", "exhaustion", "servant", "drudgery", "tax-collector", "scrubbing", "burnout", "vow", "ritual", "captive", "coercion", "robed-figure", "hooded-figure"],
  "cards": [
    {
      "name": "Mind Rot",
      "set": "Mystery Booster Cards",
      "collector_number": "7",
      "image_url": "https://cards.scryfall.io/png/front/.../<uuid>.png",
      "tags_matched": ["body-horror", "burnout", "exhaustion", "labor"],
      "why_it_fits": "Per-card prose: 1-2 sentences explaining why this specific card embodies the bundle narrative. NOT generic — the curator's voice.",
      "qty_in_bundle": 1,
      "market_price_usd": 0.20,
      "market_price_as_of": "2026-05-10",
      "market_price_source": "collectr"
    }
  ],
  "cohesion": {
    "mood": "weary",
    "register": "interior / ritual",
    "palette_hex": ["#5a4a30", "#3a2a15", "#1a1208"],
    "color_identities_present": ["mono-black", "mono-white"],
    "set_diversity": ["Throne of Eldraine", "War of the Spark"]
  },
  "pricing": {
    "card_value_subtotal_usd": 3.15,
    "labor_and_sleeve_per_card_usd": 0.10,
    "labor_and_sleeve_total_usd": 0.60,
    "cost_basis_usd": 3.75,
    "diy_seller_count_estimate": 2,
    "diy_shipping_per_seller_usd": 1.50,
    "diy_alternative_usd": 6.15,
    "diy_alternative_note": "Realistic floor; 2-3 TCGplayer sellers at plain-envelope rates.",
    "bundle_price_floor_usd": 5.00,
    "bundle_list_price_usd": 5.00,
    "shipping_policy": "buyer-paid, itemized separately at checkout; never included in list price",
    "estimated_shipping_usd": 1.50,
    "narrative_premium_usd": 1.25,
    "buyer_savings_vs_diy_usd": 1.15,
    "buyer_savings_vs_diy_pct": 19,
    "premium_justification": "The $1.25 above cost basis pays for the writing, the framing, the thesis. The buyer is not buying $3.15 of cards — they're buying a zine with cards stapled in."
  },
  "checkout": {
    "stripe_payment_url": "https://buy.stripe.com/...",
    "stripe_price_id": "price_1ABC...",
    "checkout_provider": "stripe-payment-link"
  },
  "metadata": {
    "generated_by": "bbl-bundler-v0",
    "generated_at": "2026-05-11",
    "edition_size": "1 of 1",
    "card_count": 6,
    "rarity_distribution": {"common": 5, "uncommon": 1, "rare": 0, "mythic": 0}
  }
}
```

**The `checkout` block** holds the payment integration metadata. `stripe_payment_url` is the Stripe Payment Link buyers click to actually purchase. `stripe_price_id` is the corresponding Stripe Price record (optional, used if we later switch from Payment Links to programmatic Checkout Sessions). `checkout_provider` describes which integration is in use. Possible future values: `stripe-checkout-session` (when we wire the Cloudflare Worker), `stripe-payment-link` (current), `manual` (PayPal/Venmo direct for testing). The bundle previewer renders a Buy button when `stripe_payment_url` is set and non-placeholder; placeholder URLs render as a disabled button with a hint to fill it in.

**Hard policy (alex 2026-05-11):** `bundle_list_price_usd >= 5.00` always, no
upper bound. Shipping is buyer-paid and itemized separately, NEVER baked into
the list price. The `bbl-bundler` subagent must refuse to emit a bundle JSON
where the list price drops below the floor or below cost basis (it can never
clear money) — see `memory/bbl-bundle-pricing-codified.md` for the full
pricing model and `memory/bbl-bundle-creation-subagent.md` for the agent
spec.

**Field discipline:**
- `narrative` does the persuasion work. If the title alone is the pitch, the narrative is the album-back-cover liner. Sentences in Alex's voice (or LLM mimicking, then Alex-edited).
- `anchor_tags` are the 2-5 hand-picked tags Alex (or the architect) anchored the bundle on. These should map to a hub's `tag_signals` list.
- `intent_tags` is the expanded set the matcher used to find cards. Includes anchors + LLM-expanded related tags. Surfaced on the page only for dev-mode previewer; can be hidden in buyer-facing.
- `tags_matched` per card = `intersection(card.tags_hub, intent_tags)`. Tells the user *why this card is in this bundle.*
- `why_it_fits` is per-card editorial. The architect can generate a draft; Alex edits. This is the second-most-important text in the bundle after the narrative itself.
- `hubs` is the list of foundational hub MDs this bundle anchors against. Drives the hub badges in the hero.
- `cohesion` is optional-but-recommended. Drives the cohesion panel at the bottom. Palette swatches especially are good visual proof that the bundle is *intentional* and not just tag-cluster output.

**Sample bundles directory** (`sample-bundles/`) is the validation corpus. Add
new bundles here as you draft them. The previewer's file picker can also load
arbitrary JSONs from disk for one-off testing without committing them.

**What's NOT in v0.1** (deferred):
- Per-card `flavor_text` and `oracle_text` — depends on the Scryfall flavor-text capture work parked in the earlier sketchbook entry. When that lands, previewer should display flavor text under each card image (or as a hover detail).
- Tag-heatmap matrix (rows=cards, cols=intent_tags, fill=match) — would be a nice dev-mode addition to spot which intent tags are "carrying" the bundle vs which are dead weight. Add later if useful.
- Animated reveal-on-scroll for long bundles. Current entrance animation is one-shot on load. Acceptable for 5-15 card bundles; revisit if bundles get larger.
- Print/PDF export. The buyer-facing port would benefit from a "print this bundle" button that emits a clean zine-format PDF.

---

## Storefront: Stripe Checkout, not Shopify

**Decision (Alex 2026-05-11):** when the BBL storefront launches, use Stripe Checkout embedded into the bundle previewer page on the commercial-brand domain (Diamond Legendz is shelved for commerce per the wiki). Do not use Shopify.

**Why not Shopify:**
- Built to sell many-of-the-same-with-variants. BBL sells one-of-a-kind per SKU. The platform's UX assumptions (low-stock badges, upsells, variant pickers) don't fit the product.
- $29-79/mo subscription baseline plus per-transaction fees plus app subscriptions if you want anything custom. Eats margin hard on low-volume bundles.
- Theme templating constrains the bundle page. The previewer already does the editorial work; Shopify would force a rebuild inside its box.
- Brand-thesis problem: BBL's pitch is curation-as-rebellion against algorithmic mass-output. Renting from the landlord of ecommerce undercuts the position.

**Why Stripe Checkout:**
- The bundle previewer is the product page. Add a Buy button below the cohesion panel, Stripe hosts the actual checkout (PCI-compliant, fraud-protected).
- Zero monthly fee. ~2.9% + $0.30 per transaction. Standard payment processing rate, no platform rent.
- Webhook on successful payment fires an email to a fulfillment queue with the bundle slug.
- Dev work is small: Stripe.js button, server endpoint for `create-checkout-session`, webhook handler. Less than a day of work.
- Scales to hundreds of bundles before we'd outgrow it.
- Brand-aligned: the buyer pays the curator directly, no platform obscuring the relationship.

**Other options considered:**
- BigCartel: cheaper Shopify-alike (~$10-20/mo) for indie sellers. Fits BBL better than Shopify but still imposes templating. Use as fallback if Stripe-from-scratch turns out to be too much dev work.
- Etsy: cross-listing surface for audience reach (~6.5% fee). Audience overlap with TCG collectors is weaker than the craft-curated aesthetic suggests. Consider as secondary, not primary.
- Whatnot / TCGplayer / eBay: don't fit. Whatnot is livestream-auction (wrong format), TCGplayer search is single-name-focused (no merchandising surface for bundles), eBay audience doesn't know what BBL is.
- Reddit/Discord direct sales with manual PayPal/Venmo: viable for the first 5-10 bundles before infra cost is justified. Zero platform fee, high admin overhead.

**Partially shipped 2026-05-11:** schema v0.3 landed with the `checkout` block (top-level `checkout.stripe_payment_url`, `checkout.stripe_price_id`, `checkout.checkout_provider`). The previewer renders a Buy button when the URL is set and non-placeholder. Current sample bundles ship with placeholder URLs (`https://buy.stripe.com/PLACEHOLDER_<slug>`) so the rendering can be verified before real Stripe account exists.

**Implementation plan (when the commercial brand lands):**
1. New domain points at the bundle previewer (forked from the dev-mode DL version with picker/metadata stripped).
2. Stripe account with the commercial brand, single-product checkout sessions per bundle.
3. Cloudflare Worker (since DL/PE already use Cloudflare) hosts the `create-checkout-session` endpoint and the post-payment webhook (upgrade from Payment Links to programmatic Checkout Sessions).
4. Webhook fires an email to a fulfillment inbox + writes the order to a small queue (D1 or just append-only file in repo).
5. Bundle JSON's `checkout.checkout_provider` switches from `stripe-payment-link` to `stripe-checkout-session`. Forward-compatible; no schema bump required.

---

## Symbols layer: iconographic ideology as a first-class graph dimension

**Status: SHIPPED 2026-05-11.** Layer is live at `cards/_symbols/` with one symbol (`orzhov-signet.md`) and 2 cards referencing it via the `symbols:` frontmatter field. Bot guards updated to recognize `type: symbol`. See memory file `bbl-symbols-layer-built.md` for the schema documentation and agent-integration plan. The historical sketch is preserved below for context on why the layer was built.

**The idea** (Alex 2026-05-11 during Tithe-bundle research): there is a class
of card-art content that doesn't fit cleanly into vision tags OR trivia OR
bundle prose. It's the recurring iconographic symbols that institutions and
factions in TCG worlds use to mark themselves and their property. The Orzhov
Signet is the case study: a four-pronged eclipsed-sun emblem that appears on
multiple Orzhov-faction cards (Pitiless Pontiff's throne, Tithe Drinker's
throne, the Orzhov Signet artifact card itself, almost certainly other
Orzhov cards). Per the artifact card's flavor text:

> "The form of the sigil is just as important as the sigil itself. If it's
> carried on a medallion, its bearer is a master. If it's tattooed on the
> body, its bearer is a slave."

That is, in Alex's framing, **literally functional ideology**: a single
symbol whose meaning inverts depending on how it's worn. The same emblem
marks the priest extracting tithes AND the indentured body that owes them.
The institution stamps both ends of its hierarchy with itself.

This kind of finding is too valuable to scatter across individual card MDs
or bundle prose. It should live as a first-class graph dimension so
multiple cards can reference it, future bundles can anchor on it, and
triviabot/bbl-bundler agents can query it.

**Proposed layer:** `cards/_symbols/` directory in the BBL repo, mirroring
the existing `cards/_hubs/` pattern.

Each symbol gets its own MD file with frontmatter and body:

```
cards/_symbols/orzhov-signet.md
---
type: symbol
name: Orzhov Signet (the eclipsed sun)
aliases: [orzhov-signet, eclipsed-sun, orzhov-emblem, four-pronged-sun]
faction: Orzhov Syndicate
universe: Magic: The Gathering / Ravnica
canonical_source: "Orzhov Signet artifact card (Ravnica: City of Guilds, multiple reprints)"
appears_on: [card-slug-1, card-slug-2, ...]
---

# Orzhov Signet

A four-pronged sun (an "eclipsed sun" in canonical lore) with a thin ring
perimeter and a dark center. The Orzhov Syndicate's faction emblem.

## Meaning

Per the Orzhov Signet artifact card flavor text: "The form of the sigil is
just as important as the sigil itself. If it's carried on a medallion, its
bearer is a master. If it's tattooed on the body, its bearer is a slave."
Later reprints reframe the duality as "sign of status" vs "sign of debt"
but the structural point is identical: the same icon serves opposite ends
of the institutional hierarchy.

## Where it appears

- Pitiless Pontiff (RNA #194) — throne back
- Tithe Drinker (DGM #109) — throne back
- (more candidates pending visual confirmation: Obzedat, Teysa Karlov,
  Orzhov Pontiff, Imperious Oligarch, etc.)

## Why it matters for BBL

This is the highest-leverage thesis detail for any Orzhov-anchored bundle
on the Tithe / apparatus-of-extraction thesis register. The symbol's
master-vs-slave functional duality IS the apparatus of extraction made
into iconography. Bundle prose that names the Orzhov Signet by name (not
"four-pronged golden sun") earns lore-aware buyer credibility and lets
the iconography do the thesis work.
```

**Frontmatter shape for cards that reference symbols:**

```yaml
symbols: [orzhov-signet]   # array of symbol-MD slugs
```

Cards can reference multiple symbols (some cards depict multiple faction
emblems, like guildgates or league-of-guilds collaboration art). The
symbol MDs maintain their own appears_on list, which can be cross-checked
against the cards' symbols arrays as a wikilintbot consistency check.

**How agents consume this:**

- **bbl-researcher** (vision pass) emits a `symbols_observed` field in its
  JSON output when it can clearly identify a known symbol in the art. Cross-
  referenced against the symbols/ library by apply_vision.
- **triviabot** uses the symbol MDs as a research starting point. The
  symbol's `canonical_source` field plus its appears_on list let triviabot
  build cross-card lore context cheaply.
- **bbl-bundler** uses symbols as a cohesion signal. A bundle whose cards
  share a symbol is more cohesive than a bundle whose cards don't, all
  else equal. Cross-card symbol references can be surfaced in the bundle's
  why_it_fits prose ("the same Orzhov Signet that backs the Pitiless
  Pontiff in this bundle").

**Why this isn't just another hub:**

- Hubs are conceptual themes (Labor, Rebellion, Chinese Zodiac).
- Symbols are concrete visual artifacts depicted IN card art with documented
  canonical meanings sourced from the published game.
- A symbol can support a hub (the Orzhov Signet supports the Labor hub
  because the institution-extracting-from-bodies framing is what Labor is
  about) but it isn't itself a hub. Symbols are graph-leaf primitives;
  hubs are graph-root concepts.

**Status:** sketch only as of 2026-05-11. No symbols/ directory exists yet.
First symbol that would land here: orzhov-signet.md, populated from the
Tithe-bundle research. The Tithe-bundle Pontiff + Tithe Drinker copy
already names "Orzhov Signet" as a forward-compatible move; when the
symbols/ directory lands those references resolve to a real graph node.

**Why park this in sketchbook vs build it now:**

Building the symbols layer is real architectural work: new file convention,
new bot guards in csv2mdbot / wikilintbot, new agent field, new schema
documentation. Worth a clean session, not a mid-bundle scramble. The
sketch records the design so when the work happens, the convention is
already chosen.

---

## High-resolution source art for vision passes

**The idea** (Alex 2026-05-11): the cached card PNGs at ~488×680 pixels (Scryfall's `image_uris.png` standard) leave a lot of detail too small to resolve, which is the root cause of the vision-pass confab failures we've documented all session (bat-pug-pet-with-fangs hidden under the cached-image's small frame, the four-pronged Orzhov sun motif mistaken for "halo," figure counts wrong, etc).

The fix is upstream of the model: source art at higher resolution. Two TCG APIs offer this:

- **Scryfall**: every card has an `image_uris.art_crop` URL that returns the painted illustration only, no frame, no text, no border. Same dimensions as the full card but every pixel is signal. For higher-resolution variants, the `large` and `border_crop` URLs are also available; some cards have full-art versions as separate prints.
- **PokémonTCG API**: returns an `images.large` URL per card at ~600×825, plus high-resolution scans for newer sets.

**Pipeline shape when this lands:**

1. `researchbot.py --prepare-only` already caches the full card image to `cards/_images/<game>/<set>/<slug>.png`. Add a second cache: `cards/_images/<game>/<set>/<slug>.art-crop.png` that pulls the art-only URL when available.
2. New frontmatter field `art_crop_image:` mirrors `reference_image:` but points at the art-only file.
3. `bbl-researcher` (the vision-pass subagent) reads from `art_crop_image` when present, falling back to `reference_image` otherwise. The art-crop is what the model parses; the full card is what the human reviews.
4. Visual lint step: after caching, a quick diff/check that the art_crop and the cached full card depict the same scene. Sanity check against Scryfall returning unrelated art.

**Why this matters specifically for BBL:**

The benchmark experiment (`docs/benchmark-tithe-prose.md`) showed that even with a tightened inline prompt, vision models reproduce the same failure modes (figure count wrong, missed secondary figures, color details wrong) on the cached card images. The bottleneck is pixel density on the painted area. Removing the frame doubles the resolution per painted-region pixel. That alone may move vision accuracy from "70% with human eyeball still needed" to "90% with occasional polish."

**Status:** sketch only as of 2026-05-11. No art-crop caching yet. Park this until after the Mystery Booster = The List rename pass and any other near-term janitor work clears.

**Caveat:** PokémonTCG API rate limits may apply; Scryfall is generous but still polite-by-default. The art-crop pass would run once per unique Scryfall UUID across the corpus, so even at 1000+ cards it's a one-shot job, not a per-bundle cost.

---

## Michi Method Binders for Discrete Lairs (storefront) — long-term

**Tag: long-term / storefront-side / not next-sprint**

**The idea (Alex 2026-05-15):** the current bundle-previewer shows Discrete Lair cards in a carousel. Buyers see the cards but not *what the curation is for* — the thesis that earns the bundle its existence stays invisible. A Michi-style binder page would make the curation argument legible: page by page, deliberately composed, with non-card art assets doing the thesis grounding so the cards are arranged AROUND the read, not the other way around.

The Michi method originates from TikTok creator @michimaybe_ (Instagram: peeplop) in the Pokémon TCG community. The core mechanic: 9-slot binder page, but only 5-7 of those slots hold actual cards. The remaining 2-4 slots are intentionally filled with non-card art assets — extended art prints spanning two horizontal or vertical slots, standalone card-sized art prints, cool sleeve backs used as visual texture, character cutouts, set icons, or header-title inserts. The empty/art slots are NOT absence — they are the curatorial argument made visible. The format has spread across TCG communities quickly enough that there's already an Etsy market for Michi-method-specific inserts and printable templates, a dedicated tool ecosystem (pkmnbindr.com, binderforge.com, binderview.com), and tutorial ecosystems on TikTok, Pinterest, and Elite Fourum.

**Why this maps cleanly to BBL doctrine:**

Three existing memory files already describe the principle — `bbl-narrative-first-lairs`, `bbl-museum-curation-framing`, and `bbl-no-ai-slop-thumbnails` — but the binder page is a more literal instantiation of all three simultaneously. A binder page is a physical/digital object where the thesis grounders (the art-slot inserts) literally frame the cards, structurally encoding the narrative hierarchy. The museum-curation framing is most legible here: a museum exhibit has wall text and artifact grouping; a Michi page has art inserts and card grouping. The "anti-slop" constraint from the thumbnail workflow also applies — inserts should come from real asset sources (Scryfall art crops, Bulbapedia character art, Ravensburger CDN jpegs for Lorcana, set icons from Scryfall's SVG set) rather than AI-generated filler.

This is a **storefront-side project** that lives in `Diamondlegendz/bundle-previewer/`, distinct from the BBL graph engine. The graph stays the curation engine. The binder is the storefront output format — a new render target, not a new pipeline component.

**Asset sourcing (from research, 2026-05-15):**

- **Extended art prints (multi-slot panels):** the community self-sources these via Canva with card-art dimensions (1 slot: 7.0×9.5cm; 2-slot horizontal: 14×9.5cm; 4-slot: 14×19.5cm). BBL already has Scryfall `art_crop_url` and Bulbapedia / Ravensburger CDN at high res — that's the BBL-native equivalent.
- **Etsy market for ready-made inserts:** active market for printable digital downloads — custom extended art panels spanning 9/12/16-card puzzle sets, placeholder cards, themed header inserts. Relevant as a reference for what the community will pay for and what formats feel finished.
- **Paper:** Canon photo paper letter-size is the community standard for home-printing inserts. Relevant if the bundle includes a "printable binder page" digital deliverable for buyers.
- **Digital binder preview tools for research ref:** pkmnbindr.com, binderforge.com, binderview.com — all free, Pokémon-specific. No MTG or multi-TCG equivalent found. Worth watching for layout conventions.
- **Sleeve backs as visual texture:** no dedicated free repository found — community uses whatever's on hand (premium sleeve packs like Vault X, Dragon Shield). For BBL purposes, a card-sized print of the DISCRETE LAIR badge or a solid-color brand swatch would serve the same structural role.

**Integration sketch — what BBL data feeds a binder page:**

```
bundle JSON (v0.3+)
  ├── narrative            → thesis grounder INSERT: title card + opening prose
  ├── hubs[]               → hub-node art if/when hub MDs get cover images
  ├── anchor_tags          → could inform color/palette of art inserts
  ├── cards[].image_url    → actual card slots (5-7 of 9)
  ├── cards[].art_crop_url → high-res insert candidates (characters, scenes)
  ├── cohesion.palette_hex → backgrounds for art insert panels
  └── characters[] / symbols[] → character cutouts and icon inserts from graph nodes

cards/_characters/<slug>.md → character art for "who this bundle is about" insert
cards/_symbols/<slug>.md    → icon for "what motif runs through this bundle" insert
cards/_artists/<slug>.md    → artist credit panel (anti-slop: credit is curation)
```

**Open design questions (not for this sprint):**

- Does the binder page render as an HTML view in bundle-previewer (new route/component alongside existing carousel)? As a printable PDF buyers can download alongside the digital bundle? As a buyer-facing preview image (the "binder page as thumbnail" concept)?
- Does the page format change per bundle size? (9-slot works for 5-7 card bundles; larger lairs might want 2 pages with a splash panel spanning the gutter.)
- Who curates the art inserts — Alex manually, or a layout assistant that proposes insert placement based on cohesion data and Alex A/B picks the final layout? (Same flashcard A/B pattern as the thumbnail composer sketch.)
- PDF delivery mechanism: attached to Stripe payment confirmation email? Available as a separate Etsy-style digital download? Both?
- Physical fulfillment angle: if a buyer gets a physical bundle, could the printed binder page ship WITH the cards? That's a differentiator no mass-market TCG seller offers.

**Relationship to other sketchbook concepts:**

- Builds on top of the **thumbnail composer** workflow — the same A/B picker mechanic could rank binder-page layout candidates.
- The **print/PDF export** deferred from the bundle-previewer schema entry is exactly the delivery vehicle for this.
- The **art_crop caching** work (high-res source art sketch above) directly feeds the insert asset pool.
- The **collection timeline HTML** has the same "make the labor visible" logic — binder pages make the curation visible at point-of-sale; the timeline makes it visible retrospectively.

**Status:** concept only as of 2026-05-15. No implementation. Placeholder note in `Diamondlegendz/bundle-previewer/MICHI_BINDERS_FUTURE.md`.

### Competitor findings (research 2026-05-15)

Direct WebFetch was permission-denied in the research agent context; all findings below are from WebSearch snippets and indexed content. Cloudflare-walled sites were not attempted via Puppeteer (parent-only escape hatch per task constraints).

---

#### pkmnbindr.com

- **What it does:** Free Pokémon binder organizer and generator. Primary function is digital collection management — track cards by set, cloud sync, card search. Generates binder pages in 2×2, 3×3, 3×4, and 4×4 grid formats. Buyer selects a set, picks cards per page, and the tool visualizes the layout.
- **What it misses:** No support for Michi-method-style non-card art inserts — the tool is fundamentally card-slot management, not curated composition. No multi-TCG support. No narrative or thesis layer. No PDF/shareable page output surfaced in any indexed content. Collection tracker, not a storytelling surface.
- **Data shape / file format:** Inputs appear to be card name + set selection via search UI. Output is a web preview grid. No export format confirmed from search snippets.
- **UX choices to copy:** Set-based card search pre-filtered by slot context (click a slot, search scoped to that slot's Pokémon) — the "slot-first search" flow is smart UX for a builder. Binder size selector (2×2 through 4×4) is the right abstraction.
- **UX choices to skip:** The entire paradigm — it assumes cards fill every slot uniformly and that the interesting problem is "which card goes where." BBL's interesting problem is "which slots are NOT cards and what do they say."

---

#### binderforge.com

- **What it does:** Positioned as the most feature-rich of the three. "All-in-one digital solution" for Pokémon TCG collection organization. Key differentiator is the Pokédex binder planner — builds binders organized by Pokédex number rather than by set, with live repagination based on binder size (3×3, 4×3). Includes value tracking (TCGPlayer, CardMarket, eBay price sources), drag-and-drop card re-arrangement, and shareable binder links. Free, with a Ko-fi support page indicating it's indie-built.
- **What it misses:** Same structural blind spot as pkmnbindr — no concept of art insert slots, non-card panels, or Michi-method composition. The Pokédex-first organization is clever but orthogonal to BBL's thesis-first logic. No multi-TCG support. No narrative layer.
- **Data shape / file format:** Card data pulled from a Pokémon TCG database (presumably TCGPlayer API or similar). Prices from TCGPlayer, CardMarket, eBay. No file format output confirmed — web preview with shareable link appears to be the output model.
- **UX choices to copy:** Shareable binder URL — low friction for buyer-to-buyer sharing, which maps well to the BBL storefront context. Live repagination by binder size. Value tracking per binder is interesting for BBL's cost-basis-visibility doctrine (buyer can see what market value the bundle represents).
- **UX choices to skip:** Pokédex-organization paradigm (collector completionism, not curation). Price-tracking as the primary value proposition undercuts BBL's "you're buying the thesis, not the market spread" framing.

---

#### binderview.com / pkmn.gg Binder View

- **What it does:** Two related but distinct surfaces. `binderview.com` is a standalone free tool (no login required) that shows card sets as binder pages — primarily a set-completion tracker. `pkmn.gg/binder-view` is the Pro Member version of the same idea with more customization: combine main set + trainer gallery into one view, filter/sort, show/hide price/name/number, size slider, digital binder grouping across sets. Both use a paginated binder-page layout (9, 12, or 16-pocket).
- **What it misses:** Same as above — no art insert slots. These are read-only visualization tools for existing sets, not composition tools. The free binderview.com strips out account features entirely.
- **Data shape / file format:** Read from the Pokémon TCG set database. No upload or custom data input. No confirmed export format — web view only.
- **UX choices to copy:** The size slider for card display scale is simple and useful. The "no login required" framing of binderview.com is the right default for a casual preview surface — friction kills discovery. The subset-integration (main set + trainer gallery merged) is a smart data-layer choice that reduces visual orphaning of related cards.
- **UX choices to skip:** The set-completion-tracking paradigm entirely. It's a collector's checklist tool; BBL is a curation storytelling tool.

---

#### Elite Fourum walkthrough — "Creating a Binder Preview (with Michi Method)"

**URL:** https://www.elitefourum.com/t/creating-a-binder-preview-with-michi-method/60453

- **What it does:** Tutorial article explaining how to use Canva to plan and preview a Michi-method binder page before committing to physical printing. The most useful technical reference found.
- **Key canonical dimensions confirmed:**
  - 1-slot insert: **7.0 × 9.5 cm**
  - 2-slot horizontal insert: **14.0 × 9.5 cm**
  - 4-slot insert: **14.0 × 19.5 cm**
  - (Note: these align with standard side-loader pocket dimensions — 9-pocket binder pages, 3 columns × 3 rows)
- **Canva workflow:** Create a canvas at the target cm dimensions, source art from Pinterest / Google image search, crop and resize to fit, optionally add curves/outlines. Print on Canon photo paper (letter size). The workflow is entirely manual — zero pipeline tooling.
- **Key insight:** the tutorial exists *because* none of the three binder tools above support Michi-method composition. The community workaround is Canva + manual dimension entry. This is the gap BBL can automate.
- **Community adoption signal:** The Pokémon TCG official brand used the Michi method for a Pokémon Worlds 2025 memories binder — method has gone fully mainstream. The creator (michi/@peeplop) also offers paid 1:1 coaching ($40/hr) and a free Discord, indicating the community infrastructure around this method is substantial.

---

#### Community examples surfaced

- **Etsy market for Michi inserts:** Active market for printable digital downloads — "Full Art Binder Page — Custom Extended Artwork Card Display | 9, 12, or 16-card Puzzle Set for Pokémon TCG Michi Method Binders" (etsy.com/listing/1871231409). This is a 9-16 card puzzle spread where a single artwork is sliced across the slots — exactly what BBL's `art_crop_url` + PIL slicing would produce automatically. The Etsy sellers prove buyers will pay for this format as a digital download.
- **Official Pokémon Worlds 2025 binder:** @pokemontcg on Threads used the Michi method for the Worlds 2025 memories binder, confirming the format has franchise endorsement. This also means the Michi layout is now a known commodity to the audience BBL is targeting — they'll recognize it and know what it signals.
- **TikTok tutorial ecosystem:** Dozens of creators (@h3yscollection, @acetraineranthony, @mantinewithmotion, etc.) making Michi tutorials, indicating demand for easier tooling. The manual Canva workflow is the current friction point the entire community is working around. BBL automating this for its own bundles is both practical for internal workflow and a potential differentiator if ever exposed to buyers as "your binder page, included."

---

#### Summary: what competition misses that BBL can do

| Feature | pkmnbindr | binderforge | binderview | BBL (proposed) |
|---|---|---|---|---|
| Art insert slots | No | No | No | Yes — native |
| Multi-TCG | No | No | No | Yes — MTG+Pokémon+Lorcana |
| Narrative / thesis layer | No | No | No | Yes — core doctrine |
| Art sourced from card corpus | No | No | No | Yes — art_crop_url |
| Shareable / downloadable page | Web preview | Shareable link | Web view | PDF target |
| Curated vs collection-complete | Collection | Collection | Collection | Curated |

The three tools are all solving "how do I track and preview my collection set-by-set." BBL is solving "how do I compose a curated argument with cards as evidence." These are different problems using some of the same visual grammar (binder pages, slots). No overlap in the actual design space.

---

### Art conversion pipeline

**The mechanic:** BBL already has high-res source art at the right CDN endpoints — Scryfall `art_crop_url` (painted illustration only, no frame), Bulbapedia CDN JPEGs (Sword & Shield+ at 800px+ width), Ravensburger CDN (Lorcana at 1468×2048). Converting any of these to Michi insert dimensions is a PIL one-liner:

```python
# Resize + crop to 1-slot Michi dimensions (7.0×9.5cm at 300dpi → 827×1134px)
from PIL import Image

SLOT_DIMS = {
    "1slot": (827, 1134),   # 7.0×9.5cm @ 300dpi
    "2slot_h": (1654, 1134), # 14.0×9.5cm @ 300dpi
    "4slot": (1654, 2268),  # 14.0×19.5cm @ 300dpi
}

def to_michi_slot(src_path: str, slot_type: str = "2slot_h", out_path: str = None) -> str:
    w, h = SLOT_DIMS[slot_type]
    img = Image.open(src_path).convert("RGBA")
    # Thumbnail + center-crop (no squish)
    img.thumbnail((w * 2, h * 2), Image.LANCZOS)
    left = (img.width - w) // 2
    top = (img.height - h) // 2
    img = img.crop((left, top, left + w, top + h))
    out = out_path or src_path.replace(".png", f"_{slot_type}.png")
    img.save(out, dpi=(300, 300))
    return out
```

The equivalent ImageMagick invocation:

```bash
# 2-slot horizontal at 300dpi, center-crop, no squish
magick source_art_crop.png \
  -resize 1654x1134^ \
  -gravity Center \
  -extent 1654x1134 \
  -units PixelsPerInch -density 300 \
  michi_2slot.png
```

**Sources this pipeline can draw from:**

- Scryfall `art_crop_url` — already stamped at prep time; width varies but consistently 562px+ on modern cards, suitable for 1-slot, marginal for 2-slot (upscale needed). For 2-slot panels, the Scryfall `large` image (745px) or `border_crop` variant is better.
- Bulbapedia CDN — 800px+ for modern Pokémon sets; strong candidate for 2-slot and 4-slot panels.
- Ravensburger CDN (Lorcana) — 1468×2048 is the highest-res source in the corpus; crops to any slot format without upscale penalty.
- Community art (`michi-assets/` — see below) — curated at target dimensions, no resize needed.

---

### `michi-assets/` directory

New BBL asset directory for community-sourced fan art — "the deviant-art-style unique fan stuff that makes a Michi a Michi." The card art crops are the baseline; what makes a binder page *individual* is the curated non-official material in the art slots.

**Folder structure:**

```
cards/michi-assets/
  index.json               # citation metadata for every asset (see schema below)
  characters/              # character fan art, portraits, cutouts
    <slug>.png             # e.g. charizard-fan-watercolor-2023.png
  scenes/                  # multi-character or environmental fan art
    <slug>.png
  headers/                 # title cards, typographic inserts, section dividers
    <slug>.png
  badges/                  # DISCRETE LAIR badges, BBL logos, brand marks
    <slug>.png
```

**`index.json` citation schema:**

```json
[
  {
    "slug": "charizard-fan-watercolor-2023",
    "file": "characters/charizard-fan-watercolor-2023.png",
    "slot_type": "1slot",
    "dimensions_px": [827, 1134],
    "artist_name": "h3yscollection",
    "artist_url": "https://www.tiktok.com/@h3yscollection",
    "source_url": "https://www.tiktok.com/@h3yscollection/video/XXXXXXXXXXX",
    "permission_status": "implied_personal_use",
    "permission_notes": "Creator posts tutorials encouraging personal use; no commercial restriction stated; not mass-distributed",
    "ip_owner": "Nintendo / Creatures Inc. / Game Freak",
    "tags": ["charizard", "fire", "watercolor", "fan-art"],
    "added": "2026-05-15"
  }
]
```

**Permission status vocabulary:**

- `cc0` — confirmed public domain / CC0 license
- `cc_by` — Creative Commons attribution required; credit rendered in binder page
- `explicit_personal_use` — artist explicitly said personal/non-commercial use OK
- `implied_personal_use` — artist posts in contexts implying personal use; no commercial restriction stated; BBL use is personal-use-scale optional download
- `requested` — outreach sent, response pending
- `unknown` — not yet investigated; do not use until resolved

---

### Optional-download model

Framing from Alex (verbatim, preserved): "we're making hand-curated one-offs we're not mass marketing their art, just providing it as an optional download for people that have the same interests as the artist themselves."

The operational model:

1. Bundle purchase on Stripe completes.
2. Post-payment webhook sends fulfillment email.
3. Email includes (a) the physical cards shipping confirmation and (b) an **optional** link to download a ZIP: `bundle_<slug>_binder_page.zip` containing the binder page PDF + the constituent art assets used in it.
4. The ZIP's `credits.txt` lists every asset: artist name, source URL, permission status. The credit is not buried — it's the first file in the ZIP.
5. Framing in the email: "Because you bought this bundle, you already share the interests this art was made for. The download is optional and the art assets belong to their original creators — links included so you can find their work."

This model is ethically adjacent to a museum store selling a postcard of an artwork — the postcard buyer already has an interest connection to the work. The citation discipline is what makes it defensible: the artist is credited, the source is linked, the permission status is honest. "Implied personal use" is a stretch for anything involving commerce; this is acknowledged honestly in the index.json `permission_notes` field, and any asset with `unknown` status is excluded from downloads until resolved.

Hard rule: assets with no permission investigation (`unknown`) never appear in a buyer-facing download. `implied_personal_use` assets appear only after judgment call from Alex, documented in `permission_notes`. BBL never removes attribution.

---

### Binder page JSON shape (slot-level)

When the binder page composer eventually gets built, this is the data contract it works from. Not a bundle JSON field — a separate sidecar file per bundle:

```json
{
  "schema_version": "binder-page-0.1",
  "bundle_slug": "tithe",
  "catalog_id": "Discrete Lair 001",
  "page_format": "9slot_3x3",
  "pages": [
    {
      "page_index": 0,
      "slots": [
        {
          "position": 0,
          "type": "art",
          "span": "2slot_h",
          "source": "scryfall_art_crop",
          "source_url": "https://cards.scryfall.io/art_crop/front/.../.../artcrop.jpg",
          "processed_path": "michi-assets/generated/tithe-p0-slot0.png",
          "caption": null
        },
        {
          "position": 2,
          "type": "card",
          "span": "1slot",
          "card_name": "Wicked Guardian",
          "image_url": "https://cards.scryfall.io/png/front/.../<uuid>.png",
          "why_it_fits": "The servant scrubs the floor so the lord's guests don't notice the floor."
        },
        {
          "position": 3,
          "type": "card",
          "span": "1slot",
          "card_name": "Charity Extractor",
          "image_url": "https://cards.scryfall.io/png/front/.../<uuid>.png",
          "why_it_fits": null
        },
        {
          "position": 4,
          "type": "header",
          "span": "1slot",
          "source": "michi_assets",
          "asset_slug": "discrete-lair-001-title-card",
          "processed_path": "michi-assets/headers/discrete-lair-001-title-card.png"
        },
        {
          "position": 5,
          "type": "card",
          "span": "1slot",
          "card_name": "Mind Rot",
          "image_url": "https://cards.scryfall.io/png/front/.../<uuid>.png",
          "why_it_fits": null
        },
        {
          "position": 6,
          "type": "art",
          "span": "1slot",
          "source": "michi_assets",
          "asset_slug": "orzhov-signet-icon-panel",
          "processed_path": "michi-assets/badges/orzhov-signet-icon-panel.png",
          "caption": "Orzhov Signet — the eclipsed sun"
        },
        {
          "position": 7,
          "type": "card",
          "span": "1slot",
          "card_name": "Tithe Drinker",
          "image_url": "https://cards.scryfall.io/png/front/.../<uuid>.png",
          "why_it_fits": null
        },
        {
          "position": 8,
          "type": "card",
          "span": "1slot",
          "card_name": "Pitiless Pontiff",
          "image_url": "https://cards.scryfall.io/png/front/.../<uuid>.png",
          "why_it_fits": null
        }
      ]
    }
  ]
}
```

Notes on the shape:
- `position` is 0-indexed, row-major (position 0 = top-left, position 8 = bottom-right for 3×3).
- `span` is "1slot", "2slot_h", "2slot_v", "4slot". Multi-slot inserts occupy the position of their top-left slot; downstream slots in the span are omitted from the array (they're implied occupied).
- `type` is one of: `card`, `art`, `header`, `badge`, `spacer`. `spacer` = intentional blank (sleeve back, brand swatch, or literal nothing for asymmetric layouts).
- `source` for art slots: `scryfall_art_crop`, `bulbapedia`, `ravensburger_cdn`, `michi_assets` (from the curated directory), or `generated` (BBL-produced, e.g. DISCRETE LAIR badge from template).

---

### Open questions before any implementation starts

1. **Render target: HTML, PDF, or image?** The three options serve different moments: HTML inside the bundle previewer (buyer preview, no download needed), PDF as optional download (buyer prints and inserts), static image as the "binder page as thumbnail" social card. The answer probably isn't "pick one" — it's "HTML is free, PDF is the buyer deliverable, image is the marketing asset." But each is a separate build surface and the implementation cost is additive.

2. **Who places the art inserts?** The card slots are determined by which cards are in the bundle (deterministic). The art insert slots require layout judgment — where do the 2-slot panels go? Does a title card go top-left or top-right? Is the symbol insert best at position 6 or position 8? Two options: (a) Alex curates every layout manually using a simple editor or a CLI with slot/type arguments, then A/B picks using the thumbnail composer's flashcard mechanic; (b) a layout assistant proposes N candidates based on cohesion data and Alex approves one. Option (a) is simpler to build first and preserves full curatorial authorship. Option (b) is faster at scale but risks AI layout thinking overriding Alex's eye.

3. **How many pages does a large bundle get?** A 5-7 card bundle maps cleanly to one 9-slot page with 2-4 art inserts. A 15-card bundle is three pages minimum. Do larger Discrete Lairs get a multi-page binder spread (like a zine with page turns) or a single splash page that shows only 5-7 "representative" cards? If multi-page, does each page need its own thesis insert set, or does one title-card insert + subsequent card-only pages work? This isn't a technical question — it's a product design question about what the buyer experience should be.

4. **License model for optional art downloads.** The `permission_status` vocabulary in the index.json handles this per-asset, but there's a product-level policy question underneath: does the download ZIP carry a top-level license that governs how buyers can use the binder page? Proposed framing: "Personal use only — the art in this file belongs to its credited creators; BBL is passing it through, not licensing it. Print it for your own binder. Don't resell." This is not a license in the legal sense but a clear statement of intent. The question is whether to make it explicit in the ZIP's `credits.txt` or whether that's overcommunicating to buyers who just want to print a pretty page.

5. **Multi-TCG insert asset sourcing.** The Michi community and all three tools are Pokémon-only. BBL spans MTG, Pokémon, and Lorcana, which means the binder page needs to handle art assets from three different universes — potentially in the same bundle if a Discrete Lair is intentionally cross-TCG (unlikely for Tithe-register bundles, but possible for broader thematic lairs like "labor" or "rebellion"). Does a mixed-TCG bundle get one binder page with heterogeneous card frames, or do cross-TCG bundles always get split pages per game? The frame-visual inconsistency (black-bordered MTG card next to Pokémon's colored-border card next to Lorcana's gilt frame) is a design decision, not a technical one, and it shapes what art insert work looks like for those bundles.

---

**Status (2026-05-15):** spec expansion only. No implementation. Competitor findings based on WebSearch snippets (WebFetch permission-denied in subagent context — direct site inspection deferred to parent-run Puppeteer or manual review session). The `michi-assets/` directory does not yet exist; the binder-page JSON schema above is a design sketch, not an implemented contract.

---

## (more to come)

This file is intentionally append-only for now. Add new "wouldn't it be cool" concepts below as they form. When something graduates from idea to in-progress work, move it into the README's milestones section or its own dedicated doc.

---

## Lair seed — the Blackwell register (cozy M21 commons)

**The seed (Alex, waves 153 & 155, 2026-05-19):** two M21 commons keep landing the same personal feeling — **Pridemalkin** (the felid, no. 196) and **Rambunctious Mutt** (the dog, no. 30). Alex on Pridemalkin: *"reminds me opening up cards with Andy at Blackwell our old house when I met Sarah."* On Rambunctious Mutt: *"gives me the same vibes as pridemalkin."*

The vibe is not a tag — it is a *register*. Cozy, low-stakes, slightly-goofy creature commons; the feeling of opening packs with a friend at the old house, the year a life was starting. A cat and a dog so far. This is a narrative-first lair seed in the truest sense (per the brand position): the thesis is a feeling and a place, and the cards are the evidence. The narrative — title, copy — is Alex's to author when it crystallizes; this note only records the seed and the two anchor cards so they are not lost.

**Why it matters:** this is the BBL thesis made personal. Pridemalkin is an EDHREC-4310 common worth ~40 cents by every reseller metric. Its real value is that it is a door back into a specific year. A "Blackwell register" lair is curation-as-rebellion against valuing cards by exchange-value — it sells use-value, memory, the small object that means something.

**Who adds to this list:** Alex, and only Alex. The Blackwell register is a *felt* thing, not a detectable one — it is not "cozy creature common," it is a specific memory. Do NOT auto-nominate cards into this seed from vision/trivia tags or vibe-matching. A card joins only when Alex says it lands the feeling. The agent's job here is to *record* what Alex flags, never to propose.

**Era boundary (Alex, 2026-05-19):** the felt cards come from four sets — **Theros**, **Throne of Eldraine**, **Ikoria**, and **M21** — mostly the up-to-Theros end, with some Eldraine / Ikoria / M21. Those four are the collecting-era window for the Blackwell period. A card outside those four sets is almost certainly not Blackwell-register, whatever its vibe. Pridemalkin and Rambunctious Mutt are both M21 — in window.

The lair assembles when there is a cohort, not just a pair. No node, no graph object — this lives as a sketchbook seed and (eventually) a Discrete Lair, not a layer node.
