#!/usr/bin/env python3
"""
_scratch_apply_p1_wmat — P1 (WMAT lag-ring) wire-up script.

Applies Edgelord wave-81 P1 proposals:
- Sets `characters:` frontmatter on 17 WMAT cards
- Appends to `appears_on:` on 6 existing character nodes
- Leaves 6 refusals + 5 deferred-node-pending cards unwired (per Edgelord receipts)
- crane-school-cohort.md was created separately (already has appears_on)

Deferred-node-pending cards (TB2-004, TB2-008, TB2-022, TB2-065/066/067):
  Stay unwired this pass. Re-queue when son-goten / wmat-tournament-announcer
  Nodeley nodes land.

Refusals (per Edgelord receipts):
  TB2-012 (Shin), TB2-028 (Mr. Buu), TB2-031 (Wild Tiger), TB2-032 (Otokosuki),
  TB2-037 (Chi-Chi), TB2-038 (Chi-Chi), TB2-062 (Ranfan).

Run from repo root: python _scratch_apply_p1_wmat.py
"""
from __future__ import annotations
import re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
WMAT = ROOT / "cards/dragon-ball-super/world-martial-arts-tournament"

# (card-stem, characters-list)
CARD_WIRES = [
    ("tb2-002-supreme-showdown-son-goku",                ["son-goku"]),
    ("tb2-011-heroic-duo-videl",                         ["hercule", "son-gohan"]),
    ("tb2-020-test-of-strength-son-goku",                ["son-goku"]),
    ("tb2-025-begrudging-respect-vegeta",                ["vegeta"]),
    ("tb2-026-awkward-situation-trunks",                 ["trunks"]),
    ("tb2-033-shocking-latent-ability",                  ["son-goku"]),
    ("tb2-034-son-goku-stopping-power-son-goku",         ["son-goku"]),
    ("tb2-035-fateful-reunion-son-goku",                 ["son-goku"]),
    ("tb2-043-tien-shinhan-trading-moves",               ["crane-school-cohort"]),
    ("tb2-044-best-buddy-chiaotzu",                      ["crane-school-cohort"]),
    ("tb2-046-trusting-relationship-kami",               ["namekian"]),
    ("tb2-048-mercenary-tao-trading-moves",              ["crane-school-cohort"]),
    ("tb2-049-feet-kamehameha",                          ["son-goku"]),
    ("tb2-051-unyielding-victory-son-goku",              ["son-goku"]),
    ("tb2-056-toughened-up-chiaotzu",                    ["crane-school-cohort"]),
    ("tb2-063-master-shen-martial-meister",              ["crane-school-cohort"]),
    ("tb2-064-i-m-the-world-champion",                   ["hercule"]),
    ("tb2-069-son-goku-uub-seeds-of-the-future",         ["son-goku"]),
]

# (node-md-stem, appears_on-entry-to-append)
NODE_APPENDS = [
    ("son-goku",   "dragon-ball-super/world-martial-arts-tournament/tb2-002-supreme-showdown-son-goku"),
    ("son-goku",   "dragon-ball-super/world-martial-arts-tournament/tb2-020-test-of-strength-son-goku"),
    ("son-goku",   "dragon-ball-super/world-martial-arts-tournament/tb2-033-shocking-latent-ability"),
    ("son-goku",   "dragon-ball-super/world-martial-arts-tournament/tb2-034-son-goku-stopping-power-son-goku"),
    ("son-goku",   "dragon-ball-super/world-martial-arts-tournament/tb2-035-fateful-reunion-son-goku"),
    ("son-goku",   "dragon-ball-super/world-martial-arts-tournament/tb2-049-feet-kamehameha"),
    ("son-goku",   "dragon-ball-super/world-martial-arts-tournament/tb2-051-unyielding-victory-son-goku"),
    ("son-goku",   "dragon-ball-super/world-martial-arts-tournament/tb2-069-son-goku-uub-seeds-of-the-future"),
    ("trunks",     "dragon-ball-super/world-martial-arts-tournament/tb2-026-awkward-situation-trunks"),
    ("vegeta",     "dragon-ball-super/world-martial-arts-tournament/tb2-025-begrudging-respect-vegeta"),
    ("hercule",    "dragon-ball-super/world-martial-arts-tournament/tb2-011-heroic-duo-videl"),
    ("hercule",    "dragon-ball-super/world-martial-arts-tournament/tb2-064-i-m-the-world-champion"),
    ("son-gohan",  "dragon-ball-super/world-martial-arts-tournament/tb2-011-heroic-duo-videl"),
    ("namekian",   "dragon-ball-super/world-martial-arts-tournament/tb2-046-trusting-relationship-kami"),
]


def set_characters(card_path: Path, chars: list[str]) -> bool:
    text = card_path.read_text(encoding="utf-8")
    chars_str = "[" + ", ".join(f'"{c}"' for c in chars) + "]"

    if re.search(r"^characters\s*:", text, re.MULTILINE):
        new_text, n = re.subn(
            r"^characters\s*:\s*.*$",
            f"characters: {chars_str}",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        if n == 0:
            return False
    else:
        # insert after bundles: line (canonical frontmatter slot)
        new_text, n = re.subn(
            r"^(bundles\s*:\s*.*)$",
            r"\1\ncharacters: " + chars_str,
            text,
            count=1,
            flags=re.MULTILINE,
        )
        if n == 0:
            # fallback: insert after held_for_lair
            new_text, n = re.subn(
                r"^(held_for_lair\s*:\s*.*)$",
                r"\1\ncharacters: " + chars_str,
                text,
                count=1,
                flags=re.MULTILINE,
            )
            if n == 0:
                print(f"  FAIL: cannot place characters field in {card_path.name}")
                return False
    if new_text == text:
        return False
    card_path.write_text(new_text, encoding="utf-8")
    return True


def append_appears_on(node_path: Path, entry: str) -> bool:
    text = node_path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False
    front, body = parts[1], parts[2]
    # find appears_on block (block-form expected)
    m = re.search(r"(^appears_on\s*:\s*\n((?:\s+-\s+.*\n)+))", front, re.MULTILINE)
    if not m:
        print(f"  WARN: no block-form appears_on in {node_path.name}; skip")
        return False
    block = m.group(2)
    # check duplicate
    if entry in block:
        return False
    new_line = f"  - {entry}\n"
    new_block = block + new_line
    new_front = front[:m.start(2)] + new_block + front[m.end(2):]
    new_text = parts[0] + "---" + new_front + "---" + body
    node_path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    changes = 0
    print("== Card wires ==")
    for stem, chars in CARD_WIRES:
        card = WMAT / f"{stem}.md"
        if not card.exists():
            print(f"  MISSING: {card.name}")
            continue
        if set_characters(card, chars):
            print(f"  WIRED {stem} -> {chars}")
            changes += 1
        else:
            print(f"  NOCHG {stem}")

    print()
    print("== Node appears_on appends ==")
    for node_stem, entry in NODE_APPENDS:
        node = ROOT / "cards/_characters" / f"{node_stem}.md"
        if not node.exists():
            print(f"  MISSING: {node.name}")
            continue
        if append_appears_on(node, entry):
            print(f"  APPENDED {node_stem} <- {entry.rsplit('/', 1)[-1]}")
            changes += 1
        else:
            print(f"  SKIP {node_stem} <- {entry.rsplit('/', 1)[-1]} (dup or no-block)")

    print()
    print(f"Total file changes: {changes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
