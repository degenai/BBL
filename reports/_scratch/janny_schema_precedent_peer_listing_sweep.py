#!/usr/bin/env python3
"""Janny sweep — mechanize the schema-precedent peer-listing pattern that
Dark Nodesley EX (snip-frenzy) hand-cut across waves 124-132.

Eight confirmed instances corpus-wide before DN-EX recommended mechanization
(2026-05-19): nicol-bolas, cell-saga-apparatus, dark-vassal-trio, son-goku,
zendikari-resistance, alola-kahunas, crane-school-cohort, alola-trial-captains.
Estimated yield: 80-150 wikilink conversions across ~33 unaudited character
nodes.

PATTERN — character-layer nodes carry "Modeled as a character-layer node,
not a hub" caveat bullets that enumerate sibling cohort/cycle nodes as
architectural-template precedent. Per `bbl-wikilink-vs-backtick-discipline`,
these peer-listing wikilinks should be backticks (schema citations) not
wikilinks (real-thematic edges).

GUARD — `PRESERVE_IF_RECURS_IN_SAME_FILE_AS_REAL_THEMATIC` (refined wave 132):
a wikilink at a schema-precedent line is PRESERVED if and only if the same
wikilink appears elsewhere in the same file at a non-schema-precedent line
(i.e., a real-thematic edge bullet). Recurrence at another schema-precedent
line does NOT confer real-thematic status.

USAGE:
  python reports/_scratch/janny_schema_precedent_peer_listing_sweep.py --dry-run
  python reports/_scratch/janny_schema_precedent_peer_listing_sweep.py
  python reports/_scratch/janny_schema_precedent_peer_listing_sweep.py --dry-run --scope _characters
"""
import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

# Schema-precedent phrases — if a line contains any of these, wikilinks on
# that line are SCHEMA-PRECEDENT-eligible (candidate for snipping).
# Sourced from janny_bolas_schema_precedent_sweep.py wave 124 + refinements.
SCHEMA_PHRASES = [
    "precedent",
    "Modeled as",
    "modeled as",
    "Following the",
    "following the",
    "single-character pattern",
    "structural-template",
    "structural template",
    "sibling solo-character-node",
    "single-character precedent",
    "multi-aspect single-character",
    "character-anchor membership",
    "structural precedent",
    "structural-precedent",
    "Like [[",
    "like [[",
    "single named individual",
    "named individual rather than a faction",
    "previously-flagged-and-now-commissioned",
    "anchor-attribution",
    "anchor count clears",
    "threshold rigor-bar",
    "load-bearing-name",
    "cross-universe structural-parallel",
    "designer-coordinated cycle entity",
    "designer-coordinated cohort",
    "same shape as",
    "same layer, same shape",
    "sibling designer-coordinated",
    "structurally adjacent",
    "structurally adjacent precedent",
    "modeled-as peer",
    "the Endriders precedent",
]

# Regex to extract all [[wikilinks]] from a line
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def safe_print(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("ascii", errors="replace").decode("ascii"))


def is_schema_line(line):
    return any(p in line for p in SCHEMA_PHRASES)


def find_real_thematic_recurrence(text, target_slug):
    """Return True if [[target_slug]] appears in the given text on at least
    one line that is NOT a schema-precedent line."""
    needle = f"[[{target_slug}]]"
    for line in text.splitlines():
        if needle not in line:
            continue
        if not is_schema_line(line):
            return True
    return False


def process_file(path, dry_run):
    rel = str(path.relative_to(REPO)).replace("\\", "/")
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "[[" not in text:
        return None

    lines = text.splitlines(keepends=True)
    snip_log = []   # list of (lineno, slug, "SNIP" or "KEEP", reason)
    new_lines = []
    file_changed = False

    for i, line in enumerate(lines, 1):
        if not is_schema_line(line):
            new_lines.append(line)
            continue
        slugs_on_line = WIKILINK_RE.findall(line)
        if not slugs_on_line:
            new_lines.append(line)
            continue

        # GUARD — peer-listings are ALWAYS multi-link enumerations by
        # definition. A schema-phrase line with only 1 unique wikilink
        # is almost certainly an English-sentence false-positive
        # ("Like [[iona]] before her" matches "Like [[" but is a single-
        # node real-thematic edge, not a peer-listing). Require ≥2 unique
        # wikilinks on the line before snipping.
        if len(set(slugs_on_line)) < 2:
            new_lines.append(line)
            continue

        # Process each wikilink on this schema-precedent line.
        # Convert if and only if no real-thematic recurrence anywhere in file.
        modified_line = line
        for slug in slugs_on_line:
            if find_real_thematic_recurrence(text, slug):
                snip_log.append((i, slug, "KEEP", "real-thematic recurrence in same file"))
                continue
            old = f"[[{slug}]]"
            new = f"`{slug}`"
            modified_line = modified_line.replace(old, new)
            snip_log.append((i, slug, "SNIP", "no real-thematic recurrence"))
            file_changed = True
        new_lines.append(modified_line)

    if file_changed and not dry_run:
        path.write_text("".join(new_lines), encoding="utf-8")

    if not snip_log:
        return None

    return (rel, snip_log, file_changed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--scope", default="_characters",
                    help="subdirectory under cards/ to walk (default: _characters)")
    args = ap.parse_args()

    target = REPO / "cards" / args.scope
    if not target.exists():
        safe_print(f"NO SUCH SCOPE: cards/{args.scope}")
        return

    files_touched = 0
    total_snipped = 0
    total_kept = 0
    by_file = []

    for path in sorted(target.rglob("*.md")):
        result = process_file(path, args.dry_run)
        if result is None:
            continue
        rel, snip_log, changed = result
        snips = sum(1 for _, _, action, _ in snip_log if action == "SNIP")
        keeps = sum(1 for _, _, action, _ in snip_log if action == "KEEP")
        if snips == 0 and keeps == 0:
            continue
        if changed or keeps > 0:
            by_file.append((rel, snips, keeps, snip_log))
            if changed:
                files_touched += 1
            total_snipped += snips
            total_kept += keeps

    mode = "DRY RUN" if args.dry_run else "APPLIED"
    safe_print(f"\n=== {mode} — scope: cards/{args.scope} ===")
    safe_print(f"files modified: {files_touched}")
    safe_print(f"wikilinks snipped (->backtick): {total_snipped}")
    safe_print(f"wikilinks kept (real-thematic recurrence): {total_kept}")
    safe_print("")

    for rel, snips, keeps, snip_log in by_file:
        prefix = "[DRY] " if args.dry_run else ""
        safe_print(f"{prefix}{rel}  ({snips} snip, {keeps} keep)")
        for lineno, slug, action, reason in snip_log:
            safe_print(f"   L{lineno} {action} [[{slug}]] — {reason}")


if __name__ == "__main__":
    main()
