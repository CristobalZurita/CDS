<template>
  <section id="reviews" class="home-section home-reviews">
    <div class="section-inner container">
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
.home-reviews {
  background: var(--cds-surface-dark);
}

.reviews-grid { display: grid; gap: 1.25rem; }

.review-card {
  display: flex;
  flex-direction: column;
  background: var(--layout-public-dark-card-warm);
  border: 1px solid var(--layout-public-dark-border-strong);
  box-shadow: 0 18px 34px rgba(10, 10, 10, 0.18);
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
  flex: 1;
  font-size: var(--layout-home-text-card-body, clamp(0.98rem, 0.94rem + 0.22vw, 1.08rem));
  line-height: 1.78;
  color: var(--layout-public-dark-text);
  font-style: italic;
}

.review-author {
  font-size: var(--layout-home-text-meta, var(--cds-text-sm));
  color: var(--layout-public-dark-text-soft);
  font-weight: var(--cds-font-semibold);
}

@media (min-width: 640px) {
  .reviews-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 900px) {
  .reviews-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
