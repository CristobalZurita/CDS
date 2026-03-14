<template>
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

@media (min-width: 640px) {
  .services-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 900px) {
  .services-grid { grid-template-columns: repeat(4, 1fr); }
}
</style>
