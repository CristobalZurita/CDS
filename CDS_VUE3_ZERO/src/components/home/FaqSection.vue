<template>
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
</template>

<script setup>
const faqs = [
  { q: '¿Qué tipos de equipos reparan?',        a: 'Sintetizadores analógicos y digitales, drum machines, samplers, teclados y procesadores de efectos de todas las marcas y épocas.' },
  { q: '¿Cuánto demora una reparación?',         a: 'Una revisión básica puede tardar 3-7 días hábiles. Reparaciones mayores o con espera de repuestos pueden tomar más tiempo. Siempre informamos antes de comenzar.' },
  { q: '¿Puedo traer mi equipo sin cita previa?', a: 'Recomendamos agendar antes para garantizar atención. Puedes usar el sistema de citas online o contactarnos por WhatsApp.' },
  { q: '¿Tienen garantía los trabajos realizados?', a: 'Sí. Todos los trabajos tienen garantía de 90 días sobre la reparación específica realizada.' },
  { q: '¿Trabajan con equipos vintage?',          a: 'Absolutamente. Tenemos amplia experiencia con instrumentos clásicos de los años 70-90: Moog, Roland, Korg, Yamaha, Sequential, entre otros.' },
]
</script>

<style scoped src="./homeShared.css"></style>

<style scoped>
.home-faq { background: var(--cds-background-color); }

.faq-list {
  display: grid;
  gap: 0.9rem;
  max-width: 56rem;
}

.faq-item {
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-lg);
  background: var(--cds-white);
  overflow: hidden;
  box-shadow: var(--cds-shadow-sm);
}

.faq-question {
  padding: 1.05rem 1.3rem;
  cursor: pointer;
  font-size: clamp(1rem, 0.92rem + 0.4vw, 1.2rem);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-dark);
  list-style: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.faq-question::after {
  content: '+';
  flex-shrink: 0;
  font-size: 1.1em;
  line-height: 1;
  color: var(--cds-primary);
}

.faq-question::-webkit-details-marker { display: none; }

.faq-item[open] .faq-question {
  border-bottom: 1px solid var(--cds-border-soft);
  color: var(--cds-primary);
}

.faq-item[open] .faq-question::after {
  content: '−';
}

.faq-answer {
  margin: 0;
  padding: 0 1.3rem 1.15rem;
  font-size: clamp(0.98rem, 0.9rem + 0.34vw, 1.14rem);
  line-height: 1.65;
  color: var(--cds-text-normal);
}
</style>
