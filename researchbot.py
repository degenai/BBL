#!/usr/bin/env python3
"""
researchbot — Enrich card-node MDs with reference image + DeepSeek vision analysis.

For each card-node lacking enrichment:
  1. Fetch a canonical reference image (Scryfall for MTG, PokemonTCG API for Pokemon).
  2. Run DeepSeek V4 Pro vision analysis on the image with a structured prompt.
  3. Write reference_image, tags_hub, tags_filter, and a ## Vision section back.

Processes in quantity-DESC order so high-impact cards get enriched first.
Skips cards already enriched (tags_hub non-empty), unless --force.
One-time investment per unique card. Cost amortizes across all copies.

Usage:
    python researchbot.py [--cards-dir cards] [--limit N] [--game GAME]
                          [--dry-run] [--force]
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

# --- Configuration ---

DEFAULT_CARDS_DIR = "cards"
# Image cache lives INSIDE cards/ so it's visible to the Obsidian vault (which is
# rooted at cards/). PNG files aren't graphed by Obsidian (only .md files become
# nodes), so this doesn't pollute the card graph. The underscore prefix sorts the
# folder visually distinct from card-game directories.
DEFAULT_IMAGES_DIR = "cards/_images"
DEFAULT_LIMIT = 10  # default cap per run; bump explicitly when confident
DEEPSEEK_BASE = "https://api.deepseek.com"
DEEPSEEK_ENDPOINT = f"{DEEPSEEK_BASE}/chat/completions"
DEEPSEEK_MODELS_ENDPOINT = f"{DEEPSEEK_BASE}/models"
DEEPSEEK_MODEL = "deepseek-v4-pro"  # spec default; override with --model when API lags
SCRYFALL_API = "https://api.scryfall.com"
# Sleep between Scryfall calls. Default 0.1s honors their 50–100ms recommendation.
# Bump to 1.0+ for very long sweeps or when running shortly after a 429 burst.
# Set via --scryfall-sleep CLI flag.
SCRYFALL_SLEEP = 0.1
POKEMONTCG_API = "https://api.pokemontcg.io/v2"

USER_AGENT = "BBL-researchbot/0.1 (alex.adamczyk@gmail.com)"

# Map Collectr game name → image-source strategy
GAME_STRATEGY = {
    "Magic: The Gathering": "scryfall",
    "Pokemon": "pokemontcg",
    # Other games fall through with a warning until we wire APIs for them.
}


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
        out[k.strip()] = v.strip()
    return out


def update_frontmatter_field(text: str, field: str, value: str) -> str:
    """Replace existing field or insert before closing `---`."""
    pattern = rf"^{re.escape(field)}:.*$"
    if re.search(pattern, text, flags=re.MULTILINE):
        return re.sub(pattern, f"{field}: {value}", text, count=1, flags=re.MULTILINE)
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
                        set_map: dict | None = None) -> tuple[str | None, str]:
    """Returns (image_url, confidence). confidence in {'high','low','none'}.
    high = exact set matched, low = fuzzy fallback (art may be from wrong printing),
    none = no image found at all."""
    set_map = set_map if set_map is not None else fetch_scryfall_set_map()
    code = scryfall_set_code(set_name, set_map)
    # Strip Collectr quirks like trailing "(254)" before querying Scryfall.
    card_name = normalize_card_name_for_lookup(card_name)

    # Try set-specific lookup first
    if code:
        params = {"fuzzy": card_name, "set": code}
        url = f"{SCRYFALL_API}/cards/named?{urllib.parse.urlencode(params)}"
        data = http_get_json(url)
        time.sleep(SCRYFALL_SLEEP)
        if data and not data.get("status"):  # Scryfall returns {status: 404} on miss
            img = _extract_image(data)
            if img:
                return img, "high"

    # Fallback: fuzzy without set filter — art may be wrong printing
    params = {"fuzzy": card_name}
    url = f"{SCRYFALL_API}/cards/named?{urllib.parse.urlencode(params)}"
    data = http_get_json(url)
    time.sleep(SCRYFALL_SLEEP)
    if data and not data.get("status"):
        img = _extract_image(data)
        if img:
            return img, "low"
    return None, "none"


def find_image_pokemontcg(card_name: str, set_name: str = "") -> tuple[str | None, str]:
    """PokemonTCG.io v2 API. Returns (url, confidence). High = matched with set,
    low = matched name only, none = no match."""
    def _query(q: str) -> str | None:
        url = f"{POKEMONTCG_API}/cards?q={urllib.parse.quote(q)}&pageSize=1"
        data = http_get_json(url)
        time.sleep(0.2)
        if not data:
            return None
        cards = data.get("data") or []
        if not cards:
            return None
        images = cards[0].get("images") or {}
        return images.get("large") or images.get("small")

    if set_name:
        img = _query(f'name:"{card_name}" set.name:"{set_name}"')
        if img:
            return img, "high"
    img = _query(f'name:"{card_name}"')
    if img:
        return img, "low" if set_name else "high"
    return None, "none"


def find_reference_image(game: str, card_name: str, set_name: str,
                         set_map: dict | None = None) -> tuple[str | None, str]:
    strat = GAME_STRATEGY.get(game)
    if strat == "scryfall":
        return find_image_scryfall(card_name, set_name, set_map)
    if strat == "pokemontcg":
        return find_image_pokemontcg(card_name, set_name)
    return None, "none"


# --- DeepSeek vision call ---

VISION_SYSTEM = """You are a TCG card art analyst for Bulk Graph Bundler (BBL), a project that curates trading card singles into themed Discrete Lairs (small bundles) based on art and flavor.

Your job: read a reference image of one card and emit structured JSON describing it. Be specific and grounded in the image. NEVER invent character identities — if you suspect an IP character, mark suspected_ip with a confidence level and let a human verify.

Two-tier tag emission is critical:
- tags_hub: thematically rich, cross-cutting tags suitable for curated graph hubs (cat, sunset, pie, cozy, gothic, service-worker, labor, villain, comic-relief, fire, forest, ocean). Ask: "would I curate a Discrete Lair around this concept?"
- tags_filter: mechanical / structural / compositional tags (faces-left, 2-figures, mid-shot, solo-portrait, lifegain). Filter-only, never become hubs.

Return ONLY valid JSON, no preamble, no markdown fences."""

VISION_USER_TEMPLATE = """Card metadata (for context only; rely on image for analysis):
- name: {name}
- game: {game}
- set: {set}
- card_text: (not provided)

Analyze the artwork. Return JSON with this exact schema:

{{
  "subject": "<what's depicted; if a known IP character is clearly named or unmistakable, say so. Otherwise describe.>",
  "subject_known_ip": <true|false>,
  "suspected_ip": "<character name or empty string>",
  "ip_confidence": "<none|low|med|high>",
  "ip_verified": false,
  "description": "<one-paragraph visual description>",
  "facing": "<left|right|forward|away|three-quarter|n/a>",
  "composition": "<close-up|mid-shot|wide|scene>",
  "mode": "<portrait|action|narrative|abstract>",
  "figure_count": "<solo|duo|group|crowd|none>",
  "foreground": "<short>",
  "foreground_palette": ["<color>", "..."],
  "background": "<short>",
  "background_palette": ["<color>", "..."],
  "setting": "<forest|urban|desert|ocean|mountain|indoor|dungeon|space|void|other>",
  "architecture": "<gothic|ruined|modern|organic|none>",
  "time_of_day": "<dawn|day|sunset|twilight|night|magic-hour|indeterminate>",
  "weather": "<rain|snow|fog|fire|smoke|calm|clear|storm|none>",
  "mood": "<cozy|grim|comedic|sublime|horror|action|peaceful|other>",
  "genre_cues": ["<fantasy|sci-fi|anime|photoreal|cartoon|woodcut|watercolor|...>"],
  "lighting": "<harsh|soft|backlit|rim|ambient|chiaroscuro>",
  "objects": ["<object>", "..."],
  "animals_creatures": ["<creature>", "..."],
  "food_drink": ["<item>", "..."],
  "clothing_style": "<medieval|futuristic|casual|formal|armor|naked|none>",
  "iconography": ["<symbol>", "..."],
  "emotion": "<facial expression / body language read>",
  "tags_hub": ["<thematic-tag>", "..."],
  "tags_filter": ["<mechanical-or-structural-tag>", "..."]
}}"""


def deepseek_vision_call(api_key: str, image_url: str, name: str, game: str, set_: str,
                         model: str = DEEPSEEK_MODEL) -> dict | None:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": VISION_SYSTEM},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": VISION_USER_TEMPLATE.format(
                        name=name, game=game, set=set_)},
                ],
            },
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": USER_AGENT,
    }
    resp = http_post_json(DEEPSEEK_ENDPOINT, payload, headers)
    if not resp:
        return None
    try:
        content = resp["choices"][0]["message"]["content"]
        return json.loads(content)
    except (KeyError, json.JSONDecodeError, IndexError) as e:
        print(f"  [error] could not parse DeepSeek response: {e}", file=sys.stderr)
        return None


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
            api_key: str, dry_run: bool, force: bool, model: str = DEEPSEEK_MODEL,
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
        candidates.append((-qty, last_seen, path, fm))

    candidates.sort()
    candidates = candidates[:limit]

    print(f"\nProcessing {len(candidates)} cards (qty-priority, limit={limit})\n")

    for i, (_, _, path, fm) in enumerate(candidates, 1):
        name = fm.get("name", "")
        game = fm.get("game", "")
        set_ = fm.get("set", "")
        qty = fm.get("quantity", "?")
        print(f"[{i}/{len(candidates)}] qty={qty}  {game}  {name}")

        if game not in GAME_STRATEGY:
            print(f"  -> no image strategy for game '{game}', skipping")
            report["skipped_no_strategy"] += 1
            continue

        image_url, confidence = find_reference_image(game, name, set_, set_map)
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

        print(f"  -> image: {image_url}  (art_match: {confidence})")

        # Download to local cache (high-res). Skip on dry-run.
        local_rel = ""
        if not dry_run:
            ext = url_extension(image_url)
            local_path = local_image_path(path, cards_dir, images_dir, ext)
            if download_image(image_url, local_path, force=force):
                local_rel = str(local_path).replace("\\", "/")
                print(f"  -> cached: {local_rel}")

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
                path.write_text(text, encoding="utf-8")
                print(f"  -> prepared (image cached, awaiting vision subagent)")
            report["prepared_for_vision"] += 1
            continue

        if dry_run:
            print(f"  -> [dry-run] would run vision pass and update {path.name}")
            report["processed"] += 1
            continue

        vision = deepseek_vision_call(api_key, image_url, name, game, set_, model=model)
        if not vision:
            report["errors"] += 1
            continue

        if vision.get("suspected_ip") and vision.get("ip_confidence") in ("low", "med", "high") \
                and not vision.get("ip_verified"):
            report["ip_flagged"].append(f"{game} | {name} -> suspected: {vision['suspected_ip']} ({vision['ip_confidence']})")

        update_card(path, image_url, vision, dry_run=False, art_confidence="high",
                    local_image_rel=local_rel)
        print(f"  -> enriched: tags_hub={vision.get('tags_hub')[:5] if vision.get('tags_hub') else []}")
        report["processed"] += 1

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

        image_url, confidence = find_reference_image(game, name, set_, set_map)
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

        text = path.read_text(encoding="utf-8")
        text = update_frontmatter_field(text, "reference_image", local_rel)
        text = update_frontmatter_field(text, "reference_image_source_url", image_url)
        text = update_frontmatter_field(text, "art_match_confidence", confidence)
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
                    help="Look up images and prepare prompts but do not call DeepSeek")
    ap.add_argument("--force", action="store_true",
                    help="Re-enrich even cards that already have tags_hub; re-download cached images")
    ap.add_argument("--model", type=str, default=DEEPSEEK_MODEL,
                    help=f"DeepSeek model ID (default {DEEPSEEK_MODEL}). Use --list-models to see what the API actually serves.")
    ap.add_argument("--list-models", action="store_true",
                    help="Hit /models on the DeepSeek API and print the IDs it advertises, then exit.")
    ap.add_argument("--prepare-only", action="store_true",
                    help="Image fetch + cache + frontmatter stamp only. Skips DeepSeek call. "
                         "Leaves tags_hub empty as the signal for the bbl-researcher Claude Code subagent.")
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
                     api_key or "", args.dry_run, args.force, model=args.model,
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
