"""
Convert inline YAML list form to block form in card frontmatter.

Obsidian's property panel renders block-form lists as chips, but inline-quoted
lists ([\"a\", \"b\"]) render as a single red string. Wave 92 fix.

Targets only frontmatter (between first two `---` markers). Only converts
known list-typed fields. Empty arrays [] are preserved as-is. Items with
embedded commas are handled by json-loading the whole `[...]` payload.
"""
import argparse
import json
import sys
from pathlib import Path

LIST_FIELDS = {
    "tags_hub", "tags_filter", "characters", "symbols", "bundles",
    "aliases", "appears_on", "social", "related_characters",
    "ip_resolution_for", "vision_uncertainty",
}


def convert(content: str) -> tuple[str, int]:
    """Return (new_content, num_fields_converted)."""
    lines = content.split("\n")
    out: list[str] = []
    in_fm = False
    fm_marker_count = 0
    converted = 0

    for line in lines:
        if line.strip() == "---":
            fm_marker_count += 1
            out.append(line)
            in_fm = (fm_marker_count == 1)
            continue

        if in_fm and ":" in line and "[" in line:
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]
            if ":" in stripped:
                field, _, rest = stripped.partition(":")
                rest = rest.strip()
                if (
                    field in LIST_FIELDS
                    and rest.startswith("[")
                    and rest.endswith("]")
                    and rest != "[]"
                ):
                    try:
                        items = json.loads(rest)
                    except json.JSONDecodeError:
                        # Fallback: simple split
                        inner = rest[1:-1].strip()
                        items = [v.strip().strip('"').strip("'") for v in inner.split(",")]
                        items = [v for v in items if v]
                    if isinstance(items, list) and items:
                        out.append(f"{indent}{field}:")
                        for item in items:
                            out.append(f"{indent}  - {item}")
                        converted += 1
                        continue
        out.append(line)
    return "\n".join(out), converted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="cards", help="Root dir to walk")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("paths", nargs="*", help="Specific files (overrides --root)")
    args = ap.parse_args()

    if args.paths:
        targets = [Path(p) for p in args.paths]
    else:
        root = Path(args.root)
        targets = sorted(root.rglob("*.md"))

    if args.limit:
        targets = targets[: args.limit]

    files_changed = 0
    fields_changed = 0
    for p in targets:
        try:
            content = p.read_text(encoding="utf-8")
        except Exception as e:
            print(f"SKIP {p}: {e}", file=sys.stderr)
            continue
        new, n = convert(content)
        if n > 0:
            files_changed += 1
            fields_changed += n
            if args.dry_run:
                print(f"WOULD CHANGE {p} ({n} fields)")
            else:
                p.write_text(new, encoding="utf-8")
                print(f"CHANGED {p} ({n} fields)")

    suffix = " (dry run)" if args.dry_run else ""
    print(f"\n{files_changed} files, {fields_changed} fields converted{suffix}")


if __name__ == "__main__":
    main()
