#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FONTS_DIR="$ROOT_DIR/public/fonts"

command -v fontforge >/dev/null 2>&1 || { echo "fontforge not found. Install it (apt install fontforge)"; exit 1; }
command -v woff2_compress >/dev/null 2>&1 || { echo "woff2_compress not found. Install it (apt install woff2)"; exit 1; }

find "$FONTS_DIR" -type f -iname "*.otf" | while IFS= read -r otf; do
  base="${otf%.otf}"
  echo "Processing: $otf"
  # Generate TTF if missing
  if [ ! -f "${base}.ttf" ]; then
    fontforge -lang=ff -c "Open('$otf'); Generate('${base}.ttf');"
  else
    echo "  TTF exists: ${base}.ttf"
  fi

  # Generate WOFF
  if [ ! -f "${base}.woff" ]; then
    fontforge -lang=ff -c "Open('${base}.ttf'); Generate('${base}.woff');"
  else
    echo "  WOFF exists: ${base}.woff"
  fi

  # Generate WOFF2
  if [ ! -f "${base}.woff2" ]; then
    woff2_compress "${base}.ttf"
  else
    echo "  WOFF2 exists: ${base}.woff2"
  fi

done

echo "All done. Generated TTF/WOFF/WOFF2 for OTF fonts under $FONTS_DIR"
