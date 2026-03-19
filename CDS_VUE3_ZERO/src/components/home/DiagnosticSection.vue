<template>
  <section id="diagnostic" class="home-section home-diagnostic">
    <div class="section-inner container diagnostic-layout">
      <div class="diagnostic-text">
        <h2 class="section-title">Cotiza tu instrumento</h2>
        <p>Usa nuestro cotizador IA para obtener una estimación preliminar antes de traer tu equipo al taller. Rápido, gratuito y sin compromiso.</p>
        <ul class="diagnostic-list">
          <li><i class="fas fa-check"></i> Diagnóstico orientativo inmediato</li>
          <li><i class="fas fa-check"></i> Sin necesidad de registrarte</li>
          <li><i class="fas fa-check"></i> Compatible con todos los equipos de audio</li>
        </ul>
        <router-link to="/cotizador" class="btn-section">
          <i class="fas fa-file-circle-check"></i> Ir al cotizador
        </router-link>
      </div>
      <div class="diagnostic-image">
        <img
          :src="resolveSlotOr('home.diagnostic.image', resolveImageUrl('/images/instrumentos/KORG_WAVESTATE.webp'))"
          alt="KORG Wavestate — sintetizador"
          loading="lazy"
          width="480"
          height="280"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { useSiteImages } from '@/composables/useSiteImages'
import { useMediaBinding } from '@/composables/useMediaBinding'

const { resolveImageUrl } = useSiteImages()
const { resolveSlotOr } = useMediaBinding()
</script>

<style scoped src="./homeShared.css"></style>

<style scoped>
.home-diagnostic {
  background: var(--cds-background-color);
}

.diagnostic-layout {
  display: grid;
  gap: clamp(1.35rem, 2.5vw, 2.4rem);
  align-items: stretch;
}

.diagnostic-text {
  display: grid;
  align-content: start;
  gap: 1rem;
  padding: clamp(1.25rem, 2vw, 2rem);
  border-radius: clamp(1.1rem, 2vw, 1.7rem);
  background: var(--cds-white);
  border: 1px solid var(--cds-border-card);
  box-shadow: var(--cds-shadow-sm);
}

.diagnostic-text p {
  font-size: clamp(1rem, 0.92rem + 0.38vw, 1.22rem);
  line-height: 1.65;
  color: var(--cds-text-normal);
  margin: 0;
}

.diagnostic-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.75rem;
}

.diagnostic-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-size: clamp(1rem, 0.92rem + 0.32vw, 1.16rem);
  color: var(--cds-text-normal);
  line-height: 1.5;
}

.diagnostic-list li i { color: var(--cds-primary); flex-shrink: 0; }

.diagnostic-image {
  min-height: 100%;
  border-radius: clamp(1.1rem, 2vw, 1.7rem);
  overflow: hidden;
  border: 1px solid var(--cds-border-card);
  background: var(--cds-white);
  box-shadow: var(--cds-shadow-md);
}

.diagnostic-image img {
  width: 100%;
  height: 100%;
  min-height: 320px;
  display: block;
  object-fit: cover;
}

@media (min-width: 900px) {
  .diagnostic-layout { grid-template-columns: 1fr 1fr; }
}
</style>
