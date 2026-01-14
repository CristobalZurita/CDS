"""Script pequeño para extraer imágenes y metadatos de `MANUAL_CIRUJANO.pdf`.
Requiere PyMuPDF (fitz): pip install PyMuPDF
Genera: scripts/brand_assets/ con imágenes extraídas y un JSON con metadatos.
"""
import fitz
from pathlib import Path
import json

PDF_PATH = Path("MANUAL_CIRUJANO.pdf")
OUT_DIR = Path("scripts/brand_assets")
OUT_DIR.mkdir(parents=True, exist_ok=True)

if not PDF_PATH.exists():
    print(f"PDF no encontrado: {PDF_PATH}")
    raise SystemExit(1)

print(f"Abriendo {PDF_PATH}...")
doc = fitz.open(PDF_PATH)
meta = {
    "page_count": doc.page_count,
    "fonts": set(),
    "images": []
}

for i in range(doc.page_count):
    page = doc.load_page(i)
    # extraer imágenes
    for img_index, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        ext = base_image.get("ext", "png")
        img_name = OUT_DIR / f"page_{i+1}_img_{img_index + 1}.{ext}"
        with open(img_name, "wb") as f:
            f.write(image_bytes)
        meta["images"].append(str(img_name))
        print(f"Saved image: {img_name}")
    # extraer fuentes / texto
    blocks = page.get_text("dict").get("blocks", [])
    for b in blocks:
        for line in b.get("lines", []):
            for span in line.get("spans", []):
                font = span.get("font")
                if font:
                    meta["fonts"].add(font)

# serializar fuentes
meta["fonts"] = sorted(list(meta["fonts"]))
with open(OUT_DIR / "meta.json", "w") as f:
    json.dump(meta, f, indent=2)

print("Extracción finalizada. Archivos en scripts/brand_assets/")
print(json.dumps(meta, indent=2))
