#!/usr/bin/env python3
"""
Normaliza una imagen de inventario para catalogo sin tocar el original.

- Recorta exceso de blanco
- Agrega un margen limpio
- Escala el contenido dentro de un marco fijo
- Exporta una copia .webp en carpeta destino
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "public" / "images" / "INVENTARIO" / "_catalog_preview"


def run_magick(
    input_path: Path,
    output_path: Path,
    *,
    canvas_size: int,
    content_size: int,
    fuzz: int,
    border: int,
    quality: int,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "magick",
        str(input_path),
        "-fuzz",
        f"{fuzz}%",
        "-trim",
        "+repage",
        "-bordercolor",
        "white",
        "-border",
        str(border),
        "-filter",
        "Lanczos",
        "-resize",
        f"{content_size}x{content_size}",
        "-background",
        "white",
        "-gravity",
        "center",
        "-extent",
        f"{canvas_size}x{canvas_size}",
        "-quality",
        str(quality),
        str(output_path),
    ]
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Normaliza una imagen de inventario para catalogo")
    parser.add_argument("input", help="Ruta de la imagen origen")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Carpeta destino para la copia normalizada",
    )
    parser.add_argument("--canvas-size", type=int, default=800, help="Tamano fijo del marco final")
    parser.add_argument("--content-size", type=int, default=720, help="Tamano maximo del contenido dentro del marco")
    parser.add_argument("--fuzz", type=int, default=10, help="Porcentaje de tolerancia para recorte de blanco")
    parser.add_argument("--border", type=int, default=10, help="Borde blanco antes de centrar")
    parser.add_argument("--quality", type=int, default=85, help="Calidad del webp exportado")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_path = output_dir / input_path.name

    run_magick(
        input_path,
        output_path,
        canvas_size=args.canvas_size,
        content_size=args.content_size,
        fuzz=args.fuzz,
        border=args.border,
        quality=args.quality,
    )

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
