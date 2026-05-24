#!/usr/bin/env python3
"""
researchbot — Prep card-node MDs for the bbl-researcher subagent (vision pipeline).

For each card-node lacking enrichment:
  1. Fetch a canonical reference image from the per-game source API
     (Scryfall for MTG, PokemonTCG.io for Pokemon, LorcanaJSON for Lorcana,
     Bushiroad search for Weiss, Bandai/dbzexchange for DBSCG).
  2. Cache the image locally + stamp the canonical card data into frontmatter:
     reference_image, reference_image_source_url, artist, collector_number,
     flavor_text, oracle_text, mana_cost (MTG only), image dimensions.
  3. Leave tags_hub empty as the ready-for-vision signal that the
     .claude/agents/bbl-researcher.md subagent reads via `python bbl_queue.py`.

Processes in quantity-DESC order so high-impact cards get enriched first.
Skips cards already enriched (tags_hub non-empty), unless --force.

History: Plan A was DeepSeek hosted vision (chat-completion endpoint with a
structured prompt). That code was removed wave 92.5 — vision now runs through
the subagent. --list-models is preserved as the watch signal for hosted-vision
GA per memory bbl-deepseek-vision-watch.

Usage:
    python researchbot.py --prepare-only [--cards-dir cards] [--limit N]
                          [--game GAME] [--dry-run] [--force]
    python researchbot.py --list-models     # watch signal probe
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

# Force UTF-8 on stdout/stderr. Without this, printing artist names with
# accented characters (Volkan Baǵa, Manuel Castañón, Sławomir Maniak, et al)
# crashes the prep loop on Windows because Python defaults to cp1252 for
# console output. Caught twice 2026-05-11 — first in backfill_artist.py
# (already fixed there), then again here when the MTG prep hit Diego Gisbert's
# accented name. Applied at module init so every subcommand benefits.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# --- Configuration ---

DEFAULT_CARDS_DIR = "cards"
# Image cache lives INSIDE cards/ so it's visible to the Obsidian vault (which is
# rooted at cards/). PNG files aren't graphed by Obsidian (only .md files become
# nodes), so this doesn't pollute the card graph. The underscore prefix sorts the
# folder visually distinct from card-game directories.
DEFAULT_IMAGES_DIR = "cards/_images"
DEFAULT_LIMIT = None  # unlimited by default — API rate-limit is the natural throttle.
                      # Pass --limit N explicitly when you want to chunk a run.
DEEPSEEK_BASE = "https://api.deepseek.com"
DEEPSEEK_MODELS_ENDPOINT = f"{DEEPSEEK_BASE}/models"
# Vision chat-completion endpoint + default model removed wave 92.5 along with
# the deepseek_vision_call function. Vision now routes through the Claude Code
# subagent at .claude/agents/bbl-researcher.md. --list-models is preserved as
# the watch signal for hosted-vision GA per memory bbl-deepseek-vision-watch.
SCRYFALL_API = "https://api.scryfall.com"
# Sleep between Scryfall calls. Default 0.1s honors their 50–100ms recommendation.
# Bump to 1.0+ for very long sweeps or when running shortly after a 429 burst.
# Set via --scryfall-sleep CLI flag.
SCRYFALL_SLEEP = 0.1
POKEMONTCG_API = "https://api.pokemontcg.io/v2"
BULBAPEDIA_API = "https://bulbapedia.bulbagarden.net/w/api.php"
# Bulbapedia upgrade is only worth taking when the image is meaningfully larger
# than what PokemonTCG.io serves (734×1024). Below this width threshold we
# stick with PokemonTCG.io to avoid older-set lossy uploads (e.g. Base Set
# Charizard on Bulbapedia is only 350×495 vs 734×1024 on PokemonTCG.io).
BULBAPEDIA_MIN_WIDTH = 800

USER_AGENT = "BBL-researchbot/0.1 (alex.adamczyk@gmail.com)"

# Bandai DBSCG image CDN. Single-URL formula keyed on collector_number,
# verified 100% coverage of the legacy DBSCG corpus (BT/TB/SD/P + EDBS reprints).
# Images are 260x363 thumbnails — below the Pokemon baseline but acceptable for
# vision tag-extraction. Investigation: reports/dbs_vision_strategy_findings.md.
DBS_IMAGE_BASE = "https://www.dbs-cardgame.com/images/cardlist/cardimg"
DBS_REFERER = "https://www.dbs-cardgame.com/us-en/cardlist/"
# dbzexchange Shopify store has high-res scans (867x1210) for ~30% of DBSCG
# corpus. Used as primary; Bandai is fallback. Discovery via search-suggest
# JSON API + featured_image width metadata filter.
DBZEXCHANGE_SUGGEST = "https://dbzexchange.com/search/suggest.json"

# Bushiroad EN Weiss Schwarz cardlist. 400x558 PNGs, ~100% coverage of the
# corpus's 6 active anime sets. Two-step discovery: search endpoint returns
# HTML with <img src="..."> for the matched card. Strip rarity suffix from
# collector number before searching. Investigation: reports/weiss_schwarz_vision_strategy_findings.md.
WEISS_SEARCH_BASE = "https://en.ws-tcg.com/cardlist/searchresults/"
WEISS_HOST = "https://en.ws-tcg.com"

# FFTCG (Final Fantasy TCG) image source. Marcie Discord bot's public GCS
# mirror hosts the cards keyed on `<code>_eg.jpg` (e.g. `3-122C_eg.jpg`).
# Tried Square Enix's sewest CDN first per the FFTrice precedent — it 404s
# corpus-wide as of 2026-05-17, the path/structure has moved since FFTrice's
# code was written. Marcie's mirror is community-maintained but covers the
# entire Opus run reliably. Native ~720x1024 JPEG, no art crop available.
# Code is taken verbatim from Collectr `collector_number` field.
FFTCG_IMAGE_BASE = "https://storage.googleapis.com/marcieapi-images"

# Image-quality buckets. Stamped at prep time so downstream queries can grep
# `image_quality: low` to find candidates for source-upgrade later.
#   high: ≥700px width (Scryfall/PokemonTCG.io baseline, dbzexchange hi-res hits)
#   med:  400-699px (Bushiroad EN Weiss 400x558, mid-tier scans)
#   low:  <400px (Bandai DBS 260x363, dbzexchange low-res mirrors, smaller Pokemon)
IMAGE_QUALITY_HIGH_MIN = 700
IMAGE_QUALITY_MED_MIN = 400

# Map Collectr game name → image-source strategy
GAME_STRATEGY = {
    "Magic: The Gathering": "scryfall",
    "Pokemon": "pokemontcg",
    "Dragon Ball Super": "dbs",
    "Weiss Schwarz": "weiss",
    "Lorcana": "lorcana",
    "Disney Lorcana": "lorcana",
    "Final Fantasy TCG": "fftcg",
    # Other games fall through with a warning until we wire APIs for them.
}

LORCANA_ALLCARDS_URL = "https://lorcanajson.org/files/current/en/allCards.json"
LORCANA_CACHE = Path("reports/lorcana_allcards.json")
_LORCANA_INDEX: dict | None = None  # lazy-loaded


# --- .env loading (no python-dotenv dependency) ---

def load_env(path: Path = Path(".env.local")) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# --- HTTP helpers (stdlib urllib) ---

def http_get_json(url: str, timeout: float = 20.0,
                  retries: int = 3, backoff_s: float = 1.5) -> dict | None:
    """GET a URL and parse JSON. Distinguishes:
      - 404: returns the parsed body (Scryfall returns a JSON error object on miss
        which the caller already handles via `data.get('status')`).
      - 429 / 5xx / network errors: retries with exponential backoff (default 3 attempts).
      - Other 4xx: gives up after first failure (those are real client errors and
        retrying won't help).
    Returns None only if every retry exhausted.

    Without retry-on-429, sustained Scryfall sweeps over a few hundred cards can
    silently flag cards as `needs_manual_review` because of transient throttling
    rather than real lookup failures. That's the bug this fixes.
    """
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            # 404: Scryfall returns a JSON error body — surface it to the caller, who
            # already does `data.get("status")` checks to detect the miss.
            if e.code == 404:
                try:
                    return json.loads(e.read().decode("utf-8"))
                except Exception:
                    return None
            # 429 / 5xx: transient, worth retrying.
            if e.code == 429 or e.code >= 500:
                last_err = e
                wait = backoff_s * (2 ** attempt)
                print(f"  [warn] GET {url} -> HTTP {e.code}, retrying in {wait:.1f}s "
                      f"(attempt {attempt + 1}/{retries})", file=sys.stderr)
                time.sleep(wait)
                continue
            # Other 4xx: not transient, give up.
            print(f"  [warn] GET {url} failed: HTTP {e.code} (no retry)", file=sys.stderr)
            return None
        except Exception as e:
            last_err = e
            wait = backoff_s * (2 ** attempt)
            print(f"  [warn] GET {url} -> {e}, retrying in {wait:.1f}s "
                  f"(attempt {attempt + 1}/{retries})", file=sys.stderr)
            time.sleep(wait)
    print(f"  [warn] GET {url} failed after {retries} attempts: {last_err}", file=sys.stderr)
    return None


def http_post_json(url: str, payload: dict, headers: dict, timeout: float = 60.0) -> dict | None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  [error] POST {url} {e.code}: {body[:400]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  [error] POST {url} failed: {e}", file=sys.stderr)
        return None


# --- Frontmatter I/O (parses the same minimal format csv2mdbot uses) ---

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        # Strip matching surrounding quotes (csv2mdbot's yaml_safe_scalar wraps any
        # value containing `: ` etc. in double quotes; comparisons fail without strip).
        if len(v) >= 2 and ((v[0] == '"' and v[-1] == '"') or (v[0] == "'" and v[-1] == "'")):
            v = v[1:-1]
        out[k.strip()] = v
    return out


def update_frontmatter_field(text: str, field: str, value: str) -> str:
    """Replace existing field or insert before closing `---`."""
    pattern = rf"^{re.escape(field)}:.*$"
    # Use callable replacement: re.sub interprets backslash escapes in a string
    # replacement (so a value containing literal `\n` from _flatten_for_frontmatter
    # would get expanded to a real newline and break YAML). A callable bypasses
    # that interpretation.
    replacement = f"{field}: {value}"
    if re.search(pattern, text, flags=re.MULTILINE):
        return re.sub(pattern, lambda _m: replacement, text, count=1, flags=re.MULTILINE)
    m = FRONTMATTER_RE.match(text)
    if not m:
        return text
    fm_end = m.end(1)
    return text[:fm_end] + f"\n{field}: {value}" + text[fm_end:]


def append_or_replace_section(text: str, heading: str, content: str) -> str:
    """Replace a `## heading ... (until next ## or EOF)` section, or append it."""
    pattern = rf"^## {re.escape(heading)}\s*\n.*?(?=^## |\Z)"
    new_section = f"## {heading}\n\n{content.strip()}\n\n"
    if re.search(pattern, text, flags=re.MULTILINE | re.DOTALL):
        return re.sub(pattern, new_section, text, count=1, flags=re.MULTILINE | re.DOTALL)
    if not text.endswith("\n"):
        text += "\n"
    return text + "\n" + new_section


# --- Image lookup ---

SCRYFALL_SET_CACHE = Path("reports") / "scryfall_sets.json"


def fetch_scryfall_set_map() -> dict:
    """Map: lowercased set name -> set code. Cached locally so we hit Scryfall once."""
    if SCRYFALL_SET_CACHE.exists():
        try:
            return json.loads(SCRYFALL_SET_CACHE.read_text(encoding="utf-8"))
        except Exception:
            pass
    data = http_get_json(f"{SCRYFALL_API}/sets")
    time.sleep(SCRYFALL_SLEEP)
    if not data:
        return {}
    mapping: dict[str, str] = {}
    for s in data.get("data", []):
        name = (s.get("name") or "").lower().strip()
        code = s.get("code") or ""
        if name and code:
            mapping[name] = code
    SCRYFALL_SET_CACHE.parent.mkdir(parents=True, exist_ok=True)
    SCRYFALL_SET_CACHE.write_text(json.dumps(mapping), encoding="utf-8")
    return mapping


# Hand-curated aliases for Collectr-style set names that don't normalize cleanly.
# Map: lowercased Collectr name -> Scryfall set code.
# Add entries here whenever a set name keeps showing up in the manual-review queue.
SET_NAME_ALIASES = {
    "mystery booster cards": "mb1",
    "mystery booster: retail exclusives": "fmb1",
    "classic: sixth edition": "6ed",
    "art series: zendikar rising": "azns",
    # Promo Pack: X — Scryfall stores these as ppXXX where XXX is the parent code
    "promo pack: throne of eldraine": "ppeld",
    "promo pack: zendikar rising": "ppznr",
    # Commander: X variants
    "commander: streets of new capenna": "ncc",
    "commander: zendikar rising": "znc",
}

# Hand-curated aliases for Collectr-style Pokémon set names that differ from
# PokemonTCG.io's canonical `set.name` strings. Collectr appends " Base Set"
# to first-in-generation sets; PokemonTCG.io uses the plain short name.
# Add entries here when a Pokémon set keeps showing up in the manual-review
# queue from set-name mismatch. Wave 96.9 Nurse Joy fix.
# All entries below probe-verified against PokemonTCG.io /v2/sets endpoint.
# Note: "Blister Exclusives", "Trading Card Game Classic", "SM Trainer Kit:
# Lycanroc & Alolan Raichu", "Trick or Trade BOOster Bundle" — these are NOT
# in PokemonTCG.io's set index (retail packaging, Japanese-only, or otherwise
# absent). They require curator-side resolution per card. No alias possible.
POKEMON_SET_NAME_ALIASES = {
    # Generation 8 (Sword & Shield era)
    "sword & shield base set": "Sword & Shield",
    # Generation 7 (Sun & Moon era)
    "sun & moon base set": "Sun & Moon",
    # Generation 6 (XY era)
    "xy base set": "XY",
    # Generation 1 — original is "Base" (no "Set" suffix in PokemonTCG.io)
    "base set (unlimited)": "Base",
    # Promotional / event sets
    "mcdonald's promos 2022": "McDonald's Collection 2022",
    "mcdonald's promos 2021": "McDonald's Collection 2021",
}

# Pattern: trailing " (XXX)" parenthetical — Collectr writes "Magic 2014 (M14)" while
# Scryfall's set_map key is just "Magic 2014". Strip and retry.
_SET_PAREN_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")


def scryfall_set_code(collectr_set: str, set_map: dict) -> str | None:
    """Resolve a Collectr-style set name to a Scryfall set code, with a few variant fallbacks.

    Tries, in order:
      1. Hand-curated SET_NAME_ALIASES table (handles Mystery Booster, Promo Pack, etc.)
      2. Direct lookup in the cached set_map
      3. With "set " prefix stripped
      4. With "base set " prefix stripped
      5. With trailing "(XXX)" parenthetical stripped (handles Magic 2014 (M14))
    """
    if not collectr_set:
        return None
    name = collectr_set.lower().strip()
    if name in SET_NAME_ALIASES:
        return SET_NAME_ALIASES[name]
    candidates = [
        name,
        name.replace("set ", ""),
        name.replace("base set", "").strip(),
        _SET_PAREN_SUFFIX_RE.sub("", name).strip(),
    ]
    for c in candidates:
        c = c.strip()
        if c and c in set_map:
            return set_map[c]
    return None


# Pattern: trailing " (123)" — collector number embedded in card name itself
# (e.g. "Island (254)"). Some Collectr exports include the number; Scryfall's
# fuzzy/named lookup chokes on the parenthetical. Strip it before querying.
_NAME_PAREN_NUM_RE = re.compile(r"\s*\(\d+\)\s*$")


def normalize_card_name_for_lookup(name: str) -> str:
    """Strip Collectr quirks from a card name before querying Scryfall."""
    return _NAME_PAREN_NUM_RE.sub("", name).strip()


def _extract_image(data: dict) -> str | None:
    """Pick the highest-resolution Scryfall image. Order: png > large > normal."""
    images = data.get("image_uris") or {}
    if not images and "card_faces" in data:
        faces = data.get("card_faces", [])
        if faces and faces[0].get("image_uris"):
            images = faces[0]["image_uris"]
    return images.get("png") or images.get("large") or images.get("normal")


def _extract_art_crop(data: dict) -> str | None:
    """Pick the Scryfall art_crop URL — the painting alone, no card frame.
    This is what the bbl-researcher vision pass should read; the framed card
    image is kept for human/Obsidian scannability and storefront rendering."""
    images = data.get("image_uris") or {}
    if not images and "card_faces" in data:
        faces = data.get("card_faces", [])
        if faces and faces[0].get("image_uris"):
            images = faces[0]["image_uris"]
    return images.get("art_crop")


def _flatten_for_frontmatter(text: str) -> str:
    """Collapse a multi-line string into a single line with literal `\\n`
    separators so it survives our regex-based frontmatter parser. Consumers
    that want to render multi-line can split on `\\n`. Strips leading/
    trailing whitespace. Empty input returns empty string."""
    if not text:
        return ""
    # Normalize line endings, then escape newlines + backslashes + double quotes
    # so the value survives a YAML-style "key: value" line.
    s = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    s = s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")
    return s


def _extract_card_text_scryfall(data: dict) -> tuple[str, str, str]:
    """Pull (flavor_text, oracle_text, mana_cost) from a Scryfall card response.
    All three returned as single-line strings via _flatten_for_frontmatter.
    For double-faced cards, the front face's values are used. mana_cost is the
    raw Scryfall symbol string (e.g. `{3}{R}{R}`); empty for lands / 0-cost cards.
    The mana_cost field is BBL's ground-truth source for `tags_filter` color-magic
    values, preventing the palette-vs-cost mis-tag pattern documented in
    `reports/janitor_triage.md`."""
    flavor = (data.get("flavor_text") or "").strip()
    oracle = (data.get("oracle_text") or "").strip()
    mana = (data.get("mana_cost") or "").strip()
    if not flavor and not oracle and not mana:
        faces = data.get("card_faces") or []
        if faces and isinstance(faces, list):
            face = faces[0]
            flavor = flavor or (face.get("flavor_text") or "").strip()
            oracle = oracle or (face.get("oracle_text") or "").strip()
            mana = mana or (face.get("mana_cost") or "").strip()
    return (_flatten_for_frontmatter(flavor),
            _flatten_for_frontmatter(oracle),
            _flatten_for_frontmatter(mana))


def _extract_card_text_pokemontcg(card: dict) -> tuple[str, str]:
    """Pull (flavor_text, oracle_text) from a PokemonTCG.io card response.
    Pokémon doesn't have a single oracle_text — we compose it from the card's
    rules + abilities + attacks so the local copy contains everything triviabot
    or the bundler might want without a re-fetch."""
    flavor = (card.get("flavorText") or "").strip()

    parts: list[str] = []
    for rule in card.get("rules") or []:
        rule = (rule or "").strip()
        if rule:
            parts.append(rule)
    for ability in card.get("abilities") or []:
        name = (ability.get("name") or "").strip()
        atype = (ability.get("type") or "").strip()
        text = (ability.get("text") or "").strip()
        if name or text:
            head = f"{atype}: {name}".strip(": ").strip()
            parts.append(f"[{head}] {text}" if head else text)
    for attack in card.get("attacks") or []:
        name = (attack.get("name") or "").strip()
        cost = "".join(attack.get("cost") or [])
        damage = (attack.get("damage") or "").strip()
        text = (attack.get("text") or "").strip()
        head_bits = [b for b in [name, cost and f"({cost})", damage] if b]
        head = " ".join(head_bits)
        parts.append(f"{head}: {text}" if text else head)
    oracle = "\n".join(parts).strip()

    return _flatten_for_frontmatter(flavor), _flatten_for_frontmatter(oracle)


def url_extension(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    if "." in path:
        ext = path.rsplit(".", 1)[1].lower()
        if ext in ("png", "jpg", "jpeg", "webp"):
            return f".{ext}"
    return ".jpg"


def download_image(url: str, dest: Path, force: bool = False) -> bool:
    """Download URL to dest. Returns True on success or if file already cached."""
    if dest.exists() and not force:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            dest.write_bytes(r.read())
        return True
    except Exception as e:
        print(f"  [warn] image download failed ({url}): {e}", file=sys.stderr)
        return False


def local_image_path(card_md_path: Path, cards_dir: Path, images_dir: Path, ext: str) -> Path:
    """Mirror cards/<game>/<set>/<slug>.md -> images/<game>/<set>/<slug>.<ext>."""
    rel = card_md_path.relative_to(cards_dir).with_suffix(ext)
    return images_dir / rel


def find_image_scryfall(card_name: str, set_name: str = "",
                        set_map: dict | None = None
                        ) -> tuple[str | None, str, str, str, str, str, str, str]:
    """Returns (image_url, confidence, collector_number, artist, art_crop_url,
    flavor_text, oracle_text, mana_cost).
    confidence in {'high','low','none'}; trailing strings are "" on miss.
    flavor_text and oracle_text are flattened to single-line (literal `\\n`
    separators) so they survive frontmatter; consumers may split to render.
    mana_cost is the raw Scryfall symbol string (e.g. `{3}{R}{R}`); empty for
    lands / 0-cost cards. For double-faced cards, front-face values are used."""
    set_map = set_map if set_map is not None else fetch_scryfall_set_map()
    code = scryfall_set_code(set_name, set_map)
    card_name = normalize_card_name_for_lookup(card_name)

    def _artist(data: dict) -> str:
        a = (data.get("artist") or "").strip()
        if a:
            return a
        faces = data.get("card_faces") or []
        if faces and isinstance(faces, list):
            fa = (faces[0].get("artist") or "").strip()
            if fa:
                return fa
        return ""

    def _build(data: dict, conf: str) -> tuple[str | None, str, str, str, str, str, str, str]:
        img = _extract_image(data)
        if not img:
            return None, "none", "", "", "", "", "", ""
        flavor, oracle, mana = _extract_card_text_scryfall(data)
        return (img, conf,
                str(data.get("collector_number") or "").strip(),
                _artist(data),
                _extract_art_crop(data) or "",
                flavor, oracle, mana)

    if code:
        params = {"fuzzy": card_name, "set": code}
        url = f"{SCRYFALL_API}/cards/named?{urllib.parse.urlencode(params)}"
        data = http_get_json(url)
        time.sleep(SCRYFALL_SLEEP)
        if data and not data.get("status"):
            r = _build(data, "high")
            if r[0]:
                return r

    params = {"fuzzy": card_name}
    url = f"{SCRYFALL_API}/cards/named?{urllib.parse.urlencode(params)}"
    data = http_get_json(url)
    time.sleep(SCRYFALL_SLEEP)
    if data and not data.get("status"):
        r = _build(data, "low")
        if r[0]:
            return r
    return None, "none", "", "", "", "", "", ""


def _bulbapedia_filename_candidates(name: str, set_name: str, number: str) -> list[str]:
    """Build a list of likely Bulbapedia File: page names for this card. The
    canonical pattern is `{Name}{SetName}{Number}.jpg` with spaces stripped.
    A few common name variations are also worth trying:
      - apostrophes stripped ("Farfetch'd" -> "Farfetchd")
      - number with leading zero stripped ("047" -> "47")
      - number as-given (some sets keep leading zeros)
    Returns the candidates in priority order; caller probes each until one hits."""
    if not name or not set_name or not number:
        return []
    name_strip = re.sub(r"[^A-Za-z0-9]", "", name)
    set_strip = re.sub(r"[^A-Za-z0-9]", "", set_name)
    num_unpadded = number.lstrip("0") or number
    cands = []
    # Bulbapedia tends to use unpadded numbers, but try both.
    for n in (num_unpadded, number):
        cands.append(f"{name_strip}{set_strip}{n}.jpg")
        cands.append(f"{name_strip}{set_strip}{n}.png")
    # Dedup preserving order
    seen: set[str] = set()
    out = []
    for c in cands:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def find_image_bulbapedia(card_name: str, set_name: str, number: str
                          ) -> tuple[str | None, int]:
    """Try Bulbapedia's MediaWiki API for a higher-resolution card image.
    Returns (url, width) or (None, 0) on miss. Only modern (Sword & Shield
    onward) sets reliably have >800px uploads — caller should compare width
    to BULBAPEDIA_MIN_WIDTH before adopting. No auth, no rate-limit issues
    at our request volume, but Bulbapedia asks for a descriptive User-Agent
    in their bot policy (set globally via USER_AGENT)."""
    for filename in _bulbapedia_filename_candidates(card_name, set_name, number):
        params = {
            "action": "query",
            "titles": f"File:{filename}",
            "prop": "imageinfo",
            "iiprop": "url|size|mime",
            "format": "json",
        }
        url = f"{BULBAPEDIA_API}?{urllib.parse.urlencode(params)}"
        data = http_get_json(url, timeout=10.0, retries=1)
        if not data:
            continue
        pages = (data.get("query") or {}).get("pages") or {}
        for _, page in pages.items():
            # MediaWiki quirk: pages from a shared image repo (Bulbagarden
            # Archives) include `"missing": ""` even when `imageinfo` is
            # fully populated. So we check `imageinfo` directly rather than
            # gating on `missing`.
            infos = page.get("imageinfo") or []
            if not infos:
                continue
            info = infos[0]
            img_url = info.get("url")
            width = info.get("width") or 0
            if img_url:
                return img_url, width
    return None, 0


def find_image_pokemontcg(card_name: str, set_name: str = "",
                          collector_number: str = ""
                          ) -> tuple[str | None, str, str, str, str, str, str, str]:
    """PokemonTCG.io v2 API. Returns (url, confidence, number, artist,
    art_crop_url, flavor_text, oracle_text, mana_cost).
    art_crop_url is ALWAYS "" for Pokémon (no art-only crop endpoint). mana_cost
    is ALWAYS "" for non-MTG games. The Pokémon `oracle_text` is composed from
    rules + abilities + attacks via _extract_card_text_pokemontcg, so the local
    copy contains everything triviabot or the bundler might want without a
    re-fetch.

    Number-pinning (wave 92.5): when both set_name AND collector_number are
    provided, prefer a number-pinned query that cannot be impostored by
    substring-name siblings (Switch vs Energy Switch, Potion vs Max Potion,
    etc). Falls back to name-only fuzzy match if pinned query misses.

    Set-name aliasing (wave 96.9): Collectr-style set names (e.g.
    'Sword & Shield Base Set') get translated to PokemonTCG.io canonical
    names ('Sword & Shield') via POKEMON_SET_NAME_ALIASES before any
    set.name: filter is formed. Unrecognized names pass through untouched."""
    # Resolve Collectr-style set name to PokemonTCG.io canonical name.
    if set_name:
        set_name = POKEMON_SET_NAME_ALIASES.get(set_name.lower().strip(), set_name)

    def _query(q: str) -> tuple[dict | None, str | None, str, str]:
        """Returns (raw_card, img_url, number, artist) — raw_card lets the
        caller pull flavor/oracle text without a second API call."""
        url = f"{POKEMONTCG_API}/cards?q={urllib.parse.quote(q)}&pageSize=1"
        data = http_get_json(url)
        time.sleep(0.2)
        if not data:
            return None, None, "", ""
        cards = data.get("data") or []
        if not cards:
            return None, None, "", ""
        card = cards[0]
        images = card.get("images") or {}
        img = images.get("large") or images.get("small")
        number = str(card.get("number") or "").strip()
        artist = str(card.get("artist") or "").strip()
        return card, img, number, artist

    def _pack(card: dict | None, img: str | None, number: str, artist: str,
              conf: str) -> tuple[str | None, str, str, str, str, str, str]:
        if not img:
            return None, "none", "", "", "", "", ""
        # Upgrade to Bulbapedia image when it's meaningfully higher-res than
        # PokemonTCG.io's ~734px ceiling. SWSH-era and later usually win;
        # older sets often have weaker uploads — the width gate filters those.
        bulba_url, bulba_w = find_image_bulbapedia(card_name, set_name, number)
        if bulba_url and bulba_w >= BULBAPEDIA_MIN_WIDTH:
            img = bulba_url
        flavor, oracle = _extract_card_text_pokemontcg(card or {})
        return img, conf, number, artist, "", flavor, oracle, ""

    # Number-pinned priority: collector_number kills the substring-name
    # impostor pattern. Strip "/total" suffix per Collectr's convention.
    if set_name and collector_number:
        bare_num = collector_number.split("/", 1)[0].strip().lstrip("0") or collector_number.split("/", 1)[0].strip()
        card, img, number, artist = _query(f'name:"{card_name}" set.name:"{set_name}" number:"{bare_num}"')
        if img:
            return _pack(card, img, number, artist, "high")
    if set_name:
        card, img, number, artist = _query(f'name:"{card_name}" set.name:"{set_name}"')
        if img:
            return _pack(card, img, number, artist, "high")
    card, img, number, artist = _query(f'name:"{card_name}"')
    if img:
        return _pack(card, img, number, artist, "low" if set_name else "high")
    return None, "none", "", "", "", "", "", ""


def _head_ok(url: str, referer: str | None = None, timeout: float = 10.0) -> bool:
    """HEAD probe — treat 200 as truthy. Saves downloading a thumbnail just to
    discover it's a 404 page. Used by find_image_dbs (Bandai CDN is single-URL
    formula; cheap to HEAD-check before committing to GET)."""
    headers = {"User-Agent": USER_AGENT}
    if referer:
        headers["Referer"] = referer
    try:
        req = urllib.request.Request(url, headers=headers, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def _try_dbzexchange_hires(collector_number: str
                           ) -> tuple[str | None, int]:
    """Probe dbzexchange Shopify search-suggest for a HIGH-RES (>=500px wide)
    scan of the given DBSCG collector_number. Returns (url, width_px) on hit
    or (None, 0) on miss / low-res / wrong-card-match. ~30% of legacy DBSCG
    corpus hits per investigation, rest are 260px mirrors of Bandai (we filter
    those out — Bandai fallback wins on those because it's faster + canonical)."""
    url = f"{DBZEXCHANGE_SUGGEST}?q={urllib.parse.quote(collector_number)}&resources%5Btype%5D=product&resources%5Blimit%5D=3"
    data = http_get_json(url, timeout=10.0)
    if not data:
        return None, 0
    products = (data.get("resources", {}).get("results", {}).get("products") or [])
    for p in products:
        title = str(p.get("title", "")).strip()
        # The product title starts with the collector number for correct matches
        # (e.g. "BT4-002 Baby - Rampaging Great Ape Baby"). P-prefix searches
        # alphanumerically collide with BT* cards, so verify the title matches.
        if not title.upper().startswith(collector_number.upper()):
            continue
        img = p.get("featured_image") or {}
        width = int(img.get("width") or 0)
        if width < 500:
            continue
        img_url = img.get("url") or ""
        if img_url:
            return img_url, width
    return None, 0


def find_image_dbs(card_name: str, set_name: str = "",
                   collector_number: str = ""
                   ) -> tuple[str | None, str, str, str, str, str, str]:
    """DBSCG image fetch. Tries dbzexchange Shopify hi-res first (~30% coverage
    at 867x1210); falls back to Bandai CDN (universal 260x363). Returns
    (url, confidence, number, artist='', art_crop_url='', flavor_text='',
    oracle_text='', mana_cost=''). Artist + oracle/flavor are NOT URL-derivable
    from either source — capture deferred to triviabot OCR. mana_cost is always
    "" for non-MTG games."""
    if not collector_number:
        return None, "none", "", "", "", "", "", ""
    number = collector_number.strip().upper()
    # Strip any --foil/--alt suffix that may have crept in from filename normalization.
    number = number.split("--")[0]
    # Primary: try dbzexchange hi-res
    hires_url, hires_w = _try_dbzexchange_hires(number)
    if hires_url:
        return hires_url, "high", number, "", "", "", "", ""
    # Fallback: Bandai 260x363 thumbnail
    url = f"{DBS_IMAGE_BASE}/{number}.png"
    if _head_ok(url, referer=DBS_REFERER):
        return url, "high", number, "", "", "", "", ""
    return None, "none", "", "", "", "", "", ""


def find_image_fftcg(card_name: str, set_name: str = "",
                     collector_number: str = ""
                     ) -> tuple[str | None, str, str, str, str, str, str, str]:
    """FFTCG (Final Fantasy TCG) image fetch via Marcie's GCS mirror.
    Returns (url, confidence, number, artist='', art_crop_url='',
    flavor_text='', oracle_text='', mana_cost=''). Artist + oracle/flavor are
    NOT URL-derivable from the GCS bucket — capture deferred to triviabot or
    a future FFDecks API enrichment pass. mana_cost is always "" for non-MTG.

    URL formula: {FFTCG_IMAGE_BASE}/<code>_eg.jpg where <code> is the verbatim
    Collectr `collector_number` (e.g. `3-122C`, `6-050C`, `8-001R`). HEAD-
    checked before commit to filter 404s (rare cards or codes Marcie's mirror
    hasn't backfilled yet — those need curator review). Wave 96.10 wire."""
    if not collector_number:
        return None, "none", "", "", "", "", "", ""
    code = collector_number.strip().upper().split("--")[0]
    if not code:
        return None, "none", "", "", "", "", "", ""
    url = f"{FFTCG_IMAGE_BASE}/{code}_eg.jpg"
    if _head_ok(url):
        return url, "high", code, "", "", "", "", ""
    return None, "none", "", "", "", "", "", ""


def _strip_weiss_rarity_suffix(collector_number: str) -> str:
    """Bushiroad EN search expects card numbers WITHOUT a trailing rarity
    suffix. Corpus filenames sometimes carry the rarity (e.g. "BD/WE35-E20 C"
    or "AOT/S35-E024-C"). Strip the trailing ` X` / `-X` where X is a 1-3
    char rarity code (C, U, R, RR, RRR, SR, CC, SP, PR)."""
    if not collector_number:
        return ""
    cn = collector_number.strip()
    # Match trailing ` C`, `-C`, ` RR`, etc.
    cn = re.sub(r'[-\s](C|U|R|RR|RRR|SR|CC|SP|PR|TD|PPR)$', '', cn)
    return cn


def find_image_weiss(card_name: str, set_name: str = "",
                     collector_number: str = ""
                     ) -> tuple[str | None, str, str, str, str, str, str, str]:
    """Bushiroad EN Weiss Schwarz cardlist search. Returns (url, confidence,
    number, artist='', art_crop_url='', flavor_text='', oracle_text='',
    mana_cost=''). Two-step: search endpoint returns HTML with <img src="...">
    for the matched card. Image URLs are NOT formula-derivable across all sets
    (BD/WE35 uses non-standard product folders), so we always go via search.
    mana_cost is always "" for non-MTG games."""
    if not collector_number:
        return None, "none", "", "", "", "", "", ""
    keyword = _strip_weiss_rarity_suffix(collector_number)
    if not keyword:
        return None, "none", "", "", "", "", "", ""
    url = f"{WEISS_SEARCH_BASE}?keyword={urllib.parse.quote(keyword)}"
    headers = {"User-Agent": USER_AGENT}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [warn] weiss search failed ({keyword}): {e}", file=sys.stderr)
        return None, "none", "", "", "", "", "", ""
    # Zero-result detection per investigator findings
    if "No cards were found." in html:
        return None, "none", "", "", "", "", "", ""
    # Parse: <div class="image"><img src="..."> — first match wins (search
    # returns one card per keyword in the corpus's collector-number pattern)
    m = re.search(r'<div class="image">\s*<img[^>]*src="([^"]+)"', html)
    if not m:
        # Fallback: any <img> within a card-result block
        m = re.search(r'<img[^>]*src="([^"]+\.(?:png|jpg|jpeg))"', html)
    if not m:
        return None, "none", "", "", "", "", "", ""
    img_path = m.group(1)
    if img_path.startswith("http"):
        img_url = img_path
    elif img_path.startswith("/"):
        img_url = WEISS_HOST + img_path
    else:
        # Relative path like "./images/..." or "images/..."
        img_url = WEISS_HOST + "/" + img_path.lstrip("./")
    return img_url, "high", keyword, "", "", "", "", ""


def _load_lorcana_index() -> dict:
    """Lazy-load and index LorcanaJSON allCards bulk by (setCode, number).
    Downloads to LORCANA_CACHE if not present. Index returns the card dict
    so all downstream fields (images, artistsText, flavorText, fullText)
    are available in one lookup. Set-name → setCode map built off the bulk's
    `sets` dict so BBL's set-name slugs resolve correctly."""
    global _LORCANA_INDEX
    if _LORCANA_INDEX is not None:
        return _LORCANA_INDEX
    if not LORCANA_CACHE.exists():
        LORCANA_CACHE.parent.mkdir(parents=True, exist_ok=True)
        print(f"  [info] downloading lorcana bulk to {LORCANA_CACHE}", file=sys.stderr)
        headers = {"User-Agent": USER_AGENT}
        try:
            req = urllib.request.Request(LORCANA_ALLCARDS_URL, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                LORCANA_CACHE.write_bytes(resp.read())
        except Exception as e:
            print(f"  [warn] lorcana bulk download failed: {e}", file=sys.stderr)
            _LORCANA_INDEX = {"by_key": {}, "set_name_to_code": {}}
            return _LORCANA_INDEX
    data = json.loads(LORCANA_CACHE.read_text(encoding="utf-8"))
    by_key: dict[tuple, dict] = {}
    # Promo-losing tiebreak (wave 96.6 Nurse Joy fix): LorcanaJSON can have
    # multiple cards sharing (setCode, number) when a promo print collides with
    # a standard print. E.g., WTW-36 The Horned King (id 2225) collides with
    # the Scrooge McDuck Gift Box promo (id 2714, promoGrouping P3). The promo
    # appears later in the array and silently overwrote the standard print via
    # the previous unconditional assignment. Standard prints always win now.
    def _is_promo(card: dict) -> bool:
        return bool(card.get("promoGrouping") or card.get("promoSource"))
    for c in data.get("cards", []):
        sc = str(c.get("setCode", ""))
        num = c.get("number")
        if not (sc and num is not None):
            continue
        key = (sc, int(num))
        existing = by_key.get(key)
        if existing is None:
            by_key[key] = c
            continue
        # Collision: standard print beats promo.
        if _is_promo(existing) and not _is_promo(c):
            by_key[key] = c
    set_name_to_code: dict[str, str] = {}
    for code, sinfo in data.get("sets", {}).items():
        name = (sinfo.get("name") or "").strip()
        if name:
            set_name_to_code[name.lower()] = str(code)
            # Also index without leading "The" for forgiving lookup
            if name.lower().startswith("the "):
                set_name_to_code[name[4:].lower()] = str(code)
    _LORCANA_INDEX = {"by_key": by_key, "set_name_to_code": set_name_to_code}
    return _LORCANA_INDEX


def find_image_lorcana(card_name: str, set_name: str = "",
                       collector_number: str = ""
                       ) -> tuple[str | None, str, str, str, str, str, str, str]:
    """LorcanaJSON lookup. Returns (url, confidence, number, artist,
    art_crop_url='', flavor_text, oracle_text, mana_cost=''). Lorcana has no
    clean frameless art crop (art is fused with card frame at design time),
    so art_crop_url is always empty. mana_cost is always "" for non-MTG.
    Image is 1468x2048 JPEG from official Ravensburger CDN. collector_number
    is parsed as `<num>/<total>` (the BBL Lorcana convention)."""
    if not collector_number:
        return None, "none", "", "", "", "", "", ""
    # Parse "146/204" → 146
    num_str = collector_number.split("/", 1)[0].strip()
    try:
        num = int(num_str)
    except ValueError:
        return None, "none", "", "", "", "", "", ""
    idx = _load_lorcana_index()
    code = idx["set_name_to_code"].get(set_name.lower().strip())
    if not code:
        return None, "none", "", "", "", "", "", ""
    card = idx["by_key"].get((code, num))
    if not card:
        return None, "none", "", "", "", "", "", ""
    img_url = (card.get("images") or {}).get("full", "")
    if not img_url:
        return None, "none", "", "", "", "", "", ""
    artist = (card.get("artistsText") or "").strip()
    flavor = (card.get("flavorText") or "").strip()
    # Lorcana's "fullText" is the rules-text block (includes ability names).
    # Closest equivalent to MTG oracle_text.
    oracle = (card.get("fullText") or "").strip()
    return img_url, "high", str(num), artist, "", flavor, oracle, ""


def find_reference_image(game: str, card_name: str, set_name: str,
                         set_map: dict | None = None,
                         collector_number: str = ""
                         ) -> tuple[str | None, str, str, str, str, str, str, str]:
    """Returns (image_url, confidence, collector_number, artist, art_crop_url,
    flavor_text, oracle_text, mana_cost). Empty strings on miss. Prep loop
    captures all eight into frontmatter so downstream agents (vision, trivia,
    bundler) never need to re-fetch the source API for canonical card data.
    mana_cost is MTG-only (always "" for other games).

    The collector_number kwarg is required by DBS (Bandai's CDN is keyed on
    number, not name) and ignored by Scryfall/PokemonTCG strategies."""
    strat = GAME_STRATEGY.get(game)
    if strat == "scryfall":
        return find_image_scryfall(card_name, set_name, set_map)
    if strat == "pokemontcg":
        return find_image_pokemontcg(card_name, set_name, collector_number)
    if strat == "dbs":
        return find_image_dbs(card_name, set_name, collector_number)
    if strat == "weiss":
        return find_image_weiss(card_name, set_name, collector_number)
    if strat == "lorcana":
        return find_image_lorcana(card_name, set_name, collector_number)
    if strat == "fftcg":
        return find_image_fftcg(card_name, set_name, collector_number)
    return None, "none", "", "", "", "", "", ""


def measure_image(path: Path) -> tuple[int, int, str]:
    """Returns (width_px, height_px, quality_bucket) for a downloaded image.
    quality_bucket ∈ {'high', 'med', 'low', 'unknown'}. Used to stamp
    image quality into frontmatter so downstream queries can grep cards
    that may benefit from a source upgrade later (Alex 2026-05-14: "we
    need a tag for low quality images that it looks like we'll be snagging").
    PIL is optional — falls back to ('unknown') on import error so the
    pipeline doesn't break for environments without Pillow."""
    try:
        from PIL import Image  # noqa: PLC0415 (lazy import is intentional)
    except ImportError:
        return 0, 0, "unknown"
    try:
        with Image.open(path) as im:
            w, h = im.size
    except Exception:
        return 0, 0, "unknown"
    if w >= IMAGE_QUALITY_HIGH_MIN:
        return w, h, "high"
    if w >= IMAGE_QUALITY_MED_MIN:
        return w, h, "med"
    return w, h, "low"


# --- Vision pipeline note ---
#
# Plan A (DeepSeek hosted vision API) was the original target — see the
# "DeepSeek vision watch" memory for context. The full prompt + chat-completion
# call lived here before wave 92.5 deleted it. Vision now runs through the
# subagent at `.claude/agents/bbl-researcher.md`, dispatched per card by the
# parent Claude Code session. researchbot.py's role is reduced to: fetch
# canonical card data + image, stamp frontmatter, leave tags_hub empty as the
# ready-for-subagent signal. The DeepSeek-models probe at --list-models is
# preserved as the watch signal for when hosted vision GA'es — re-introducing
# Plan A is a deliberate future move, not a recovery operation.


# --- Vision data → MD update ---

def render_yaml_list(items: list) -> str:
    if not items:
        return "[]"
    safe = [str(x).replace('"', '\\"') for x in items]
    return "[" + ", ".join(f'"{x}"' for x in safe) + "]"


def vision_body_section(v: dict) -> str:
    """Render the vision data as a readable ## Vision section."""
    lines = []
    # IP flag at the very top of the Vision section so a human reviewer sees it
    # immediately when scanning the card. Obsidian renders this as a yellow callout;
    # other markdown viewers fall back to a styled blockquote. The IP guardrail is
    # protective work — it's worth being prominent rather than buried mid-section.
    if v.get("suspected_ip") and v.get("ip_confidence") not in (None, "", "none"):
        verified = "verified" if v.get("ip_verified") else "unverified"
        lines.append(f"> [!warning] Suspected IP: **{v['suspected_ip']}** "
                     f"(confidence: {v.get('ip_confidence')}, {verified})")
        lines.append("> Reviewer: confirm whether the depicted figure is canonically this character. "
                     "If yes, set `ip_verified: true` in frontmatter. If no, clear `suspected_ip`.")
        lines.append("")
    if v.get("description"):
        lines.append(v["description"].strip())
    lines.append("")
    lines.append("**Subject:** " + (v.get("subject") or ""))
    lines.append("")
    lines.append("**Composition:** " + ", ".join(filter(None, [
        v.get("composition"), v.get("mode"), f"figures: {v.get('figure_count', '')}", f"facing: {v.get('facing', '')}",
    ])))
    lines.append("**Setting:** " + ", ".join(filter(None, [
        v.get("setting"), v.get("architecture") if v.get("architecture") not in ("none", None) else None,
        v.get("time_of_day"), v.get("weather") if v.get("weather") not in ("none", None) else None,
    ])))
    if v.get("foreground"):
        lines.append(f"**Foreground:** {v['foreground']}  *(palette: {', '.join(v.get('foreground_palette', []))})*")
    if v.get("background"):
        lines.append(f"**Background:** {v['background']}  *(palette: {', '.join(v.get('background_palette', []))})*")
    lines.append("**Mood / lighting:** " + ", ".join(filter(None, [v.get("mood"), v.get("lighting")])))
    if v.get("emotion"):
        lines.append(f"**Emotion read:** {v['emotion']}")
    if v.get("objects"):
        lines.append(f"**Objects:** {', '.join(v['objects'])}")
    if v.get("animals_creatures"):
        lines.append(f"**Creatures:** {', '.join(v['animals_creatures'])}")
    if v.get("food_drink"):
        lines.append(f"**Food/drink:** {', '.join(v['food_drink'])}")
    if v.get("iconography"):
        lines.append(f"**Iconography:** {', '.join(v['iconography'])}")
    if v.get("genre_cues"):
        lines.append(f"**Genre cues:** {', '.join(v['genre_cues'])}")
    return "\n".join(lines)


def update_card(path: Path, image_url: str, vision: dict, dry_run: bool,
                art_confidence: str = "high", manual_review_reason: str = "",
                local_image_rel: str = "") -> None:
    """Apply vision data to a card MD. art_confidence in {high, low, none}.
    `local_image_rel` is a project-relative path like images/<game>/<set>/<slug>.png;
    when present, frontmatter `reference_image` stores the local path and the body
    embeds the image via Obsidian shortcut syntax."""
    text = path.read_text(encoding="utf-8")
    if local_image_rel:
        text = update_frontmatter_field(text, "reference_image", local_image_rel)
        text = update_frontmatter_field(text, "reference_image_source_url", image_url or "")
    else:
        text = update_frontmatter_field(text, "reference_image", image_url or "")
    text = update_frontmatter_field(text, "art_match_confidence", art_confidence)
    needs_review = art_confidence in ("low", "none") or bool(manual_review_reason)
    text = update_frontmatter_field(text, "needs_manual_review", "true" if needs_review else "false")
    if manual_review_reason:
        text = update_frontmatter_field(text, "manual_review_reason", manual_review_reason)
    text = update_frontmatter_field(text, "tags_hub", render_yaml_list(vision.get("tags_hub", [])))
    text = update_frontmatter_field(text, "tags_filter", render_yaml_list(vision.get("tags_filter", [])))
    for key in ("mood", "time_of_day", "setting"):
        if vision.get(key):
            text = update_frontmatter_field(text, key, vision[key])
    if vision.get("subject_known_ip"):
        text = update_frontmatter_field(text, "subject_known_ip", "true" if vision["subject_known_ip"] else "false")
    if vision.get("suspected_ip"):
        text = update_frontmatter_field(text, "suspected_ip", vision["suspected_ip"])
        text = update_frontmatter_field(text, "ip_confidence", vision.get("ip_confidence", "low"))
        text = update_frontmatter_field(text, "ip_verified", "true" if vision.get("ip_verified") else "false")

    body_parts = []
    if local_image_rel:
        # Standard markdown image syntax with a path relative to the card MD.
        # Image cache lives at cards/_images/<game>/<set>/<slug>.png — same nesting
        # depth as the card itself. From cards/<game>/<set>/<slug>.md to
        # cards/_images/<game>/<set>/<slug>.png we go up two (out of <set> + <game>)
        # and then back down into _images/<game>/<set>/. Forward slashes work
        # cross-platform in markdown image refs.
        rel = local_image_rel.replace("\\", "/")
        # local_image_rel is project-relative ("cards/_images/<game>/<set>/<slug>.png").
        # Strip the leading "cards/" since the embed is relative to a card MD inside cards/.
        if rel.startswith("cards/"):
            rel_from_cards = rel[len("cards/"):]
        else:
            rel_from_cards = rel
        rel_from_card = "../../" + rel_from_cards
        body_parts.append(f"![{path.stem}]({rel_from_card})")
        body_parts.append("")
    if needs_review:
        body_parts.append(
            "> ⚠ **Manual review needed.** Art match is uncertain — visual specifics in this analysis "
            "may not reflect the printing you actually own. Tags below are provisional."
        )
        body_parts.append("")
    body_parts.append(vision_body_section(vision))
    body = "\n".join(body_parts).strip()
    text = append_or_replace_section(text, "Vision", body)
    if not dry_run:
        path.write_text(text, encoding="utf-8")
        # Normalize frontmatter (block-form lists + scalar quoting + tags-last).
        # update_card is now the second chokepoint alongside apply_vision.py;
        # both route through bbl_schema.normalize_file for hygiene parity.
        try:
            from bbl_schema import normalize_file as _normalize_file
            _normalize_file(path)
        except ImportError:
            pass


# --- Main loop ---

def is_already_enriched(fm: dict) -> bool:
    """Skip cards that already have a non-empty tags_hub list."""
    raw = (fm.get("tags_hub") or "").strip()
    return bool(raw) and raw not in ("[]", '""', "''")


def is_already_prepared(fm: dict, card_path: Path) -> bool:
    """Skip cards that already have a high-confidence Scryfall match cached on disk.

    Without this guard, --prepare-only re-queries Scryfall for every already-prepared
    card, wasting hundreds of API calls per sweep. The guard returns True only when
    BOTH the frontmatter says we matched at high confidence AND the cached image
    file actually exists on disk — covers the case where someone deletes the cache.
    """
    if fm.get("art_match_confidence") != "high":
        return False
    ref = (fm.get("reference_image") or "").strip()
    if not ref:
        return False
    return Path(ref).exists()


def list_deepseek_models(api_key: str) -> list[str]:
    """Probe the hosted DeepSeek API for the model IDs it currently serves.
    Useful when vision support lags behind announced model names."""
    req = urllib.request.Request(DEEPSEEK_MODELS_ENDPOINT, method="GET")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("User-Agent", USER_AGENT)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[error] models probe failed: {e}", file=sys.stderr)
        return []
    return [m.get("id", "") for m in data.get("data", []) if m.get("id")]


def process(cards_dir: Path, images_dir: Path, limit: int, game_filter: str | None,
            api_key: str, dry_run: bool, force: bool,
            prepare_only: bool = False) -> dict:
    report = {"processed": 0, "skipped_enriched": 0, "skipped_no_image": 0,
              "skipped_no_strategy": 0, "deferred_low_confidence": 0,
              "prepared_for_vision": 0, "errors": 0,
              "ip_flagged": [], "manual_review_queue": []}

    set_map = fetch_scryfall_set_map()

    # Gather candidates, sorted by qty DESC then last_seen DESC
    candidates = []
    for path in cards_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if game_filter and fm.get("game", "").lower() != game_filter.lower():
            continue
        if not force and is_already_enriched(fm):
            report["skipped_enriched"] += 1
            continue
        # In --prepare-only flow, also skip cards that already have a high-confidence
        # Scryfall match with the image on disk — no point burning the API call.
        if prepare_only and not force and is_already_prepared(fm, path):
            report["skipped_enriched"] += 1
            continue
        try:
            qty = int(fm.get("quantity") or 0)
        except ValueError:
            qty = 0
        last_seen = fm.get("last_seen", "")
        # Truly-unprepped (no reference_image) sorts BEFORE already-prepped
        # (re-prep / refresh) so new CSV ingest doesn't starve behind high-qty
        # older backlog. Within each group: highest quantity, then most recent.
        has_ref = bool((fm.get("reference_image") or "").strip())
        candidates.append((has_ref, -qty, last_seen, path, fm))

    candidates.sort()
    candidates = candidates[:limit]  # Python's slice handles None as "no limit"

    print(f"\nProcessing {len(candidates)} cards "
          f"(unprepped-first, then qty-priority; limit={limit or 'unlimited'})\n")

    for i, (_, _, _, path, fm) in enumerate(candidates, 1):
        name = fm.get("name", "")
        game = fm.get("game", "")
        set_ = fm.get("set", "")
        qty = fm.get("quantity", "?")
        print(f"[{i}/{len(candidates)}] qty={qty}  {game}  {name}")

        if game not in GAME_STRATEGY:
            print(f"  -> no image strategy for game '{game}', skipping")
            report["skipped_no_strategy"] += 1
            continue

        image_url, confidence, collector_number, artist, art_crop_url, flavor_text, oracle_text, mana_cost = find_reference_image(
            game, name, set_, set_map, collector_number=fm.get("collector_number", "") or "")
        if not image_url:
            print(f"  -> reference image not found, flagging for manual review")
            report["skipped_no_image"] += 1
            report["manual_review_queue"].append(str(path))
            if not dry_run:
                empty_vision = {"tags_hub": [], "tags_filter": []}
                update_card(path, "", empty_vision, dry_run=False,
                            art_confidence="none",
                            manual_review_reason=f"No reference image found via {GAME_STRATEGY[game]} for set '{set_}'")
            continue

        # Backfill no-num-* MDs inline: when Collectr's CSV had an empty Card Number
        # but the upstream API knows the collector_number, rename the MD before any
        # further work. Keeps the corpus tidy without a separate cleanup pass.
        if collector_number and not dry_run and path.stem.startswith("no-num-"):
            new_stem = f"{collector_number}-{path.stem[len('no-num-'):]}"
            new_path = path.with_name(new_stem + ".md")
            if not new_path.exists():
                # Stamp collector_number into frontmatter before the rename so the
                # file is internally consistent if anything else reads it before
                # the image-cache write below.
                text = path.read_text(encoding="utf-8")
                text = update_frontmatter_field(text, "collector_number", collector_number)
                path.write_text(text, encoding="utf-8")
                path.rename(new_path)
                print(f"  -> backfilled collector_number={collector_number}, renamed to {new_path.name}")
                path = new_path  # downstream image-cache + frontmatter writes target the new path

        print(f"  -> image: {image_url}  (art_match: {confidence})")

        # Download full card image to local cache. Skip on dry-run.
        local_rel = ""
        local_art_rel = ""
        img_w, img_h, img_quality = 0, 0, "unknown"
        if not dry_run:
            ext = url_extension(image_url)
            local_path = local_image_path(path, cards_dir, images_dir, ext)
            if download_image(image_url, local_path, force=force):
                local_rel = str(local_path).replace("\\", "/")
                img_w, img_h, img_quality = measure_image(local_path)
                quality_note = f" [{img_w}x{img_h} {img_quality}]" if img_w else ""
                print(f"  -> cached: {local_rel}{quality_note}")
            # Also cache art_crop (frameless artwork) when present. Filename
            # stem gets a "--art" suffix so it sits beside the full-card image
            # in the same directory: <slug>.png + <slug>--art.jpg. This is the
            # vision-agent input; the full card is the human/Obsidian view.
            if art_crop_url:
                art_ext = url_extension(art_crop_url)
                art_local_path = local_path.with_name(local_path.stem + "--art" + art_ext)
                if download_image(art_crop_url, art_local_path, force=force):
                    local_art_rel = str(art_local_path).replace("\\", "/")
                    print(f"  -> art_crop cached: {local_art_rel}")

        if confidence == "low":
            print(f"  -> art match uncertain (set lookup failed); deferring to manual review with text-only tags")
            report["deferred_low_confidence"] += 1
            report["manual_review_queue"].append(str(path))
            if not dry_run:
                empty_vision = {"tags_hub": [], "tags_filter": []}
                update_card(path, image_url, empty_vision, dry_run=False,
                            art_confidence="low",
                            manual_review_reason=(
                                f"Set '{set_}' did not match a known set code or the card was not in that set; "
                                "fuzzy fallback returned art that may be from a different printing."
                            ),
                            local_image_rel=local_rel)
            continue

        if prepare_only:
            if dry_run:
                print(f"  -> [dry-run] would prepare {path.name} for vision subagent")
            else:
                # Stamp reference_image (+ source URL) and confidence; leave tags_hub empty
                # so the bbl-researcher Claude Code subagent picks this up as ready-for-vision.
                text = path.read_text(encoding="utf-8")
                if local_rel:
                    text = update_frontmatter_field(text, "reference_image", local_rel)
                    text = update_frontmatter_field(text, "reference_image_source_url", image_url or "")
                else:
                    text = update_frontmatter_field(text, "reference_image", image_url or "")
                text = update_frontmatter_field(text, "art_match_confidence", "high")
                text = update_frontmatter_field(text, "needs_manual_review", "false")
                if artist:
                    text = update_frontmatter_field(text, "artist", artist)
                if local_art_rel:
                    text = update_frontmatter_field(text, "art_crop_image", local_art_rel)
                    text = update_frontmatter_field(text, "art_crop_source_url", art_crop_url or "")
                if flavor_text:
                    text = update_frontmatter_field(text, "flavor_text", flavor_text)
                if oracle_text:
                    text = update_frontmatter_field(text, "oracle_text", oracle_text)
                if mana_cost:
                    text = update_frontmatter_field(text, "mana_cost", mana_cost)
                if img_w:
                    text = update_frontmatter_field(text, "image_width", str(img_w))
                    text = update_frontmatter_field(text, "image_height", str(img_h))
                    text = update_frontmatter_field(text, "image_quality", img_quality)
                path.write_text(text, encoding="utf-8")
                # Normalize frontmatter via bbl_schema chokepoint (wave 92.5).
                try:
                    from bbl_schema import normalize_file as _normalize_file
                    _normalize_file(path)
                except ImportError:
                    pass
                art_note = "+art_crop" if local_art_rel else ""
                txt_note = " +text" if (flavor_text or oracle_text) else ""
                qual_note = f" {img_quality}" if img_w else ""
                print(f"  -> prepared (image cached{qual_note} {art_note}{txt_note}, artist={artist or '?'}, awaiting vision subagent)")
            report["prepared_for_vision"] += 1
            continue

        # Vision pass branch removed wave 92.5 — vision now routes through
        # the .claude/agents/bbl-researcher.md subagent. researchbot.py without
        # --prepare-only is a no-op past this point; the prepare-only branch
        # above is the only meaningful path. Kept the loop structure intact in
        # case Plan A revives (deepseek hosted vision GA per --list-models watch).
        if not prepare_only:
            print(f"  -> skipped (vision pipeline runs through bbl-researcher subagent; use --prepare-only)")
            report["skipped_no_strategy"] += 1
            continue

    return report


def retry_flagged(cards_dir: Path, images_dir: Path,
                  game_filter: str | None, set_filter: str | None,
                  sleep_s: float, force: bool = False) -> dict:
    """Walk cards with needs_manual_review: true, re-run the lookup, recover what we can.

    Many cards end up flagged due to transient Scryfall failures (network hiccups, rate-
    limit blips) rather than genuine "set/name doesn't exist" misses. This retry pass uses
    a gentler sleep between requests and re-stamps successful lookups so they're picked up
    by the next prepare/vision flow.
    """
    set_map = fetch_scryfall_set_map()
    flagged: list[tuple[Path, dict]] = []
    for path in cards_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if fm.get("needs_manual_review", "").lower() != "true":
            continue
        if game_filter and fm.get("game", "").lower() != game_filter.lower():
            continue
        if set_filter and fm.get("set", "").lower() != set_filter.lower():
            continue
        # If already has high-confidence image stamped, nothing to retry unless --force.
        if not force and fm.get("art_match_confidence") == "high" \
                and (fm.get("reference_image") or "").strip():
            continue
        flagged.append((path, fm))

    print(f"\nRetrying {len(flagged)} flagged cards "
          f"(game={game_filter or 'all'}, set={set_filter or 'all'}, sleep={sleep_s}s)\n")

    recovered = 0
    low_conf = 0
    still_failed = 0
    no_strategy = 0

    for i, (path, fm) in enumerate(flagged, 1):
        name = fm.get("name", "")
        game = fm.get("game", "")
        set_ = fm.get("set", "")
        print(f"[{i}/{len(flagged)}] {game} | {name} ({set_})")

        if game not in GAME_STRATEGY:
            print(f"  -> no image strategy for game '{game}', skipping")
            no_strategy += 1
            continue

        image_url, confidence, _collector_number, artist, art_crop_url, flavor_text, oracle_text, mana_cost = find_reference_image(
            game, name, set_, set_map, collector_number=fm.get("collector_number", "") or "")
        # Slightly longer sleep than the bulk prep loop — we're re-trying the cards Scryfall
        # already failed on once, so be polite.
        time.sleep(sleep_s)

        if not image_url:
            print(f"  -> still no image (strategy={GAME_STRATEGY[game]}), leaving flagged")
            still_failed += 1
            continue

        ext = url_extension(image_url)
        local_path = local_image_path(path, cards_dir, images_dir, ext)
        if not download_image(image_url, local_path, force=force):
            print(f"  -> got URL ({image_url}) but download failed, leaving flagged")
            still_failed += 1
            continue
        local_rel = str(local_path).replace("\\", "/")

        # Cache art_crop alongside the full card image when present.
        local_art_rel = ""
        if art_crop_url:
            art_ext = url_extension(art_crop_url)
            art_local_path = local_path.with_name(local_path.stem + "--art" + art_ext)
            if download_image(art_crop_url, art_local_path, force=force):
                local_art_rel = str(art_local_path).replace("\\", "/")

        text = path.read_text(encoding="utf-8")
        text = update_frontmatter_field(text, "reference_image", local_rel)
        text = update_frontmatter_field(text, "reference_image_source_url", image_url)
        text = update_frontmatter_field(text, "art_match_confidence", confidence)
        if artist:
            text = update_frontmatter_field(text, "artist", artist)
        if local_art_rel:
            text = update_frontmatter_field(text, "art_crop_image", local_art_rel)
            text = update_frontmatter_field(text, "art_crop_source_url", art_crop_url)
        if flavor_text:
            text = update_frontmatter_field(text, "flavor_text", flavor_text)
        if oracle_text:
            text = update_frontmatter_field(text, "oracle_text", oracle_text)
        if confidence == "high":
            text = update_frontmatter_field(text, "needs_manual_review", "false")
            text = update_frontmatter_field(
                text, "manual_review_reason", "")
            print(f"  -> RECOVERED (high confidence): {local_rel}")
            recovered += 1
        else:
            # Keep flagged but with image now available — Alex can manually approve via triage later.
            text = update_frontmatter_field(
                text, "manual_review_reason",
                f"Set '{set_}' did not match a known set code or the card was not in that set; "
                "fuzzy fallback returned art that may be from a different printing.")
            print(f"  -> low-confidence URL cached, kept flagged for human review")
            low_conf += 1
        path.write_text(text, encoding="utf-8")
        # Normalize via bbl_schema chokepoint (wave 92.6).
        try:
            from bbl_schema import normalize_file as _normalize_file
            _normalize_file(path)
        except ImportError:
            pass

    print("\n=== retry-flagged report ===")
    print(f"  Recovered (high confidence):  {recovered}")
    print(f"  Low-confidence (image cached, still flagged): {low_conf}")
    print(f"  Still failed (no image):      {still_failed}")
    print(f"  Skipped (no game strategy):   {no_strategy}")
    return {"recovered": recovered, "low_conf": low_conf,
            "still_failed": still_failed, "no_strategy": no_strategy}


def main():
    global SCRYFALL_SLEEP
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cards-dir", type=Path, default=Path(DEFAULT_CARDS_DIR))
    ap.add_argument("--images-dir", type=Path, default=Path(DEFAULT_IMAGES_DIR),
                    help=f"Local image cache directory (default {DEFAULT_IMAGES_DIR})")
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                    help=f"Max cards to process this run (default {DEFAULT_LIMIT})")
    ap.add_argument("--game", type=str, default=None,
                    help='Process only one game (e.g. "Magic: The Gathering" or "Pokemon")')
    ap.add_argument("--dry-run", action="store_true",
                    help="Look up images and prepare prompts without writing to disk.")
    ap.add_argument("--force", action="store_true",
                    help="Re-enrich even cards that already have tags_hub; re-download cached images")
    ap.add_argument("--list-models", action="store_true",
                    help="Watch signal: probe the DeepSeek hosted API for served model IDs (per memory "
                         "bbl-deepseek-vision-watch). When a vision model appears here without 'beta', "
                         "Plan A's hosted-vision pipeline becomes a viable alternative to the current "
                         "Claude-subagent path. Exits after printing.")
    ap.add_argument("--prepare-only", action="store_true",
                    help="Image fetch + cache + frontmatter stamp only. Leaves tags_hub empty as the "
                         "signal for the .claude/agents/bbl-researcher.md subagent to pick up "
                         "(via `python bbl_queue.py`). This is the standard mode since wave 92.5.")
    ap.add_argument("--scryfall-sleep", type=float, default=SCRYFALL_SLEEP,
                    help=f"Seconds between Scryfall calls in --prepare-only / vision flows "
                         f"(default {SCRYFALL_SLEEP}). Bump to ~1.0 for long sweeps after a 429 burst, "
                         "or to be extra polite on multi-hundred-card runs. Does not affect --retry-flagged "
                         "(which has its own --retry-sleep flag).")
    ap.add_argument("--refresh-set-map", action="store_true",
                    help="Re-fetch the Scryfall /sets endpoint and rewrite reports/scryfall_sets.json. "
                         "Use this when set lookups fail for sets that should obviously match "
                         "(e.g. cached map is stale). Safe to run any time; just one API call.")
    ap.add_argument("--retry-flagged", action="store_true",
                    help="Walk every card with needs_manual_review: true and re-run the image lookup. "
                         "Many flagged cards are transient Scryfall failures rather than real misses — "
                         "this pass recovers them. Uses a gentler sleep (--retry-sleep) and re-stamps "
                         "successful matches. Cards with low-confidence fallback URLs stay flagged "
                         "(image cached) so a human reviewer can approve. Doesn't talk to DeepSeek.")
    ap.add_argument("--retry-sleep", type=float, default=0.25,
                    help="Seconds to sleep between Scryfall calls in --retry-flagged mode (default 0.25).")
    ap.add_argument("--set", dest="set_filter", default=None,
                    help='In --retry-flagged mode, restrict to one set (case-insensitive match against frontmatter `set:`).')
    args = ap.parse_args()

    load_env()
    api_key = os.environ.get("DEEPSEEK_API_KEY")

    if args.list_models:
        if not api_key:
            print("ERROR: DEEPSEEK_API_KEY not found in env or .env.local", file=sys.stderr)
            sys.exit(1)
        ids = list_deepseek_models(api_key)
        if not ids:
            print("(no models returned — check error above)")
            sys.exit(1)
        print("DeepSeek hosted-API model IDs:")
        for mid in ids:
            print(f"  - {mid}")
        sys.exit(0)

    # --prepare-only doesn't talk to DeepSeek at all, so no API key required.
    if not api_key and not args.dry_run and not args.prepare_only:
        print("ERROR: DEEPSEEK_API_KEY not found in env or .env.local", file=sys.stderr)
        sys.exit(1)

    if not args.cards_dir.exists():
        print(f"ERROR: cards dir not found: {args.cards_dir}", file=sys.stderr)
        sys.exit(1)

    SCRYFALL_SLEEP = args.scryfall_sleep
    if SCRYFALL_SLEEP != 0.1:
        print(f"Scryfall inter-request sleep set to {SCRYFALL_SLEEP}s")

    if args.refresh_set_map:
        if SCRYFALL_SET_CACHE.exists():
            SCRYFALL_SET_CACHE.unlink()
            print(f"Removed stale {SCRYFALL_SET_CACHE}")
        new_map = fetch_scryfall_set_map()
        print(f"Refreshed set map: {len(new_map)} entries written to {SCRYFALL_SET_CACHE}")
        # Quick sanity check: see if the entries we know we want are present.
        for k in ("mystery booster", "magic 2014", "throne of eldraine", "zendikar rising"):
            print(f"  {k!r}: {new_map.get(k, '(missing)')!r}")
        sys.exit(0)

    if args.retry_flagged:
        retry_flagged(args.cards_dir, args.images_dir,
                      args.game, args.set_filter, args.retry_sleep, args.force)
        sys.exit(0)

    report = process(args.cards_dir, args.images_dir, args.limit, args.game,
                     api_key or "", args.dry_run, args.force,
                     prepare_only=args.prepare_only)

    print("\n=== researchbot run report ===")
    print(f"  Processed:                {report['processed']}")
    print(f"  Prepared for vision:      {report['prepared_for_vision']}")
    print(f"  Skipped (already enriched): {report['skipped_enriched']}")
    print(f"  Skipped (no image found): {report['skipped_no_image']}")
    print(f"  Skipped (no strategy):    {report['skipped_no_strategy']}")
    print(f"  Deferred (low confidence): {report['deferred_low_confidence']}")
    print(f"  Errors:                   {report['errors']}")
    if report["manual_review_queue"]:
        print(f"\n  Manual review queue ({len(report['manual_review_queue'])} cards):")
        for f in report["manual_review_queue"][:20]:
            print(f"    - {f}")
        if len(report["manual_review_queue"]) > 20:
            print(f"    ... +{len(report['manual_review_queue']) - 20} more")
    if report["ip_flagged"]:
        print(f"\n  IP verification needed ({len(report['ip_flagged'])}):")
        for f in report["ip_flagged"]:
            print(f"    - {f}")


if __name__ == "__main__":
    main()
