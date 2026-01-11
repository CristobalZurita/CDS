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
                            class="gallery-image">
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
import PageSection from "@/vue/components/layout/PageSection.vue"
import PageSectionHeader from "@/vue/components/layout/PageSectionHeader.vue"
import PageSectionContent from '@/vue/components/layout/PageSectionContent.vue'

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
        image: "/images/instrumentos/KORG_MICROKORG_XL.jpg",
        description: "Formación musical clásica desde temprana edad. Percusionista, marimbista, comprensión profunda del sonido y la música."
    },
    {
        year: "2000s",
        title: "Cineasta",
        image: "/images/instrumentos/YAMAHA_DX7_MK1.jpg",
        description: "Experiencia en audiovisual, sonido para cine, post-producción y diseño de audio en contextos creativos."
    },
    {
        year: "2005",
        title: "Técnico en Electrónica",
        image: "/images/instrumentos/KORG_KINGKORG.jpg",
        description: "Formación técnica en automatización industrial en Duoc. Base electrónica y entendimiento de circuitos."
    },
    {
        year: "2008-2010",
        title: "Síntesis y Diseño Sonoro",
        image: "/images/instrumentos/KORG_M1.jpg",
        description: "Estudios con Ernesto Romeo en Argentina. Síntesis sustractiva, FM, granular. Diseño sonoro avanzado."
    },
    {
        year: "2010-2014",
        title: "Formación Continua",
        image: "/images/instrumentos/YAMAHA_MONTAGE_8.jpg",
        description: "Clases particulares en Chile con varios especialistas. Integración de conocimientos musicales y técnicos."
    },
    {
        year: "2014",
        title: "El Origen del Taller",
        image: "/images/instrumentos/KORG_ELECTRIBE_EMX.jpg",
        description: "Alrededor de 2014, nace la necesidad de crear un espacio dedicado a la reparación especializada de equipos musicales electrónicos."
    },
    {
        year: "2015-2018",
        title: "Luthería Electrónica",
        image: "/images/instrumentos/ROLAND_D50.jpg",
        description: "Ampliación del taller: teclados, pianos eléctricos, sintetizadores, drum machines, procesadores de efecto, pedales."
    },
    {
        year: "2018-2019",
        title: "Taller en Providencia",
        image: "/images/instrumentos/KORG_TRITON.jpg",
        description: "Local comercial en Providencia, Santiago. Consolidación de procesos, experiencia con diversos modelos y estilos musicales."
    },
    {
        year: "2020",
        title: "Marimbista Profesional",
        image: "/images/instrumentos/YAMAHA_MONTAGE_7.jpg",
        description: "Integración del trabajo como marimbista profesional. Posesión de marimba propia. Música y técnica unidas."
    },
    {
        year: "2024",
        title: "Valparaíso y Proyección",
        image: "/images/instrumentos/KORG_WAVESTATE.png",
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
@import "/src/scss/_theming.scss";

// ============================================
// SECCIÓN ARRIBA: 2 COLUMNAS (Texto + Galería)
// ============================================

.about-top-section {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 520px;
  gap: 2.5rem;
  align-items: center;
  margin-bottom: 2rem;
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
        margin-bottom: 1rem;
        font-size: 2rem;
        font-weight: 600;
    }

    p {
        margin-bottom: 0.8rem;
        line-height: 1.55;
        font-size: 1.3rem;

        &:last-child {
            margin-bottom: 0;
        }
    }
}



.gallery-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0;
    color: $text-normal;
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
    border-radius: 8px;
    overflow: hidden;
    background: white;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.gallery-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

// ============================================
// DIVISOR
// ============================================

.about-divider {
    height: 3px;
    background: linear-gradient(to right, transparent, $light-2, transparent);
    margin: 1rem 0 2rem 0;
}

// ============================================
// SECCIÓN ABAJO: 1 COLUMNA (Timeline + Info)
// ============================================

.about-bottom-section {
    margin-top: 1rem;
    
}

.history-title {
    font-size: 2.3rem;
    font-weight: 600;
    margin-bottom: 1rem;
    text-align: center;
    color: $text-normal;
}

// ============================================
// TIMELINE HORIZONTAL
// ============================================

.horizontal-timeline-wrapper {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1.5rem;
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
    transition: all 0.3s ease;
    color: $text-normal;

    &:hover {
        background: $light-2;
        border-color: $primary;
        color: $primary;
    }

    i {
        font-size: 0.9rem;
    }
}

.horizontal-timeline {
    flex: 1;
    display: flex;
    gap: 1.2rem;
    overflow-x: auto;
    scroll-behavior: smooth;
    padding: 0.8rem 0;

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
    transition: all 0.3s ease;
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
    margin: 0 auto 0.4rem;
    background: white;
    transition: all 0.3s ease;
}

.event-year {
    font-size: 0.7rem;
    font-weight: 600;
    color: $text-muted;
    text-align: center;
    line-height: 1.1;
    transition: color 0.3s ease;
}

.timeline-event-label {
    font-size: 0.8rem;
    color: $text-muted;
    font-weight: 500;
    line-height: 1.2;
    transition: all 0.3s ease;
    word-break: break-word;
}

// ============================================
// INFORMACIÓN DEL EVENTO
// ============================================

.event-info{
  background: rgba($light-2, 0.3);
  border-radius: 6px;
  padding: 0.85rem;
  margin-top: 1.5rem;

  font-size: 2.05rem;
  line-height: 1.6;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100vw;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);

  text-align: center;


    h4 {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        color: $text-normal;
    }

    p {
        font-size: .95rem;
        line-height: 1.6;
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
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }

    .gallery-preview {
        min-height: 250px;
    }

    .about-identity {
        h3 {
            font-size: 1.2rem;
        }

        p {
            font-size: 0.9rem;
        }
    }
}

@include media-breakpoint-down(md) {
    .about-top-section {
        gap: 1rem;
    }

    .timeline-nav {
        width: 35px;
        height: 35px;
    }

    .horizontal-timeline {
        gap: 1rem;
    }

    .timeline-event {
        min-width: 95px;
    }

    .timeline-event-marker {
        width: 48px;
        height: 48px;
    }

    .event-info {
        padding: 1.2rem;

        h4 {
            font-size: 1rem;
            margin-bottom: 0.6rem;
        }

        p {
            font-size: 0.9rem;
        }
    }

    .gallery-preview {
        min-height: 220px;
    }

    .history-title {
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
}

@include media-breakpoint-down(sm) {
    .about-top-section {
        gap: 0.8rem;
        margin-bottom: 1rem;
    }

    .about-identity {
        h3 {
            font-size: 1.1rem;
            margin-bottom: 0.8rem;
        }

        p {
            font-size: 0.85rem;
            margin-bottom: 0.6rem;
            line-height: 1.5;
        }
    }

    .gallery-title {
        font-size: 1rem;
    }

    .gallery-preview {
        min-height: 200px;
    }

    .about-divider {
        margin: 1rem 0 1.5rem 0;
    }

    .about-bottom-section {
        margin-top: 1rem;
    }

    .history-title {
        font-size: 1rem;
        margin-bottom: 0.8rem;
    }

    .horizontal-timeline-wrapper {
        gap: 0.6rem;
        margin-bottom: 1rem;
    }

    .timeline-nav {
        width: 32px;
        height: 32px;

        i {
            font-size: 0.8rem;
        }
    }

    .horizontal-timeline {
        gap: 0.8rem;
        padding: 0.5rem 0;
    }

    .timeline-event {
        min-width: 85px;
    }

    .timeline-event-marker {
        width: 42px;
        height: 42px;
        margin-bottom: 0.3rem;
    }

    .event-year {
        font-size: 0.65rem;
        line-height: 1;
    }

    .timeline-event-label {
        font-size: 0.7rem;
        line-height: 1.1;
    }

    .event-info {
        padding: 1rem;
        margin-top: 1rem;

        h4 {
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }

        p {
            font-size: 0.8rem;
            line-height: 1.5;
        }
    }
}
</style>