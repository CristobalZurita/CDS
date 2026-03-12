# CLOUDINARY - PASO A PASO OFICIAL

## OBJETIVO
Cargar imágenes desde Cloudinary (servidor externo) en lugar del servidor local para ahorrar espacio.

---

## PASO 1: Estructura consolidada (YA HECHO)

Se eliminaron duplicados y se consolidó TODO en:

### Backend (único servicio):
- `backend/app/services/cloudinary_service.py` - ÚNICO servicio para:
  - Subir imágenes a Cloudinary
  - Resolver URLs de imágenes (convertir /images/ → https://res.cloudinary.com/...)
  - Generar firmas para upload directo

### Scripts (solo los esenciales):
- `scripts/upload_all_images_to_cloudinary.py` - Subir todas las fotos locales a Cloudinary
- `scripts/configure_cloudinary_preset.py` - Configurar upload preset
- `scripts/scan_database_images.py` - Escanear imágenes en base de datos

### Frontend (única utilidad):
- `CDS_VUE3_ZERO/src/utils/cloudinary.js` - Convierte rutas locales a URLs de Cloudinary

### Mapeo:
- `image-mapping.json` - Mapea rutas locales a URLs de Cloudinary

---

## PASO 2: Configuración según documentación oficial de Cloudinary

### 2.1 Crear cuenta y obtener credenciales
```bash
# Ir a: https://cloudinary.com/console
# Obtener:
# - Cloud Name
# - API Key  
# - API Secret
```

### 2.2 Configurar variables de entorno
```bash
# En backend/.env o exportar:
export CLOUDINARY_CLOUD_NAME="dgwwi77ic"
export CLOUDINARY_API_KEY="tu_api_key"
export CLOUDINARY_API_SECRET="tu_api_secret"
export CLOUDINARY_URL="cloudinary://API_KEY:API_SECRET@CLOUD_NAME"
```

### 2.3 Crear Upload Preset (Unsigned)
```bash
# Ejecutar script:
python scripts/configure_cloudinary_preset.py

# O manualmente en Cloudinary Console:
# Settings > Upload > Add upload preset
# - Name: "cirujano_unsigned"
# - Signing Mode: Unsigned
# - Folder: "cirujano"
```

---

## PASO 3: Subir imágenes a Cloudinary

### Opción A: Script automático (TODO)
```bash
# Subir TODAS las imágenes locales a Cloudinary:
python scripts/upload_all_images_to_cloudinary.py
```

### Opción B: Manual desde consola Cloudinary
1. Ir a https://cloudinary.com/console/media_library
2. Crear carpetas: `instrumentos/`, `INVENTARIO/`, `logo/`
3. Drag & drop de imágenes desde `public/images/`

---

## PASO 4: Conectar la web a Cloudinary

### 4.1 Backend - Devolver URLs de Cloudinary
El servicio `cloudinary_service.py` ya tiene:
```python
def resolve_image_url(local_path: str) -> str:
    # PRIMERO busca en image-mapping.json
    # LUEGO busca en Cloudinary API
    # Retorna URL de Cloudinary o local si no encuentra
```

Ya está conectado en:
- `backend/app/routers/inventory.py` - Para imágenes de productos
- `backend/app/routers/images.py` - API de resolución de imágenes

### 4.2 Frontend - Usar URLs de Cloudinary
```javascript
// Usar toCloudinaryUrl donde se carguen imágenes dinámicas:
import { toCloudinaryUrl } from '../CDS_VUE3_ZERO/src/utils/cloudinary.js'

// Ejemplo:
const imageUrl = toCloudinaryUrl('/images/instrumentos/AKAI_MPC.webp')
// Retorna: https://res.cloudinary.com/dgwwi77ic/image/upload/v123/AKAI_MPC.webp
```

---

## PASO 5: Verificar funcionamiento

### Test 1: API de resolución
```bash
curl "http://localhost:8000/api/v1/images/resolve?path=/images/INVENTARIO/BOTON_ARCADE_3_2MM_NEGRO.webp"
```
Debe retornar URL de Cloudinary, no local.

### Test 2: Inventario
```bash
curl "http://localhost:8000/api/v1/inventory/" | grep image_url
```
Las imágenes deben venir con URLs de Cloudinary.

### Test 3: Cambiar nombre en Cloudinary
1. Ir a Cloudinary Console
2. Renombrar una imagen
3. Recargar la web
4. **La imagen debe aparecer rota** (confirmando que carga desde Cloudinary)

---

## RESUMEN DE FLUJO

```
1. Imagen en Cloudinary: https://res.cloudinary.com/.../foto.webp
   ↓
2. Backend devuelve URL de Cloudinary (no /images/local)
   ↓
3. Frontend muestra imagen desde CDN de Cloudinary
   ↓
4. Servidor local NO gasta ancho de banda ni espacio
```

---

## ARCHIVOS MODIFICADOS

- `backend/app/services/cloudinary_service.py` - Consolidado con funciones de resolución
- `backend/app/routers/inventory.py` - Import actualizado
- `backend/app/routers/images.py` - Import actualizado
- `backend/app/services/cloudinary_catalog_service.py` - ELIMINADO (duplicado)
- `scripts/` - Eliminados duplicados

## ARCHIVOS QUE USAN CLOUDINARY

### Backend:
- `backend/app/services/cloudinary_service.py` - Servicio único
- `backend/app/routers/images.py` - API de imágenes
- `backend/app/routers/inventory.py` - Resuelve URLs de productos

### Frontend:
- `CDS_VUE3_ZERO/src/utils/cloudinary.js` - Utilidad de URLs
- Necesita conectarse en: `useInstrumentsCatalog.ts`, componentes Vue

### Scripts:
- `scripts/upload_all_images_to_cloudinary.py` - Subir fotos
- `scripts/configure_cloudinary_preset.py` - Configurar preset
