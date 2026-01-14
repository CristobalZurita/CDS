# Brand assets extracted from MANUAL_CIRUJANO.pdf

This file summarizes the assets and recommended steps after extracting content from the manual PDF.

## Extracted files
- scripts/brand_assets/meta.json — metadata (fonts found, page count)
- scripts/brand_assets/page_17_img_1.jpeg — image (logo / brand image candidate)
- scripts/brand_assets/page_18_img_1.jpeg
- scripts/brand_assets/page_19_img_1.jpeg
- scripts/brand_assets/page_20_img_1.jpeg
- scripts/brand_assets/palette.json — dominant colors extracted from images

## Fonts found (embedded in PDF)
- Digna04 (Digna04-Regular, Digna04-Bold, Digna04-Thin)
- CervoNeueCon (Regular, Medium, SemiBold, XtrBold)
- CormorantGaramond
- SteelfishRg

**Note:** embedded fonts may be licensed. To use them on the web, obtain proper webfont files or choose equivalent Google Fonts / licensed alternatives.

## Fonts added to the project
- The Cervo family and Steelfish were copied to `public/fonts/` (see `public/fonts/CERVO/` and `public/fonts/steelfish rg.otf`).
- The project now includes `@font-face` declarations in `src/scss/_brand.scss`. Please verify license terms before deploying to production.
- I generated web-optimized font formats: `woff2` and `woff` (and `ttf` fallbacks) for all the OTFs and placed them alongside the originals under `public/fonts/`.
- Conversion was done locally with `fontforge` + `woff2_compress`. Files present now include `*.woff2`, `*.woff`, `*.ttf` and the original `*.otf`.
**Reminder:** double-check the license for each font family; hosting webfonts may require a webfont license even if the font is embedded in the PDF.

## Scripts & reproducibility

I added a helper script `scripts/generate_webfonts.sh` which automates converting `.otf` files under `public/fonts/` into `ttf`, `woff` and `woff2` using `fontforge` and `woff2_compress`.

Example (run locally):

```bash
# Install required system packages (Debian/Ubuntu example):
sudo apt-get install -y fontforge woff2
# Run the helper script
./scripts/generate_webfonts.sh
```

The script is idempotent and will skip existing generated files. Keep in mind this installs system utilities and should be run on a trusted machine.

## Palette (suggested mapping)
- Primary: #ec6b00 (orange)
- Secondary: #ac612a (warm brown)
- Accent: #c7814e
- Muted/Neutral: #8f9799
- Background / paper: #f5f5f5 - #f6f6f6
- Text: #3e3c38 (vintage black)

## What I changed in the project
- Added `scripts/extract_brand_assets.py` to extract images and fonts from the PDF (requires PyMuPDF).
- Added `scripts/get_brand_palette.py` to generate `scripts/brand_assets/palette.json` (requires Pillow).
- Added `src/scss/_brand.scss` with brand variables and a small mixin.
- Imported `_brand.scss` in `src/scss/style.scss`.
- Updated `DashboardPanel.vue` to use the brand palette for cards.

## Suggested next steps
1. Confirm the primary/secondary colors from the manual (check the extracted images visually).
2. Obtain webfont files or choose licensed equivalents and add `@font-face` declarations.
3. Replace or adapt other components to use `$brand-*` variables for consistent theming.
4. Consider a small design audit to decide which components get accent vs primary color.

