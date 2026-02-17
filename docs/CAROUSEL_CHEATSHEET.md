# 🎠 CAROUSEL CHEAT SHEET

## Usa esto ahora

```vue
<template>
  <InstrumentCarousel 
    :instrument="myInstrument"
    :show-photo-label="true"
    @photo-changed="onPhotoChange"
  />
</template>

<script setup>
import InstrumentCarousel from '@/components/InstrumentCarousel.vue'

const onPhotoChange = (photoName) => {
  console.log('Foto actual:', photoName)
}
</script>
```

---

## Estructura de Datos

```typescript
interface Instrument {
  id: string
  marca: string
  modelo: string
  foto_principal: string        // "CASIO_CZ_101"
  fotos_adicionales: string[]   // ["CASIO_CZ_101_BACK", ...]
}
```

---

## Props

| Prop | Tipo | Requerido | Descripción |
|------|------|-----------|-------------|
| `instrument` | Instrument | ✅ | El instrumento a mostrar |
| `show-photo-label` | Boolean | ❌ | Mostrar etiqueta (Vista Principal, etc.) |

---

## Eventos

```typescript
// @photo-changed
{
  type: 'photo-changed',
  detail: 'CASIO_CZ_101_BACK'  // Nombre de la foto
}
```

---

## Comportamiento

| Caso | Resultado |
|------|-----------|
| 1 foto | Imagen estática (sin carousel) |
| 2-3 fotos | Carousel completo |
| 4+ fotos | Carousel completo |

---

## Archivos

```
✅ src/components/InstrumentCarousel.vue     (419 líneas)
✅ src/composables/useInstruments.ts         (auto-sync)
✅ backend/app/api/sync.py                   (API endpoints)
✅ src/data/instruments.json                 (249 instrumentos)
✅ public/images/instrumentos/               (WEBP photos)
```

---

## Testing Rápido

```typescript
// En DevTools:
const testData = {
  id: 'test',
  marca: 'CASIO',
  modelo: 'CZ-101',
  foto_principal: 'CASIO_CZ_101',
  fotos_adicionales: ['CASIO_CZ_101_BACK', 'CASIO_CZ_101_LATERAL']
}
// Pasa como prop :instrument="testData"
// Debe mostrar 3 fotos con carousel
```

---

## Troubleshooting

**"No veo las flechas"**
- Verifica: `fotos_adicionales` no está vacío
- Los archivos `.webp` existen en `public/images/instrumentos/`

**"Las fotos no cargan"**
- Abre DevTools → Network
- Verifica que las URLs son correctas
- `public/images/instrumentos/MARCA_MODELO.webp`

**"Se ve pixelado"**
- Las miniaturas son 50px/60px/80px (por diseño)

---

## Próximos Pasos

1. Importa en tu vista
2. Pasa el instrumento como prop
3. ¡Listo! Ya funciona

---

**¿Necesitas más? Lee:**
- `docs/CAROUSEL_INTEGRATION.md` (guía completa)
- `docs/CAROUSEL_EXAMPLES.md` (ejemplos detallados)
- `docs/CAROUSEL_COMPLETION_SUMMARY.md` (resumen técnico)
