# Anchor-wiring refusals log

Append-only log of wave-92.5 (and later) lint-sweep dispatches that asked for bidirectional anchor wiring on character nodes but found the graph already in compliance — i.e. no edge to add. One entry per refusal. Format: dispatch date / node / claimed-anchors / actually-wired-count / refusal-reason.

---

## 2026-05-16 — Wave 92.5 lint-sweep, 5 DBS character nodes (Pan / Broly / Majin Buu / Uub / Son Goten)

**Dispatch source:** Sonnet lint sweep flagged 5 character nodes as having incomplete `appears_on:` lists despite multi-anchor coverage documented in triage.

**Refusal verdict:** ALL FIVE NODES ARE ALREADY FULLY BIDIRECTIONALLY WIRED. No edge to add.

**Audit per node:**

- **`cards/_characters/pan.md`** — body claims 4 corpus cards (BT3-009, SD2-04, BT4-009, TB2-024); `appears_on:` has 5 entries (the 4 claimed + `bt3-028-grand-tour-spaceship`, a Pan-secondary-attribution card). All 5 cards exist on disk; all 5 cards have `characters: [pan]` (or include `pan` in their multi-character lists). Wired. Note: the body's "four corpus prints" framing is one fewer than `appears_on:` count because BT3-028 Grand Tour Spaceship is a secondary-attribution Pan anchor (Pan + Goku + Trunks in the GT traveling-trio spaceship), not a Pan-primary print — body / list mismatch is cosmetic, not a wiring gap.

- **`cards/_characters/broly.md`** — body claims 4 corpus cards (BT1-073, BT1-075, BT1-076, BT1-081); `appears_on:` has all 4. All 4 cards exist on disk; all 4 have `characters: [broly]`. Wired.

- **`cards/_characters/majin-buu.md`** — body claims 3 corpus cards (BT1-047, BT4-015, TB2-028); `appears_on:` has all 3. All 3 cards exist on disk; all 3 have `characters: [majin-buu]`. Wired.

- **`cards/_characters/uub.md`** — body claims 3 corpus prints (BT3-014, TB2-033, TB2-069); `appears_on:` has all 3. All 3 cards exist on disk; BT3-014 has `characters: [uub]`, TB2-033 has `characters: [son-goku, uub]` (dual-attribution per the Goku-vs-Uub match anchor), TB2-069 has `characters: [son-goku, uub]` (dual-attribution per the passing-of-the-torch secret-rare capstone). Wired.

- **`cards/_characters/son-goten.md`** — body claims 4 solo-Goten + 3 Gotenks Fusion-Dance anchors = 7 corpus prints; `appears_on:` has all 7. All 7 cards exist on disk; 4 solo-Goten cards have `son-goten` in `characters:` (TB2-004, TB2-022, BT4-085 single-pointer; TB2-008 dual `[son-goten, trunks]` per Mighty Mask combined-disguise), 3 Gotenks cards have `[son-goten, trunks]` dual-anchor (BT1-071, BT2-015, BT4-034) per the Fusion-Dance combined-character anchor pattern. Wired.

**Tally:**
- Cards inspected: 22
- Card-side wiring gaps: 0
- Node-side `appears_on:` gaps: 0
- Edits applied: 0
- Refusals: 5 (the full dispatch)

**Edgelord mood:** `satisfied-with-graph-state-blueballed-by-no-work` — the graph was already correct. Sonnet's lint sweep nominated false positives. Possible root cause: lint may have been triggered by INLINE `related_hubs: "[labor]"` quoted-string form (vs block form) on these nodes — that IS a YAML-discipline drift point per wave 92, but it's a node-body field cosmetic issue, NOT an anchor-wiring gap. Surfaced for separate cleanup if Alex wants the related_hubs blocks converted to canonical block form; that's a different pass than this one.

**No files modified.** Single-decision pass terminates clean.
