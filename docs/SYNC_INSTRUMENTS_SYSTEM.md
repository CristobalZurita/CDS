# Sistema de Sincronización Automática de Instrumentos

## Resumen

El proyecto ahora tiene un **sistema aditivo y automatizado** para mantener la lista de instrumentos sincronizada con los archivos WEBP reales en `/public/images/instrumentos/`.

**Principio**: Solo **AÑADE** nuevos instrumentos, **NUNCA** quita existentes.

---

## 📊 Estado Actual

- **Total de archivos WEBP**: 249 archivos (incluyendo variantes)
- **Instrumentos únicos**: 212 bases (sin variantes)
- **Variantes soportadas**: BACK, FRONT, MK1, MK2, XL, S, PLUS, etc.
- **Última sincronización**: Incluye todos los 212 instrumentos

### Desglose de Instrumentos

| Marca | Cantidad | Ejemplos |
|-------|----------|----------|
| KORG | 60+ | microKORG, KARMA, Triton, Volca series |
| YAMAHA | 50+ | DX7, PSR-SX series, MODX, Montage |
| AKAI | 30+ | MPC series, MPK series |
| CASIO | 20+ | CZ-101, WK series |
| Access Virus | 7 | A, B, C, Indigo, KB, TI |
| Arturia | 7 | BeatStep Pro, Microfreak, Keylab |
| Roland | 15+ | D-50, JD-800, JP-08, JX-03 |
| Otros | 25+ | Alesis, Kawai, Novation, Behringer, etc. |

---

## 🚀 Cómo Usar

### Opción 1: Sincronización Manual (Local)

```bash
npm run sync:instruments
```

Esto ejecuta el script Python que:
1. Audita `/public/images/instrumentos/` 
2. Extrae instrumentos únicos (elimina variantes)
3. Compara con `src/assets/data/instruments.json`
4. **Mantiene** todos los existentes
5. **Añade** solo los nuevos encontrados
6. Guarda el JSON actualizado

### Opción 2: Sincronización Automática (CI/CD)

Cuando hagas **push con nuevos archivos WEBP**:

```bash
git add public/images/instrumentos/*.webp
git commit -m "add: New instrument photos"
git push
```

**GitHub Actions** ejecutará automáticamente:
1. El sincronizador
2. Cometeará los cambios al JSON
3. Hará push de vuelta a la rama

---

## 📝 Estructura de Archivos

### Archivo WEBP

```
/public/images/instrumentos/KORG_MICROKORG.webp          ← Base
/public/images/instrumentos/KORG_MICROKORG_MK1.webp      ← Variante
/public/images/instrumentos/KORG_MICROKORG_XL.webp       ← Variante
/public/images/instrumentos/KORG_MICROKORG_BACK.webp     ← Variante
```

### Entrada JSON (una sola para todas las variantes)

```json
{
  "id": "korg-microkorg",
  "brand": "korg",
  "model": "microKORG",
  "type": "Keyboard / Synthesizer",
  "photo_key": "KORG_MICROKORG",
  "imagen_url": "/images/instrumentos/KORG_MICROKORG.webp",
  ...
}
```

El componente Vue detecta automáticamente variantes (MK1, XL, etc.) al cargar.

---

## 🔍 Cómo Añadir Nuevos Instrumentos

### Paso 1: Añadir las fotos

```bash
# Copiar archivos WEBP al directorio
cp ~/Descargas/NUEVA_MARCA_MODELO*.webp public/images/instrumentos/

# Nombre recomendado: MARCA_MODELO(_VARIANTE).webp
# Ej:
# - MOOG_MOOGERFOOGER.webp (base)
# - MOOG_MOOGERFOOGER_BACK.webp (variante)
```

### Paso 2: Ejecutar sincronización

```bash
npm run sync:instruments
```

### Paso 3: Verificar y comitear

```bash
git add public/images/instrumentos/ src/assets/data/instruments.json
git commit -m "add(instruments): Add NUEVA_MARCA models with photos"
git push
```

Listo. El sistema:
- ✅ Automáticamente detectó nuevos instrumentos
- ✅ Los añadió al JSON
- ✅ Mantuvo los existentes intactos
- ✅ El componente los carga sin cambios

---

## 🎨 Cómo Funcionan las Variantes

### En Disco

```
KORG_MICROKORG.webp
KORG_MICROKORG_MK1.webp
KORG_MICROKORG_XL.webp
KORG_MICROKORG_BACK.webp
```

### En el JSON (una sola entrada)

```json
{
  "photo_key": "KORG_MICROKORG"
}
```

### En el Componente Vue

```typescript
// InteractiveInstrumentDiagnostic.vue
const variants = await catalog.getInstrumentImageVariants(model)
// Retorna: ["/images/instrumentos/KORG_MICROKORG_MK1.webp", ...]
```

Las variantes se detectan y cargan automáticamente.

---

## ⚙️ Configuración del Sincronizador

### Variantes Soportadas

El script reconoce automáticamente estas variantes:

```python
'_BACK', '_FRONT', '_TOP', '_LATERAL', '_SIDE',
'_MK1', '_MK2', '_MK3', '_MK4', '_MK5',
'_XL', '_S', '_PLUS', '_PRO', '_LITE',
'_DELUXE', '_STANDARD', '_COMPACT',
'_V1', '_V2', '_V3', '_VINTAGE', '_MODERN',
'_BLACK', '_WHITE', '_SILVER', '_GOLD',
'_RACK', '_A', '_B', '_C', '_D', '_E', '_F'
```

Para añadir más variantes, edita `scripts/sync_instruments.py`:

```python
self.VARIANTS = [
    '_BACK', '_FRONT', ...
    '_TU_NUEVA_VARIANTE',  # ← Agregar aquí
]
```

### Template de Nuevos Instrumentos

Edita el template en `scripts/sync_instruments.py` para cambiar valores por defecto:

```python
INSTRUMENT_TEMPLATE = {
    "type": "Keyboard / Synthesizer",  # ← Cambiar si es necesario
    "year": 2024,
    "components": { ... },
    "valor_estimado": {
        "min": 300000,
        "max": 1500000,
    },
    ...
}
```

---

## 🔄 Flujo Automatizado

### Localmente

```
Añadir fotos WEBP
    ↓
npm run sync:instruments
    ↓
Verifica diferencias
    ↓
Mantiene existentes
    ↓
Añade nuevos
    ↓
Guarda JSON
    ↓
git add + git push
```

### CI/CD (GitHub Actions)

```
git push (con nuevas fotos)
    ↓
GitHub Actions detecta cambios en /public/images/instrumentos/
    ↓
Ejecuta scripts/sync_instruments.py
    ↓
Compara con JSON actual
    ↓
Si hay cambios: auto-commit y push
    ↓
Rama actualizada con nuevos instrumentos
```

---

## 📋 Ejemplo Real

### Escenario: Añadir Nord Lead

1. **Paso 1**: Copiar archivos
   ```bash
   cp ~/norte_lead.webp public/images/instrumentos/NORD_LEAD.webp
   cp ~/norte_lead_back.webp public/images/instrumentos/NORD_LEAD_BACK.webp
   ```

2. **Paso 2**: Sincronizar
   ```bash
   npm run sync:instruments
   ```

3. **Resultado en JSON**:
   ```json
   {
     "id": "nord-lead",
     "brand": "nord",
     "model": "LEAD",
     "photo_key": "NORD_LEAD",
     "imagen_url": "/images/instrumentos/NORD_LEAD.webp"
   }
   ```

4. **Componente detecta automáticamente**:
   - `NORD_LEAD.webp` → imagen principal
   - `NORD_LEAD_BACK.webp` → galería de variantes

---

## 🛠️ Troubleshooting

### Problema: Script dice "No hay cambios" pero añadí fotos

**Solución**: 
1. Verifica que el nombre siga el patrón: `MARCA_MODELO(_VARIANTE).webp`
2. Usa mayúsculas para MARCA
3. Sin espacios, solo guiones bajos

### Problema: Quiero cambiar un instrumento existente

**Importante**: El sistema es ADITIVO. Para cambiar:
1. Edita manualmente `src/assets/data/instruments.json`
2. O borra y recrea el JSON (NO recomendado)

### Problema: Tengo una foto que no es instrumento

**Solución**: Úsala en otra carpeta, o renómbrala (ej: `_LOGO_` al inicio)
- El script IGNORA archivos en `/LOGOS/`

---

## 📚 Archivos Relacionados

- `scripts/sync_instruments.py` - Sincronizador principal (ADITIVO)
- `.github/workflows/sync-instruments.yml` - CI/CD automático
- `src/assets/data/instruments.json` - Base de datos de instrumentos
- `src/composables/useInstrumentsCatalog.ts` - Lógica de carga de imágenes
- `src/vue/components/quotation/InteractiveInstrumentDiagnostic.vue` - UI que usa los datos

---

## 📈 Próximas Mejoras (Futuro)

- [ ] Panel para editarmanualmente metadatos sin script
- [ ] Validación automática de WEBP (tamaño, formato)
- [ ] Compresión automática de imágenes
- [ ] Búsqueda fuzzy de instrumentos
- [ ] Historial de cambios en JSON

---

## ✅ Checklist para Mantener el Sistema

- [ ] Archivos WEBP en `/public/images/instrumentos/`
- [ ] Nombres en formato `MARCA_MODELO(_VARIANTE).webp`
- [ ] Ejecutar `npm run sync:instruments` después de añadir fotos
- [ ] Verificar cambios en JSON antes de comitear
- [ ] Nunca editar manualmente photo_key (usa el script)
- [ ] GitHub Actions ejecuta automático en push

---

**Última revisión**: Febrero 2026  
**Estado**: ✅ PRODUCCIÓN  
**Sistema**: ADITIVO (Solo añade, nunca quita)
