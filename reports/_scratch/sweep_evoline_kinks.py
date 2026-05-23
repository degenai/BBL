"""
sweep_evoline_kinks.py

Apply Alex's wave-174 rule: evolution-line cohort nodes wikilink each other
ONLY when canonically-mechanically entangled (Cloyster's Shellder biting Slowpoke's
tail). Same-node-shape similarity ("sibling Pokemon evolution-line cohort, different
region, different axis") is schema-precedent, not real-thematic — should be backtick
per `bbl-wikilink-vs-backtick-discipline`.

Conservative heuristic: backtick body wikilinks in any See-also bullet whose prose
contains a divergence-marker phrase. Leaves bullets that describe shared specific
theme (folklore source, character relation, etc.) alone.

No canonical-entanglement line pairs exist in the current corpus (no cloyster-line,
slowpoke-line, eevee-line, hitmon-line nodes yet), so the rule says: backtick all
flagged bullets, no exceptions.

Frontmatter `related_characters:` is NOT modified — those are structured semantic
pointers that need curatorial judgment per entry; this script flags them for review.

Dry-run by default. --apply to write.
"""
import os, re, glob, sys

APPLY = "--apply" in sys.argv
DIVERGENCE_MARKERS = (
    "different region",
    "different cohort axis",
    "different cohort structure",
    "different cohort type",
    "different node-shape",
    "different node shape",
    "structural precedent",
    "structurally adjacent on the",
    "structurally distinct",
    "different generations",
    "sibling Pokemon designer-coordinated",
    "sibling Pokemon evolutionary-line",
    "designer-coordinated evolutionary-line cohort",
)

WIKILINK = re.compile(r"\[\[([^\]|\[]+)\]\]")

def backtick_all(text):
    return WIKILINK.sub(lambda m: "`" + m.group(1) + "`", text)

total_files = 0
related_chars_review = []

for f in sorted(glob.glob("cards/_characters/*-line.md")):
    raw = open(f, encoding="utf-8").read()
    lines = raw.split("\n")

    # Locate See-also section
    in_see_also = False
    changes = []
    new_lines = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("## "):
            in_see_also = s.lower().startswith("## see also") or "sibling and parent placement" in s.lower()
            new_lines.append(ln)
            continue
        if in_see_also and s.startswith("- ") and any(m in ln for m in DIVERGENCE_MARKERS):
            converted = backtick_all(ln)
            if converted != ln:
                changes.append(s[:90])
                new_lines.append(converted)
                continue
        new_lines.append(ln)

    # Report related_characters cross-line entries for review
    m = re.search(r"^related_characters:\s*\n((?:\s*-\s+\S+\s*\n)+)", raw, re.M)
    if m:
        block = m.group(1)
        cross_lines = [l.strip()[2:].strip() for l in block.splitlines()
                       if re.match(r"^\s*-\s+[\w-]+-line\s*$", l)]
        if cross_lines:
            related_chars_review.append((f, cross_lines))

    if changes:
        total_files += 1
        print(f, "|", len(changes), "bullets backticked:")
        for c in changes:
            print("    " + c + ("..." if len(c) >= 90 else ""))
        if APPLY:
            open(f, "w", encoding="utf-8", newline="\n").write("\n".join(new_lines))

print("\n%d files affected. %s\n" % (total_files, "APPLIED." if APPLY else "DRY RUN — pass --apply to write."))

if related_chars_review:
    print("=== related_characters frontmatter cross-line pointers (NOT touched, review-only) ===")
    for f, xs in related_chars_review:
        print("%s : %s" % (f, ", ".join(xs)))
