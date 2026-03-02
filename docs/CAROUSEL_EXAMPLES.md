# 🎠 InstrumentCarousel - Ejemplos de Uso

## Ejemplo 1: CASIO_CZ_101 (3 Vistas)

```json
{
  "id": "casio_cz_101",
  "marca": "CASIO",
  "modelo": "CZ_101",
  "foto_principal": "CASIO_CZ_101",
  "fotos_adicionales": [
    "CASIO_CZ_101_BACK",
    "CASIO_CZ_101_LATERAL"
  ],
  "tipos": ["sintetizador"]
}
```

### Resultado Visual en el Carrusel:

```
┌─────────────────────────────────────────────┐
│  CASIO CZ-101                               │
├─────────────────────────────────────────────┤
│                                             │
│  ◄        [FOTO PRINCIPAL]         ►       │
│                                             │
│  🔷🔷🔷                                     │ (miniaturas)
│  ◆ ◇ ◇                                      │ (● = activa)
│                                             │
│  Vista Principal  (1/3)                    │
└─────────────────────────────────────────────┘
```

**Interacciones:**
- Click ► flecha derecha → Muestra CASIO_CZ_101_BACK
- Click ◇ miniatura → Salta a CASIO_CZ_101_LATERAL
- Click ◄ flecha izquierda → Vuelve a CASIO_CZ_101

---

## Ejemplo 2: AKAI_APC_64 (2 Vistas)

```json
{
  "id": "akai_apc_64",
  "marca": "AKAI",
  "modelo": "APC_64",
  "foto_principal": "AKAI_APC_64",
  "fotos_adicionales": [
    "AKAI_APC_64_BACK"
  ],
  "tipos": ["controlador"]
}
```

### Resultado Visual:

```
┌─────────────────────────────────────────────┐
│  AKAI APC-64                                │
├─────────────────────────────────────────────┤
│                                             │
│  ◄        [FOTO PRINCIPAL]         ►       │
│                                             │
│  🔷🔷                                       │ (2 miniaturas)
│  ◆ ◇                                        │
│                                             │
│  Vista Principal  (1/2)                    │
└─────────────────────────────────────────────┘
```

---

## Ejemplo 3: MOOG_MINIMOOG (1 Vista)

```json
{
  "id": "moog_minimoog",
  "marca": "MOOG",
  "modelo": "MINIMOOG",
  "foto_principal": "MOOG_MINIMOOG",
  "fotos_adicionales": [],
  "tipos": ["sintetizador"]
}
```

### Resultado Visual (SIN Carrusel):

```
┌─────────────────────────────────────────────┐
│  MOOG MINIMOOG                              │
├─────────────────────────────────────────────┤
│                                             │
│        [FOTO PRINCIPAL]                    │
│                                             │
│  (Sin flechas, sin miniaturas)             │
│  (Display estático)                        │
│                                             │
└─────────────────────────────────────────────┘
```

**⚠️ ADAPTATIVO:** Solo muestra carousel si `fotos_adicionales.length > 0`

---

## 🎯 Uso en Component (Template)

```vue
<template>
  <div class="instrument-card">
    <!-- Encabezado -->
    <h3>{{ instrument.marca }} {{ instrument.modelo }}</h3>
    
    <!-- Carrusel (reemplaza imagen estática) -->
    <InstrumentCarousel 
      :instrument="instrument"
      :show-photo-label="true"
      @photo-changed="onPhotoChange"
    />
    
    <!-- Información adicional -->
    <div class="info">
      <p>Total de fotos: {{ instrument.fotos_adicionales.length + 1 }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import InstrumentCarousel from '@/components/InstrumentCarousel.vue'

const onPhotoChange = (photoName: string) => {
  console.log(`📷 Usuario viendo: ${photoName}`)
}
</script>

/* Estilos en la capa Sass global */
.instrument-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  max-width: 500px;
}
```

---

## 📊 Componentes del Carrusel

### 1. **Área Principal (500px ancho max)**
- Muestra una foto a la vez (foto_principal o fotos_adicionales[index])
- Transición suave (fade-in 300ms)
- Responsive: se adapta al ancho disponible

### 2. **Botones de Navegación**
```
◄ Button (Anterior)  |  ► Button (Siguiente)
```
- Chevron izquierda/derecha (FontAwesome)
- Deshabilitados en límites (primera/última foto)
- Hover effect (cambio de opacidad)

### 3. **Carrusel de Miniaturas**
```
[Thumb1] [Thumb2] [Thumb3]
```
- 80px ancho en desktop
- 60px en tablet
- 50px en móvil
- Click = salta a esa foto
- Borde resaltado en miniatura activa
- Scroll horizontal si hay muchas

### 4. **Indicadores**
- **Número:** "1/3", "2/3", "3/3"
- **Etiqueta:** "Vista Principal", "Vista Trasera", "Vista Lateral"

---

## 🎨 Estilos Personalizables

Si necesitas personalizar el carrusel, puedes editar `src/components/InstrumentCarousel.vue`:

```scss
// Cambiar tamaño de miniaturas
.thumbnail {
  width: 80px;  // Cambiar aquí
  height: 80px;
}

// Cambiar color de borde activo
.thumbnail.active {
  border-color: #2c5aa0;  // Color azul
}

// Cambiar velocidad de transición
.carousel-image {
  animation: fadeIn 0.3s;  // Cambiar duración
}
```

---

## 🧪 Testing Manual

### Test 1: Instrumento con 3 fotos
```
1. Abre CASIO_CZ_101
2. ✓ Debe mostrar 3 miniaturas
3. ✓ Flecha derecha debe funcionar
4. ✓ Click en miniatura 3 debe mostrar foto 3
5. ✓ Flecha izquierda debe deshabilitarse en foto 1
```

### Test 2: Instrumento con 1 foto
```
1. Abre MOOG_MINIMOOG
2. ✓ NO debe mostrar flechas
3. ✓ NO debe mostrar miniaturas
4. ✓ Solo imagen estática
```

### Test 3: Responsive
```
1. Abre CASIO_CZ_101
2. Desktop: miniaturas 80px
3. Tablet (768px): miniaturas 60px
4. Móvil (480px): miniaturas 50px
5. ✓ Todo debe verse bien en cada breakpoint
```

---

## 🔄 Ciclo de Vida del Carrusel

```
1. Component Mount
   ↓
2. Calcular total de fotos = foto_principal + fotos_adicionales.length
   ↓
3. Si total === 1:
   └─→ Render estático (sin carousel)
   
4. Si total > 1:
   └─→ Render carousel completo
      ├─ Botones de navegación
      ├─ Carrusel de miniaturas
      └─ Indicadores

5. User Interaction:
   ├─ Click flecha ► → currentIndex++
   ├─ Click flecha ◄ → currentIndex--
   ├─ Click miniatura → currentIndex = selectedIndex
   └─ Emit: @photo-changed("PHOTO_NAME")

6. Update Photo Display:
   └─ Actualizar imagen y etiqueta
```

---

## 📱 Breakpoints Responsive

| Dispositivo | Ancho | Miniatura | Foto |
|-------------|-------|-----------|------|
| Desktop | > 768px | 80px | 500px |
| Tablet | 480-768px | 60px | 350px |
| Móvil | < 480px | 50px | 300px |

---

## ✨ Características Avanzadas (Futuro)

Posibles mejoras que podrían agregarse:

1. **Navegación por teclado**
   - Arrow keys para cambiar foto
   - Enter para descargar foto

2. **Navegación por touch**
   - Swipe derecha → foto anterior
   - Swipe izquierda → foto siguiente

3. **Auto-rotate**
   - Opción para rotar fotos automáticamente cada 5s

4. **Full-screen**
   - Click foto para ver a tamaño completo

5. **Zoom**
   - Pinch-to-zoom en móvil

---

## 📝 Notas

- Las fotos vienen de `public/images/instrumentos/*.webp`
- Los nombres están en `instruments.json` (foto_principal, fotos_adicionales)
- El sistema es LITERAL: solo lista fotos que existen en el disco
- No hay inventos ni inferencias de datos

---

**¡Listo para usar! 🚀**
