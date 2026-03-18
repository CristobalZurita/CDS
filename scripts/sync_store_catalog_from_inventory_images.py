#!/usr/bin/env python3
"""
Sincroniza el catalogo de tienda usando media_assets como fuente primaria
y CDS_VUE3_ZERO/public/images/INVENTARIO solo como fallback controlado.

- Reutiliza productos existentes cuando el nombre/SKU calza con la imagen.
- Si no existe un producto razonable, crea uno derivado del nombre del archivo.
- Publica el producto en tienda y asigna un precio base de 1000 CLP si aun no tiene precio.
- No inventa stock: conserva cantidades reales o crea stock en 0 para items nuevos.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
DEFAULT_DB_PATH = BACKEND_ROOT / "cirujano.db"

os.environ.setdefault("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
os.environ.setdefault("ENVIRONMENT", "development")
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.database import SessionLocal  # type: ignore  # noqa: E402
from app.models.category import Category  # type: ignore  # noqa: E402
from app.models.inventory import Product  # type: ignore  # noqa: E402
from app.models.media import MediaAsset  # type: ignore  # noqa: E402
from app.models.stock import Stock  # type: ignore  # noqa: E402
from app.services.cloudinary_service import build_legacy_local_path, extract_filename_from_local_path  # type: ignore  # noqa: E402


IMAGE_DIR = ROOT / "CDS_VUE3_ZERO" / "public" / "images" / "INVENTARIO"
INVENTORY_LEGACY_PREFIX = build_legacy_local_path("INVENTARIO")
GENERIC_PRICE = 1000
STEM_PREFIXES = (
    "CONECTOR_",
    "DIODO_",
    "CAPACITOR_",
    "SWITCH_",
    "MICRO_",
    "PANTALLA_",
    "RESISTENCIA_",
)
STEM_EQUIVALENTS: dict[str, tuple[str, ...]] = {
    "CAPACITOR_CERAMICO": ("CAP_C", "CAPACITOR"),
    "CAPACITOR_ELECTROLITICO": ("CAP_E",),
    "CONECTOR_MIDI_PCB": ("MIDI_CON",),
    "CONECTOR_MIDI_VOLANTE": ("MIDI_CONECTOR_VOLANTE",),
    "PANTALLA_OLED": ("OLED", "OLED2"),
}


@dataclass(frozen=True)
class ImageRule:
    category: str
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class CatalogImage:
    name: str
    local_url: str


FILE_RULES: dict[str, ImageRule] = {
    "3PDT": ImageRule("otros", ("3PDT", "SWITCH 3PDT")),
    "AUDIO_ADAPTADOR_3_5_A_6_3": ImageRule("conectores", ("ADAPTADOR 3.5 A 6.3", "ADAPTADOR TS", "ADAPTADOR TRS")),
    "AUDIO_JACK_CHASIS_MONO_6_3": ImageRule("conectores", ("JACK 1/4 MONO", "JACK 6.3 MONO")),
    "AUDIO_JACK_CHASIS_ST_6_3": ImageRule("conectores", ("JACK 1/4 ESTEREO", "JACK 6.3 ESTEREO")),
    "AUDIO_PLUG_ST_6_3": ImageRule("conectores", ("PLUG 6.3 ESTEREO", "JACK 1/4 ESTEREO")),
    "ARDUINO-FIXED": ImageRule("ic's", ("ARDUINO",)),
    "BOTON_CHICO_MPC": ImageRule("otros", ("BOTON PULSADOR", "PULSADOR 6X6")),
    "BOTON_GRANDE_B_MPC": ImageRule("otros", ("BOTON PULSADOR", "PULSADOR 12X12")),
    "BOTON_GRANDE_R_MICROKORG": ImageRule("otros", ("BOTON PULSADOR",)),
    "BOTON_GRANDE_R_MPC": ImageRule("otros", ("BOTON PULSADOR",)),
    "CAP_C": ImageRule("capacitores", ("CAPACITOR CERAMICO",)),
    "CAP_E": ImageRule("capacitores electroliticos", ("CAPACITOR ELECTROLITICO",)),
    "DESLIZANTE_NEGRO": ImageRule("otros", ("DESLIZANTE", "POTENCIOMETRO DESLIZANTE")),
    "DESLIZANTE_VERDE": ImageRule("otros", ("DESLIZANTE", "POTENCIOMETRO DESLIZANTE")),
    "DPDT": ImageRule("otros", ("DPDT", "SWITCH DPDT")),
    "DISPLAY16X2": ImageRule("ic's", ("DISPLAY 16X2", "LCD 16X2")),
    "ENCODER_EC11": ImageRule("otros", ("ENCODER", "EC11")),
    "ESP32": ImageRule("ic's", ("ESP32", "ESP32 WROOM")),
    "FUSIBLE": ImageRule("otros", ("FUSIBLE", "PORTAFUSIBLE")),
    "INTEGRADO": ImageRule("ic's", ("IC", "INTEGRADO")),
    "JACK_DC_2_1_PCB": ImageRule("conectores", ("JACK DC 2.1",)),
    "JACK_DC_CHASIS_2_1_PCB": ImageRule("conectores", ("JACK DC 2.1", "PANEL")),
    "KNOB_METAL": ImageRule("otros", ("KNOB", "PERILLA")),
    "KNOB_PLASTICO": ImageRule("otros", ("KNOB", "PERILLA")),
    "KNOB_REDONDO_ONDULADO": ImageRule("otros", ("KNOB", "PERILLA")),
    "LED_3MM": ImageRule("diodo led", ("LED 3MM",)),
    "LED_5MM": ImageRule("diodo led", ("LED 5MM",)),
    "LED_BI_5MM_3_PIN": ImageRule("diodo led", ("LED BICOLOR 5MM", "LED BI 5MM")),
    "LED_BLINK_5MM_AZUL": ImageRule("diodo led", ("LED BLINK 5MM", "LED AZUL 5MM")),
    "LED_RGB_3MM_2PIN": ImageRule("diodo led", ("LED RGB 3MM", "LED RGB 5MM")),
    "MIDI_CON": ImageRule("conectores", ("DIN5 MIDI HEMBRA", "MIDI HEMBRA")),
    "MIDI_CONECTOR_VOLANTE": ImageRule("conectores", ("DIN5 MIDI MACHO", "MIDI MACHO")),
    "OLED2": ImageRule("ic's", ("OLED",)),
    "PCB_ANGOSTA": ImageRule("otros", ("PCB",)),
    "PCB_KIT": ImageRule("otros", ("PCB",)),
    "PCB_KIT_02": ImageRule("otros", ("PCB",)),
    "PCB_KIT_03": ImageRule("otros", ("PCB",)),
    "PIEZO_35": ImageRule("otros", ("PIEZO",)),
    "PLUG_DC_TORNILLO": ImageRule("conectores", ("PLUG DC",)),
    "PLUG_PLASTICO_AUDIO_3_5": ImageRule("conectores", ("JACK 3.5", "PLUG 3.5")),
    "PLUG__METAL_AUDIO_3_5": ImageRule("conectores", ("JACK 3.5", "PLUG 3.5")),
    "POTE_MONO_RK09": ImageRule("otros", ("POTENCIOMETRO", "RK09", "MONO")),
    "POTE_MONO_WH148": ImageRule("otros", ("POTENCIOMETRO", "WH148", "MONO")),
    "POTE_ST_WH148": ImageRule("otros", ("POTENCIOMETRO", "WH148", "ESTEREO")),
    "PULSADOR_12X12_CUADRADO": ImageRule("otros", ("BOTON PULSADOR 12X12", "PULSADOR 12X12")),
    "PULSADOR_12X12_REDONDO": ImageRule("otros", ("BOTON PULSADOR 12X12", "PULSADOR 12X12")),
    "PULSADOR_6X6_2_PIN": ImageRule("otros", ("PULSADOR 6X6 2PIN", "BOTON PULSADOR 6X6")),
    "PULSADOR_6X6_4_PIN": ImageRule("otros", ("PULSADOR 6X6 4PIN", "BOTON PULSADOR 6X6")),
    "RCA_CHASIS": ImageRule("conectores", ("RCA HEMBRA",)),
    "RCA_PLUG": ImageRule("conectores", ("RCA MACHO",)),
    "RESISTENCIA": ImageRule("resistencias", ("RESISTENCIA",)),
    "SPDT": ImageRule("otros", ("SPDT", "SWITCH SPDT")),
    "SWITCH_ROTATORIO_LORNIN": ImageRule("otros", ("SWITCH ROTATORIO",)),
    "TRANSISTOR_TO220": ImageRule("transistores", ("TRANSISTOR", "MOSFET", "TO220")),
    "TRANSISTOR_TO92": ImageRule("transistores", ("TRANSISTOR", "TO92")),
    "TRIMPOT": ImageRule("otros", ("TRIMPOT", "TRIM POT")),
    "USB_B": ImageRule("conectores", ("USB TIPO B",)),
    "USB_MICRO": ImageRule("conectores", ("MICRO USB", "USB MICRO")),
    "USB_MINI_HORIZONTAL": ImageRule("conectores", ("MINI USB",)),
    "USB_MINI_VERTICAL": ImageRule("conectores", ("MINI USB",)),
    "BOBINA": ImageRule("otros", ("BOBINA", "INDUCTOR")),
}

def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def pretty_name_from_stem(stem: str) -> str:
    raw = stem.replace(".jpg", "")
    raw = raw.replace("-", " ").replace("_", " ")
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw.title()


def preferred_name(stem: str) -> str:
    aliases = candidate_aliases(stem)
    label = ""
    if aliases:
        label = aliases[0].strip()
        if len(label) <= 2 and len(aliases) > 1:
            label = aliases[1].strip()
        if label:
            return label.title()
    return pretty_name_from_stem(stem)


def parse_meta(description: str | None) -> tuple[dict, str | None]:
    text = str(description or "").strip()
    if not text:
        return {}, None
    if not text.startswith("{"):
        return {}, text
    try:
        payload = json.loads(text)
    except Exception:
        return {}, text
    if not isinstance(payload, dict):
        return {}, text
    plain = str(payload.get("text") or "").strip() or None
    return payload, plain


def dump_meta(meta: dict, plain_text: str | None) -> str | None:
    payload = dict(meta)
    if plain_text:
        payload["text"] = plain_text
    if not payload:
        return plain_text
    return json.dumps(payload, ensure_ascii=False)


def category_name_map(session) -> dict[str, Category]:
    rows = session.query(Category).all()
    mapping: dict[str, Category] = {}
    for row in rows:
        mapping[normalize_text(row.name)] = row
    return mapping


def infer_category_key(stem: str) -> str:
    rule = FILE_RULES.get(stem)
    if rule:
        return normalize_text(rule.category)
    if stem == "CAPACITOR_ELECTROLITICO":
        return normalize_text("Capacitores Electroliticos")
    if stem == "CAPACITOR_CERAMICO":
        return normalize_text("Capacitores")
    if stem.startswith("CONECTOR"):
        return normalize_text("conectores")
    if stem.startswith("DIODO"):
        return normalize_text("diodo led")
    if stem.startswith("CAPACITOR"):
        return normalize_text("capacitores")
    if stem.startswith("MICRO") or stem.startswith("PANTALLA") or stem.startswith("DISPLAY"):
        return normalize_text("Ic's")
    if stem.startswith("SWITCH"):
        return normalize_text("otros")
    if stem.startswith("CAP_E"):
        return normalize_text("Capacitores Electroliticos")
    if stem.startswith("CAP"):
        return normalize_text("Capacitores")
    if stem.startswith("LED"):
        return normalize_text("Diodo Led")
    if stem.startswith("USB") or "JACK" in stem or "MIDI" in stem or "RCA" in stem or "PLUG" in stem:
        return normalize_text("conectores")
    if stem.startswith("TRANSISTOR"):
        return normalize_text("Transistores")
    if stem.startswith("RESISTENCIA"):
        return normalize_text("Resistencias")
    if stem.startswith("ARDUINO") or stem.startswith("ESP32") or stem.startswith("OLED") or stem.startswith("DISPLAY"):
        return normalize_text("Ic's")
    return normalize_text("otros")


def candidate_aliases(stem: str) -> tuple[str, ...]:
    rule = FILE_RULES.get(stem)
    if rule and rule.aliases:
        return rule.aliases
    return (pretty_name_from_stem(stem),)


def stem_variants(stem: str) -> set[str]:
    variants = {normalize_text(stem)}
    changed = True
    while changed:
        changed = False
        current = list(variants)
        for value in current:
            for prefix in STEM_PREFIXES:
                if value.startswith(prefix):
                    stripped = value[len(prefix):]
                    if stripped and stripped not in variants:
                        variants.add(stripped)
                        changed = True
        for value in current:
            for alias in STEM_EQUIVALENTS.get(value, ()):
                normalized_alias = normalize_text(alias)
                if normalized_alias and normalized_alias not in variants:
                    variants.add(normalized_alias)
                    changed = True
    return {value for value in variants if value}


def _product_identity_variants(product: Product) -> set[str]:
    variants = set()
    normalized_sku = normalize_text(product.sku)
    normalized_name = normalize_text(product.name)

    if normalized_sku:
        variants.add(normalized_sku)
        sku_parts = normalized_sku.split("_")
        if len(sku_parts) > 1:
            variants.add("_".join(sku_parts[1:]))
    if normalized_name:
        variants.add(normalized_name)
    return {value for value in variants if value}


def exact_alias_match(stem: str, product: Product) -> bool:
    aliases = {normalize_text(alias) for alias in candidate_aliases(stem)}
    aliases.update(stem_variants(stem))
    aliases = {alias for alias in aliases if alias}
    product_variants = _product_identity_variants(product)
    return any(alias in product_variants for alias in aliases)


def ensure_meta_flags(product: Product) -> None:
    meta, plain_text = parse_meta(product.description)
    # Preserve explicit manual flags; only set defaults when keys are missing.
    if "enabled" not in meta:
        meta["enabled"] = True
    if "store_visible" not in meta:
        meta["store_visible"] = True
    product.description = dump_meta(meta, plain_text)


def ensure_stock_row(session, product: Product) -> Stock:
    stock = (
        session.query(Stock)
        .filter(
            Stock.component_table == "products",
            Stock.component_id == product.id,
        )
        .first()
    )
    if stock:
        return stock
    stock = Stock(
        component_table="products",
        component_id=product.id,
        quantity=int(product.quantity or 0),
        minimum_stock=int(product.min_quantity or 0),
    )
    session.add(stock)
    session.flush()
    return stock


def _normalized_stem_from_filename(filename: str) -> str:
    return normalize_text(Path(filename).stem.replace(".jpg", "").replace(".JPG", ""))


def _inventory_image_url(filename: str) -> str:
    return build_legacy_local_path(f"INVENTARIO/{filename}")


def _media_asset_filename(asset: MediaAsset) -> str:
    original = str(asset.original_filename or "").strip()
    asset_format = str(asset.format or "").strip().lstrip(".")

    if original:
        parsed = Path(original)
        if parsed.suffix:
            return parsed.name
        if asset_format:
            return f"{parsed.name}.{asset_format}"
        return parsed.name

    public_leaf = str(asset.public_id or "").split("/")[-1].strip()
    if not public_leaf:
        return ""
    if "." in public_leaf or not asset_format:
        return public_leaf
    return f"{public_leaf}.{asset_format}"


def load_inventory_images(session) -> list[CatalogImage]:
    assets = []
    for asset in session.query(MediaAsset).order_by(MediaAsset.id.asc()).all():
        folder = str(asset.folder or "").upper()
        public_id = str(asset.public_id or "").upper()
        if "INVENTARIO" not in folder and not public_id.startswith("INVENTARIO/"):
            continue
        filename = _media_asset_filename(asset)
        if not filename:
            continue
        assets.append(
            CatalogImage(
                name=filename,
                local_url=_inventory_image_url(filename),
            )
        )

    if assets:
        unique_assets: dict[str, CatalogImage] = {}
        for image in assets:
            unique_assets.setdefault(image.name, image)
        return sorted(unique_assets.values(), key=lambda image: image.name)

    if not IMAGE_DIR.exists():
        return []

    return [
        CatalogImage(
            name=path.name,
            local_url=_inventory_image_url(path.name),
        )
        for path in sorted(IMAGE_DIR.iterdir())
        if path.is_file()
    ]


def extract_inventory_image_name(image_url: str | None) -> str:
    return extract_filename_from_local_path(image_url or "", expected_relative_prefix="INVENTARIO")


def find_best_image_match(filename: str, images: list[CatalogImage]) -> CatalogImage | None:
    missing_variants = stem_variants(_normalized_stem_from_filename(filename))
    for image in images:
        live_variants = stem_variants(_normalized_stem_from_filename(image.name))
        if missing_variants & live_variants:
            return image
    return None


def build_catalog_status() -> dict:
    session = SessionLocal()
    try:
        images = load_inventory_images(session)
        files = sorted(image.name for image in images)
        products = session.query(Product).filter(Product.image_url.like(f"{INVENTORY_LEGACY_PREFIX}/%")).all()

        linked_images = []
        explicit_store_visible = 0
        sellable_now = 0
        with_nonzero_stock = 0

        for product in products:
            image_name = extract_inventory_image_name(product.image_url)
            if image_name:
                linked_images.append(image_name)

            meta, _ = parse_meta(product.description)
            if meta.get("store_visible") is True:
                explicit_store_visible += 1

            stock = (
                session.query(Stock)
                .filter(
                    Stock.component_table == "products",
                    Stock.component_id == product.id,
                )
                .first()
            )
            quantity = int((stock.quantity if stock else product.quantity) or 0)
            min_stock = int((stock.minimum_stock if stock else product.min_quantity) or 0)

            available_stock = quantity
            if stock:
                available_stock = int(
                    stock.quantity
                    - stock.quantity_reserved
                    - stock.quantity_in_transit
                    - stock.quantity_damaged
                    - stock.quantity_under_review
                    - stock.quantity_internal_use
                    - stock.quantity_in_work
                )

            sellable_stock = max(int(available_stock or 0) - int(min_stock or 0), 0)
            if quantity > 0:
                with_nonzero_stock += 1
            if sellable_stock > 0:
                sellable_now += 1

        file_set = set(files)
        linked_set = set(linked_images)

        return {
            "files_count": len(files),
            "linked_products_count": len(products),
            "explicit_store_visible_count": explicit_store_visible,
            "with_nonzero_stock_count": with_nonzero_stock,
            "sellable_now_count": sellable_now,
            "pending_images_count": len(file_set - linked_set),
            "orphan_rows_count": len(linked_set - file_set),
            "pending_images": sorted(file_set - linked_set),
            "orphan_rows": sorted(linked_set - file_set),
        }
    finally:
        session.close()


def match_existing_product(session, stem: str, used_product_ids: set[int]) -> Product | None:
    for product in session.query(Product).all():
        if int(product.id) in used_product_ids:
            continue
        if exact_alias_match(stem, product):
            return product
    return None


def create_product_from_image(session, stem: str, filename: str, categories_by_key: dict[str, Category]) -> Product:
    category_key = infer_category_key(stem)
    category = categories_by_key.get(category_key)
    if not category:
        category = categories_by_key[normalize_text("otros")]

    sku = normalize_text(stem)
    name = preferred_name(stem)
    meta = {
        "enabled": True,
        "store_visible": True,
        "text": name,
    }

    product = Product(
        category_id=category.id,
        name=name,
        sku=sku,
        description=json.dumps(meta, ensure_ascii=False),
        price=GENERIC_PRICE,
        quantity=0,
        min_quantity=0,
        image_url=_inventory_image_url(filename),
    )
    session.add(product)
    session.flush()
    ensure_stock_row(session, product)
    return product


def sync_catalog(apply_changes: bool) -> dict:
    session = SessionLocal()
    try:
        categories = session.query(Category).all()
        categories_by_key = category_name_map(session)

        images = load_inventory_images(session)

        matched = []
        created = []
        relinked = []
        cleared = []
        used_product_ids: set[int] = set()

        for image_path in images:
            stem = normalize_text(Path(image_path.name).stem.replace(".jpg", "").replace(".JPG", ""))
            product = match_existing_product(session, stem, used_product_ids)

            if product:
                product.image_url = image_path.local_url
                if int(product.price or 0) <= 0:
                    product.price = GENERIC_PRICE
                ensure_meta_flags(product)
                stock = ensure_stock_row(session, product)
                matched.append(
                    {
                        "image": image_path.name,
                        "product_id": product.id,
                        "sku": product.sku,
                        "name": product.name,
                        "stock": int(stock.quantity or 0),
                        "min_stock": int(stock.minimum_stock or 0),
                    }
                )
                used_product_ids.add(int(product.id))
                continue

            product = create_product_from_image(session, stem, image_path.name, categories_by_key)
            created.append(
                {
                    "image": image_path.name,
                    "product_id": product.id,
                    "sku": product.sku,
                    "name": product.name,
                }
            )
            used_product_ids.add(int(product.id))

        image_names = {image.name for image in images}
        linked_products = session.query(Product).filter(Product.image_url.like(f"{INVENTORY_LEGACY_PREFIX}/%")).all()
        for product in linked_products:
            current_name = extract_inventory_image_name(product.image_url)
            if not current_name or current_name in image_names:
                continue

            replacement = find_best_image_match(current_name, images)
            if replacement:
                product.image_url = replacement.local_url
                ensure_meta_flags(product)
                relinked.append(
                    {
                        "product_id": product.id,
                        "sku": product.sku,
                        "from": current_name,
                        "to": replacement.name,
                    }
                )
                continue

            product.image_url = None
            cleared.append(
                {
                    "product_id": product.id,
                    "sku": product.sku,
                    "from": current_name,
                }
            )

        if apply_changes:
            session.commit()
        else:
            session.rollback()

        return {
            "images": len(images),
            "matched": len(matched),
            "created": len(created),
            "relinked": len(relinked),
            "cleared": len(cleared),
            "matched_items": matched,
            "created_items": created,
            "relinked_items": relinked,
            "cleared_items": cleared,
        }
    finally:
        session.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincroniza catalogo de tienda desde media_assets con fallback local controlado de inventario")
    parser.add_argument("--apply", action="store_true", help="Aplica cambios sobre la DB")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}"),
        help="DATABASE_URL explícita para evitar apuntar a una DB equivocada",
    )
    args = parser.parse_args()

    os.environ["DATABASE_URL"] = args.database_url

    result = sync_catalog(apply_changes=args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
