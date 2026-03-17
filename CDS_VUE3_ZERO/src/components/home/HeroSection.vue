<template>
  <section id="hero" class="home-hero">
    <div class="hero-bg" aria-hidden="true"></div>

    <div class="hero-content">
      <img
        :src="resolveSlotOr('home.hero.logo', resolveImageUrl('/images/logo/NUEVO_cirujano.webp'))"
        alt="Cirujano de Sintetizadores"
        class="hero-logo"
        width="1800"
        height="1220"
        loading="eager"
      />

      <p class="hero-tagline">
        RESTAURACIÓN &nbsp;·&nbsp; MANTENCIÓN &nbsp;·&nbsp; REPARACIÓN
      </p>

      <div class="hero-actions">
        <router-link to="/agendar" class="btn-hero btn-hero-primary">
          <i class="fas fa-calendar-check"></i>
          Agenda tu hora
        </router-link>
        <router-link to="/cotizador" class="btn-hero btn-hero-outline">
          <i class="fas fa-file-circle-check"></i>
          Cotiza tu instrumento
        </router-link>
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

<style scoped>
.home-hero {
  position: relative;
  min-height: calc(100svh - var(--cds-header-height, 96px));
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 2rem 1.25rem;
  gap: 1.25rem;
}

.hero-logo {
  width: clamp(1500px, 50vw, 500px);
  height: auto;
}

@media (max-width: 639px) {
  .hero-logo {
    width: min(82vw, 400px);
  }
}

.hero-tagline {
  margin: 0;
  font-size: clamp(3rem, 4vw + 3rem, 3rem);
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--cds-primary);
  -webkit-text-stroke: 1px var(--cds-dark);
  paint-order: stroke fill;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--cds-space-sm);
  margin-top: 0.5rem;
}

.btn-hero {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 48px;
  padding: 0.75rem 1.4rem;
  border-radius: var(--cds-radius-md);
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  text-decoration: none;
  transition: transform 0.15s, box-shadow 0.15s;
}

.btn-hero:hover { transform: translateY(-1px); }

.btn-hero-primary {
  background: var(--cds-primary);
  color: var(--cds-white);
  border: 2px solid var(--cds-primary);
  -webkit-text-stroke: 1px var(--cds-dark);
  paint-order: stroke fill;
  font-size: var(--cds-text-lg);
}

.btn-hero-outline {
  background: transparent;
  color: var(--cds-white);
  border: 2px solid var(--cds-white);
  -webkit-text-stroke: 1.5px var(--cds-dark);
  paint-order: stroke fill;
  font-size: var(--cds-text-lg);
}
</style>
