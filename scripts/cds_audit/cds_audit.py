#!/usr/bin/env python3
"""CDS audit: document -> DB -> code evidence. Generates checklists.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
PDF_PATH = ROOT / "CDS_DOCUMENTO.pdf"
TMP_DIR = Path("/tmp")
DOC_TXT = TMP_DIR / "cds_documento.txt"
ITEMS_TSV = TMP_DIR / "cds_items.txt"
CHECKLIST_TSV = TMP_DIR / "cds_checklist.tsv"

SKIP_DIRS = {"node_modules", "dist", "venv", ".git", "uploads", "database", "image", "reports"}
TEXT_EXTS = {".js", ".ts", ".vue", ".scss", ".css", ".md", ".json", ".yml", ".yaml", ".toml", ".txt", ".py", ".ini", ".cjs", ".mjs"}

TECH_MAP = {
    "vue": "package.json",
    "composition": "package.json",
    "vite": "package.json",
    "bootstrap": "package.json",
    "scss": "src/scss/_variables.scss",
    "pinia": "package.json",
    "router": "package.json",
    "vitest": "package.json",
    "jest": "package.json",
    "axios": "package.json",
    "fastapi": "backend/requirements.txt",
    "sqlalchemy": "backend/requirements.txt",
    "pydantic": "backend/requirements.txt",
    "asyncpg": "backend/requirements.txt",
    "celery": "backend/requirements.txt",
    "redis": "backend/requirements.txt",
    "python-jose": "backend/requirements.txt",
    "slowapi": "backend/requirements.txt",
    "alembic": "backend/alembic.ini",
    "emailjs": "src/composables/emails.js",
}

MANUAL_HINTS = [
    ("módulo de autenticación", "backend/app/api/v1/endpoints/auth.py"),
    ("modulo de autenticacion", "backend/app/api/v1/endpoints/auth.py"),
    ("módulo de diagnósticos con ia", "backend/app/models/diagnostic.py"),
    ("modulo de diagnosticos con ia", "backend/app/models/diagnostic.py"),
    ("sistema de cotizaciones", "backend/app/models/quote.py"),
    ("gestión de reparaciones", "backend/app/models/repair.py"),
    ("gestion de reparaciones", "backend/app/models/repair.py"),
    ("gestión de instrumentos", "backend/app/models/instrument.py"),
    ("gestion de instrumentos", "backend/app/models/instrument.py"),
    ("sistema de usuarios y roles", "backend/app/models/permission.py"),
    ("composables y lógica reutilizable", "src/composables"),
    ("composables y logica reutilizable", "src/composables"),
    ("sistema de estilos", "src/scss/_variables.scss"),
    ("testing", "tests"),
    ("configuración y deployment", "docs/DEPLOYMENT.md"),
    ("configuracion y deployment", "docs/DEPLOYMENT.md"),
    ("gestión de estado", "src/stores"),
    ("gestion de estado", "src/stores"),
    ("pwa", "public/manifest.json"),
    ("manifest.json", "public/manifest.json"),
    ("service worker", "public/sw.js"),
]

STOPWORDS = {
    "sistema", "documento", "modulo", "módulo", "gestion", "gestión", "panel",
    "publico", "público", "pagina", "página", "completo", "completa",
    "frontend", "backend", "datos", "servicio", "servicios", "modelo", "modelos",
    "api", "rest", "general", "del", "para", "con", "los", "las", "una", "un",
    "por", "and", "the", "with", "from", "http", "https", "www", "com", "de",
    "en", "a", "y", "o", "si", "no",
}


def run_mutool_extract() -> None:
    if DOC_TXT.exists():
        return
    # use mutool to extract text from PDF
    import subprocess
    subprocess.run(["mutool", "draw", "-F", "text", "-o", str(DOC_TXT), str(PDF_PATH)], check=True)


def parse_doc_items(text: str) -> List[Tuple[str, str, str]]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    items: List[Tuple[str, str, str]] = []
    section = ""
    subsection = ""
    for l in lines:
        if re.match(r"^\d+\.", l):
            section = l
            subsection = ""
            continue
        if re.match(r"^\d+\.\d+", l):
            subsection = l
            continue
        if l.startswith("•"):
            items.append((section, subsection, l.lstrip("•").strip()))
        if ":" in l and not l.startswith("http"):
            if any(k in l for k in [
                "Framework", "Build Tool", "UI Framework", "Estilos", "State Management",
                "Routing", "Testing", "Comunicación", "ORM", "Base de datos",
                "Autenticación", "Validación", "Async DB", "Workers", "Logging",
                "Email", "IA", "Storage"
            ]):
                items.append((section, subsection, l))
    # de-dup
    seen = set()
    uniq: List[Tuple[str, str, str]] = []
    for it in items:
        if it in seen:
            continue
        seen.add(it)
        uniq.append(it)
    return uniq


def iter_files() -> Iterable[Path]:
    for p in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file():
            if p.suffix.lower() in TEXT_EXTS or p.name in {"package.json", "requirements.txt"}:
                if p.stat().st_size > 2_000_000:
                    continue
                yield p


def build_word_index(files: Iterable[Path]) -> dict:
    word_re = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_\-]{3,}")
    index = {}
    for p in files:
        try:
            text = p.read_text(errors="ignore").lower()
        except Exception:
            continue
        for w in set(word_re.findall(text)):
            if w not in index:
                index[w] = p
    return index


def keywords(item: str) -> List[str]:
    words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_\-/]+", item)
    keys = []
    for w in words:
        wl = w.lower()
        if len(wl) < 3:
            continue
        if wl in STOPWORDS:
            continue
        keys.append(wl)
    for tok in TECH_MAP:
        if tok in item.lower() and tok not in keys:
            keys.append(tok)
    return list(dict.fromkeys(keys))


def classify_item(item: str, index: dict, file_index: dict) -> Tuple[str, str]:
    # explicit file mention
    m = re.search(r"([\w.-]+\.(json|vue|ts|js|py|scss|css))", item.lower())
    if m:
        fname = re.sub(r"[^a-z0-9_.-]", "", m.group(1))
        p = file_index.get(fname)
        if not p:
            for key, path in file_index.items():
                if key == fname or key.endswith(fname):
                    p = path
                    break
        return ("EXISTE" if p else "NO EXISTE", str(p.relative_to(ROOT)) if p else "")

    item_clean = re.sub(r"\s+", " ", item.lower()).strip()
    for hint, path in MANUAL_HINTS:
        if hint in item_clean:
            p = ROOT / path
            return ("EXISTE" if p.exists() else "NO EXISTE", path)

    for k, path in TECH_MAP.items():
        if k in item.lower():
            p = ROOT / path
            if not p.exists():
                return "NO EXISTE", path
            if k == "jest":
                txt = (ROOT / "package.json").read_text().lower()
                return ("EXISTE" if "jest" in txt else "NO CUMPLE", "package.json")
            return "EXISTE", path

    keys = keywords(item)
    for k in keys:
        if k in index:
            return "EXISTE", str(index[k].relative_to(ROOT))
    return "NO EXISTE", ""


def write_checklist(rows: List[Tuple[str, str, str, str, str]], out_path: Path) -> None:
    out_path.write_text(
        "Seccion\tSubseccion\tItem\tEstado\tEvidencia\n" +
        "\n".join(["\t".join(r) for r in rows])
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(TMP_DIR / "cds_cross_final.tsv"))
    args = parser.parse_args()

    run_mutool_extract()
    text = DOC_TXT.read_text(errors="ignore")
    items = parse_doc_items(text)
    ITEMS_TSV.write_text("\n".join(["\t".join(it) for it in items]))

    files = list(iter_files())
    file_index = {p.name.lower(): p for p in files}
    index = build_word_index(files)

    rows = []
    for sec, sub, item in items:
        item_text = " ".join([s for s in (sec, sub, item) if s]).strip()
        status, evid = classify_item(item_text, index, file_index)
        rows.append((sec, sub, item, status, evid))

    write_checklist(rows, Path(args.out))


if __name__ == "__main__":
    main()
