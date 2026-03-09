<template>
  <main class="home-page">

    <!-- ═══════════════════════════════════════ HERO ═══════════════════════ -->
    <section id="hero" class="home-hero">
      <div class="hero-bg" aria-hidden="true"></div>

      <div class="hero-content">
        <img
          src="/images/logo/NUEVO_cirujano.webp"
          alt="Cirujano de Sintetizadores"
          class="hero-logo"
          width="1800"
          height="1220"
          loading="eager"
        />

        <p class="hero-tagline">
          RESTAURACIÓN &nbsp;·&nbsp; MANTENCIÓN &nbsp;·&nbsp; REPARACIÓN
        </p>

        <div class="hero-actions">
          <router-link to="/agendar" class="btn-hero btn-hero-primary">
            <i class="fas fa-calendar-check"></i>
            Agenda tu hora
          </router-link>
          <router-link to="/cotizador-ia" class="btn-hero btn-hero-outline">
            <i class="fas fa-file-circle-check"></i>
            Cotiza tu instrumento
          </router-link>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════ NOSOTROS ══════════════════ -->
    <section id="about" class="home-section home-about">
      <div class="section-inner">
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
            <img
              :src="historyEvents[activeHistoryIdx].image"
              :alt="historyEvents[activeHistoryIdx].title"
              class="about-image"
              loading="lazy"
              width="500"
              height="350"
            />
          </div>
        </div>

        <!-- Timeline -->
        <div class="history-block">
          <h3 class="history-title">Nuestra Historia</h3>

          <div class="timeline-wrap">
            <button class="timeline-arrow" @click="prevHistory" aria-label="Anterior">
              <i class="fas fa-chevron-left"></i>
            </button>

            <div class="timeline-track" ref="timelineRef">
              <button
                v-for="(ev, i) in historyEvents"
                :key="i"
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

    <!-- ═══════════════════════════════════════ SERVICIOS ════════════════ -->
    <section id="services" class="home-section home-services">
      <div class="section-inner">
        <h2 class="section-title">Nuestros Servicios</h2>
        <p class="section-lead">Atención técnica especializada para instrumentos electrónicos, desde la revisión inicial hasta la calibración final.</p>

        <div class="services-grid">
          <article v-for="svc in services" :key="svc.title" class="service-card">
            <div class="service-icon">
              <i :class="svc.icon"></i>
            </div>
            <h3>{{ svc.title }}</h3>
            <p>{{ svc.desc }}</p>
          </article>
        </div>

        <div class="section-actions">
          <router-link to="/agendar" class="btn-section">
            <i class="fas fa-calendar-check"></i> Agendar revisión
          </router-link>
          <router-link to="/cotizador-ia" class="btn-section btn-section-outline">
            <i class="fas fa-file-invoice-dollar"></i> Cotizador IA
          </router-link>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════ COTIZAR ══════════════════ -->
    <section id="diagnostic" class="home-section home-diagnostic">
      <div class="section-inner diagnostic-layout">
        <div class="diagnostic-text">
          <h2 class="section-title">Cotiza tu instrumento</h2>
          <p>Usa nuestro cotizador IA para obtener una estimación preliminar antes de traer tu equipo al taller. Rápido, gratuito y sin compromiso.</p>
          <ul class="diagnostic-list">
            <li><i class="fas fa-check"></i> Diagnóstico orientativo inmediato</li>
            <li><i class="fas fa-check"></i> Sin necesidad de registrarte</li>
            <li><i class="fas fa-check"></i> Compatible con todos los equipos de audio</li>
          </ul>
          <router-link to="/cotizador-ia" class="btn-section">
            <i class="fas fa-file-circle-check"></i> Ir al cotizador IA
          </router-link>
        </div>
        <div class="diagnostic-image">
          <img
            src="/images/instrumentos/KORG_WAVESTATE.webp"
            alt="KORG Wavestate — sintetizador"
            loading="lazy"
            width="480"
            height="280"
          />
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════ TRABAJOS ═════════════════ -->
    <section id="featured" class="home-section home-featured">
      <div class="section-inner">
        <h2 class="section-title">Trabajos Realizados</h2>
        <p class="section-lead">Una muestra de los equipos que han pasado por el taller.</p>

        <div class="featured-grid">
          <div v-for="inst in featuredInstruments" :key="inst.name" class="featured-card">
            <img
              :src="inst.image"
              :alt="inst.name"
              loading="lazy"
              width="300"
              height="200"
            />
            <p>{{ inst.name }}</p>
          </div>
        </div>

        <div class="section-actions">
          <router-link to="/tienda" class="btn-section">
            <i class="fas fa-cart-shopping"></i> Ver tienda
          </router-link>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════ PREGUNTAS ════════════════ -->
    <section id="faq" class="home-section home-faq">
      <div class="section-inner">
        <h2 class="section-title">Preguntas Frecuentes</h2>

        <div class="faq-list">
          <details v-for="faq in faqs" :key="faq.q" class="faq-item">
            <summary class="faq-question">{{ faq.q }}</summary>
            <p class="faq-answer">{{ faq.a }}</p>
          </details>
        </div>

        <div class="section-actions">
          <router-link to="/terminos" class="btn-section btn-section-outline">
            <i class="fas fa-file-lines"></i> Términos y condiciones
          </router-link>
          <router-link to="/privacidad" class="btn-section btn-section-outline">
            <i class="fas fa-shield-halved"></i> Política de privacidad
          </router-link>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════ OPINIONES ════════════════ -->
    <section id="reviews" class="home-section home-reviews">
      <div class="section-inner">
        <h2 class="section-title">Opiniones</h2>
        <p class="section-lead">Lo que dicen nuestros clientes sobre el servicio.</p>

        <div class="reviews-grid">
          <article v-for="rev in reviews" :key="rev.author" class="review-card">
            <div class="review-stars">
              <i v-for="n in 5" :key="n" class="fas fa-star"></i>
            </div>
            <p class="review-text">{{ rev.text }}</p>
            <footer class="review-author">— {{ rev.author }}</footer>
          </article>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════ CONTACTO ═════════════════ -->
    <section id="contact" class="home-section home-contact">
      <div class="section-inner">
        <h2 class="section-title">Contacto</h2>

        <div class="contact-layout">

          <!-- Formulario -->
          <div class="contact-form-wrap">
            <h3>Envíanos un mensaje</h3>
            <form class="contact-form" @submit.prevent="submitContact" novalidate>
              <div class="form-field">
                <label for="cf-name"><i class="fas fa-signature"></i> Nombre</label>
                <input id="cf-name" v-model="form.name" type="text" placeholder="Tu nombre" required autocomplete="name" />
              </div>
              <div class="form-field">
                <label for="cf-email"><i class="fas fa-envelope"></i> Email</label>
                <input id="cf-email" v-model="form.email" type="email" placeholder="tu@email.com" required autocomplete="email" />
              </div>
              <div class="form-field">
                <label for="cf-subject"><i class="fas fa-pen-to-square"></i> Asunto</label>
                <input id="cf-subject" v-model="form.subject" type="text" placeholder="Asunto del mensaje" required />
              </div>
              <div class="form-field">
                <label for="cf-message"><i class="fas fa-comment"></i> Mensaje</label>
                <textarea id="cf-message" v-model="form.message" rows="5" placeholder="Describe tu consulta..." required></textarea>
              </div>

              <p v-if="formError" class="form-msg form-msg-error">
                <i class="fas fa-triangle-exclamation"></i> {{ formError }}
              </p>
              <p v-if="formSuccess" class="form-msg form-msg-success">
                <i class="fas fa-circle-check"></i> Mensaje enviado. Te contactaremos pronto.
              </p>

              <button type="submit" class="btn-submit" :disabled="formSending">
                <i class="fas fa-envelope"></i>
                {{ formSending ? 'Enviando…' : 'Enviar mensaje' }}
              </button>
            </form>
          </div>

          <!-- Info + mapa -->
          <div class="contact-info-wrap">
            <div class="contact-card">
              <p><i class="fas fa-location-dot"></i> <strong>Eusebio Lillo 362, Valparaíso</strong></p>
              <p><i class="fas fa-phone"></i> <a href="tel:+56982957538">+56 9 8295 7538</a></p>
              <p><i class="fas fa-envelope"></i> <a href="mailto:contacto@cirujanodesintetizadores.com">contacto@cirujanodesintetizadores.com</a></p>
              <div class="contact-channels">
                <a href="https://wa.me/56982957538" target="_blank" rel="noopener noreferrer">
                  <i class="fa-brands fa-whatsapp"></i> WhatsApp
                </a>
                <a href="https://www.instagram.com/cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer">
                  <i class="fa-brands fa-instagram"></i> Instagram
                </a>
                <a href="https://www.facebook.com/Cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer">
                  <i class="fa-brands fa-facebook"></i> Facebook
                </a>
              </div>
            </div>

            <div class="contact-map">
              <iframe
                src="https://www.google.com/maps?q=Eusebio+Lillo+362,+Valpara%C3%ADso,+Chile&output=embed"
                title="Ubicación del taller"
                loading="lazy"
                referrerpolicy="no-referrer-when-downgrade"
              ></iframe>
            </div>
          </div>

        </div>
      </div>
    </section>

  </main>
</template>

<script setup>
import { ref } from 'vue'
import api from '@new/services/api'

/* ─── Historia ─── */
const historyEvents = [
  { year: 'Inicios', title: 'Músico de Conservatorio', image: '/images/instrumentos/KORG_MICROKORG_XL.webp',  description: 'Formación musical clásica desde temprana edad. Percusionista, marimbista, comprensión profunda del sonido.' },
  { year: '2000s',  title: 'Cineasta',                 image: '/images/instrumentos/YAMAHA_DX7_MK1.webp',    description: 'Experiencia en audiovisual, sonido para cine, post-producción y diseño de audio en contextos creativos.' },
  { year: '2005',   title: 'Técnico en Electrónica',   image: '/images/instrumentos/KORG_KINGKORG.webp',      description: 'Formación técnica en automatización industrial en Duoc. Base electrónica y entendimiento de circuitos.' },
  { year: '2008',   title: 'Síntesis y Diseño Sonoro', image: '/images/instrumentos/KORG_M1.webp',            description: 'Estudios con Ernesto Romeo en Argentina. Síntesis sustractiva, FM, granular. Diseño sonoro avanzado.' },
  { year: '2010',   title: 'Formación Continua',       image: '/images/instrumentos/YAMAHA_MONTAGE_8.webp',   description: 'Clases particulares en Chile con varios especialistas. Integración de conocimientos musicales y técnicos.' },
  { year: '2014',   title: 'El Origen del Taller',     image: '/images/instrumentos/KORG_ELECTRIBE_EMX.webp', description: 'Nace el espacio dedicado a la reparación especializada de equipos musicales electrónicos.' },
  { year: '2015',   title: 'Luthería Electrónica',     image: '/images/instrumentos/ROLAND_D50.webp',         description: 'Ampliación del taller: teclados, pianos eléctricos, sintetizadores, drum machines, procesadores de efecto.' },
  { year: '2018',   title: 'Taller en Providencia',    image: '/images/instrumentos/KORG_TRITON.webp',        description: 'Local comercial en Providencia, Santiago. Consolidación de procesos con diversos modelos y estilos.' },
  { year: '2020',   title: 'Marimbista Profesional',   image: '/images/instrumentos/YAMAHA_MONTAGE_7.webp',   description: 'Integración del trabajo como marimbista profesional. Música y técnica unidas.' },
  { year: '2024',   title: 'Valparaíso',               image: '/images/instrumentos/KORG_WAVESTATE.webp',     description: 'Cirujano de Sintetizadores en Valparaíso. Servicio especializado regional y nacional.' },
]

const activeHistoryIdx = ref(0)
const timelineRef = ref(null)

function selectHistory(i) {
  activeHistoryIdx.value = i
  const el = timelineRef.value?.querySelectorAll('.timeline-node')[i]
  el?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
}
function prevHistory() {
  selectHistory((activeHistoryIdx.value - 1 + historyEvents.length) % historyEvents.length)
}
function nextHistory() {
  selectHistory((activeHistoryIdx.value + 1) % historyEvents.length)
}

/* ─── Servicios ─── */
const services = [
  { icon: 'fas fa-screwdriver-wrench', title: 'Reparación',     desc: 'Diagnóstico completo y reparación de fallas eléctricas, mecánicas y de firmware en sintetizadores y teclados.' },
  { icon: 'fas fa-heart-pulse',        title: 'Mantención',     desc: 'Limpieza interna, revisión de fuente de poder, lubricación de controles y verificación de voltajes.' },
  { icon: 'fas fa-sliders',            title: 'Modificación',   desc: 'Instalación de MIDI retrofit, expansiones de voz, mods de filtro y personalización a medida.' },
  { icon: 'fas fa-calculator',         title: 'Presupuesto IA', desc: 'Cotización preliminar asistida por IA para evaluar el alcance del trabajo antes de traer tu equipo.' },
]

/* ─── Trabajos destacados ─── */
const featuredInstruments = [
  { name: 'KORG Wavestate',   image: '/images/instrumentos/KORG_WAVESTATE.webp' },
  { name: 'KORG Wavestation', image: '/images/instrumentos/KORG_WAVESTATION.webp' },
  { name: 'Roland D-50',      image: '/images/instrumentos/ROLAND_D50.webp' },
  { name: 'Yamaha DX7 MkI',   image: '/images/instrumentos/YAMAHA_DX7_MK1.webp' },
  { name: 'KORG M1',          image: '/images/instrumentos/KORG_M1.webp' },
  { name: 'KORG Triton',      image: '/images/instrumentos/KORG_TRITON.webp' },
]

/* ─── FAQ ─── */
const faqs = [
  { q: '¿Qué tipos de equipos reparan?',        a: 'Sintetizadores analógicos y digitales, drum machines, samplers, teclados y procesadores de efectos de todas las marcas y épocas.' },
  { q: '¿Cuánto demora una reparación?',         a: 'Una revisión básica puede tardar 3-7 días hábiles. Reparaciones mayores o con espera de repuestos pueden tomar más tiempo. Siempre informamos antes de comenzar.' },
  { q: '¿Puedo traer mi equipo sin cita previa?', a: 'Recomendamos agendar antes para garantizar atención. Puedes usar el sistema de citas online o contactarnos por WhatsApp.' },
  { q: '¿Tienen garantía los trabajos realizados?', a: 'Sí. Todos los trabajos tienen garantía de 90 días sobre la reparación específica realizada.' },
  { q: '¿Trabajan con equipos vintage?',          a: 'Absolutamente. Tenemos amplia experiencia con instrumentos clásicos de los años 70-90: Moog, Roland, Korg, Yamaha, Sequential, entre otros.' },
]

/* ─── Opiniones ─── */
const reviews = [
  { author: 'Rodrigo M.', text: 'Excelente servicio. Repararon mi DX7 en tiempo récord y quedó impecable. Muy profesionales y con conocimiento real del instrumento.' },
  { author: 'Camila V.',  text: 'Llevé mi Korg MS2000 que nadie más quería tocar. Lo dejaron como nuevo. Muy recomendable.' },
  { author: 'Felipe A.',  text: 'Puntualidad, honestidad en el diagnóstico y precio justo. El mejor taller de sintetizadores que he conocido en Chile.' },
]

/* ─── Formulario de contacto ─── */
const form = ref({ name: '', email: '', subject: '', message: '' })
const formSending = ref(false)
const formSuccess = ref(false)
const formError = ref('')

async function submitContact() {
  formError.value = ''
  formSuccess.value = false

  if (!form.value.name || !form.value.email || !form.value.subject || !form.value.message) {
    formError.value = 'Por favor completa todos los campos.'
    return
  }

  formSending.value = true
  try {
    await api.post('/contact/', {
      name: form.value.name,
      email: form.value.email,
      subject: form.value.subject,
      message: form.value.message,
    })
    formSuccess.value = true
    form.value = { name: '', email: '', subject: '', message: '' }
  } catch {
    formError.value = 'Error al enviar el mensaje. Intenta de nuevo o contáctanos por WhatsApp.'
  } finally {
    formSending.value = false
  }
}
</script>

<style scoped>
/* ═══════════════════════════ BASE ════════════════════════════ */
.home-page {
  display: flex;
  flex-direction: column;
}

.home-section {
  scroll-margin-top: 72px;
}

.section-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 1.25rem;
}

.section-title {
  margin: 0 0 0.75rem;
  font-size: var(--cds-text-3xl);
  font-family: var(--cds-headings-font-family), var(--cds-font-family-base), sans-serif;
  color: var(--cds-dark);
  line-height: var(--cds-leading-tight);
}

.section-lead {
  margin: 0 0 2rem;
  font-size: var(--cds-text-lg);
  color: var(--cds-text-muted);
  line-height: var(--cds-leading-normal);
}

.section-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 2rem;
}

/* ═══════════════════════════ BUTTONS ═════════════════════════ */
.btn-hero {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 48px;
  padding: 0.75rem 1.4rem;
  border-radius: 0.6rem;
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  text-decoration: none;
  transition: transform 0.15s, box-shadow 0.15s;
}

.btn-hero:hover { transform: translateY(-1px); }

.btn-hero-primary {
  background: var(--cds-primary);
  color: var(--cds-white);
  border: 2px solid var(--cds-primary);
      -webkit-text-stroke: 1px #111; /* delineado */
  paint-order: stroke fill;
      font-size: var(--cds-text-lg);
}

.btn-hero-outline {
  background: transparent;
  color: var(--cds-white);
  border: 2px solid var(--cds-white);
      -webkit-text-stroke: 1px #111; /* delineado */
  paint-order: stroke fill;
    font-size: var(--cds-text-lg);
}

.btn-section {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 44px;
  padding: 0.65rem 1.25rem;
  border-radius: 0.55rem;
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  text-decoration: none;
  background: var(--cds-primary);
  color: var(--cds-white);
  border: 2px solid var(--cds-primary);
  transition: opacity 0.15s;
  

}

.btn-section:hover { opacity: 0.88; }

.btn-section-outline {
  background: transparent;
  color: var(--cds-primary);
  border-color: var(--cds-primary);
  
}

/* ═══════════════════════════ HERO ════════════════════════════ */
.home-hero {
  position: relative;
  min-height: 90svh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background-image: url('/images/logo/LOGO_HOME.png');
  background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  filter: brightness(0.39) saturate(1) blur(0.35rem);
  z-index: 0;
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 2rem 1.25rem;
  gap: 1.25rem;
}

.hero-logo {
  width: clamp(1300px, 145vw, 1700px);
  height: auto;
}

@media (max-width: 639px) {
  .hero-logo {
    width: min(82vw, 400px);
  }
}

.hero-tagline {
  margin: 0;
  font-size: clamp(3rem, 4vw + 3rem, 3rem);
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgb(255, 115, 0);
    -webkit-text-stroke: 1.5px #111; /* delineado */
  paint-order: stroke fill;

}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.85rem;
  margin-top: 0.5rem;
}

/* ═══════════════════════════ ABOUT ═══════════════════════════ */
.home-about {
  background: var(--cds-background-color);
}

.about-grid {
  display: grid;
  gap: 2rem;
  align-items: start;
}

.about-text h3 {
  margin: 0 0 0.75rem;
  font-size: var(--cds-text-xl);
  color: var(--cds-primary);
}

.about-text p {
  margin: 0 0 1rem;
  font-size: var(--cds-text-base);
  line-height: var(--cds-leading-relaxed);
  color: var(--cds-text-normal);
}

.about-image-wrap {
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(62, 60, 56, 0.18);
}

.about-image {
  width: 100%;
  height: clamp(200px, 22vw, 320px);
  object-fit: cover;
  display: block;
}

.history-block {
  margin-top: 2.5rem;
  padding-top: 2rem;
  border-top: 1px solid var(--cds-border-soft);
}

.history-title {
  margin: 0 0 1rem;
  font-size: var(--cds-text-xl);
  color: var(--cds-dark);
}

.timeline-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.timeline-arrow {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: var(--cds-dark);
  color: var(--cds-white);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
}

.timeline-track {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  scroll-behavior: smooth;
  scrollbar-width: none;
  flex: 1;
  padding: 0.25rem 0;
}

.timeline-track::-webkit-scrollbar { display: none; }

.timeline-node {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--cds-border-soft);
  border-radius: 0.5rem;
  background: var(--cds-white);
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  text-align: center;
  min-width: 64px;
}

.timeline-node.active {
  background: var(--cds-primary);
  border-color: var(--cds-primary);
  color: var(--cds-white);
}

.node-year {
  font-weight: var(--cds-font-bold);
  font-size: var(--cds-text-xs);
}

.node-label {
  font-size: 0.7rem;
  line-height: 1.2;
  max-width: 70px;
}

.history-desc {
  margin: 1rem 0 0;
  font-size: var(--cds-text-base);
  line-height: var(--cds-leading-relaxed);
  color: var(--cds-text-normal);
}

/* ═══════════════════════════ SERVICES ════════════════════════ */
.home-services {
  background: var(--cds-dark);
}

.home-services .section-title { color: var(--cds-white); }
.home-services .section-lead  { color: rgba(255, 255, 255, 0.75); }

.services-grid {
  display: grid;
  gap: 1.25rem;
  grid-template-columns: 1fr;
}

.service-card {
  background: color-mix(in srgb, var(--cds-white) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--cds-white) 15%, transparent);
  border-radius: 0.75rem;
  padding: 1.5rem;
  color: var(--cds-white);
}

.service-icon {
  font-size: 1.8rem;
  color: var(--cds-primary);
  margin-bottom: 0.75rem;
}

.service-card h3 {
  margin: 0 0 0.5rem;
  font-size: clamp(1.1rem, 1.05rem + 0.5vw, 1.35rem);
  color: var(--cds-white);
}

.service-card p {
  margin: 0;
  font-size: var(--cds-text-sm);
  line-height: var(--cds-leading-relaxed);
  color: rgba(255, 255, 255, 0.78);
}

.home-services .btn-section-outline {
  color: var(--cds-white);
  border-color: rgba(255, 255, 255, 0.5);
}

/* ═══════════════════════════ DIAGNOSTIC ══════════════════════ */
.home-diagnostic {
  background: var(--cds-background-color);
}

.diagnostic-layout {
  display: grid;
  gap: 2rem;
  align-items: center;
}

.diagnostic-text p {
  font-size: var(--cds-text-base);
  line-height: var(--cds-leading-relaxed);
  color: var(--cds-text-normal);
  margin: 0 0 1.25rem;
}

.diagnostic-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1.5rem;
  display: grid;
  gap: 0.5rem;
}

.diagnostic-list li {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: var(--cds-text-base);
  color: var(--cds-text-normal);
}

.diagnostic-list li i { color: var(--cds-primary); flex-shrink: 0; }

.diagnostic-image {
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(62, 60, 56, 0.15);
}

.diagnostic-image img { width: 100%; height: auto; display: block; }

/* ═══════════════════════════ FEATURED ════════════════════════ */
.home-featured { background: var(--cds-light); }

.featured-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(2, 1fr);
}

.featured-card {
  border-radius: 0.65rem;
  overflow: hidden;
  background: var(--cds-white);
  box-shadow: 0 4px 12px rgba(62, 60, 56, 0.1);
}

.featured-card img {
  width: 100%;
  height: 130px;
  object-fit: cover;
  display: block;
}

.featured-card p {
  margin: 0;
  padding: 0.5rem 0.75rem;
  font-size: var(--cds-text-xs);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-text-normal);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ═══════════════════════════ FAQ ═════════════════════════════ */
.home-faq { background: var(--cds-background-color); }

.faq-list { display: grid; gap: 0.75rem; }

.faq-item {
  border: 1px solid var(--cds-border-soft);
  border-radius: 0.6rem;
  background: var(--cds-white);
  overflow: hidden;
}

.faq-question {
  padding: 1rem 1.25rem;
  cursor: pointer;
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-dark);
  list-style: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.faq-question::-webkit-details-marker { display: none; }

.faq-item[open] .faq-question {
  border-bottom: 1px solid var(--cds-border-soft);
  color: var(--cds-primary);
}

.faq-answer {
  margin: 0;
  padding: 1rem 1.25rem;
  font-size: var(--cds-text-base);
  line-height: var(--cds-leading-relaxed);
  color: var(--cds-text-normal);
}

/* ═══════════════════════════ REVIEWS ════════════════════════ */
.home-reviews { background: var(--cds-dark); }

.home-reviews .section-title { color: var(--cds-white); }
.home-reviews .section-lead  { color: rgba(255, 255, 255, 0.7); }

.reviews-grid { display: grid; gap: 1.25rem; }

.review-card {
  background: color-mix(in srgb, var(--cds-white) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--cds-white) 15%, transparent);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.review-stars {
  color: var(--cds-primary);
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
  display: flex;
  gap: 0.15rem;
}

.review-text {
  margin: 0 0 1rem;
  font-size: var(--cds-text-base);
  line-height: var(--cds-leading-relaxed);
  color: rgba(255, 255, 255, 0.85);
  font-style: italic;
}

.review-author {
  font-size: var(--cds-text-sm);
  color: rgba(255, 255, 255, 0.6);
  font-weight: var(--cds-font-semibold);
}

/* ═══════════════════════════ CONTACT ════════════════════════ */
.home-contact { background: var(--cds-background-color); }

.contact-layout { display: grid; gap: 2rem; align-items: start; }

.contact-form-wrap h3 {
  margin: 0 0 1.25rem;
  font-size: var(--cds-text-xl);
  color: var(--cds-dark);
}

.contact-form { display: grid; gap: 1rem; }

.form-field { display: grid; gap: 0.4rem; }

.form-field label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-text-normal);
}

.form-field label i {
  color: var(--cds-primary);
  font-size: 0.85rem;
}

.form-field input,
.form-field textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--cds-border-strong);
  border-radius: 0.5rem;
  font-size: 1rem;
  font-family: inherit;
  color: var(--cds-text-normal);
  background: var(--cds-white);
  line-height: var(--cds-leading-normal);
  transition: border-color 0.15s;
}

.form-field input:focus,
.form-field textarea:focus {
  outline: none;
  border-color: var(--cds-primary);
}

.form-field textarea { resize: vertical; min-height: 120px; }

.form-msg {
  margin: 0;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-size: var(--cds-text-sm);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-msg-error  { background: #fff0f0; color: #c0392b; border: 1px solid #f5c6cb; }
.form-msg-success { background: #f0fff4; color: var(--cds-success); border: 1px solid #c3e6cb; }

.btn-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 48px;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.55rem;
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn-submit:disabled { opacity: 0.65; cursor: not-allowed; }

.contact-card {
  background: var(--cds-white);
  border: 1px solid var(--cds-border-soft);
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.contact-card p {
  margin: 10.05px;
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-size: var(--cds-text-base);
  color: var(--cds-text-normal);
}

.contact-card p i { color: var(--cds-primary); flex-shrink: 0; margin-top: 0.1rem; }
.contact-card a { color: var(--cds-primary); text-decoration: none; }

.contact-channels {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 4px solid var(--cds-border-soft);
}

.contact-channels a {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-text-normal);
  text-decoration: none;
}

.contact-channels a:hover { color: var(--cds-primary); }

.contact-map {
  border-radius: 0.75rem;
  overflow: hidden;
  height: 300px;
  box-shadow: 0 4px 14px rgba(62, 60, 56, 0.12);
}

.contact-map iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}

/* ═══════════════════════════ RESPONSIVE ══════════════════════ */
@media (min-width: 640px) {
  .services-grid      { grid-template-columns: repeat(2, 1fr); }
  .featured-grid      { grid-template-columns: repeat(3, 1fr); }
  .reviews-grid       { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 900px) {
  .about-grid         { grid-template-columns: 1fr 1fr; }
  .diagnostic-layout  { grid-template-columns: 1fr 1fr; }
  .contact-layout     { grid-template-columns: 1fr 1fr; }
  .services-grid      { grid-template-columns: repeat(4, 1fr); }
  .featured-grid      { grid-template-columns: repeat(3, 1fr); }
  .reviews-grid       { grid-template-columns: repeat(3, 1fr); }
}
</style>
