"""
bbl_bundle_promote - bundle lifecycle transition primitive.

Three states: proposed -> accepted -> assembled. Each transition moves the
bundle JSON between subdirs of `bundles/` and mutates the affected cards'
frontmatter according to the lifecycle doctrine in `bbl-bundler.md`.

Usage:
    python scripts/bbl_bundle_promote.py <slug> accepted
    python scripts/bbl_bundle_promote.py <slug> assembled

Transitions:

  proposed -> accepted:
    - Move bundles/proposed/<slug>.json -> bundles/accepted/<slug>.json
    - Set lifecycle.accepted_at = today
    - Update status field to "accepted"
    - For each card in bundle: stamp `accepted_bundle: <slug>` and set
      `held_for_lair = qty_in_bundle` on frontmatter
    - Normalize via bbl_schema after each card write

  accepted -> assembled:
    - Move bundles/accepted/<slug>.json -> bundles/assembled/<slug>.json
    - Set lifecycle.assembled_at = today
    - Update status field to "assembled"
    - For each card in bundle: subtract qty_in_bundle from `quantity`
    - If quantity hits 0, move card MD to `archive/<game>/<set>/<file-stem>.md`
      preserving all enrichment (per `bbl-archive-as-knowledge-store` memory)
    - Normalize via bbl_schema after each card write

Refusal cases:
    - Bundle not found in source state directory
    - For assembled: any card has quantity < qty_in_bundle
    - For assembled: any card MD not found (already archived externally, etc.)

Idempotent within a single state — re-running `accepted` on an already-accepted
bundle is a no-op (file already in target dir, fields already set). Cross-state
re-runs refuse with a clear message.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from bbl_schema import normalize_file  # noqa: E402

BUNDLES_DIR = ROOT / "bundles"
CARDS_DIR = ROOT / "cards"
ARCHIVE_DIR = ROOT / "archive"


def _read_frontmatter_block(text: str) -> tuple[int, int, str] | None:
    m = re.match(r"^(---\s*\n)(.*?)(\n---\s*\n)", text, re.DOTALL)
    if not m:
        return None
    return m.start(2), m.end(2), m.group(2)


def _set_scalar_field(text: str, field: str, value: str) -> str:
    """Set a top-level scalar frontmatter field, inserting before tags: if present."""
    pattern = rf"^{re.escape(field)}:.*$"
    if re.search(pattern, text, flags=re.MULTILINE):
        return re.sub(pattern, f"{field}: {value}", text, count=1, flags=re.MULTILINE)
    # Insert before tags: block if present
    fb = _read_frontmatter_block(text)
    if not fb:
        return text
    _, fm_end, fm_text = fb
    tags_m = re.search(r"^tags:\s*\n", fm_text, re.MULTILINE)
    new_line = f"{field}: {value}\n"
    if tags_m:
        insert_at_fm = tags_m.start()
        new_fm = fm_text[:insert_at_fm] + new_line + fm_text[insert_at_fm:]
    else:
        new_fm = fm_text.rstrip("\n") + "\n" + new_line.rstrip("\n")
    return f"---\n{new_fm}\n---\n" + text[fm_end + 5:]  # +5 for "\n---\n"


def _get_scalar_field(text: str, field: str) -> str:
    m = re.search(rf"^{re.escape(field)}:\s*(.*?)\s*$", text, re.MULTILINE)
    return m.group(1).strip(' "\'') if m else ""


def _card_md_path(card_md_path_key: str) -> Path:
    """card_md_path_key is `<game>/<set>/<file-stem>` — resolve to cards/<key>.md."""
    return CARDS_DIR / f"{card_md_path_key}.md"


def _stamp_accepted_state(card_path: Path, bundle_slug: str, qty_in_bundle: int) -> str:
    text = card_path.read_text(encoding="utf-8")
    text = _set_scalar_field(text, "accepted_bundle", bundle_slug)
    text = _set_scalar_field(text, "held_for_lair", str(qty_in_bundle))
    card_path.write_text(text, encoding="utf-8")
    normalize_file(card_path)
    return "stamped"


def _decrement_and_maybe_archive(card_path: Path, qty_in_bundle: int) -> tuple[str, int]:
    """Returns (action, new_quantity). action ∈ {decremented, archived}."""
    text = card_path.read_text(encoding="utf-8")
    current_qty = int(_get_scalar_field(text, "quantity") or "0")
    if current_qty < qty_in_bundle:
        raise ValueError(f"insufficient quantity ({current_qty} < {qty_in_bundle}) on {card_path.name}")
    new_qty = current_qty - qty_in_bundle
    text = _set_scalar_field(text, "quantity", str(new_qty))
    # Clear held_for_lair since the bundle is now assembled, not pending
    text = _set_scalar_field(text, "held_for_lair", "0")
    today = date.today().isoformat()
    if new_qty == 0:
        text = _set_scalar_field(text, "archived_on", today)
        rel = card_path.relative_to(CARDS_DIR)
        archive_target = ARCHIVE_DIR / rel
        archive_target.parent.mkdir(parents=True, exist_ok=True)
        archive_target.write_text(text, encoding="utf-8")
        normalize_file(archive_target)
        card_path.unlink()
        return ("archived", new_qty)
    else:
        card_path.write_text(text, encoding="utf-8")
        normalize_file(card_path)
        return ("decremented", new_qty)


def promote_to_accepted(slug: str) -> dict:
    src = BUNDLES_DIR / "proposed" / f"{slug}.json"
    dst = BUNDLES_DIR / "accepted" / f"{slug}.json"
    if not src.exists():
        if dst.exists():
            return {"outcome": "already-accepted", "bundle": str(dst)}
        raise FileNotFoundError(f"bundle not in proposed/: {src}")
    bundle = json.loads(src.read_text(encoding="utf-8"))
    today = date.today().isoformat()
    bundle["status"] = "accepted"
    bundle.setdefault("lifecycle", {})["accepted_at"] = today
    actions = []
    for card in bundle.get("cards", []):
        cp = _card_md_path(card["card_md_path"])
        if not cp.exists():
            raise FileNotFoundError(f"card md missing: {cp}")
        result = _stamp_accepted_state(cp, slug, card.get("qty_in_bundle", 1))
        actions.append((card["name"], result))
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    src.unlink()
    return {"outcome": "promoted-to-accepted", "bundle": str(dst), "cards_stamped": len(actions)}


def promote_to_assembled(slug: str) -> dict:
    src = BUNDLES_DIR / "accepted" / f"{slug}.json"
    dst = BUNDLES_DIR / "assembled" / f"{slug}.json"
    if not src.exists():
        if dst.exists():
            return {"outcome": "already-assembled", "bundle": str(dst)}
        raise FileNotFoundError(f"bundle not in accepted/: {src}")
    bundle = json.loads(src.read_text(encoding="utf-8"))
    today = date.today().isoformat()
    # Pre-flight: verify each card has sufficient quantity before any mutation
    for card in bundle.get("cards", []):
        cp = _card_md_path(card["card_md_path"])
        if not cp.exists():
            raise FileNotFoundError(f"card md missing: {cp}")
        text = cp.read_text(encoding="utf-8")
        current_qty = int(_get_scalar_field(text, "quantity") or "0")
        qty_in_bundle = card.get("qty_in_bundle", 1)
        if current_qty < qty_in_bundle:
            raise ValueError(f"insufficient quantity ({current_qty} < {qty_in_bundle}) on {cp.name}")
    # All cards pass — perform mutations
    bundle["status"] = "assembled"
    bundle.setdefault("lifecycle", {})["assembled_at"] = today
    actions = []
    for card in bundle.get("cards", []):
        cp = _card_md_path(card["card_md_path"])
        action, new_qty = _decrement_and_maybe_archive(cp, card.get("qty_in_bundle", 1))
        actions.append((card["name"], action, new_qty))
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    src.unlink()
    archived = sum(1 for _, a, _ in actions if a == "archived")
    decremented = sum(1 for _, a, _ in actions if a == "decremented")
    return {
        "outcome": "promoted-to-assembled",
        "bundle": str(dst),
        "cards_archived": archived,
        "cards_decremented": decremented,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug", help="Bundle slug (matches the .json filename without extension)")
    ap.add_argument("state", choices=["accepted", "assembled"],
                    help="Target state. Must follow proposed -> accepted -> assembled order.")
    args = ap.parse_args()

    try:
        if args.state == "accepted":
            result = promote_to_accepted(args.slug)
        else:
            result = promote_to_assembled(args.slug)
    except (FileNotFoundError, ValueError) as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 1
    for k, v in result.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
