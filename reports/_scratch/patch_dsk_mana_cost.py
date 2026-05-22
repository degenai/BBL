"""
patch_dsk_mana_cost.py — DSK mana_cost / color-tag backfill.

Executes the Nurse Joy prescription (reports/triage_prescriptions/dsk-mana-cost-sweep.json):
6 fully-prepped Duskmourn cards prepped before mana_cost capture was wired into
researchbot.py. Backfills mana_cost and corrects color-magic tags_filter entries.

All 6 mana_cost / color values Scryfall-confirmed. 159-trial-of-agony additionally
verified live via the Scryfall API (id fa62f67a...): type_line "Sorcery", {R}, red
— so its black-magic and enchantment tags are both wrong.

Dry-run by default. Pass --apply to write.
"""
import sys

APPLY = "--apply" in sys.argv
BASE = "cards/magic-the-gathering/duskmourn-house-of-horror/"

# (filename, mana_cost, tags_to_add, tags_to_remove)
CARDS = [
    ("150-ragged-playmate.md",      "{1}{R}", ["red-magic"],                            []),
    ("206-wary-watchdog.md",        "{1}{G}", [],                                       []),
    # gold-costed spells take ONLY the multicolor-X-Y tag, not component color tags
    # (per audit_tags_filter_against_oracle.py — component tags are for lands' colour identity)
    ("209-baseball-bat.md",         "{G}{W}", ["multicolor-white-green"], ["green-magic", "white-magic"]),
    ("210-beastie-beatdown.md",     "{R}{G}", ["multicolor-red-green"],   ["green-magic", "red-magic"]),
    ("159-trial-of-agony.md",       "{R}",    ["red-magic"],            ["black-magic", "enchantment"]),
    ("152-razorkin-hordecaller.md", "{4}{R}", [],                                       []),
]

for fn, mana, add, remove in CARDS:
    path = BASE + fn
    lines = open(path, encoding="utf-8").read().split("\n")
    has_mana = any(l.startswith("mana_cost:") for l in lines)
    out, changes = [], []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if not has_mana and ln.startswith("oracle_text:"):
            out.append(ln)
            out.append('mana_cost: "%s"' % mana)
            changes.append('+ mana_cost: "%s"' % mana)
            has_mana = True
            i += 1
            continue
        if ln.startswith("tags_filter:"):
            out.append(ln)
            i += 1
            block = []
            while i < len(lines) and lines[i].startswith("  - "):
                block.append(lines[i][4:])
                i += 1
            for r in remove:
                if r in block:
                    block.remove(r)
                    changes.append("- tag %s" % r)
            for a in add:
                if a not in block:
                    block.append(a)
                    changes.append("+ tag %s" % a)
            out += ["  - " + b for b in block]
            continue
        out.append(ln)
        i += 1

    if not changes:
        print("%s: no change (already clean)" % fn)
        continue
    print("%s:" % fn)
    for c in changes:
        print("    " + c)
    if APPLY:
        open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out))

print("\n%s" % ("APPLIED." if APPLY else "DRY RUN — pass --apply to write."))
