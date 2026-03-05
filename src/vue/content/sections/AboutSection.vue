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
