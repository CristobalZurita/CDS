# Solución para Reparar Imágenes de Cloudinary

## Problema Identificado

Las URLs en `image-mapping.json` devuelven **404 Not Found** porque:
1. Faltan los números de versión (`v1773305964`) en las URLs
2. La estructura de carpetas en Cloudinary puede ser diferente

## Pasos para Reparar

### 1. Obtener Credenciales de Cloudinary

Ve a https://cloudinary.com/console y obtén:
- API Key
- API Secret

### 2. Configurar Variables de Entorno

```bash
export CLOUDINARY_API_KEY=tu_api_key
export CLOUDINARY_API_SECRET=tu_api_secret
```

### 3. Analizar Estructura Actual en Cloudinary

```bash
cd /mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN
python3 scripts/analyze_cloudinary_structure.py
```

Esto mostrará:
- Cuántas imágenes hay en Cloudinary
- La estructura real de carpetas
- Ejemplos de URLs correctas

### 4. Reparar image-mapping.json

```bash
cd /mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN
python3 scripts/fix_cloudinary_urls.py
```

Este script:
- Hace backup de `image-mapping.json`
- Obtiene las URLs reales desde Cloudinary API
- Actualiza cada entrada con la URL correcta (con versión)
- Muestra estadísticas de cuántas se repararon

### 5. Verificar Reparación

```bash
curl -sI "URL_CORREGIDA" | head -1
# Debe devolver HTTP/2 200
```

## Estructura de Scripts Creados

| Script | Función |
|--------|---------|
| `scripts/diagnose_cloudinary.py` | Diagnóstico general del problema |
| `scripts/analyze_cloudinary_structure.py` | Analiza la estructura real en Cloudinary |
| `scripts/fix_cloudinary_urls.py` | **Principal**: Repara image-mapping.json |
| `scripts/scan_database_images.py` | Escanea la BD por referencias a imágenes |

## Código Existente que Usa las Imágenes

Las funciones `toCloudinaryUrl` existen en:
- `CDS_VUE3_ZERO/src/utils/cloudinary.js`
- `CDS_VUE3_ZERO/src/utils/publicImageCatalog.js`
- `CDS_VUE3_ZERO/src/composables/useSiteImages.js`

Estas funciones generan URLs en tiempo real. Si las URLs en `image-mapping.json` están correctas, el código debería funcionar correctamente.

## Nota Importante

**NO MODIFICAR** el código fuente existente a menos que sea necesario. La solución debe ser:
- **ADITIVA**: Solo agregar/corregir el JSON
- **DECONSTRUCTIVA**: Usar lo que ya existe, reparar lo que está roto
