# 🎯 SISTEMA DE SINCRONIZACIÓN AUTOMÁTICA DE INSTRUMENTOS

## Resumen Ejecutivo

El sistema ahora es **INTELIGENTE Y AUTOMÁTICO**:

✅ **Auto-detección**: Si agregas fotos → se auto-sincroniza (sin intervención manual)  
✅ **Inteligencia**: Sabe si hay cambios → no reinventa, solo añade nuevos  
✅ **Dos métodos**: Startup automático + Carga desde Dashboard  
✅ **Mismo script**: Ambos métodos usan `sync_instruments.py`  

---

## Cómo Funciona

### 1️⃣ MÉTODO 1: AUTO-SYNC AL INICIAR (Recomendado)

**Flujo:**
```
Usuario abre la app
    ↓
App.vue monta (onMounted)
    ↓
useInstruments() se ejecuta
    ↓
Intenta POST /api/instruments/sync
    ↓
Backend ejecuta: python3 scripts/sync_instruments.py
    ↓
Script lee /public/images/instrumentos/*.webp
    ↓
Compara con metadatos en .sync_metadata.json
    ↓
Si hay cambios → Genera JSON nuevo
    ↓
Frontend recibe JSON actualizado
    ↓
Instrumentos disponibles en la app ✅
```

**En App.vue:**
```typescript
import { useInstruments } from '@/composables/useInstruments'

export default {
  setup() {
    const { instruments, loading, lastSync } = useInstruments()
    // ✅ Auto-sincroniza al montar, sin que hagas nada
    
    return { instruments, loading, lastSync }
  }
}
```

### 2️⃣ MÉTODO 2: CARGA MANUAL DESDE DASHBOARD

**Flujo:**
```
Usuario hace click "Actualizar instrumentos" (en dashboard)
    ↓
Componente ejecuta: await sync(true) ← force=true
    ↓
Frontend hace POST /api/instruments/sync?force=true
    ↓
Backend ejecuta: python3 scripts/sync_instruments.py --force
    ↓
Script FUERZA resincronización (incluso sin cambios)
    ↓
Genera JSON nuevo
    ↓
Frontend recibe resultado
    ↓
Modal muestra: "✅ 5 instrumentos nuevos agregados"
```

**En un componente Dashboard:**
```typescript
import { useInstruments } from '@/composables/useInstruments'

export default {
  setup() {
    const { sync, loading, lastSync } = useInstruments()
    
    async function handleManualSync() {
      loading.value = true
      const success = await sync(true) // force=true
      
      if (success) {
        showNotification('✅ Sincronización completada')
      }
    }
    
    return { handleManualSync, loading, lastSync }
  }
}
```

---

## Detalles Técnicos

### Metadatos (.sync_metadata.json)

Guardado en: `src/data/.sync_metadata.json`

Contiene:
```json
{
  "last_count": 249,
  "last_hash": "abc123...",
  "last_sync": "2026-02-16T10:30:45.123456",
  "files_processed": ["AKAI_APC_64", "AKAI_APC_64_BACK", ...],
  "added_count": 5,
  "status": "synced|updated|virgin"
}
```

**Propósito**: Detectar cambios sin releer todos los archivos cada vez

### Script Inteligente (sync_instruments.py)

**Lo que hace:**
1. Lee metadatos anteriores
2. Cuenta archivos actuales en `/public/images/instrumentos/`
3. Computa SHA256 hash de todos los nombres
4. **Si NO hay cambios** → Salta (más rápido ⚡)
5. **Si hay cambios** → Resincroniza JSON

**Argumentos:**
```bash
# Modo normal (inteligente)
python3 scripts/sync_instruments.py
# → Solo sincroniza si hay cambios

# Modo fuerza (full resync)
python3 scripts/sync_instruments.py --force
# → Siempre resincroniza

# Desde npm
npm run sync:instruments
npm run sync:instruments:force
```

### Endpoint API

**GET /api/instruments/sync**
- Solo retorna JSON actual (sin ejecutar script)
- Para obtener estado rápido

**POST /api/instruments/sync**
- Ejecuta script automáticamente
- `?force=true` → fuerza resincronización
- Retorna JSON generado

**GET /api/instruments/status**
- Información de sincronización (timestamps, conteos)
- Sin ejecutar nada

---

## Flujo de Datos: Ejemplo Real

### Escenario: Agregas 3 fotos nuevas manualmente

```
1. Copias fotos a /public/images/instrumentos/
   - ROLAND_TR808.webp (nueva)
   - ROLAND_TR808_BACK.webp (nueva, variante)
   - YAMAHA_CS80.webp (nueva)

2. Usuario abre la app (o hace click "Sincronizar")

3. Script ejecuta:
   - Lee disco: 252 archivos ahora (antes 249)
   - Lee metadatos: last_count=249
   - Detecta cambio: 252 != 249
   
4. Script sincroniza:
   - Identifica: ROLAND_TR808 + ROLAND_TR808_BACK
   - Identifica: YAMAHA_CS80
   - Crea nuevos registros en JSON
   - PRESERVA los 214 anteriores (NO reinventa)
   
5. Resultado:
   - 216 bases + 37 variantes = 252 total
   - JSON updated con 3 instrumentos nuevos
   - Metadatos guardados

6. Frontend recibe JSON y muestra instrumentos nuevos ✅
```

---

## Lógica de Variantes

El script detecta variantes **LITERALMENTE**:

```
Si archivo = BASE_NAME + "_SUFFIX"
  donde SUFFIX ∈ {BACK, FRONT, LATERAL, MK1, MK2, ...}
  Y BASE_NAME existe en la lista
  
  → Es variante de BASE_NAME
  
Sino → Es instrumento base independiente
```

**Ejemplos:**

| Archivo | Tipo | Razón |
|---------|------|-------|
| `AKAI_APC_64` | Base | No tiene sufijo |
| `AKAI_APC_64_BACK` | Variante | Empieza con base + sufijo válido |
| `KORG_ELECTRIBE_2A` | Base | 2A NO es sufijo conocido = parte del nombre |
| `YAMAHA_DX7_MK1` | Base | MK1 es parte del nombre, no hay `YAMAHA_DX7` base |
| `YAMAHA_DX7_MK1_BACK` | Variante | Empieza con base existente + sufijo válido |

---

## Archivos Involucrados

### Frontend
- `src/composables/useInstruments.ts` - Hook auto-sync
- `src/data/instruments.json` - JSON generado (READONLY)
- `src/data/.sync_metadata.json` - Metadatos de sincronización

### Backend
- `backend/app/api/sync.py` - Endpoints REST
- `scripts/sync_instruments.py` - Script inteligente
- `public/images/instrumentos/` - Carpeta de fotos

### Configuración
- `package.json` - Scripts npm
- `.github/workflows/sync-instruments.yml` - CI/CD (opcional)

---

## Ventajas de Este Diseño

✅ **Automático**: No requiere intervención manual  
✅ **Inteligente**: Detecta cambios, no reinventa  
✅ **Rápido**: 2ª ejecución es más rápida (metadatos)  
✅ **Aditivo**: Solo añade, NUNCA sobreescribe  
✅ **Dos métodos**: Startup + Manual con mismo código  
✅ **Robusto**: Fallback a JSON si API no disponible  
✅ **Observable**: Logs detallados de cambios detectados  

---

## Casos de Uso

### Caso 1: Usuario agrega 1 foto en el dashboard
1. Dashboard tiene botón "Sincronizar instrumentos"
2. Usuario hace click
3. Componente ejecuta `sync(true)`
4. Script detecta 1 nuevo archivo
5. JSON se actualiza con 1 instrumento nuevo
6. Modal muestra confirmación ✅

### Caso 2: Usuario abre la app
1. App.vue carga
2. useInstruments() se ejecuta automáticamente
3. Script detecta cambios (o no los detecta)
4. JSON cargado + mostrado en la app ✅

### Caso 3: Carga masiva desde API externa
1. Endpoint API recibe archivos: `POST /api/upload`
2. Archivos se copian a `/public/images/instrumentos/`
3. Script se ejecuta automáticamente (CI/CD)
4. JSON generado
5. Usuarios ven nuevos instrumentos la próxima vez que abran app ✅

---

## Troubleshooting

**P: El script no encuentra los archivos**
R: Verifica que `/public/images/instrumentos/` exista y contenga `.webp`

**P: JSON no se actualiza**
R: Ejecuta con `--force`: `npm run sync:instruments:force`

**P: El API dice "endpoint not found"**
R: Verifica que `backend/app/api/sync.py` esté registrado en Flask

**P: Script muy lento**
R: Normal en primera ejecución. Luego usa metadatos = más rápido

---

## Roadmap Futuro

- [ ] Validar fotos (dimensiones, formatos)
- [ ] Generar thumbnails automáticamente
- [ ] Cache del JSON (Redis)
- [ ] Notificaciones en tiempo real (WebSockets)
- [ ] Historial de cambios (auditoría)

---

**Última actualización**: 16 Feb 2026  
**Status**: ✅ PRODUCCIÓN LISTA
