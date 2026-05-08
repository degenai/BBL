"""One-shot Phase 1 applier — writes 3 hand-curated vision analyses to card MDs.
Re-runnable: also downloads hi-res PNGs to images/ and stores local paths."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from researchbot import update_card, download_image, local_image_path, url_extension

CARDS_DIR = Path("cards")
IMAGES_DIR = Path("images")

CARDS = [
    {
        "path": "cards/magic-the-gathering/alara-reborn/no-num-vectis-dominator.md",
        "url": "https://cards.scryfall.io/png/front/1/c/1cfb7589-a53e-4580-bd92-641fd4785934.png?1562640010",
        "art_confidence": "high",
        "manual_review_reason": "",
        "vision": {
            "subject": "A robed human wizard standing atop the brow of a colossal dormant construct, casting magic with a raised hand emitting brilliant white-yellow light",
            "subject_known_ip": False,
            "suspected_ip": "",
            "ip_confidence": "none",
            "ip_verified": False,
            "description": (
                "A wizard in dark blue-black robes and ornate plated armor stands small but central "
                "atop the massive head/brow of a slumbering tan-and-gold construct that fills most "
                "of the lower frame. The wizard raises one arm to channel a brilliant beam of "
                "white-yellow light. A large pale-blue luminous orb (the construct's eye?) is "
                "visible at lower right, suggesting the colossus is sentient and being controlled. "
                "Sky is saturated yellow-gold with abstract mountainous forms in the distance. "
                "Strong vertical, dramatic, dominant composition."
            ),
            "facing": "three-quarter",
            "composition": "wide",
            "mode": "scene",
            "figure_count": "solo",
            "foreground": "Slumbering golden-tan stone construct fills the frame; a glowing pale-blue orb visible at lower right",
            "foreground_palette": ["ochre", "gold", "tan", "pale blue"],
            "background": "Saturated yellow-gold sky over abstract distant terrain",
            "background_palette": ["yellow", "gold", "ochre"],
            "setting": "other",
            "architecture": "none",
            "time_of_day": "indeterminate",
            "weather": "none",
            "mood": "sublime",
            "genre_cues": ["fantasy", "painterly", "high-fantasy"],
            "lighting": "backlit",
            "objects": ["robe", "plate-armor", "spell-light"],
            "animals_creatures": ["dormant construct/colossus"],
            "food_drink": [],
            "clothing_style": "armor",
            "iconography": [],
            "emotion": "focused, dominating, imperious",
            "tags_hub": ["wizard", "spellcasting", "colossus", "psychic-dominance", "golden-light", "robed-figure"],
            "tags_filter": ["solo", "wide-shot", "three-quarter-facing", "scene-mode", "artifact-creature", "multicolor-white-black", "named-character"],
        },
    },
    {
        "path": "cards/magic-the-gathering/core-set-2021/65-roaming-ghostlight.md",
        "url": "https://cards.scryfall.io/png/front/4/6/469a2b07-1ab4-450b-a29a-35b8907bfc65.png?1706239830",
        "art_confidence": "low",
        "manual_review_reason": "Scryfall fuzzy lookup returned the Ravnica Clue Edition (CLU) printing; the inventory says Core Set 2021 (M21). Visual specifics may not match the printing actually owned.",
        "vision": {
            "subject": "A formless luminous spirit composed of a bright white-blue orb at center surrounded by translucent flowing veils and chains tipped with smaller glowing spheres",
            "subject_known_ip": False,
            "suspected_ip": "",
            "ip_confidence": "none",
            "ip_verified": False,
            "description": (
                "Central brilliant white-blue orb of light radiates outward through translucent "
                "flowing veils. Several chains hang downward from the spirit's body, each ending "
                "in smaller dimmer orbs. The figure floats in a dark cloudy void scattered with "
                "motes of light. Strong blue/teal palette with a luminous white core. Mood is "
                "melancholy, drifting, ethereal — a soul wandering. (Note: image is Ravnica: "
                "Clue Edition reprint art; original Core 2021 art may differ.)"
            ),
            "facing": "n/a",
            "composition": "mid-shot",
            "mode": "abstract",
            "figure_count": "solo",
            "foreground": "Bright luminous orb with translucent veils and downward-trailing chains tipped with smaller spheres",
            "foreground_palette": ["white", "pale blue", "teal"],
            "background": "Dark cloudy void scattered with small bright motes",
            "background_palette": ["black", "deep blue", "dark teal"],
            "setting": "void",
            "architecture": "none",
            "time_of_day": "night",
            "weather": "fog",
            "mood": "melancholy",
            "genre_cues": ["fantasy", "ethereal", "painterly"],
            "lighting": "luminous",
            "objects": ["chains", "veils", "orbs"],
            "animals_creatures": ["spirit"],
            "food_drink": [],
            "clothing_style": "none",
            "iconography": [],
            "emotion": "mournful, drifting, untethered",
            "tags_hub": ["ghost", "spirit", "chains", "ethereal", "melancholy", "blue-magic"],
            "tags_filter": ["solo", "mid-shot", "abstract-mode", "no-face", "blue-mono", "creature-spirit", "flying"],
        },
    },
    {
        "path": "cards/magic-the-gathering/invasion/no-num-smoldering-tar.md",
        "url": "https://cards.scryfall.io/png/front/f/c/fcdc55c0-c8ac-49d5-969b-9bf0ee8e696c.png?1562946036",
        "art_confidence": "high",
        "manual_review_reason": "",
        "vision": {
            "subject": "An armored woman in a tall pointed conical headdress stands frontally in a ritual chamber holding a disembodied hand, surrounded by smoking braziers",
            "subject_known_ip": False,
            "suspected_ip": "",
            "ip_confidence": "none",
            "ip_verified": False,
            "description": (
                "A frontally-posed woman dominates the composition. She wears segmented dark "
                "armor with reddish accents and multiple buckled straps, plus a tall pointed "
                "black-and-red conical headdress. Her gloved left hand holds a small "
                "severed/disembodied hand. Several short pedestal-braziers flank her, emitting "
                "thick rising pale-grey smoke columns. The background is a saturated deep red — "
                "flames, void, or hellish glow. Aesthetic is sinister-ritualistic, witchy, "
                "alchemical, high-fantasy classic."
            ),
            "facing": "forward",
            "composition": "mid-shot",
            "mode": "portrait",
            "figure_count": "solo",
            "foreground": "Armored ritualist with conical headdress holding a severed hand; standing braziers flank her emitting thick smoke columns",
            "foreground_palette": ["dark brown", "red-brown", "black", "dull silver"],
            "background": "Saturated deep red wall of light with vertical pale smoke pillars",
            "background_palette": ["deep red", "crimson", "black smoke", "grey"],
            "setting": "indoor",
            "architecture": "none",
            "time_of_day": "indeterminate",
            "weather": "smoke",
            "mood": "grim",
            "genre_cues": ["fantasy", "painterly", "high-fantasy"],
            "lighting": "ambient",
            "objects": ["braziers", "severed-hand", "conical-headdress", "armor", "smoke-pillars"],
            "animals_creatures": [],
            "food_drink": [],
            "clothing_style": "armor",
            "iconography": [],
            "emotion": "imperious, ritualistic, calmly cruel",
            "tags_hub": ["witch", "ritual", "smoke", "severed-hand", "blood-red", "sinister-priestess", "occult"],
            "tags_filter": ["solo", "mid-shot", "portrait-mode", "forward-facing", "enchantment", "black-red", "female-figure"],
        },
    },
]

for c in CARDS:
    p = Path(c["path"])
    url = c["url"]
    ext = url_extension(url)
    local_path = local_image_path(p, CARDS_DIR, IMAGES_DIR, ext)
    if download_image(url, local_path, force=True):
        local_rel = str(local_path).replace("\\", "/")
        print(f"  cached: {local_rel}")
    else:
        local_rel = ""
    # Roaming Ghostlight stays low-confidence: clear vision content so reviewer rebuilds it
    vision = c["vision"] if c.get("art_confidence", "high") == "high" else {
        "subject": "",
        "subject_known_ip": False,
        "suspected_ip": "",
        "ip_confidence": "none",
        "ip_verified": False,
        "description": "",
        "tags_hub": [],
        "tags_filter": [],
    }
    update_card(p, url, vision, dry_run=False,
                art_confidence=c.get("art_confidence", "high"),
                manual_review_reason=c.get("manual_review_reason", ""),
                local_image_rel=local_rel)
    print(f"  enriched: {p}")
print("done")
