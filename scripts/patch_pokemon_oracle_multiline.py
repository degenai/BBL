"""Patch Pokemon cards where multi-attack oracle_text was written across multiple
unquoted YAML lines. Pattern:

    oracle_text: "Attack 1 text..."
    Attack 2 text
    Attack 3 text
    image_width: 868   <- first recognizable key terminates the run

The fix collects the continuation lines and rewrites as a single quoted scalar
with literal `\\n` separators, matching what _flatten_for_frontmatter intended.

Root cause was a re.sub-replacement-escape bug in researchbot.py
update_frontmatter_field (fixed); this script repairs the 57 cards that
landed with the busted shape.
"""

from __future__ import annotations

import glob
import re
import sys
from pathlib import Path

_KEY_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_-]*:")
_ORACLE_RE = re.compile(r'^oracle_text: "(.*)"$')


def patch_text(text: str) -> tuple[str, bool]:
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    patched = False
    while i < len(lines):
        line = lines[i]
        m = _ORACLE_RE.match(line)
        if not m:
            out.append(line)
            i += 1
            continue
        # Look ahead: collect continuation lines until next key, blank, or `---`.
        head_value = m.group(1)
        continuations: list[str] = []
        j = i + 1
        while j < len(lines):
            nxt = lines[j]
            if nxt.strip() == "" or nxt.strip() == "---":
                break
            if _KEY_RE.match(nxt):
                break
            continuations.append(nxt.rstrip())
            j += 1
        if not continuations:
            out.append(line)
            i += 1
            continue
        # Merge into a single quoted scalar with literal `\n` separators.
        parts = [head_value] + continuations
        # Escape any embedded double-quotes in the continuation lines (head_value
        # was already quoted-safely so its embedded quotes are escape-escaped).
        escaped_parts = [p.replace("\\", "\\\\").replace('"', '\\"') if k > 0 else p
                          for k, p in enumerate(parts)]
        merged = "\\n".join(escaped_parts)
        out.append(f'oracle_text: "{merged}"')
        patched = True
        i = j  # skip the consumed continuation lines
    return "\n".join(out), patched


def main(argv: list[str]) -> int:
    write = "--write" in argv
    root = Path("cards/pokemon")
    paths = [Path(p) for p in glob.glob(str(root / "**/*.md"), recursive=True)]
    touched = 0
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        new, did = patch_text(text)
        if did:
            touched += 1
            if write:
                p.write_text(new, encoding="utf-8")
                print(f"  patched: {p}")
            else:
                print(f"  WOULD patch: {p}")
    mode = "WROTE" if write else "DRY RUN (use --write)"
    print(f"\n{mode}: {touched} cards patched")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
