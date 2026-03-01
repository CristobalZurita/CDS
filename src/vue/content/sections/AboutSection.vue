<template>
    <!-- About Section -->
    <PageSection variant="default"
                 :id="props.id">
        <!-- Title -->
        <PageSectionHeader title="*Quiénes somos y nuestra historia*"/>

        <!-- Content -->
        <PageSectionContent>
        <!-- SECCIÓN 1: DOS COLUMNAS (ARRIBA) -->
        <div class="about-top-section">
            <!-- COLUMNA IZQUIERDA: TEXTO -->
            <div class="about-text-column">
                <div class="about-identity">
                    <h3>Cirujano de Sintetizadores</h3>
                    <p>
                        <strong>Un taller dedicado a la reparación, mantenimiento y personalización de sintetizadores, drum machines, teclados y otros equipos de audio.</strong>
                    </p>
                    <p>
                        Cada instrumento se revisa en detalle: limpieza interna, revisión de fuente de poder, reemplazo de componentes cuando es necesario y calibraciones finas para recuperar estabilidad y buen sonido.
                    </p>
                    <p>
                        El objetivo es devolver a tus equipos su confiabilidad y carácter sonoro, respetando su diseño original o integrando modificaciones creativas cuando el proyecto lo requiere.
                    </p>
                </div>
            </div>

            <!-- COLUMNA DERECHA: GALERÍA INTERACTIVA -->
            <div class="about-gallery-column">
                <div class="gallery-preview">
                    <div class="gallery-image-wrapper">
                        <img 
                            v-if="activeEvent"
                            :src="activeEvent.image"
                            :alt="activeEvent.title"
                            class="gallery-image"
                            loading="lazy"
                            width="500"
                            height="500">
                    </div>
                </div>
            </div>
        </div>

        <!-- SEPARADOR -->
        <div class="about-divider"></div>

        <!-- SECCIÓN 2: UNA COLUMNA (ABAJO) - TIMELINE HORIZONTAL -->
        <div class="about-bottom-section">
            <h3 class="history-title">Nuestra Historia</h3>
            
            <div class="horizontal-timeline-wrapper">
                <button 
                    v-if="historyEvents.length > 1" 
                    class="timeline-nav timeline-nav-prev"
                    @click="scrollTimeline('prev')"
                    aria-label="Ver eventos anteriores">
                    <i class="fa-solid fa-chevron-left"></i>
                </button>

                <div class="horizontal-timeline" ref="timelineContainer">
                    <div 
                        v-for="(event, index) in historyEvents"
                        :key="index"
                        class="timeline-event"
                        :class="{ active: activeEventIndex === index }"
                        @click="selectEvent(index)">
                        <div class="timeline-event-marker">
                            <span class="event-year">{{ event.year }}</span>
                        </div>
                        <div class="timeline-event-label">{{ event.title }}</div>
                    </div>
                </div>

                <button 
                    v-if="historyEvents.length > 1" 
                    class="timeline-nav timeline-nav-next"
                    @click="scrollTimeline('next')"
                    aria-label="Ver eventos siguientes">
                    <i class="fa-solid fa-chevron-right"></i>
                </button>
            </div>

            <!-- INFO DEL EVENTO SELECCIONADO -->
<div class="event-info">
  {{ activeEvent?.title }}. {{ activeEvent?.description }}
</div>


        </div>
        </PageSectionContent>
    </PageSection>
</template>

<script setup>
import { ref, computed } from "vue"
import PageSection from "/src/vue/components/layout/PageSection.vue"
import PageSectionHeader from "/src/vue/components/layout/PageSectionHeader.vue"
import PageSectionContent from "/src/vue/components/layout/PageSectionContent.vue"

const props = defineProps({
    id: String
})

const timelineContainer = ref(null)
const activeEventIndex = ref(0)

// EVENTOS DE HISTORIA (expandidos)
const historyEvents = [
    {
        year: "Inicios",
        title: "Músico de Conservatorio",
        image: "/images/instrumentos/KORG_MICROKORG_XL.webp",
        description: "Formación musical clásica desde temprana edad. Percusionista, marimbista, comprensión profunda del sonido y la música."
    },
    {
        year: "2000s",
        title: "Cineasta",
        image: "/images/instrumentos/YAMAHA_DX7_MK1.webp",
        description: "Experiencia en audiovisual, sonido para cine, post-producción y diseño de audio en contextos creativos."
    },
    {
        year: "2005",
        title: "Técnico en Electrónica",
        image: "/images/instrumentos/KORG_KINGKORG.webp",
        description: "Formación técnica en automatización industrial en Duoc. Base electrónica y entendimiento de circuitos."
    },
    {
        year: "2008-2010",
        title: "Síntesis y Diseño Sonoro",
        image: "/images/instrumentos/KORG_M1.webp",
        description: "Estudios con Ernesto Romeo en Argentina. Síntesis sustractiva, FM, granular. Diseño sonoro avanzado."
    },
    {
        year: "2010-2014",
        title: "Formación Continua",
        image: "/images/instrumentos/YAMAHA_MONTAGE_8.webp",
        description: "Clases particulares en Chile con varios especialistas. Integración de conocimientos musicales y técnicos."
    },
    {
        year: "2014",
        title: "El Origen del Taller",
        image: "/images/instrumentos/KORG_ELECTRIBE_EMX.webp",
        description: "Alrededor de 2014, nace la necesidad de crear un espacio dedicado a la reparación especializada de equipos musicales electrónicos."
    },
    {
        year: "2015-2018",
        title: "Luthería Electrónica",
        image: "/images/instrumentos/ROLAND_D50.webp",
        description: "Ampliación del taller: teclados, pianos eléctricos, sintetizadores, drum machines, procesadores de efecto, pedales."
    },
    {
        year: "2018-2019",
        title: "Taller en Providencia",
        image: "/images/instrumentos/KORG_TRITON.webp",
        description: "Local comercial en Providencia, Santiago. Consolidación de procesos, experiencia con diversos modelos y estilos musicales."
    },
    {
        year: "2020",
        title: "Marimbista Profesional",
        image: "/images/instrumentos/YAMAHA_MONTAGE_7.webp",
        description: "Integración del trabajo como marimbista profesional. Posesión de marimba propia. Música y técnica unidas."
    },
    {
        year: "2024",
        title: "Valparaíso y Proyección",
        image: "/images/instrumentos/KORG_WAVESTATE.webp",
        description: "Cirujano de Sintetizadores en Valparaíso. Servicio especializado regional y nacional. Criterio profesional, mediciones rigurosas, pruebas en contexto musical."
    }
]

const activeEvent = computed(() => historyEvents[activeEventIndex.value])

const selectEvent = (index) => {
    activeEventIndex.value = index
    // Auto-scroll timeline hacia el evento
    if (timelineContainer.value) {
        const activeEl = timelineContainer.value.querySelectorAll('.timeline-event')[index]
        if (activeEl) {
            activeEl.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
        }
    }
}

const scrollTimeline = (direction) => {
    if (!timelineContainer.value) return
    
    // Navegación circular con flechas
    if (direction === 'next') {
        const nextIndex = (activeEventIndex.value + 1) % historyEvents.length
        selectEvent(nextIndex)
    } else {
        const prevIndex = (activeEventIndex.value - 1 + historyEvents.length) % historyEvents.length
        selectEvent(prevIndex)
    }
}
</script>

<style lang="scss" scoped>
@use "@/scss/_core.scss" as *;

// ============================================
// SECCIÓN ARRIBA: 2 COLUMNAS (Texto + Galería)
// ============================================

.about-top-section {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 520px;
  gap: $spacer-xl;
  align-items: center;
  margin-bottom: $spacer-lg;
}


.about-gallery-column {
  width: 520px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}



.about-text-column {
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.about-identity {
    h3 {
        @include h3-style;
        margin-bottom: $spacer-md;
    }

    p {
        font-size: $text-lg;           // 18px (era 1.3rem = 20.8px)
        line-height: $lh-relaxed;      // 1.6 (era 1.55)
        margin-bottom: $spacer-sm;

        &:last-child {
            margin-bottom: 0;
        }
    }
}



.gallery-title {
    font-size: $h4-size;               // 24px (era 1.5rem)
    font-weight: $fw-semibold;
    margin: 0;
    color: $text-color;
}

.gallery-preview {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 280px;
}

.gallery-image-wrapper {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: $border-radius-md;
    overflow: hidden;
    background: white;
    box-shadow: $shadow-md;
}

.gallery-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: $transition-base;
}

// ============================================
// DIVISOR
// ============================================

.about-divider {
    height: 3px;
    background: linear-gradient(to right, transparent, $light-2, transparent);
    margin: $spacer-md 0 $spacer-xl 0;
}

// ============================================
// SECCIÓN ABAJO: 1 COLUMNA (Timeline + Info)
// ============================================

.about-bottom-section {
    margin-top: $spacer-md;
}

.history-title {
    font-size: $h2-size;
    font-weight: $fw-semibold;
    margin-bottom: $spacer-md;
    text-align: center;
    color: $text-normal;
}

// ============================================
// TIMELINE HORIZONTAL
// ============================================

.horizontal-timeline-wrapper {
    display: flex;
    align-items: center;
    gap: $spacer-sm;
    margin-bottom: $spacer-lg;
    position: relative;
}

.timeline-nav {
    flex-shrink: 0;
    width: 38px;
    height: 38px;
    border: 2px solid $light-2;
    background: white;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: $transition-base;
    color: $text-normal;

    &:hover {
        background: $light-2;
        border-color: $primary;
        color: $primary;
    }

    i {
        font-size: $text-sm;
    }
}

.horizontal-timeline {
    flex: 1;
    display: flex;
    gap: $spacer-md;
    overflow-x: auto;
    scroll-behavior: smooth;
    padding: $spacer-sm 0;

    scrollbar-width: none;
    -ms-overflow-style: none;

    &::-webkit-scrollbar {
        display: none;
    }
}

.timeline-event {
    flex-shrink: 0;
    text-align: center;
    cursor: pointer;
    transition: $transition-base;
    min-width: 110px;

    &:hover {
        transform: translateY(-4px);
    }

    &.active {
        .timeline-event-marker {
            border-color: $primary;
            background: $primary;
            box-shadow: 0 0 12px rgba($primary, 0.3);

            .event-year {
                color: white;
            }
        }

        .timeline-event-label {
            color: $primary;
            font-weight: 600;
        }
    }
}

.timeline-event-marker {
    width: 55px;
    height: 55px;
    border: 3px solid $light-2;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto $spacer-xs;
    background: white;
    transition: $transition-base;
}

.event-year {
    font-size: $text-2xs;
    font-weight: $fw-semibold;
    color: $text-muted;
    text-align: center;
    line-height: $lh-tight;
    transition: $transition-base;
}

.timeline-event-label {
    font-size: $text-xs;
    color: $text-muted;
    font-weight: $fw-medium;
    line-height: $lh-tight;
    transition: $transition-base;
    word-break: break-word;
}

// ============================================
// INFORMACIÓN DEL EVENTO
// ============================================

.event-info{
  background: rgba($light-2, 0.3);
  border-radius: $border-radius-md;
  padding: $spacer-sm;
  margin-top: $spacer-lg;

  font-size: $h3-size;
  line-height: $lh-relaxed;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100vw;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);

  text-align: center;


    h4 {
        font-size: $h6-size;
        font-weight: $fw-semibold;
        margin-bottom: $spacer-sm;
        color: $text-normal;
    }

    p {
        font-size: $text-base;
        line-height: $lh-relaxed;
        color: $text-muted;
        margin: 0;
    }
}

// ============================================
// RESPONSIVE
// ============================================

@include media-breakpoint-down(lg) {
    .about-top-section {
        grid-template-columns: 1fr;
        gap: $spacer-lg;
        margin-bottom: $spacer-lg;
    }

    .gallery-preview {
        min-height: 250px;
    }

    .about-identity {
        h3 {
            font-size: $text-xl;
        }

        p {
            font-size: $text-sm;
        }
    }
}

@include media-breakpoint-down(md) {
    .about-top-section {
        gap: $spacer-md;
    }

    .timeline-nav {
        width: 35px;
        height: 35px;
    }

    .horizontal-timeline {
        gap: $spacer-md;
    }

    .timeline-event {
        min-width: 95px;
    }

    .timeline-event-marker {
        width: 48px;
        height: 48px;
    }

    .event-info {
        padding: $spacer-md;

        h4 {
            font-size: $text-base;
            margin-bottom: $spacer-xs;
        }

        p {
            font-size: $text-sm;
        }
    }

    .gallery-preview {
        min-height: 220px;
    }

    .history-title {
        font-size: $h6-size;
        margin-bottom: $spacer-md;
    }
}

@include media-breakpoint-down(sm) {
    .about-top-section {
        gap: $spacer-sm;
        margin-bottom: $spacer-md;
    }

    .about-identity {
        h3 {
            font-size: $h6-size;
            margin-bottom: $spacer-sm;
        }

        p {
            font-size: $text-xs;
            margin-bottom: $spacer-xs;
            line-height: $lh-normal;
        }
    }

    .gallery-title {
        font-size: $text-base;
    }

    .gallery-preview {
        min-height: 200px;
    }

    .about-divider {
        margin: $spacer-md 0 $spacer-lg 0;
    }

    .about-bottom-section {
        margin-top: $spacer-md;
    }

    .history-title {
        font-size: $text-base;
        margin-bottom: $spacer-sm;
    }

    .horizontal-timeline-wrapper {
        gap: $spacer-xs;
        margin-bottom: $spacer-md;
    }

    .timeline-nav {
        width: 32px;
        height: 32px;

        i {
            font-size: $text-xs;
        }
    }

    .horizontal-timeline {
        gap: $spacer-sm;
        padding: $spacer-xs 0;
    }

    .timeline-event {
        min-width: 85px;
    }

    .timeline-event-marker {
        width: 42px;
        height: 42px;
        margin-bottom: $spacer-xs;
    }

    .event-year {
        font-size: $text-2xs;
        line-height: $lh-none;
    }

    .timeline-event-label {
        font-size: $text-2xs;
        line-height: $lh-tight;
    }

    .event-info {
        padding: $spacer-md;
        margin-top: $spacer-md;

        h4 {
            font-size: $text-base;
            margin-bottom: $spacer-xs;
        }

        p {
            font-size: $text-xs;
            line-height: $lh-normal;
        }
    }
}
</style>