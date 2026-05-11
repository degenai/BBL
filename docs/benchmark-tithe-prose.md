# Bundle prose benchmark — Tithe, 2026-05-11

Comparison of the curator-authored why_it_fits (after reading the actual cached PNGs) versus a fresh general-purpose agent given an inline instruction + the cached PNG. Goal: measure whether a minimal inline prompt can replicate curator-quality prose, or whether human eyeball is still required.

The agent prompt was deliberately short. It contained: the bundle thesis, an instruction to Read the image and count figures correctly, copy-quality rules (no em dashes, no "X as Y", no cute jokes, no dev-meta), an instruction to surface flavor text verbatim from Scryfall if present.

The agent did NOT see: my benchmark, the bundle JSON, the other cards in the bundle, or any cross-card context. Each agent saw only its own card's image plus the instruction.

---

## 1. Wicked Guardian (ToE #109)

**Benchmark (mine):**
> A crowned noblewoman seated on a stone throne under elaborate dark arches. A servant on hands and knees in the foreground, scrubbing the floor. The frame holds them both in one shot. Flavor text: "Some are born to greatness. You were born to scrub greatness's floors." Mark Rosewater's Eldraine preview essay named this card as part of the set's Cinderella arc; the inequality is the design.

**Agent's:**
> A single noblewoman stands at the top of a short flight of stone steps in a vaulted interior, gown spilling down the risers in heavy folds of black and deep purple. She faces the viewer directly, hands lowered and composed, framed by an arched window and dim chandelier light behind her. The composition puts her on a literal pedestal above whoever is reading the card, and the flavor text closes the deal: "Some are born to greatness. You were born to scrub greatness's floors."

**Verdict:** **Benchmark wins.** Agent missed the servant entirely. The bundle is anchored on the noble-and-servant pair; cutting the servant cuts the thesis hook. Agent also says the noble "stands" when she's seated on the throne. Smooth prose, wrong content.

---

## 2. Charity Extractor (WAR #81)

**Benchmark (mine):**
> One armored knight in profile, ornate teal-and-gold plate, right hand held forward with a shallow collection plate. Cathedral or temple architecture behind. Flavor text: "War or no war, your donations are due, as always."

**Agent's:**
> Two armored figures in matching peaked, fluted Orzhov helms stand shoulder to shoulder, the front one holding out a small silver dish at waist height while the second looms behind in identical plate. The helmets fully cover their faces, reducing the pair to interchangeable uniformed hands collecting on behalf of something above them. "War or no war, your donations are due, as always."

**Verdict:** **Benchmark wins.** Agent invented a second figure — same mistake my original (pre-correction) prose made. This is the exact failure mode Alex caught. Inline prompt didn't save it.

---

## 3. Pitiless Pontiff (RNA #194)

**Benchmark (mine):**
> Vampire priest with dark hair, dagger raised in her right hand, the other hand reaching down toward a victim out of frame. Behind her head a gold filigree sunburst halo, the church's design language. Flavor text: "Pay in gold. Pay in blood. Pay with the servitude of your spirit kin. But pay you must."

**Agent's:**
> A single robed figure stands at center, arms spread wide in a vestment-like mantle, the hood casting their face in shadow while gold filigree glints across the chest and collar. The pose is liturgical, mid-pronouncement, and the bone-pale hand extended outward turns the gesture from blessing into demand. "Pay in gold. Pay in blood. Pay with the servitude of your spirit kin. But pay you must."

**Verdict:** **Benchmark wins.** Agent says the hood "casts the face in shadow" — actually the face is visible. Missed the dagger entirely. Missed the implied victim below frame. Reads as a generic robed-figure card.

---

## 4. Mortify (RNA #192)

**Benchmark (mine):**
> Red-haired figure in dark formal attire, light radiating outward from her chest in a stylized motion-blur composition. Flavor text: "Your debt is erased." Attributed to Hilgur, an Orzhov euthanist. The word euthanist tells you what the erasure costs.

**Agent's:**
> A pale woman in a high-collared Orzhov robe stands at the center of a cracked stone vault, arms spread, gold light fracturing the wall behind her into spreading fissures. Her expression is composed and clerical, the gesture deliberate, the destruction radiating outward from her open palms like an audit being delivered in person. "Your debt is erased." —Hilgur, Orzhov euthanist

**Verdict:** **Benchmark wins.** Agent missed the red hair (the exact confab my original prose had). Invented a "cracked stone vault" setting. Says the light comes from her palms when in the actual art it radiates from her chest. Pretty prose, wrong specifics.

---

## 5. Tithe Drinker (DGM #109)

**Benchmark (mine):**
> Vampire seated on an elaborate stone throne, two attendant figures flanking her at lower height. Heavy gold ornamentation on the throne. The card is named for the figure's job: collecting blood and coin on the Orzhov's behalf. MTG lore frames the Orzhov as the Church of Deals, part church and part bank.

**Agent's:**
> A single figure dominates the frame, a red-skinned vampire in a heavy gold-embroidered Orzhov collar, lifting a wide goblet to her painted lips. Behind her, two cloaked attendants hover in the candlelit dark of what looks like a chapel or counting-house, watching her drink. The collar and chalice do the same work as a ledger, and the second figures present are there to witness the levy being taken, not to stop it.

**Verdict:** **Mixed.** Agent caught the goblet/chalice (which I missed) and the two attendants (which I had). Missed the throne specifically. The "collar and chalice do the same work as a ledger" framing is solid. Probably the closest match in the test.

---

## 6. Lawmage's Binding (RNA #190)

**Benchmark (mine):**
> A horned red-skinned captive bound by white-and-blue chains of magic, body twisted in the wrappings. The casters aren't in the frame. The institution is the bindings themselves. First instant-speed Pacifism in MTG history per the set's design retrospective, written to outpace the defendant.

**Agent's:**
> A single robed figure stands head-on against a pale aureole, arms spread wide, wrists and torso wrapped in luminous red filigree that loops outward like a script being written onto the body. The hood is deep blue with gold trim, the face shadowed; the binding glyphs trail off the shoulders into the corners of the frame, so the spell reads less as combat magic and less as a leash issued by an office. No second figure appears, which is the point: the subject of the binding is offscreen, already restrained by the uniform alone.

**Verdict:** **Benchmark wins.** Agent confused who's in frame. Says "the subject of the binding is offscreen" when the captive IS the central figure. Gets the color of the bindings wrong (red vs white-and-blue). Smooth but inverted.

---

## 7. Lunarch Mantle (PLST #A25-24)

**Benchmark (mine):**
> A dark-armored figure with huge white angel wings spread behind them, sword pointed downward at the ground. The card is the Aura, not the figure. The wings are added to the soldier the church already had. Flavor speaker: Manfried Ulmach, Chief Inquisitor of the Lunarch Inquisition.

**Agent's:**
> A hooded, dark-armored figure stands frontal against a stone wall, head bowed beneath a white-feathered angelic wing-collar that frames the shoulders, both gauntleted hands gripping a longsword held point-down before the body. The blacked-out face and the downward blade read less like a blessing received than a sentence about to be executed, with the celestial vestment functioning as the warrant. "A boon from the angels should never be cast aside." —Manfried Ulmach, Chief Inquisitor

**Verdict:** **Agent wins.** Same essential details (dark armor, white wings, sword pointed down, Ulmach as speaker). Agent ALSO surfaced the full flavor text quote which I had not. Agent's "sentence about to be executed" framing is sharper than my "the wings are added" closer.

---

## 8. Reverent Hoplite (THB #33)

**Benchmark (mine):**
> A single mounted rider in armor, banner raised, framed against the stylized Theros night-sky constellation field. The card creates a token for every devotion-to-white permanent you control, so one rider on the card is the entire formation a buyer assembles around it. Flavor text: "Zeal is the sharpest blade, and piety the strongest shield."

**Agent's:**
> A single figure on foot, a white-robed acolyte holding a tall standard topped with a sun emblem, marching at the head of a column of spearmen whose shields and helms recede into the background. The standard-bearer's posture is ceremonial rather than martial, and the soldiers behind her move in lockstep because the icon they follow has authorized the violence. "Zeal is the sharpest blade, and piety the strongest shield."

**Verdict:** **Disputed — both descriptions might be wrong.** Curator (me) says mounted rider; agent says foot standard-bearer leading a column. Without a third look at the actual physical card neither read is conclusively right. Worth Alex's eyeball.

---

## 9. Secure the Scene (M21 #35)

**Benchmark (mine):**
> One armored officer with a vertical staff raised, blue magical glow radiating around the staff. Flavor text by Judith the Scourge Diva, a Rakdos character calling out an Azorius arrest: "You know it's a great show when the Azorius arrest the props, too!" Two copies of this one in the bundle; the institution rarely arrives alone.

**Agent's:**
> A bearded, balding figure in blue-and-white robes stands centered, gripping a tall staff topped with an ornate finial; both hands clasp the shaft and his eyes are closed in concentration. The robes are formal, layered, and trimmed with metal fittings, the dress of an official rather than a soldier. A single uniformed authority figure, alone in frame, performing the paperwork side of removal.
>
> "You know it's a great show when the Azorius arrest the props, too!"
> —Judith, the Scourge Diva

**Verdict:** **Mixed.** Agent has more specific physical detail (bearded, balding, eyes closed, formal robes vs my "armored officer" — agent is probably more accurate on that). Agent missed the multi-copy 2× context (which the bundle JSON has but the agent didn't see). Agent's "paperwork side of removal" is a nice line.

---

## Summary scorecard

| Card | Winner | Why |
| --- | --- | --- |
| Wicked Guardian | Benchmark | Agent missed the servant |
| Charity Extractor | Benchmark | Agent invented a second knight |
| Pitiless Pontiff | Benchmark | Agent missed the dagger and the victim |
| Mortify | Benchmark | Agent missed the red hair (same confab my draft had) |
| Tithe Drinker | Roughly tied | Agent caught the goblet I missed; I caught the throne |
| Lawmage's Binding | Benchmark | Agent inverted which figure is in frame |
| Lunarch Mantle | Agent | Same content, plus the flavor text I missed |
| Reverent Hoplite | Disputed | Mounted-vs-foot disagreement; needs physical card check |
| Secure the Scene | Mixed | Agent better on figure detail; missed multi-copy context |

**Topline finding:** the minimal inline prompt produced curator-comparable prose on 2-3 of 9 cards. On the other 6-7, the agent reproduced the same vision-pass failure modes my original prose had — figure count errors, missed secondary figures, invented props, missed color details. The thesis-grounding language tended to come out smoother in the agent's prose (better single-sentence framing) but on noisier ground truth.

**What this means for the future bbl-bundler agent:**

- The inline-prompt approach is not sufficient on its own. Vision passes (whether by bbl-researcher or an inline-prompt one-off) have consistent failure modes that no amount of "look at the actual image" instruction reliably catches.
- Two paths forward:
  - **(A)** Add a verification step. After the agent writes the why_it_fits, a second agent (or the same agent in a second pass) verifies the description against the image and lists any disagreements. Curator resolves.
  - **(B)** Inline-prompt produces a draft; curator eyeballs and edits before publish. The agent is a first-pass-helper, not a publisher. This is the realistic expectation for buyer-facing copy.
- The flavor-text fetch behavior worked well on most cards (Lunarch Mantle agent even surfaced flavor text I had missed). That part of the inline prompt is solid.
- The "no X as Y" / "no em dash" / "no cute meta-joke" rules mostly held but the agents adapted around them ("X functioning as Y", "X like Y"). The forbidden-pattern list could be more comprehensive but at some point you're playing whack-a-mole.

**Recommended next step:** treat the inline-prompt agent as a draft generator. Curator does the eyeball pass against actual images before publish. The bundle-creation flow should explicitly include a "compare draft to image" QA step.
