<template>
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
</template>

<script setup>
const reviews = [
  { author: 'Rodrigo M.', text: 'Excelente servicio. Repararon mi DX7 en tiempo récord y quedó impecable. Muy profesionales y con conocimiento real del instrumento.' },
  { author: 'Camila V.',  text: 'Llevé mi Korg MS2000 que nadie más quería tocar. Lo dejaron como nuevo. Muy recomendable.' },
  { author: 'Felipe A.',  text: 'Puntualidad, honestidad en el diagnóstico y precio justo. El mejor taller de sintetizadores que he conocido en Chile.' },
]
</script>

<style scoped src="./homeShared.css"></style>

<style scoped>
.home-reviews { background: var(--cds-dark); }

.home-reviews .section-lead  { color: rgba(255, 255, 255, 0.7); }

.reviews-grid { display: grid; gap: 1.25rem; }

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

@media (min-width: 640px) {
  .reviews-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 900px) {
  .reviews-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
