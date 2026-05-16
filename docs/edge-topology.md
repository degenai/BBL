# BBL Edge Topology

> A reader's map for how cards and layer nodes connect in the BBL graph. Three different edge protocols coexist with different invariants. Knowing which protocol you're in prevents the next contributor (human or agent) from breaking one by reasoning from another.

## TL;DR

| Protocol | Direction | Surface | Authoritative side | Sync enforced by |
|---|---|---|---|---|
| **card ↔ card** | bidirectional (manual mirror) | `## Connections` section body | both, manually mirrored | reviewer eyes + Edgelord |
| **card ↔ layer-node** | bidirectional (automatic sync expected) | frontmatter list fields | both (must match) | `bbl_node_audit.py` |
| **card → hub** | one-way, no back-pointer | `tags_hub` array on cards | card side only | implicit (tag match at query time) |

If you write an edge that doesn't fit one of these protocols, you're inventing a fourth one. Stop and read this doc first.

---

## Protocol 1 — card ↔ card

**Where it lives:** the card MD's `## Connections` section body. Prose bullets with `[[wikilinks]]` to other card stems.

**Shape:**
```markdown
## Connections

- [[070-189-snubbull]] — Cross-print Snubbull species 3-print stack member. LOT-137 …
- [[115-264-snubbull]] — Same species, Sword & Shield-era timid-bullied flavor variant …
```

**Direction:** bidirectional by manual mirror. Snubbull A points at Snubbull B; Snubbull B should reciprocate with its own bullet in its own `## Connections` section. The mirror is not policed by any audit — it's a discipline.

**When to use:** card-to-card thematic edges that have semantic substance — cross-print cohorts, designer-coordinated pairs, mechanical-mirror dyads, flavor-text-attributed call-backs.

**When NOT to use:**
- Schema/precedent citations ("per the X precedent established in…") → use backticks instead, per `bbl-wikilink-vs-backtick-discipline` memory. Wikilinks to other cards on the basis of citing a methodology rule are maladaptive (caught wave 92 on Lunatone + Solrock).
- Pointers FROM a card TO a layer node → use Protocol 2 instead. Card-to-layer goes through frontmatter, not body prose.

**Invariants:**
- The wikilink target uses the card MD's filename stem (no extension, no path).
- Both cards live in the same Obsidian vault root (`cards/`) so vault-wide name resolution works regardless of subfolder.
- Each bullet ends with citation in backticks: `` `[source 1; source 2]` ``.
- Mirror is reciprocal. If you write A→B, B→A is your debt.

**Tooling:** `bbl_node_audit.py` flags card-cross-reference wikilinks as INFORMATIONAL only (139 found at last audit). They're not layer-node references; they're vault-wide cross-refs. No bidirectional enforcement.

---

## Protocol 2 — card ↔ layer-node

**Where it lives:**
- Card side: frontmatter list field per layer kind — `characters:`, `symbols:`, `artists:` (via `artist:` scalar — special case).
- Layer-node side: `appears_on:` list in the layer node's frontmatter.

**Shape:**

Card frontmatter:
```yaml
characters:
  - kaya
  - foundway-associates
symbols:
  - suspect
```

Layer node frontmatter (`cards/_characters/kaya.md`):
```yaml
appears_on:
  - magic-the-gathering/war-of-the-spark/220-kaya-orzhov-usurper
  - magic-the-gathering/aether-revolt/24-kaya-bane-of-the-dead
```

**Direction:** bidirectional with strict sync expected. Both sides must list each other. If only one side points, that's drift.

**When to use:** card depicts a named character, contains a designer-coordinated mechanical-or-visual primitive, or credits an illustrator. The layer node is the canonical home for any cross-card aggregation of that entity.

**Invariants:**
- Both fields use **block form YAML** (`field:\n  - slug`), never inline JSON. Inline-quoted lists render as one red string in Obsidian (wave 92 fix). The `bbl_schema.normalize_file()` chokepoint enforces this; all writers should route through it.
- Layer-node `appears_on:` path-keys take the shape `<game>/<set>/<file-stem>` (no `cards/` prefix, no `.md` extension).
- Card frontmatter slugs reference an existing layer node MD under `cards/_<kind>/<slug>.md`. Dangling slugs are flagged by `bbl_node_audit.py` as `dangling_wikilink`.
- Layer node anchor threshold: `_characters/`, `_symbols/`, and `_artists/` nodes need **≥3 anchor cards** before commissioning, per `bbl-edgelord-node-rigor-audit` memory. Below threshold = node refuses creation; Mr. Nodeley stages a future-wave trigger instead.

**Tooling:**
- `bbl_node_audit.py` runs a two-way diff: `drift_forward` (node says it has a card, card doesn't point back) and `drift_reverse` (card points at node, node's appears_on doesn't list card). Both must be resolved manually.
- `bbl_schema.py` enforces block-form on the YAML side; new writes must route through `normalize_file()`.

**Reciprocal sub-node case (wave 92 example):** when a card references both a parent layer node and a sub-node (e.g., `characters: [theros-pantheon, mogis]`), BOTH nodes' `appears_on:` lists should include the card. Mr. Nodeley's wave 92 mogis commission caught this — Skophos Warleader points at both, both should reciprocate.

---

## Protocol 3 — card → hub (one-way, by design)

**Where it lives:** card's `tags_hub:` block-form list. The hub doesn't carry a reciprocal `appears_on:` or membership list.

**Shape:**

Card frontmatter:
```yaml
tags_hub:
  - labor
  - rebellion
  - apparatus-of-extraction
```

Hub MD (`cards/_hubs/labor.md`):
```yaml
type: hub
name: Labor
brand_weight: foundational
# NO appears_on field. Hubs deliberately don't carry card membership lists.
```

**Direction:** one-way, card to hub. Hubs are conceptual lenses, not aggregation pages. Membership is implicit at query time (find all cards where `tags_hub` contains `labor`).

**Why this asymmetry exists:** the locked-in doctrine per `bbl-bundles-are-destructive-on-graph` memory. Cards sell. The graph mutates per bundle. Hubs are bundle-tier anchors that shouldn't churn with inventory. If we wired hubs to cards via `appears_on:`, every sold-out card would dirty the hub. The triple-thesis hubs (Labor, Rebellion, Stewardship per `_triple-thesis` meta-doc) stay card-edge-disconnected by design.

**When to use:** card carries the hub's thematic register at thesis-strength. Hub tags should be tags that would make compelling bundle titles ("Labor lair", "Rebellion lair"), not generic descriptors. Curated vocabulary per `bbl-hubs-hand-curated` memory.

**When NOT to use:**
- Mechanical or compositional descriptors → those go in `tags_filter` (Tier 2 tags, never become hubs).
- Color-magic / card-type filter tags → `tags_filter`, sourced from frontmatter `mana_cost` + `oracle_text` per the wave-92.5 spec amendment.
- Coined narrow compounds → over-narrow tags hurt downstream lair assembly (per `bbl-tag-broad-net` memory — vision pass should over-nominate broad tags, 8-12 per card).

**Tooling:**
- No bidirectional audit. Membership is implicit.
- `bbl_node_audit.py` does NOT flag below-threshold hubs because hand-curated foundational hubs have no `appears_on:` to count from (known gap — see triage entry).
- Bases dashboards (`cards/_views/`) query `tags_hub` matches at view time, not via hub-side data.

---

## Cross-protocol patterns

**Layer-node ↔ layer-node** (e.g., `_characters/caterpie-line.md` `## See also` block linking other `_characters/` nodes): these are real graph edges between peer nodes, not schema citations. Wikilinks are correct here. The audit treats them as layer-node references.

**Layer-node `related_hubs:`**: a layer node can carry a `related_hubs:` list pointing at hub slugs. This is a node-to-hub edge, complementary to the card→hub flow but at the layer-aggregate scale. Wave 92 caught some character nodes with `related_hubs:` in inline quoted-string form (`"[labor]"`) — should be block form per the YAML discipline.

**Symbol ↔ character cross-edges** (e.g., `_symbols/suspect.md` `related_characters: [agency]`): allowed when a symbol is mechanically tied to a character-faction. Reciprocal `related_symbols:` on the character side is optional.

---

## Wave 92.5 hygiene tax

All three protocols depend on the YAML staying parse-clean for Obsidian's property panel:

- **Block-form list fields** — `bbl_schema.normalize_block_form_lists()` converts inline JSON to block. Triggered automatically by `apply_vision.py` and `researchbot.update_card`.
- **Scalar quoting** — strings containing `: ` (embedded colon-space) get quoted by `bbl_schema.normalize_scalar_quoting()`. Without quoting, Obsidian's parser treats the value as a map and the whole property panel goes red.
- **Tags-last ordering** — `tags:` block must be the last frontmatter field. Top-level keys following a block-list get rendered as dashes (orphaned). `bbl_schema.normalize_tags_last()` enforces.

All three normalizations live in `bbl_schema.py` and are called by every BBL writer that touches frontmatter. If you write to a card MD via any other path, call `normalize_file(path)` after.

---

## Decision flow for new edges

```
Is the edge between two card MDs?
├─ Yes → Protocol 1 (## Connections bullets, manual mirror)
└─ No
   ├─ Is one side a layer node (character / symbol / artist)?
   │  ├─ Yes → Protocol 2 (frontmatter list, bidirectional, audit-policed)
   │  └─ No
   │     └─ Is one side a hub?
   │        ├─ Yes → Protocol 3 (tags_hub on card; no hub-side back-pointer)
   │        └─ No → You're inventing a fourth protocol. Stop. Ask.
```

---

## See also

- `bbl_node_audit.py` — the audit script that polices Protocol 2 bidirectional sync.
- `bbl_schema.py` — shared frontmatter normalization. All writers should route through `normalize_file()`.
- `docs/connections-standard.md` — Protocol 1 prose conventions and citation style.
- Memory: `bbl-wikilink-vs-backtick-discipline`, `bbl-bundles-are-destructive-on-graph`, `bbl-hubs-hand-curated`, `bbl-edgelord-node-rigor-audit`.
