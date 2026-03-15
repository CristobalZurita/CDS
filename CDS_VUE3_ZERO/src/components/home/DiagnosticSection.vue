<template>
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

@media (min-width: 900px) {
  .diagnostic-layout { grid-template-columns: 1fr 1fr; }
}
</style>
