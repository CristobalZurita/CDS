<template>
  <section id="about" class="home-section home-about">
    <div class="section-inner container">
      <h2 class="section-title">Quiénes somos</h2>

      <div class="about-grid">
        <div class="about-text">
          <h3>Cirujano de Sintetizadores</h3>
          <p>
            <strong>Taller especializado en reparación, mantenimiento y personalización de sintetizadores, drum machines, teclados y otros equipos de audio.</strong>
          </p>
          <p>
            Cada instrumento se revisa en detalle: limpieza interna, revisión de fuente de poder, reemplazo de componentes cuando es necesario y calibraciones finas para recuperar estabilidad y buen sonido.
          </p>
          <p>
            El objetivo es devolver a tus equipos su confiabilidad y carácter sonoro, respetando su diseño original o integrando modificaciones creativas cuando el proyecto lo requiere.
          </p>
        </div>

        <div class="about-image-wrap">
          <button
            class="about-image-trigger"
            type="button"
            :aria-label="`Ver foto completa: ${historyEvents[activeHistoryIdx].title}`"
            @click="openHistoryImage"
          >
            <img
              :src="historyEvents[activeHistoryIdx].image"
              :alt="historyEvents[activeHistoryIdx].title"
              class="about-image"
              loading="lazy"
              width="500"
              height="350"
            />
          </button>
        </div>
      </div>

      <!-- Timeline -->
      <div class="history-block">
        <h3 class="history-title">Nuestra Historia</h3>

        <div class="timeline-wrap">
          <button class="timeline-arrow" @click="prevHistory" aria-label="Anterior">
            <i class="fas fa-chevron-left"></i>
          </button>

          <div class="timeline-track">
            <button
              v-for="(ev, i) in historyEvents"
              :key="i"
              :ref="el => { if (el) nodeRefs[i] = el }"
              class="timeline-node"
              :class="{ active: activeHistoryIdx === i }"
              @click="selectHistory(i)"
            >
              <span class="node-year">{{ ev.year }}</span>
              <span class="node-label">{{ ev.title }}</span>
            </button>
          </div>

          <button class="timeline-arrow" @click="nextHistory" aria-label="Siguiente">
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>

        <p class="history-desc">
          <strong>{{ historyEvents[activeHistoryIdx].title }}.</strong>
          {{ historyEvents[activeHistoryIdx].description }}
        </p>
      </div>
    </div>
  </section>

  <Teleport to="body">
    <Transition name="lightbox">
      <div
        v-if="historyLightboxOpen"
        ref="lightboxRef"
        class="history-lightbox"
        role="dialog"
        aria-modal="true"
        :aria-label="`Foto ampliada: ${historyEvents[activeHistoryIdx].title}`"
        tabindex="-1"
        @click.self="closeHistoryImage"
        @keydown.esc="closeHistoryImage"
      >
        <button
          class="history-lightbox-close"
          type="button"
          aria-label="Cerrar imagen ampliada"
          @click="closeHistoryImage"
        >
          <i class="fas fa-xmark"></i>
        </button>
        <img
          :src="historyEvents[activeHistoryIdx].image"
          :alt="historyEvents[activeHistoryIdx].title"
          class="history-lightbox-image"
        />
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useSiteImages } from '@/composables/useSiteImages'
import { useMediaBinding } from '@/composables/useMediaBinding'

const { resolveImageUrl } = useSiteImages()
const { resolveSlotOr } = useMediaBinding()

const historyEventsRaw = [
  { year: '1999', slotKey: 'about.timeline.1999', title: 'Músico de Conservatorio', image: '/images/personales/marimba.webp',         description: 'Formación musical clásica desde temprana edad. Percusionista, marimbista, comprensión profunda del sonido.' },
  { year: '2008', slotKey: 'about.timeline.2008', title: 'Cineasta',                image: '/images/personales/cine.webp',             description: 'Experiencia en audiovisual, sonido para cine, post-producción y diseño de audio en contextos creativos.' },
  { year: '2013', slotKey: 'about.timeline.2013', title: 'Técnico en Electrónica',  image: '/images/personales/tecnico.webp',           description: 'Formación técnica en automatización industrial en Duoc. Base electrónica y entendimiento de circuitos.' },
  { year: '2014', slotKey: 'about.timeline.2014', title: 'Síntesis y Diseño Sonoro',image: '/images/personales/electronica.webp',       description: 'Clases particulares en Chile con varios especialistas. Integración de conocimientos musicales y técnicos.' },
  { year: '2015', slotKey: 'about.timeline.2015', title: 'El Origen del Taller',    image: '/images/personales/origen.webp',             description: 'Nace el espacio dedicado a la reparación especializada de equipos musicales electrónicos.' },
  { year: '2016', slotKey: 'about.timeline.2016', title: 'Luthería Electrónica',    image: '/images/personales/lutheria.webp',           description: 'Ampliación del taller: teclados, pianos eléctricos, sintetizadores, drum machines, procesadores de efecto.' },
  { year: '2019', slotKey: 'about.timeline.2019', title: 'Formación Continua',      image: '/images/personales/ernesto.webp',            description: 'Estudios con Ernesto Romeo en Argentina. Síntesis sustractiva, FM, granular. Diseño sonoro avanzado.' },
  { year: '2020', slotKey: 'about.timeline.2020', title: 'Taller en Providencia',   image: '/images/personales/providencia..webp',       description: 'Local comercial en Providencia, Santiago. Consolidación de procesos con diversos modelos y estilos.' },
  { year: '2021', slotKey: 'about.timeline.2021', title: 'Marimbista Profesional',  image: '/images/personales/marimbista.webp',         description: 'Integración del trabajo como marimbista profesional. Música y técnica unidas.' },
  { year: '2023', slotKey: 'about.timeline.2023', title: 'Valparaíso',              image: '/images/personales/valparaiso.webp',         description: 'Cirujano de Sintetizadores en Valparaíso. Servicio especializado regional y nacional.' },
]

const historyEvents = computed(() =>
  historyEventsRaw.map(ev => ({
    ...ev,
    image: resolveSlotOr(ev.slotKey, resolveImageUrl(ev.image))
  }))
)

const activeHistoryIdx = ref(0)
const nodeRefs = ref([])
const lightboxRef = ref(null)
const historyLightboxOpen = ref(false)

function selectHistory(i) {
  activeHistoryIdx.value = i
  nodeRefs.value[i]?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
}
function prevHistory() {
  selectHistory((activeHistoryIdx.value - 1 + historyEvents.value.length) % historyEvents.value.length)
}
function nextHistory() {
  selectHistory((activeHistoryIdx.value + 1) % historyEvents.value.length)
}
function openHistoryImage() {
  historyLightboxOpen.value = true
}
function closeHistoryImage() {
  historyLightboxOpen.value = false
}

watch(historyLightboxOpen, val => {
  if (val) nextTick(() => lightboxRef.value?.focus())
})
</script>

<style scoped src="./homeShared.css"></style>
<style scoped>
.home-about {
  background: var(--cds-background-color);
}

.about-grid {
  display: grid;
  gap: clamp(1.4rem, 3vw, 2.6rem);
  align-items: start;
}

.about-text {
  display: grid;
  gap: 0.95rem;
  padding: clamp(1.25rem, 2vw, 2rem);
  border-radius: clamp(1.1rem, 2vw, 1.7rem);
  background: var(--cds-white);
  border: 1px solid var(--cds-border-card);
  box-shadow: var(--cds-shadow-sm);
}

.about-text h3 {
  margin: 0;
  font-size: var(--cds-text-xl);
  color: var(--cds-primary);
}

.about-text p {
  margin: 0;
  font-size: clamp(1rem, 0.92rem + 0.42vw, 1.3rem);
  line-height: 1.68;
  color: var(--cds-text-normal);
}

.about-image-wrap {
  position: relative;
  border-radius: clamp(1.25rem, 2vw, 2rem);
  overflow: hidden;
  border: 1px solid var(--cds-border-card);
  box-shadow: var(--cds-shadow-md);
  width: min(100%, 650px);
  aspect-ratio: 3 / 2;
  max-width: 100%;
  margin: 0 auto;
  background: var(--cds-white);
}

.about-image-wrap::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  box-shadow:
    inset 0 0 0 2px rgba(0, 0, 0, 0.78),
    inset 0 0 84px rgba(0, 0, 0, 0.28);
}

.about-image-trigger {
  width: 100%;
  height: 100%;
  padding: 0;
  border: none;
  background: transparent;
  cursor: zoom-in;
}

.about-image {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  object-position: center;
}

.history-block {
  width: 100%;
  margin-top: 0.4rem;
  padding: clamp(1.3rem, 2.3vw, 2rem);
  border-radius: clamp(1.1rem, 2vw, 1.7rem);
  background: var(--cds-white);
  border: 1px solid var(--cds-border-card);
  box-shadow: var(--cds-shadow-sm);
}

.history-title {
  margin: 0 0 1rem;
  font-size: var(--cds-text-xl);
  color: var(--cds-dark);
  text-align: center;
}

.timeline-wrap {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  width: 100%;
  margin: 0 auto;
}

.timeline-arrow {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: var(--cds-dark);
  color: var(--cds-white);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
}

.timeline-track {
  display: flex;
  gap: 0.75rem;
  overflow-x: auto;
  scroll-behavior: smooth;
  scrollbar-width: none;
  flex: 1;
  padding: 0.35rem 0;
}

.timeline-track::-webkit-scrollbar { display: none; }

.timeline-node {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.38rem;
  padding: 0.75rem 1.15rem;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-sm);
  background: var(--cds-white);
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, transform 0.15s;
  text-align: center;
  min-width: 112px;
  min-height: 96px;
}

.timeline-node:hover {
  transform: translateY(-1px);
}

.timeline-node.active {
  background: var(--cds-primary);
  border-color: var(--cds-primary);
  color: var(--cds-white);
  box-shadow: 0 16px 28px rgba(236, 107, 0, 0.18);
}

.node-year {
  font-weight: var(--cds-font-bold);
  font-size: var(--cds-text-xs);
}

.node-label {
  font-size: 0.9rem;
  line-height: 1.25;
  max-width: 114px;
}

.history-desc {
  max-width: 56rem;
  margin: 1.35rem auto 0;
  font-size: clamp(1rem, 0.92rem + 0.38vw, 1.25rem);
  line-height: 1.65;
  color: var(--cds-text-normal);
  text-align: center;
}

.history-lightbox {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(35, 34, 31, 0.82);
  outline: none;
}

.history-lightbox-image {
  width: min(96vw, 1280px);
  max-height: 90vh;
  object-fit: contain;
  border-radius: var(--cds-radius-md);
  background: var(--cds-white);
  box-shadow: 0 20px 44px rgba(0, 0, 0, 0.35);
}

.history-lightbox-close {
  position: absolute;
  top: 0.9rem;
  right: 0.9rem;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: var(--cds-radius-pill);
  background: var(--cds-dark);
  color: var(--cds-white);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.2rem;
}

/* Transition del lightbox — Vue gestiona el ciclo enter/leave */
.lightbox-enter-active,
.lightbox-leave-active {
  transition: opacity 0.2s ease;
}
.lightbox-enter-from,
.lightbox-leave-to {
  opacity: 0;
}

@media (min-width: 900px) {
  .about-grid { grid-template-columns: 1fr 1fr; }
}
</style>
