## Michi insert assets

DA-aesthetic fan art for the wall-text slots of Michi-method binder pages on Discrete Lair storefront renders.

Per `docs/sketchbook.md` "Michi Method Binders for Discrete Lairs" + `bbl-bundler.md` Step 13 (Michi-method binder composition assessment).

### Aesthetic register

Intentionally myspace-era DeviantArt: hand-drawn, un-polished, fan-creative. Contra the AI-slop ban (`bbl-no-ai-slop-thumbnails`). What makes a binder page individual is the curated non-official material in the art slots — the card art crops are the baseline; the inserts are the personality.

### Directory layout

- `hub/<hub-slug>/` — assets keyed to foundational hubs (labor, rebellion, stewardship). Bundles tagged with a hub draw inserts from its directory.
- `anchor_tag/<tag-slug>/` — assets keyed to specific anchor tags (factory, drone, noble, etc). Finer-grained than hub-tier.
- `extended-art/` (future) — multi-slot horizontal/vertical art panels designed to span 2x1 or 1x2 or larger areas.

### Asset metadata

Each asset file should be accompanied by a sibling `.meta.json` describing:
- `source_url` — where the art came from (DeviantArt page, Tumblr post, Twitter/X post, Pinterest, fan blog, Etsy listing)
- `creator_handle` — original artist's online handle if known
- `permission_status` — `permission-confirmed` / `public-domain` / `unclear` / `for-internal-comp-only`
- `panel_dimensions_slots` — `[1, 1]` for single-slot, `[2, 1]` for horizontal-extended, `[1, 2]` for vertical-extended, `[3, 1]` for full-row, etc.
- `keyed_to` — array of hub/anchor_tag slugs this art grounds

### Population

Curator-sourced. The `bbl-bundler` Step 13 Michi assessment will flag `missing_insert_asset:` in its sidecar when a needed thesis grounder doesn't have a candidate in this directory — that's the signal to source one.
