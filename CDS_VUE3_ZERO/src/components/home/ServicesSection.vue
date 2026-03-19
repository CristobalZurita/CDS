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
  background: var(--cds-dark);
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
  background: #4a4641;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 18px 34px rgba(10, 10, 10, 0.18);
}

.service-icon {
  width: 3.25rem;
  height: 3.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--cds-radius-pill);
  font-size: 1.4rem;
  color: var(--cds-primary);
  background: rgba(236, 107, 0, 0.12);
}

.service-card h3 {
  margin: 0;
  font-size: clamp(1.1rem, 1.05rem + 0.5vw, 1.35rem);
  color: var(--cds-white);
  line-height: 1.05;
}

.service-card p {
  margin: 0;
  font-size: clamp(0.96rem, 0.88rem + 0.32vw, 1.14rem);
  line-height: 1.62;
  color: rgba(255, 255, 255, 0.78);
}

.home-services .btn-section-outline {
  background: transparent;
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
