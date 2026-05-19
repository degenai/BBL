import json
import glob
from pathlib import Path

src_dir = Path(r"C:\Users\alexa\Desktop\Diamondlegendz\bundle-previewer\michi-inserts\drone")
inserts = []
for meta_path in sorted(src_dir.glob("*.meta.json")):
    m = json.loads(meta_path.read_text(encoding="utf-8"))
    inserts.append({
        "image_file": m["image_file"],
        "creator_handle": m["creator_handle"],
        "source_url": m["source_url"],
        "panel_dimensions_slots": m["panel_dimensions_slots"],
        "theme_fit": m["theme_fit"],
        "permission_status": m["permission_status"],
    })

print(f"{len(inserts)} inserts")
out = src_dir / "_manifest.json"
out.write_text(json.dumps({"bundle_slug": "drone", "inserts": inserts}, indent=2),
               encoding="utf-8")
print(f"wrote: {out}")
