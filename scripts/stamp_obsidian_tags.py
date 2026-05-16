"""
Stamp Obsidian-native `tags:` frontmatter onto cards and layer nodes so the
tag pane works as a vault-status dashboard.

Card tags:
  - card
  - <game-slug>             # mtg, pokemon, dbs, lorcana, weiss
  - vision-passed           # tags_hub populated
  - trivia-passed           # `## Trivia` section present
  - ip-verified             # ip_verified: true
  - ip-pending              # suspected_ip set AND ip_verified: false
  - manual-review           # needs_manual_review: true

Layer node tags (when frontmatter `type:` is hub|symbol|character|artist):
  - layer
  - <type>

Pure additive — never touches existing keys other than `tags`. Reads card
state from frontmatter + body markers. Idempotent.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

GAME_TAG_MAP = {
    "Magic: The Gathering": "mtg",
    "Magic": "mtg",
    "MTG": "mtg",
    "Pokemon": "pokemon",
    "Pokémon": "pokemon",
    "Dragon Ball Super": "dbs",
    "Dragon Ball Super Card Game": "dbs",
    "DBS": "dbs",
    "Lorcana": "lorcana",
    "Disney Lorcana": "lorcana",
    "Weiss Schwarz": "weiss",
    "WeissSchwarz": "weiss",
    "Force of Will": "fow",
    "Sorcery": "sorcery",
}


def fm_block(text: str) -> tuple[int, int, str] | None:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None
    return m.start(), m.end(), m.group(1)


def read_field(fm_text: str, field: str) -> str:
    m = re.search(rf"^{re.escape(field)}:\s*(.*?)\s*$", fm_text, re.MULTILINE)
    return m.group(1) if m else ""


def field_present_nonempty(fm_text: str, field: str) -> bool:
    inline = re.search(rf"^{re.escape(field)}:\s*\[([^\]]*)\]\s*$", fm_text, re.MULTILINE)
    if inline and inline.group(1).strip():
        return True
    block = re.search(rf"^{re.escape(field)}:\s*\n\s+-\s+\S+", fm_text, re.MULTILINE)
    return bool(block)


def derive_card_tags(fm_text: str, body: str) -> list[str]:
    tags = ["card"]
    game_raw = read_field(fm_text, "game")
    slug = GAME_TAG_MAP.get(game_raw)
    if slug:
        tags.append(slug)
    if field_present_nonempty(fm_text, "tags_hub"):
        tags.append("vision-passed")
    if "## Trivia" in body:
        tags.append("trivia-passed")
    if read_field(fm_text, "ip_verified").lower() == "true":
        tags.append("ip-verified")
    elif read_field(fm_text, "suspected_ip") and read_field(fm_text, "ip_verified").lower() == "false":
        tags.append("ip-pending")
    if read_field(fm_text, "needs_manual_review").lower() == "true":
        tags.append("manual-review")
    return tags


def derive_layer_tags(fm_text: str) -> list[str] | None:
    t = read_field(fm_text, "type")
    if t in {"hub", "symbol", "character", "artist"}:
        return ["layer", t]
    return None


def render_tags_block(tags: list[str]) -> str:
    if not tags:
        return ""
    lines = ["tags:"]
    for t in tags:
        lines.append(f"  - {t}")
    return "\n".join(lines)


def replace_or_insert_tags(text: str, fm_text: str, new_block: str, fm_end: int) -> str:
    # Remove existing `tags:` (block OR inline) inside frontmatter
    existing_block = re.search(r"^tags:\s*\n(?:\s+-\s+.*\n)+", fm_text, re.MULTILINE)
    existing_inline = re.search(r"^tags:\s*\[.*?\]\s*$", fm_text, re.MULTILINE)
    new_fm = fm_text
    if existing_block:
        new_fm = new_fm[: existing_block.start()] + new_fm[existing_block.end():]
    elif existing_inline:
        new_fm = new_fm[: existing_inline.start()] + new_fm[existing_inline.end():]
    # Append the new block at the end of frontmatter
    if not new_fm.endswith("\n"):
        new_fm += "\n"
    new_fm += new_block + "\n"
    # Reassemble document
    return f"---\n{new_fm}---\n" + text[fm_end:]


def process(path: Path) -> tuple[bool, list[str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return (False, [])
    fb = fm_block(text)
    if not fb:
        return (False, [])
    _, fm_end, fm_text = fb
    body = text[fm_end:]
    # Layer node?
    layer_tags = derive_layer_tags(fm_text)
    if layer_tags:
        new_tags = layer_tags
    else:
        # Skip non-cards (non-layer) — must have `game:` field
        if not read_field(fm_text, "game"):
            return (False, [])
        new_tags = derive_card_tags(fm_text, body)
    new_block = render_tags_block(new_tags)
    new_text = replace_or_insert_tags(text, fm_text, new_block, fm_end)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return (True, new_tags)
    return (False, new_tags)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="cards")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("paths", nargs="*")
    args = ap.parse_args()

    if args.paths:
        targets = [Path(p) for p in args.paths]
    else:
        targets = sorted(Path(args.root).rglob("*.md"))
    if args.limit:
        targets = targets[: args.limit]

    changed = 0
    for p in targets:
        if args.dry_run:
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            fb = fm_block(text)
            if not fb:
                continue
            _, fm_end, fm_text = fb
            body = text[fm_end:]
            tags = derive_layer_tags(fm_text) or (
                derive_card_tags(fm_text, body) if read_field(fm_text, "game") else None
            )
            if tags:
                print(f"WOULD STAMP {p}: {tags}")
                changed += 1
        else:
            ok, tags = process(p)
            if ok:
                changed += 1
                if changed <= 20 or changed % 200 == 0:
                    print(f"STAMPED {p}: {tags}")
    print(f"\n{changed} files stamped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
