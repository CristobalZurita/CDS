<template>
  <div class="app-root">

    <HeroSection />
    <ContactSection />
    <SiteFooter />

    <!-- Botón flotante WhatsApp -->
    <a
      class="floating-whatsapp"
      href="https://wa.me/56982957538"
      target="_blank"
      rel="noopener noreferrer"
      aria-label="Contactar por WhatsApp"
    >
      <i class="fa-brands fa-whatsapp"></i>
    </a>

    <!-- Scroll to top -->
    <button
      v-show="showScrollTop"
      class="scroll-top"
      type="button"
      aria-label="Ir arriba"
      @click="scrollToTop"
    >
      <i class="fas fa-arrow-up"></i>
    </button>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import HeroSection from './components/HeroSection.vue'
import ContactSection from './components/ContactSection.vue'
import SiteFooter from './components/SiteFooter.vue'

const scrollY = ref(0)
const showScrollTop = computed(() => scrollY.value > 300)

function onScroll() { scrollY.value = window.scrollY }
function scrollToTop() { window.scrollTo({ top: 0, behavior: 'smooth' }) }

onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style>
.app-root {
  min-height: 100svh;
  display: flex;
  flex-direction: column;
}

/* WhatsApp flotante — izquierda */
.floating-whatsapp {
  position: fixed;
  left: 1rem;
  bottom: 1.25rem;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: var(--cds-whatsapp);
  color: var(--cds-white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.55rem;
  text-decoration: none;
  z-index: 999;
  box-shadow: 0 4px 14px color-mix(in srgb, var(--cds-whatsapp) 45%, transparent);
  transition: transform 0.2s, box-shadow 0.2s;
}

.floating-whatsapp:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 20px color-mix(in srgb, var(--cds-whatsapp) 55%, transparent);
}

/* Scroll top — derecha */
.scroll-top {
  position: fixed;
  right: 1rem;
  bottom: 1.25rem;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  border: none;
  background: var(--cds-primary);
  color: var(--cds-white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  cursor: pointer;
  z-index: 999;
  box-shadow: 0 4px 14px color-mix(in srgb, var(--cds-primary) 35%, transparent);
  transition: transform 0.2s, box-shadow 0.2s;
}

.scroll-top:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 20px color-mix(in srgb, var(--cds-primary) 50%, transparent);
}

@media (max-width: 599px) {
  .floating-whatsapp { width: 38px; height: 38px; font-size: 1.15rem; }
  .scroll-top        { width: 36px; height: 36px; font-size: 0.85rem; }
}

@media (min-width: 768px) {
  .floating-whatsapp {
    left: 1.5rem;
    bottom: 1.5rem;
    width: 54px;
    height: 54px;
    font-size: 1.75rem;
  }
  .scroll-top {
    right: 1.5rem;
    bottom: 1.5rem;
    width: 50px;
    height: 50px;
  }
}
</style>
