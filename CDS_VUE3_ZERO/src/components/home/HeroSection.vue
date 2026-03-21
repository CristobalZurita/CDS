<template>
  <section id="hero" class="home-hero">
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

    <OscilloscopeStrip class="hero-oscilloscope" />
  </section>
</template>

<script setup>
import OscilloscopeStrip from '@/components/home/OscilloscopeStrip.vue'
import { useSiteImages } from '@/composables/useSiteImages'
import { useMediaBinding } from '@/composables/useMediaBinding'

const { resolveImageUrl } = useSiteImages()
const { resolveSlotOr } = useMediaBinding()
</script>

<style scoped>
.home-hero {
  --hero-pad-top: clamp(2.6rem, 5.8vw, 4.8rem);
  --hero-pad-inline: clamp(1.25rem, 5vw, 3rem);
  --hero-pad-bottom: clamp(3.75rem, 8vw, 5.75rem);
  --hero-gap: clamp(1rem, 2.2vw, 1.7rem);
  --hero-osc-height: clamp(8.8rem, 10vw, 7rem);
  --hero-logo-width: min(72vw, 1500px);
  --hero-logo-margin-bottom: -0.35rem;
  --hero-service-size: clamp(1.28rem, 1.08rem + 1.05vw, 1.92rem);
  --hero-service-letter: 0.12em;
  --hero-btn-min-height: 72px;
  --hero-btn-pad-block: 1rem;
  --hero-btn-pad-inline: 2rem;
  --hero-btn-font-size: clamp(1rem, 0.86rem + 0.65vw, 1.35rem);
  min-height: calc(100svh - var(--layout-header-height, var(--cds-header-height, 96px)));
  min-height: calc(100dvh - var(--layout-header-height, var(--cds-header-height, 96px)));
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  background: var(--cds-light);
  position: relative;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  width: 100%;
  max-width: var(--layout-content-max, var(--cds-content-max));
  margin-inline: auto;
  padding:
    var(--hero-pad-top)
    var(--hero-pad-inline)
    calc(var(--hero-pad-bottom) + var(--hero-osc-height));
  gap: var(--hero-gap);
}

.hero-logo {
  width: var(--hero-logo-width);
  max-width: none;
  height: auto;
  object-fit: contain;
  margin-bottom: var(--hero-logo-margin-bottom);
}

.hero-tagline {
  margin-top: 1px;
  max-width: 70ch;
  font-size: var(--hero-service-size);
  font-family: var(--layout-home-font-family-heading, var(--layout-home-font-family-base, var(--cds-font-family-base)), sans-serif);
  font-weight: var(--cds-font-bold );
  line-height: 1.08;
  letter-spacing: var(--hero-service-letter);
  text-transform: uppercase;
  color: var(--cds-primary);
  text-wrap: balance;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.75rem;
  margin-top: 0.25rem;
  width: 100%;
}

.btn-hero {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: var(--hero-btn-min-height);
  padding: var(--hero-btn-pad-block) var(--hero-btn-pad-inline);
  border-radius: var(--cds-radius-pill);
  font-size: var(--hero-btn-font-size);
  font-family: var(--layout-home-font-family-base, var(--cds-font-family-base), sans-serif);
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.02em;
  text-transform: uppercase;
  text-decoration: none;
  transition: transform 0.15s, box-shadow 0.15s, background 0.15s;
  box-shadow: 0 16px 30px rgba(35, 34, 31, 0.14);
  border: 2px solid transparent;
}

.btn-hero:hover {
  transform: translateY(-1px);
}

.btn-hero-primary {
  background: var(--cds-primary);
  color: var(--cds-white);
  border: 2px solid var(--cds-primary);
}

.btn-hero-outline {
  background: var(--cds-surface-1);
  color: var(--cds-dark);
  border-color: var(--cds-border-card);
}

.hero-oscilloscope {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 50px;
  width: 100%;
  --oscilloscope-height: var(--hero-osc-height);
}

@media (min-width: 600px) and (max-width: 899px) {
  .home-hero {
    --hero-logo-width: min(76vw, 620px);
    --hero-service-size: clamp(1.3rem, 2.7vw, 1.72rem);
  }
}

@media (max-width: 599px) {
  .home-hero {
    --hero-pad-top: clamp(1rem, 4.2vw, 1.35rem);
    --hero-pad-inline: clamp(1rem, 4.5vw, 1.4rem);
    --hero-pad-bottom: clamp(1rem, 3vw, 1.4rem);
    --hero-gap: clamp(0.75rem, 2.6vw, 1rem);
    --hero-osc-height: clamp(3.8rem, 11vw, 4.8rem);
    --hero-logo-width: min(92vw, 440px);
    --hero-logo-margin-bottom: 0;
    --hero-service-size: clamp(1.05rem, 4.2vw, 1.28rem);
    --hero-service-letter: 0.06em;
    --hero-btn-min-height: 3.7rem;
    --hero-btn-pad-block: 0.88rem;
    --hero-btn-pad-inline: 1.25rem;
    --hero-btn-font-size: clamp(0.96rem, 4vw, 1.08rem);
    min-height: auto;
  }

  .hero-actions {
    width: 100%;
    flex-direction: column;
    align-items: center;
  }

  .btn-hero {
    width: min(92vw, 22rem);
  }
}
</style>
