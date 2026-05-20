"""Strip ` (#NNN)` Pokedex hash-suffixes from suspected_ip values.

Per Nurse Joy wave-157 triage (reports/triage_prescriptions/suspected-ip-hash-suffix-cleanup.json):
38 card MDs + 38 vision-pending JSONs carry `suspected_ip: "Amoonguss (#591)"`-form values.
Obsidian reads `#591` inside the scalar as a tag fragment -> phantom numeric tag-nodes.

This scrub only touches lines/values that actually contain a `(#NNN)` group, and strips
ONLY that group -- it does not de-quote anything, so a colon-bearing name (e.g. Type: Null)
that legitimately needs quotes is left intact. Idempotent; safe to re-run.
"""
import glob
import json
import re
from pathlib import Path

HASH = re.compile(r"\s*\(#\d+\)")

md_patched = []
for fpath in glob.glob("cards/**/*.md", recursive=True):
    p = Path(fpath)
    text = p.read_text(encoding="utf-8")
    new = re.sub(
        r"^suspected_ip:.*\(#\d+\).*$",
        lambda m: HASH.sub("", m.group(0)),
        text,
        flags=re.MULTILINE,
    )
    if new != text:
        p.write_text(new, encoding="utf-8")
        md_patched.append(fpath)

json_patched = []
for fpath in glob.glob("reports/vision_pending/**/*.json", recursive=True):
    p = Path(fpath)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        continue
    val = data.get("suspected_ip")
    if not isinstance(val, str) or "(#" not in val:
        continue
    new_val = HASH.sub("", val).strip()
    if new_val != val:
        data["suspected_ip"] = new_val
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        json_patched.append((fpath, val, new_val))

print(f"card MDs patched: {len(md_patched)}")
for f in md_patched:
    print(f"  {f}")
print(f"vision JSONs patched: {len(json_patched)}")
for f, old, new in json_patched:
    print(f"  {f}: {old!r} -> {new!r}")
