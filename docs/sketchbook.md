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
a single bundle JSON into a hero (title + subtitle + narrative + hub badges +
anchor tags) + card grid (image + name + matched tags + why-it-fits) +
cohesion panel + metadata footer. Default loads from
`sample-bundles/sleep-when-youre-dead.json`. File picker for ad-hoc loads.

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
  "schema_version": "0.2",
  "title": "Sleep when you're dead",
  "subtitle": "for the figures who never stop working",
  "narrative": "Long-form prose paragraph that does the persuasion work. Reads as the bundle's marketing copy. NOT a tag-cluster description — a thesis.",
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

**Implementation plan (when the commercial brand lands):**
1. New domain points at the bundle previewer (forked from the dev-mode DL version with picker/metadata stripped).
2. Stripe account with the commercial brand, single-product checkout sessions per bundle.
3. Cloudflare Worker (since DL/PE already use Cloudflare) hosts the `create-checkout-session` endpoint and the post-payment webhook.
4. Webhook fires an email to a fulfillment inbox + writes the order to a small queue (D1 or just append-only file in repo).
5. Bundle JSON gains a `stripe_price_id` field linking each bundle to its Stripe product/price record. Schema bump to v0.3 when this lands.

---

## Symbols layer: iconographic ideology as a first-class graph dimension

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

## (more to come)

This file is intentionally append-only for now. Add new "wouldn't it be cool" concepts below as they form. When something graduates from idea to in-progress work, move it into the README's milestones section or its own dedicated doc.
