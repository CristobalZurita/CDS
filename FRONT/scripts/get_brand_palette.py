"""Extrae colores dominantes de las imágenes extraídas del manual.
Genera scripts/brand_assets/palette.json con colores en formato hex.
"""
from PIL import Image
from pathlib import Path
import json

IN_DIR = Path("scripts/brand_assets")
OUT_FILE = IN_DIR / "palette.json"

images = list(IN_DIR.glob("*.jpeg"))
if not images:
    print("No images found to analyze.")
    raise SystemExit(1)

def get_top_colors(img_path, n=5):
    img = Image.open(img_path).convert('RGBA')
    img = img.resize((200, 200))
    # remove transparent pixels
    pixels = [p for p in img.getdata() if p[3] > 0]
    # build histogram
    counts = {}
    for r,g,b,a in pixels:
        key = (r,g,b)
        counts[key] = counts.get(key, 0) + 1
    sorted_colors = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top = [c[0] for c in sorted_colors[:n]]
    return top

palette = {}
for img in images:
    top = get_top_colors(img, n=6)
    hex_colors = ['#{:02x}{:02x}{:02x}'.format(r,g,b) for r,g,b in top]
    palette[str(img.name)] = hex_colors

with open(OUT_FILE, 'w') as f:
    json.dump(palette, f, indent=2)

print(f"Palette written to {OUT_FILE}")
print(json.dumps(palette, indent=2))
