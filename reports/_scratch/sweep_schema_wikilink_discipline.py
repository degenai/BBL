"""
sweep_schema_wikilink_discipline.py

Backticks wikilinks that are schema/architectural-precedent citations, per
memory `bbl-wikilink-vs-backtick-discipline`. Targets two conventional
patterns where the wikilinks reliably mean "structural precedent," not
"real-thematic edge":

  1. The "Modeled as a [layer] node, not a hub or symbol. Like X, Y, Z..."
     paragraph used in cohort/symbol/hub nodes. Every wikilink in that
     paragraph is a precedent example for the modeling choice.

  2. Standalone See-also bullets like `- [[endriders]] — foundational
     precedent for hosting collective entities under _characters/`. Pure
     schema citation.

Frontmatter (`related_hubs:`, `related_characters:`, `appears_on:`) is
structured semantic wiring and is left alone. Real-thematic sibling-cohort
bullets in "Sibling and parent placement" sections are also left alone —
too mixed for an auto-sweep; spot-fix those individually.

Dry-run by default. Pass --apply to write.
"""
import os, re, glob, sys

APPLY = "--apply" in sys.argv
TARGET_DIRS = ["cards/_characters", "cards/_symbols", "cards/_hubs", "cards/_artists"]

SCHEMA_PHRASES = (
    "Modeled as a character-layer node",
    "Modeled as a symbol-layer node",
    "Modeled as a hub-layer node",
    "per the Endriders precedent",
    "per the endriders precedent",
)
ENDRIDERS_BULLET = re.compile(r"^\s*-\s+\[\[endriders\]\]\s+—\s+")

WIKILINK = re.compile(r"\[\[([^\]|\[]+)\]\]")

def backtick_all(text):
    return WIKILINK.sub(lambda m: "`" + m.group(1) + "`", text)

total_files = 0
for d in TARGET_DIRS:
    for f in sorted(glob.glob(os.path.join(d, "*.md"))):
        lines = open(f, encoding="utf-8").read().split("\n")
        changes = []
        new_lines = []
        for i, ln in enumerate(lines):
            if any(p in ln for p in SCHEMA_PHRASES) or ENDRIDERS_BULLET.match(ln):
                converted = backtick_all(ln)
                if converted != ln:
                    changes.append(i + 1)
                    new_lines.append(converted)
                    continue
            new_lines.append(ln)
        if changes:
            total_files += 1
            print("%s | lines: %s" % (f, changes))
            if APPLY:
                open(f, "w", encoding="utf-8", newline="\n").write("\n".join(new_lines))

print("\n%d files affected. %s" % (total_files, "APPLIED." if APPLY else "DRY RUN — pass --apply to write."))
