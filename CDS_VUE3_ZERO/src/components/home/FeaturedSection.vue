<template>
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
</template>

<script setup>
import { computed } from 'vue'
import { useSiteImages } from '@/composables/useSiteImages'

const { resolveImageArray } = useSiteImages()

const featuredInstrumentsRaw = [
  { name: 'KORG Wavestate',   image: '/images/instrumentos/KORG_WAVESTATE.webp' },
  { name: 'KORG Wavestation', image: '/images/instrumentos/KORG_WAVESTATION.webp' },
  { name: 'Roland D-50',      image: '/images/instrumentos/ROLAND_D50.webp' },
  { name: 'Yamaha DX7 MkI',   image: '/images/instrumentos/YAMAHA_DX7_MK1.webp' },
  { name: 'KORG M1',          image: '/images/instrumentos/KORG_M1.webp' },
  { name: 'KORG Triton',      image: '/images/instrumentos/KORG_TRITON.webp' },
]

const featuredInstruments = computed(() => resolveImageArray(featuredInstrumentsRaw))
</script>

<style scoped src="./homeShared.css"></style>

<style scoped>
.home-featured { background: var(--cds-light); }

.featured-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(2, 1fr);
}

.featured-card {
  border-radius: var(--cds-radius-sm);
  overflow: hidden;
  background: var(--cds-white);
  box-shadow: var(--cds-shadow-sm);
}

.featured-card img {
  width: 100%;
  height: 130px;
  object-fit: cover;
  display: block;
}

.featured-card p {
  margin: 0;
  padding: var(--cds-space-xs) var(--cds-space-sm);
  font-size: var(--cds-text-xs);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-text-normal);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (min-width: 640px) {
  .featured-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (min-width: 900px) {
  .featured-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
