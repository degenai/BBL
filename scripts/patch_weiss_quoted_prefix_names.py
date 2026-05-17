"""Patch Weiss Schwarz cards whose `name:` value starts with a `"<Modifier>"`
prefix followed by trailing text. YAML reads the leading `"` as opening a
quoted scalar, closes it at the next `"`, and chokes on the trailing chars.

    name: "104th Cadet Corps Class" Marco   <- INVALID YAML
    name: '"104th Cadet Corps Class" Marco' <- valid (single-quoted wraps)

Single-quoted YAML scalars don't interpret backslash escapes and accept
literal `"` characters without further escaping. The only inner escape needed
is `'` → `''` (we have none in these names; sweep verifies).
"""

from __future__ import annotations

import glob
import re
import sys
from pathlib import Path

_PATTERN = re.compile(r'^name: "([^"]*)" (.+)$', re.M)


def patch_text(text: str) -> tuple[str, bool]:
    def _sub(m: re.Match[str]) -> str:
        prefix, rest = m.group(1), m.group(2).rstrip()
        full = f'"{prefix}" {rest}'
        # Single-quote wrap. Escape any literal single quotes by doubling.
        escaped = full.replace("'", "''")
        return f"name: '{escaped}'"

    new = _PATTERN.sub(_sub, text)
    return new, new != text


def main(argv: list[str]) -> int:
    write = "--write" in argv
    touched = 0
    for f in glob.glob("cards/**/*.md", recursive=True):
        fn = f.replace("\\", "/")
        if "/_" in fn:
            continue
        try:
            text = Path(f).read_text(encoding="utf-8")
        except Exception:
            continue
        new, did = patch_text(text)
        if not did:
            continue
        touched += 1
        if write:
            Path(f).write_text(new, encoding="utf-8")
            print(f"  patched: {f}")
        else:
            print(f"  WOULD patch: {f}")
    mode = "WROTE" if write else "DRY RUN (use --write)"
    print(f"\n{mode}: {touched} cards patched")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
