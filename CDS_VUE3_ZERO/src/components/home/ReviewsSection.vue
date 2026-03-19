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
  background: var(--cds-dark);
}

.reviews-grid { display: grid; gap: 1.25rem; }

.review-card {
  display: flex;
  flex-direction: column;
  background: #4a4641;
  border: 1px solid #5f5a54;
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
  font-size: clamp(1.7rem, 0.92rem + 0.34vw, 1.16rem);
  line-height: 1.65;
  color: #f2eee7;
  font-style: italic;
}

.review-author {
  font-size: var(--cds-text-sm);
  color: #cdc5bb;
  font-weight: var(--cds-font-semibold);
}

@media (min-width: 640px) {
  .reviews-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 900px) {
  .reviews-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
