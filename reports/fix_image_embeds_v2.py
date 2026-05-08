#!/usr/bin/env python3
"""Migration: rewrite image embeds to standard markdown with relative path,
and inject an IP-flag callout at the top of any card with a suspected_ip.

Why
---
The earlier fix (fix_image_embeds.py) used Obsidian wikilink format
`![[images/<game>/<set>/<slug>.png]]`, which only resolves when the vault root
is the project root. The actual vault is `cards/`, so wikilinks pointing at
`images/...` look outside the vault and Obsidian renders a "not found" stub.

This migration switches to standard markdown `![alt](relative-path)` with
`../../../images/...` traversal — works regardless of vault config and also
renders on GitHub. Idempotent on re-run.

It also injects an IP callout at the top of the Vision section for any card
whose frontmatter has `suspected_ip` populated. Per Alex: "ip should be more
human scannable."

Run from the project root:
    python reports/fix_image_embeds_v2.py            # apply
    python reports/fix_image_embeds_v2.py --dry-run  # preview
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
# Catches both new-style wikilinks (![[images/...]]) and possible bare-filename
# leftovers, plus already-correct standard markdown so re-runs are no-ops.
WIKILINK_EMBED_RE = re.compile(r"!\[\[[^\]]+\.(?:png|jpg|jpeg)\]\]")
STD_MD_EMBED_RE = re.compile(r"!\[[^\]]*\]\([^)]+\.(?:png|jpg|jpeg)\)")
# Existing IP-callout signature so we don't double-inject.
IP_CALLOUT_RE = re.compile(r"^>\s*\[!warning\]\s*Suspected IP:", re.M)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip()
    return out


def relative_path_from_card(card_md: Path, image_rel: str) -> str:
    """Compute the path from card_md's directory to the image, given image_rel
    as a project-relative path like `images/<game>/<set>/<slug>.png`."""
    image_abs = (ROOT / image_rel).resolve()
    rel = os.path.relpath(image_abs, card_md.parent)
    return rel.replace("\\", "/")


def fix_card(card_md: Path, dry_run: bool = False) -> dict:
    """Returns a dict describing what changed: {embed_rewritten, ip_injected, skipped}."""
    text = card_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    image_rel = (fm.get("reference_image") or "").strip()
    suspected_ip = fm.get("suspected_ip", "").strip().strip('"').strip("'")
    ip_conf = fm.get("ip_confidence", "").strip()
    ip_verified_raw = fm.get("ip_verified", "").strip().lower()

    result = {"embed_rewritten": False, "ip_injected": False, "skipped_no_image": False}

    if not image_rel:
        result["skipped_no_image"] = True
        return result

    # 1. Rewrite embed format. Find the existing embed and replace it with
    #    standard-markdown using a relative path.
    new_rel = relative_path_from_card(card_md, image_rel)
    correct_embed = f"![{card_md.stem}]({new_rel})"

    # Look for any embed pointing at this image. Prefer matching by basename
    # since the wikilink may use the project-relative path while the standard
    # markdown may use a different relative form across re-runs.
    img_basename = Path(image_rel).name

    def is_our_embed(match: str) -> bool:
        return img_basename in match

    new_text = text
    matched = False
    for pattern in (WIKILINK_EMBED_RE, STD_MD_EMBED_RE):
        for m in pattern.finditer(text):
            if is_our_embed(m.group()):
                new_text = new_text.replace(m.group(), correct_embed, 1)
                matched = True
                break
        if matched:
            break

    if matched and new_text != text:
        result["embed_rewritten"] = True
        text = new_text

    # 2. Inject IP callout if suspected_ip is present and we haven't already.
    if suspected_ip and ip_conf and ip_conf not in ("none", '""', ""):
        if not IP_CALLOUT_RE.search(text):
            verified_word = "verified" if ip_verified_raw == "true" else "unverified"
            callout = (
                f"> [!warning] Suspected IP: **{suspected_ip}** "
                f"(confidence: {ip_conf}, {verified_word})\n"
                "> Reviewer: confirm whether the depicted figure is canonically this character. "
                "If yes, set `ip_verified: true` in frontmatter. If no, clear `suspected_ip`.\n"
            )
            # Insert immediately after the "## Vision" heading.
            vision_re = re.compile(r"^(## Vision\s*\n)", re.M)
            if vision_re.search(text):
                text = vision_re.sub(r"\1\n" + callout + "\n", text, count=1)
                result["ip_injected"] = True

    if not dry_run and (result["embed_rewritten"] or result["ip_injected"]):
        card_md.write_text(text, encoding="utf-8")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="Show what would change without writing.")
    args = ap.parse_args()

    cards_dir = ROOT / "cards"
    if not cards_dir.exists():
        print(f"ERROR: cards/ not found at {cards_dir}", file=sys.stderr)
        return 1

    n_cards = 0
    n_embeds_fixed = 0
    n_ips_injected = 0
    n_skipped = 0

    for card_md in cards_dir.rglob("*.md"):
        n_cards += 1
        r = fix_card(card_md, dry_run=args.dry_run)
        if r["skipped_no_image"]:
            n_skipped += 1
            continue
        if r["embed_rewritten"]:
            n_embeds_fixed += 1
        if r["ip_injected"]:
            n_ips_injected += 1

    verb = "would fix" if args.dry_run else "fixed"
    print(f"Walked {n_cards} card MDs:")
    print(f"  {verb} embed: {n_embeds_fixed}")
    print(f"  {verb} IP callout injected: {n_ips_injected}")
    print(f"  skipped (no reference_image): {n_skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
