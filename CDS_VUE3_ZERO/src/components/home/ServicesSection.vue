<template>
  <section id="services" class="home-section home-services">
    <div class="section-inner container">
      <h2 class="section-title">Quiénes somos y qué hacemos</h2>
      <p class="section-lead">
        Taller especializado en reparación, mantenimiento y personalización de sintetizadores, drum machines,
        teclados y otros equipos electrónicos musicales.
      </p>

      <div class="services-overview">
        <article class="services-story">
          <h3>Cirujano de Sintetizadores</h3>
          <p>
            <strong>
              Cada instrumento se revisa con criterio de taller: limpieza interna, diagnóstico fino, revisión de
              fuente, reemplazo de componentes y calibración cuando corresponde.
            </strong>
          </p>
          <p>
            El objetivo no es solo que vuelva a encender, sino que recupere estabilidad, respuesta y carácter sonoro,
            respetando su diseño original o integrando modificaciones cuando el proyecto realmente lo pide.
          </p>
        </article>

        <aside class="services-scope" aria-label="Alcance del taller">
          <h3>Alcance del taller</h3>
          <ul>
            <li>Sintetizadores, teclados y pianos eléctricos.</li>
            <li>Drum machines, módulos, pedales y procesadores.</li>
            <li>Soporte técnico, mantención y proyectos especiales.</li>
          </ul>
        </aside>
      </div>

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
        <router-link to="/cotizador" class="btn-section btn-section-outline">
          <i class="fas fa-file-invoice-dollar"></i> Cotizar
        </router-link>
      </div>
    </div>
  </section>
</template>

<script setup>
const services = [
  { icon: 'fas fa-screwdriver-wrench', title: 'Reparación',     desc: 'Diagnóstico completo y reparación de fallas eléctricas, mecánicas y de firmware en sintetizadores y teclados.' },
  { icon: 'fas fa-heart-pulse',        title: 'Mantención',     desc: 'Limpieza interna, revisión de fuente de poder, lubricación de controles y verificación de voltajes.' },
  { icon: 'fas fa-sliders',            title: 'Modificación',   desc: 'Instalación de MIDI retrofit, expansiones de voz, mods de filtro y personalización a medida.' },
  { icon: 'fas fa-calculator',         title: 'Presupuesto IA', desc: 'Cotización preliminar asistida por IA para evaluar el alcance del trabajo antes de traer tu equipo.' },
]
</script>

<style scoped src="./homeShared.css"></style>

<style scoped>
.home-services {
  background: var(--cds-surface-dark);
}

.home-services .section-title {
  max-width: 16ch;
}

.services-overview {
  display: grid;
  gap: 1rem;
}

.services-story,
.services-scope {
  display: grid;
  gap: 0.8rem;
  min-height: 100%;
  padding: var(--layout-home-card-padding, var(--cds-space-lg));
  border-radius: var(--cds-radius-lg);
  border: 1px solid var(--layout-public-dark-border);
  box-shadow: 0 18px 34px rgba(10, 10, 10, 0.22);
}

.services-story {
  background: var(--layout-public-dark-panel);
  color: var(--layout-public-dark-text);
}

.services-scope {
  background: var(--layout-public-dark-panel-alt);
  color: var(--layout-public-dark-text-soft);
  align-content: start;
}

.services-story h3,
.services-scope h3 {
  margin: 0;
  font-size: var(--layout-home-text-card-title, clamp(1.1rem, 1.05rem + 0.5vw, 1.35rem));
  font-family: var(--layout-home-font-family-heading, var(--layout-home-font-family-base, var(--cds-font-family-base)), sans-serif);
  line-height: 1.12;
  letter-spacing: -0.01em;
}

.services-story h3 {
  color: var(--cds-white);
}

.services-scope h3 {
  color: var(--cds-warm-support);
}

.services-story p,
.services-scope li {
  margin: 0;
  font-size: var(--layout-home-text-card-body, clamp(0.96rem, 0.88rem + 0.32vw, 1.14rem));
  line-height: 1.7;
}

.services-scope ul {
  margin: 0;
  padding-left: 1.15rem;
  display: grid;
  gap: 0.6rem;
}

.services-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

.service-card {
  color: var(--cds-white);
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  background: var(--layout-public-dark-card);
  border: 1px solid var(--layout-public-dark-border);
  box-shadow: 0 18px 34px rgba(10, 10, 10, 0.28);
}

.service-icon {
  width: 3.9rem;
  height: 3.9rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--cds-radius-pill);
  font-size: 1.72rem;
  color: var(--cds-primary);
  background: var(--layout-public-icon-surface);
  border: 1px solid var(--layout-public-icon-border);
  box-shadow: 0 10px 22px rgba(16, 18, 21, 0.18);
}

.service-card h3 {
  margin: 0;
  font-size: var(--layout-home-text-card-title, clamp(1.1rem, 1.05rem + 0.5vw, 1.35rem));
  font-family: var(--layout-home-font-family-heading, var(--layout-home-font-family-base, var(--cds-font-family-base)), sans-serif);
  color: var(--cds-white);
  line-height: 1.12;
  letter-spacing: -0.01em;
}

.service-card p {
  margin: 0;
  font-size: var(--layout-home-text-card-body, clamp(0.96rem, 0.88rem + 0.32vw, 1.14rem));
  line-height: 1.7;
  color: var(--layout-public-dark-text-soft);
}

.home-services .btn-section-outline {
  background: var(--layout-public-dark-panel-alt);
  color: var(--cds-white);
  border-color: var(--layout-public-dark-border-strong);
}

@media (min-width: 640px) {
  .services-overview {
    grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
  }

  .services-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 900px) {
  .services-grid { grid-template-columns: repeat(4, 1fr); }
}
</style>
