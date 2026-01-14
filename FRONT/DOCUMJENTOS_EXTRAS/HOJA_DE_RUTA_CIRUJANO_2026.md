# 🔧 HOJA DE RUTA — CIRUJANO DE SINTETIZADORES
## Sistema Web Integral 2026

---

## 📋 RESUMEN EJECUTIVO

### Lo que TIENES (código existente en VOLCADO08):
- ✅ Frontend Vue 3 + Vite funcionando
- ✅ Landing page con secciones: Hero, About, Services, History, FAQ, Reviews, Contact
- ✅ Identidad visual aplicada (colores, tipografías, logos)
- ✅ Componentes del wizard de diagnóstico (DiagnosticWizard.vue, DiagnosticSection.vue, FloatingQuoteButton.vue)
- ✅ Composable useDiagnostic.js con lógica de cotización
- ✅ Datos JSON (42 marcas, 10 instrumentos, 25+ fallas)
- ✅ Estructura backend FastAPI (main.py, config.py, schemas.py, routers/)
- ✅ Variables SCSS corregidas para pantallas grandes

### Lo que FALTA implementar:
- ❌ Integración del wizard en App.vue (conexión)
- ❌ Formulario de contacto funcional (envío de emails)
- ❌ Sistema de agendamiento de citas
- ❌ Base de datos real (PostgreSQL)
- ❌ Backend operativo en servidor
- ❌ Portal de clientes (seguimiento de reparaciones)
- ❌ Panel de administración
- ❌ Inventario del taller

---

## 🎯 TU VISIÓN DEL SISTEMA

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CIRUJANO DE SINTETIZADORES                       │
│                     Sistema Web Integral                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  🌐 PÚBLICO (Lo que ven los clientes)                              │
│  ├── Landing Page (mostrar tu trabajo)                             │
│  ├── Formulario de Contacto (mensajes)                             │
│  ├── Sistema de Agendamiento (fecha/hora revisión)                 │
│  └── Cotizador Online (simulador de precio)                        │
│                                                                     │
│  🔐 PRIVADO (Tu panel de administración)                           │
│  ├── Base de Datos de Trabajos (historial reparaciones)            │
│  ├── Inventario del Taller (componentes, herramientas)             │
│  ├── Gestión de Clientes (contactos, historial)                    │
│  └── Estadísticas del Negocio (ingresos, marcas más reparadas)     │
│                                                                     │
│  👤 PORTAL CLIENTES (opcional, fase posterior)                     │
│  ├── Ver estado de su reparación                                   │
│  └── Historial de servicios                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 PLAN DE IMPLEMENTACIÓN POR FASES

### ══════════════════════════════════════════════════════════════════
### FASE 0: PUESTA EN MARCHA INMEDIATA (2-4 horas)
### ══════════════════════════════════════════════════════════════════

**Objetivo:** Hacer funcionar el frontend actual con las nuevas funcionalidades.

#### Paso 0.1: Verificar estructura del proyecto
```bash
cd /ruta/a/tu/proyecto/cirujano-front
ls -la src/
```

Debe existir:
```
src/
├── assets/data/         ← brands.json, instruments.json, faults.json
├── composables/         ← useDiagnostic.js
├── scss/               ← _variables.scss (corregido)
└── vue/
    ├── components/
    │   ├── articles/   ← DiagnosticWizard.vue
    │   └── widgets/    ← FloatingQuoteButton.vue
    └── sections/       ← DiagnosticSection.vue
```

#### Paso 0.2: Integrar componentes en App.vue

Editar `src/vue/stack/App.vue`:

```vue
<template>
    <StateProviderLayer>
        <FeedbacksLayer>
            <ContentLayer>
                <Master/>
            </ContentLayer>
        </FeedbacksLayer>
    </StateProviderLayer>
    
    <!-- AGREGAR: Botón flotante FUERA de los layers -->
    <FloatingQuoteButton />
</template>

<script setup>
import StateProviderLayer from "/src/vue/stack/StateProviderLayer.vue"
import FeedbacksLayer from "/src/vue/stack/FeedbacksLayer.vue"
import ContentLayer from "/src/vue/stack/ContentLayer.vue"
import Master from "/src/vue/content/Master.vue"
import FloatingQuoteButton from "/src/vue/components/widgets/FloatingQuoteButton.vue"  // ← AGREGAR
import {useEmails} from "/src/composables/emails.js"
import {onMounted} from "vue"

const emails = useEmails()

onMounted(() => {
    emails.init()
})
</script>
```

#### Paso 0.3: Integrar DiagnosticSection en HomePage

Editar `src/vue/content/pages/HomePage.vue` y agregar DiagnosticSection después de ServicesSection (o donde prefieras):

```vue
<template>
    <div>
        <HeroSection />
        <AboutSection />
        <ServicesSection />
        <DiagnosticSection />  <!-- ← AGREGAR AQUÍ -->
        <HistorySection />
        <FaqSection />
        <ReviewsSection />
        <ContactSection />
    </div>
</template>

<script setup>
// ... imports existentes ...
import DiagnosticSection from "/src/vue/sections/DiagnosticSection.vue"  // ← AGREGAR
</script>
```

#### Paso 0.4: Probar
```bash
npm run dev
# Abrir http://localhost:5173
```

**Verificar:**
- [ ] Botón flotante naranja en esquina inferior derecha
- [ ] Click en botón → scroll a sección de diagnóstico
- [ ] Wizard muestra 42 marcas
- [ ] Selección funciona paso a paso
- [ ] Cotización se calcula correctamente

---

### ══════════════════════════════════════════════════════════════════
### FASE 1: LANDING PAGE COMPLETA (1 semana)
### ══════════════════════════════════════════════════════════════════

**Objetivo:** Tener una landing page profesional con formulario de contacto funcional.

#### 1.1 Formulario de Contacto Funcional

**Opción A: EmailJS (más simple, gratis hasta 200 emails/mes)**

```bash
npm install @emailjs/browser
```

Editar `src/composables/emails.js`:
```javascript
import emailjs from '@emailjs/browser'

export function useEmails() {
    const EMAILJS_SERVICE_ID = 'tu_service_id'
    const EMAILJS_TEMPLATE_ID = 'tu_template_id'
    const EMAILJS_PUBLIC_KEY = 'tu_public_key'

    const init = () => {
        emailjs.init(EMAILJS_PUBLIC_KEY)
    }

    const sendContactEmail = async (formData) => {
        try {
            const result = await emailjs.send(
                EMAILJS_SERVICE_ID,
                EMAILJS_TEMPLATE_ID,
                {
                    from_name: formData.name,
                    from_email: formData.email,
                    subject: formData.subject,
                    message: formData.message
                }
            )
            return { success: true, result }
        } catch (error) {
            return { success: false, error }
        }
    }

    return { init, sendContactEmail }
}
```

**Opción B: Backend propio (más control, requiere servidor)**
→ Ver Fase 3

#### 1.2 Mejoras visuales pendientes

Ya implementadas en _variables.scss:
- [x] Tipografía aumentada (+14-17%)
- [x] Breakpoints corregidos para 4K
- [x] Botón flotante con animación

Pendiente verificar:
- [ ] Responsive en móvil (375px)
- [ ] Responsive en tablet (768px)
- [ ] Velocidad de carga (Lighthouse)

#### 1.3 SEO Básico

Agregar en `index.html`:
```html
<head>
    <!-- Ya existente -->
    <meta name="description" content="...">
    
    <!-- AGREGAR -->
    <meta name="keywords" content="reparación sintetizadores, Valparaíso, servicio técnico, Moog, Roland, Korg">
    <meta property="og:title" content="Cirujano de Sintetizadores">
    <meta property="og:description" content="Servicio técnico especializado en reparación de sintetizadores">
    <meta property="og:image" content="/images/logo/logo_square_002.png">
    <meta property="og:url" content="https://tudominio.cl">
    <link rel="canonical" href="https://tudominio.cl">
</head>
```

---

### ══════════════════════════════════════════════════════════════════
### FASE 2: SISTEMA DE COTIZACIÓN COMPLETO (2 semanas)
### ══════════════════════════════════════════════════════════════════

**Objetivo:** Cotizador online funcional que envía cotizaciones por email.

#### 2.1 Expandir catálogo de instrumentos

Actualizar `src/assets/data/instruments.json` con los instrumentos que más reparas:

```json
{
  "instruments": [
    // Los 10 existentes +
    {
      "id": "roland-juno-106",
      "brand": "roland",
      "model": "Juno-106",
      "type": "Analog Polysynth",
      "year": 1984,
      "components": {
        "faders": 6,
        "botones": 20,
        "teclado": 61,
        "aftertouch": false,
        "lcd": false,
        "leds": 12
      },
      "valor_estimado": { "min": 1500000, "max": 2500000 },
      "fallas_comunes": ["voice_chip_80017a", "slider_intermitente", "teclado_oxidado"]
    }
    // ... más instrumentos
  ]
}
```

**Instrumentos prioritarios a agregar:**
1. Roland Juno-106, Juno-60, Jupiter-4
2. Korg Polysix, Mono/Poly, MS-20
3. Yamaha DX7, CS-60, CS-80
4. Prophet-5, Prophet-600
5. Oberheim OB-8, OB-Xa
6. ARP Odyssey, 2600

#### 2.2 Refinar precios base de fallas

Actualizar `src/assets/data/faults.json` con precios reales:

```json
{
  "KEYBOARD_DEAD_KEY": {
    "id": "KEYBOARD_DEAD_KEY",
    "name": "Tecla(s) sin respuesta",
    "category": "keyboard",
    "basePrice": 15000,  // ← PRECIO REAL por tecla
    "unit": "por_tecla",
    "description": "Tecla no produce sonido ni transmite MIDI"
  },
  "ENCODER_INTERMITTENT": {
    "id": "ENCODER_INTERMITTENT",
    "name": "Encoder/Potenciómetro intermitente",
    "category": "controls",
    "basePrice": 18000,  // ← PRECIO REAL
    "unit": "por_unidad"
  }
  // ...
}
```

#### 2.3 Envío de cotización por email

Agregar en DiagnosticWizard.vue (Paso 5):

```javascript
const sendQuote = async () => {
    const quoteData = diagnostic.getQuoteData()
    
    // Enviar al cliente
    await emailjs.send('service_id', 'quote_template', {
        to_email: quoteData.client.email,
        client_name: quoteData.client.name,
        instrument: `${quoteData.equipment.brand} ${quoteData.equipment.model}`,
        problems: quoteData.diagnostics.faults.map(f => f.name).join(', '),
        total: formatCurrency(quoteData.diagnostics.quote.finalCost)
    })
    
    // Notificar a ti mismo
    await emailjs.send('service_id', 'notification_template', {
        to_email: 'cristobal@cirujano.cl',
        // ... datos de la cotización
    })
}
```

#### 2.4 Descarga de PDF de cotización

```bash
npm install jspdf
```

```javascript
import { jsPDF } from 'jspdf'

const downloadPDF = () => {
    const quote = diagnostic.calculateQuote()
    const doc = new jsPDF()
    
    // Logo
    doc.addImage('/images/logo/logo_horizontal.png', 'PNG', 10, 10, 50, 20)
    
    // Título
    doc.setFontSize(20)
    doc.text('COTIZACIÓN DE SERVICIO', 70, 25)
    
    // Datos del equipo
    doc.setFontSize(12)
    doc.text(`Equipo: ${quote.brand.name} ${quote.instrument.model}`, 10, 50)
    doc.text(`Valor estimado: ${formatCurrency(quote.instrument.valor_estimado.min)}`, 10, 60)
    
    // Problemas detectados
    doc.text('Problemas detectados:', 10, 80)
    quote.faults.forEach((fault, i) => {
        doc.text(`• ${fault.name}: ${formatCurrency(fault.basePrice)}`, 15, 90 + (i * 10))
    })
    
    // Total
    doc.setFontSize(16)
    doc.text(`TOTAL ESTIMADO: ${formatCurrency(quote.finalCost)}`, 10, 150)
    
    // Guardar
    doc.save(`cotizacion_${Date.now()}.pdf`)
}
```

---

### ══════════════════════════════════════════════════════════════════
### FASE 3: SISTEMA DE AGENDAMIENTO (2 semanas)
### ══════════════════════════════════════════════════════════════════

**Objetivo:** Permitir a clientes agendar fecha/hora para revisión.

#### 3.1 Opciones de implementación

**Opción A: Calendly (más rápido, externo)**
- Crear cuenta en calendly.com
- Integrar iframe en la página
- Sincroniza con Google Calendar

```vue
<template>
    <div class="scheduling-section">
        <h2>Agenda tu revisión</h2>
        <iframe 
            src="https://calendly.com/cirujano-sintetizadores/revision"
            width="100%"
            height="600"
            frameborder="0"
        ></iframe>
    </div>
</template>
```

**Opción B: Sistema propio (más control)**

Requiere:
- Backend con base de datos
- Tabla de disponibilidad
- Sistema de confirmación por email
- Integración con Google Calendar API

#### 3.2 Flujo de agendamiento propio

```
Cliente → Selecciona fecha → Selecciona hora disponible → 
→ Ingresa datos de contacto → Describe equipo brevemente →
→ Recibe confirmación por email → Tú recibes notificación
```

---

### ══════════════════════════════════════════════════════════════════
### FASE 4: BACKEND Y BASE DE DATOS (3-4 semanas)
### ══════════════════════════════════════════════════════════════════

**Objetivo:** Sistema completo con persistencia de datos.

#### 4.1 Base de datos PostgreSQL

```sql
-- Clientes
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    direccion TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Equipos (catálogo)
CREATE TABLE equipos_catalogo (
    id SERIAL PRIMARY KEY,
    marca VARCHAR(100) NOT NULL,
    modelo VARCHAR(100) NOT NULL,
    tipo VARCHAR(50),
    año INTEGER,
    componentes JSONB,
    valor_min INTEGER,
    valor_max INTEGER,
    tier VARCHAR(20)
);

-- Reparaciones (trabajos del taller)
CREATE TABLE reparaciones (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    equipo_catalogo_id INTEGER REFERENCES equipos_catalogo(id),
    equipo_descripcion TEXT,
    serial_number VARCHAR(100),
    problemas_reportados TEXT,
    diagnostico TEXT,
    estado VARCHAR(50) DEFAULT 'INGRESADO',
    costo_cotizado INTEGER,
    costo_final INTEGER,
    fecha_ingreso TIMESTAMP DEFAULT NOW(),
    fecha_entrega_estimada TIMESTAMP,
    fecha_entrega_real TIMESTAMP,
    notas_tecnicas TEXT,
    fotos JSONB
);

-- Inventario
CREATE TABLE inventario (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    categoria VARCHAR(100),
    cantidad INTEGER DEFAULT 0,
    cantidad_minima INTEGER DEFAULT 1,
    ubicacion VARCHAR(100),
    proveedor VARCHAR(255),
    costo_unitario INTEGER,
    notas TEXT
);

-- Cotizaciones (historial)
CREATE TABLE cotizaciones (
    id SERIAL PRIMARY KEY,
    cliente_email VARCHAR(255),
    cliente_nombre VARCHAR(255),
    equipo_info JSONB,
    problemas JSONB,
    monto_estimado INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    convertida_a_reparacion_id INTEGER REFERENCES reparaciones(id)
);
```

#### 4.2 Backend FastAPI completo

Ya tienes la estructura en `backend/`. Falta:

1. Conectar a PostgreSQL real
2. Implementar endpoints faltantes
3. Agregar autenticación JWT
4. Deploy en Railway/Render/DigitalOcean

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### 4.3 Hosting recomendado

| Componente | Servicio | Costo |
|------------|----------|-------|
| Frontend | Vercel | Gratis |
| Backend | Railway | ~$5/mes |
| Base de datos | Railway PostgreSQL | ~$5/mes |
| Emails | EmailJS | Gratis (200/mes) |
| Dominio | NIC Chile | ~$15.000/año |

---

### ══════════════════════════════════════════════════════════════════
### FASE 5: PANEL DE ADMINISTRACIÓN (4-6 semanas)
### ══════════════════════════════════════════════════════════════════

**Objetivo:** Tu panel privado para gestionar el taller.

#### 5.1 Funcionalidades del panel

```
┌─────────────────────────────────────────────────────────────────┐
│  🔧 PANEL ADMIN - CIRUJANO DE SINTETIZADORES                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Dashboard                                                   │
│  ├── Trabajos activos: 5                                       │
│  ├── Cotizaciones pendientes: 3                                │
│  ├── Ingresos del mes: $850.000                                │
│  └── Próximas citas: 2                                         │
│                                                                 │
│  🔧 Reparaciones                                                │
│  ├── Ver todas                                                 │
│  ├── Crear nueva                                               │
│  ├── Filtrar por estado                                        │
│  └── Actualizar estado                                         │
│                                                                 │
│  👥 Clientes                                                    │
│  ├── Lista de clientes                                         │
│  ├── Historial por cliente                                     │
│  └── Agregar cliente                                           │
│                                                                 │
│  📦 Inventario                                                  │
│  ├── Componentes electrónicos                                  │
│  ├── Herramientas                                              │
│  ├── Alertas de stock bajo                                     │
│  └── Agregar ítem                                              │
│                                                                 │
│  📅 Agenda                                                      │
│  ├── Citas del día                                             │
│  ├── Calendario semanal                                        │
│  └── Bloquear horarios                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.2 Estados de reparación

```
INGRESADO → EN_DIAGNÓSTICO → ESPERANDO_REPUESTO → 
→ EN_REPARACIÓN → PRUEBAS → FINALIZADO → ENTREGADO
```

---

## 📅 CRONOGRAMA SUGERIDO

| Semana | Fase | Entregables |
|--------|------|-------------|
| 1 | Fase 0 | Frontend funcionando con wizard integrado |
| 2 | Fase 1 | Landing completa + formulario de contacto |
| 3-4 | Fase 2 | Cotizador completo + envío email + PDF |
| 5-6 | Fase 3 | Sistema de agendamiento básico |
| 7-10 | Fase 4 | Backend + base de datos + deploy |
| 11-16 | Fase 5 | Panel de administración |

---

## 🛠️ PRÓXIMOS PASOS INMEDIATOS

### HOY:
1. [ ] Verificar que todos los archivos del VOLCADO08 existen en tu proyecto
2. [ ] Integrar FloatingQuoteButton en App.vue
3. [ ] Integrar DiagnosticSection en HomePage.vue
4. [ ] Ejecutar `npm run dev` y probar

### ESTA SEMANA:
1. [ ] Configurar EmailJS para formulario de contacto
2. [ ] Agregar 10+ instrumentos que más reparas
3. [ ] Ajustar precios base de fallas
4. [ ] Probar responsive en móvil

### PRÓXIMA SEMANA:
1. [ ] Implementar envío de cotización por email
2. [ ] Crear template PDF de cotización
3. [ ] Evaluar Calendly vs sistema propio para agendamiento

---

## 📞 COMANDOS ÚTILES

```bash
# Desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview

# Limpiar cache si hay problemas
rm -rf node_modules
npm install
npm run dev

# Backend (cuando lo implementes)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 📚 ARCHIVOS CLAVE DEL PROYECTO

| Archivo | Función |
|---------|---------|
| `src/vue/stack/App.vue` | Componente raíz |
| `src/vue/content/pages/HomePage.vue` | Página principal |
| `src/vue/sections/DiagnosticSection.vue` | Sección del cotizador |
| `src/vue/components/articles/DiagnosticWizard.vue` | Wizard de 5 pasos |
| `src/vue/components/widgets/FloatingQuoteButton.vue` | Botón flotante |
| `src/composables/useDiagnostic.js` | Lógica del cotizador |
| `src/assets/data/brands.json` | 42 marcas |
| `src/assets/data/instruments.json` | 10+ instrumentos |
| `src/assets/data/faults.json` | 25+ tipos de fallas |
| `src/scss/_variables.scss` | Variables de estilo |

---

**Documento creado:** Enero 2026  
**Proyecto:** Cirujano de Sintetizadores  
**Estado:** LISTO PARA COMENZAR FASE 0
