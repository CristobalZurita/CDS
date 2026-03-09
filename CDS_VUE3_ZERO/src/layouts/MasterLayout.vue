<template>
  <div class="master-layout">

    <header class="site-header">
      <div class="site-header-inner">

        <router-link to="/" class="brand-link" @click="menuOpen = false">
          <img
            src="/images/logo/logo_square_004.webp"
            alt="Cirujano de Sintetizadores"
            class="brand-logo"
            width="44"
            height="44"
          />
          <span class="brand-name">Cirujano de Sintetizadores</span>
        </router-link>

        <nav id="primary-nav" class="site-nav" :class="{ 'is-open': menuOpen }">

          <!-- En home: anchors de sección -->
          <template v-if="isHome">
            <a
              v-for="sec in navSections"
              :key="sec.id"
              :href="`#${sec.id}`"
              class="site-nav-link"
              @click="menuOpen = false"
            >{{ sec.name }}</a>
          </template>

          <!-- En otras páginas: volver a Inicio -->
          <router-link
            v-else
            to="/"
            class="site-nav-link"
            @click="menuOpen = false"
          >Inicio</router-link>

          <router-link to="/calculadoras" class="site-nav-link site-nav-caps" @click="menuOpen = false">Calculadoras</router-link>
          <router-link to="/tienda" class="site-nav-link site-nav-caps" @click="menuOpen = false">Tienda</router-link>

          <router-link
            v-if="isAuthenticated"
            to="/dashboard"
            class="site-nav-link site-nav-caps"
            @click="menuOpen = false"
          >Dashboard</router-link>
          <router-link
            v-else
            to="/login"
            class="site-nav-link site-nav-caps"
            @click="menuOpen = false"
          >Iniciar Sesión</router-link>

        </nav>

        <!-- Cotizar — siempre visible, derecha del header -->
        <router-link to="/cotizador-ia" class="nav-cotizar" aria-label="Ir al cotizador IA">
          <i class="fas fa-file-invoice-dollar"></i>
          <span class="nav-cotizar-label">Cotizar</span>
        </router-link>

        <button
          class="nav-toggle"
          type="button"
          :aria-expanded="String(menuOpen)"
          aria-controls="primary-nav"
          aria-label="Abrir menú"
          @click="menuOpen = !menuOpen"
        >
          <i class="fas fa-bars"></i>
        </button>

      </div>
    </header>

    <main class="site-body">
      <router-view />
    </main>

    <footer class="site-footer">
      <div class="site-footer-grid">

        <section class="footer-brand">
          <img
            src="/images/logo/logo_square_004.webp"
            alt="Cirujano de Sintetizadores"
            class="footer-logo"
            width="56"
            height="56"
          />
          <p class="footer-brand-name">Cirujano de Sintetizadores</p>
          <p class="footer-brand-tagline">
            Taller especializado en reparación, restauración y modificación de
            sintetizadores, teclados y equipos de audio.
          </p>
        </section>

        <section>
          <h2>Servicios</h2>
          <div class="site-footer-links">
            <a href="#services">Reparación y restauración</a>
            <a href="#services">Mantención preventiva</a>
            <a href="#services">Modificaciones</a>
            <router-link to="/cotizador-ia">Cotizador IA</router-link>
            <router-link to="/calculadoras">Calculadoras</router-link>
          </div>
        </section>

        <section>
          <h2>Redes</h2>
          <div class="site-footer-links">
            <a href="https://www.instagram.com/cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer">
              <i class="fa-brands fa-instagram"></i> Instagram
            </a>
            <a href="https://www.facebook.com/Cirujanodesintetizadores/" target="_blank" rel="noopener noreferrer">
              <i class="fa-brands fa-facebook"></i> Facebook
            </a>
            <a href="https://wa.me/56982957538" target="_blank" rel="noopener noreferrer">
              <i class="fa-brands fa-whatsapp"></i> WhatsApp
            </a>
          </div>
        </section>

        <section>
          <h2>Contacto</h2>
          <div class="site-footer-links">
            <a href="tel:+56982957538">
              <i class="fas fa-phone"></i> +56 9 8295 7538
            </a>
            <a href="mailto:contacto@cirujanodesintetizadores.com">
              <i class="fas fa-envelope"></i> contacto@cirujanodesintetizadores.com
            </a>
            <span><i class="fas fa-location-dot"></i> Valparaíso, Chile</span>
          </div>
        </section>

      </div>

      <div class="site-footer-legal">
        <span>© {{ currentYear }} Cirujano de Sintetizadores</span>
        <span>·</span>
        <router-link to="/privacidad">Política de privacidad</router-link>
        <span>·</span>
        <router-link to="/terminos">Términos y condiciones</router-link>
        <span>·</span>
        <a href="https://github.com/CristobalZurita/cirujano-front" target="_blank" rel="noopener noreferrer">
          Repositorio
        </a>
      </div>
    </footer>

    <!-- Botón flotante WhatsApp — izquierda -->
    <a
      class="floating-whatsapp"
      href="https://wa.me/56982957538"
      target="_blank"
      rel="noopener noreferrer"
      aria-label="Contactar por WhatsApp"
    >
      <i class="fa-brands fa-whatsapp"></i>
    </a>

    <!-- Volver arriba — derecha abajo -->
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
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@new/composables/useAuth'
import { useHomePage } from '@new/composables/useHomePage'

const { isAuthenticated } = useAuth()
const { sections } = useHomePage()
const route = useRoute()

// Solo las secciones navegables (excluir hero)
const navSections = computed(() => sections.value.filter(s => s.id !== 'hero'))

const isHome = computed(() => route.path === '/')

const menuOpen = ref(false)

const currentYear = new Date().getFullYear()

// Scroll-to-top
const scrollY = ref(0)
const showScrollTop = computed(() => scrollY.value > 300)

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function _onScroll() {
  scrollY.value = window.scrollY
}

onMounted(() => window.addEventListener('scroll', _onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', _onScroll))
</script>

<style scoped>
.master-layout {
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr auto;
}

/* ─── HEADER ─── */
.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--cds-dark);
  border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 20%, var(--cds-dark));
}

.site-header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1rem;
  min-height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.brand-link {
  color: var(--cds-white);
  text-decoration: none;
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.01em;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.brand-logo {
  width: 44px;
  height: 44px;
  border-radius: 0.35rem;
  flex-shrink: 0;
}

.brand-name {
  font-size: var(--cds-text-sm);
  line-height: 1.2;
  display: none;
}

@media (min-width: 480px) {
  .brand-name {
    display: block;
  }
}

/* ─── NAV ─── */
.site-nav {
  display: none;
  flex-wrap: wrap;
  gap: 0.2rem;
  align-items: center;
  flex: 1;
}

.site-nav.is-open {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--cds-dark);
  padding: 0.75rem 1rem 1rem;
  border-top: 1px solid color-mix(in srgb, var(--cds-light) 15%, var(--cds-dark));
  z-index: 99;
}

.site-nav-link {
  color: var(--cds-white);
  text-decoration: none;
  min-height: 40px;
  padding: 0.45rem 0.65rem;
  border-radius: 0.45rem;
  font-size: var(--cds-text-base);
  display: inline-flex;
  align-items: center;
  transition: background 0.15s;
  white-space: nowrap;
}

.site-nav-link:hover {
  background: color-mix(in srgb, var(--cds-white) 12%, transparent);
}

.site-nav-link.router-link-active {
  background: color-mix(in srgb, var(--cds-primary) 55%, black);
}

.site-nav-caps {
  text-transform: uppercase;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.04em;
}

/* ─── COTIZAR (navbar derecha, siempre visible) ─── */
.nav-cotizar {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.85rem;
  border-radius: 0.45rem;
  background: var(--cds-primary);
  color: var(--cds-white);
  text-decoration: none;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.02em;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background 0.15s, transform 0.15s;
}

.nav-cotizar:hover {
  background: color-mix(in srgb, var(--cds-primary) 85%, black);
  transform: translateY(-1px);
}

.nav-cotizar-label {
  display: none;
}

@media (min-width: 480px) {
  .nav-cotizar-label {
    display: inline;
  }
}

/* ─── HAMBURGER ─── */
.nav-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 0.4rem;
  background: transparent;
  color: var(--cds-white);
  font-size: 1.15rem;
  cursor: pointer;
  flex-shrink: 0;
}

.nav-toggle:hover {
  background: color-mix(in srgb, var(--cds-white) 15%, transparent);
}

/* Desktop: mostrar nav, ocultar hamburger */
@media (min-width: 1200px) {
  .site-nav {
    display: flex;
    position: static;
    flex-direction: row;
    padding: 0;
    border-top: none;
  }

  .nav-toggle {
    display: none;
  }
}

/* ─── MAIN ─── */
.site-body {
  min-height: 0;
}

/* ─── FOOTER ─── */
.site-footer {
  background: var(--cds-footer-bg-highlight-color);
  color: var(--cds-white);
  padding: 2.5rem 1rem 1rem;
}

.site-footer-grid {
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  gap: 2rem;
  grid-template-columns: 1fr;
}

.site-footer h2 {
  margin: 0 0 0.75rem;
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: color-mix(in srgb, var(--cds-white) 60%, transparent);
}

.site-footer p {
  margin: 0;
  font-size: var(--cds-text-sm);
  line-height: var(--cds-leading-normal);
  color: color-mix(in srgb, var(--cds-white) 75%, transparent);
}

/* Brand column */
.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.footer-logo {
  width: 52px;
  height: 52px;
  border-radius: 0.4rem;
}

.footer-brand-name {
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-white);
  margin: 0;
  line-height: 1.2;
}

.footer-brand-tagline {
  font-size: var(--cds-text-sm);
  color: color-mix(in srgb, var(--cds-white) 65%, transparent);
  line-height: 1.5;
  margin: 0;
}

.site-footer-links {
  display: grid;
  gap: 0.5rem;
}

.site-footer a {
  color: color-mix(in srgb, var(--cds-white) 75%, transparent);
  font-size: var(--cds-text-sm);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  transition: color 0.15s;
}

.site-footer a:hover {
  color: var(--cds-white);
}

.site-footer-links span {
  color: color-mix(in srgb, var(--cds-white) 65%, transparent);
  font-size: var(--cds-text-sm);
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.site-footer-legal {
  max-width: 1280px;
  margin: 2rem auto 0;
  padding-top: 1rem;
  border-top: 1px solid color-mix(in srgb, var(--cds-white) 12%, transparent);
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  font-size: var(--cds-text-xs);
  color: color-mix(in srgb, var(--cds-white) 50%, transparent);
}

.site-footer-legal a {
  color: color-mix(in srgb, var(--cds-white) 50%, transparent);
  font-size: var(--cds-text-xs);
}

.site-footer-legal a:hover {
  color: var(--cds-white);
}

@media (min-width: 600px) {
  .site-footer-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .site-footer-grid {
    grid-template-columns: 2fr repeat(3, minmax(0, 1fr));
  }
}

/* ─── BOTONES FLOTANTES ─── */

/* WhatsApp — izquierda */
.floating-whatsapp {
  position: fixed;
  left: 1rem;
  bottom: 1.25rem;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #25d366;
  color: var(--cds-white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.55rem;
  text-decoration: none;
  z-index: 999;
  box-shadow: 0 4px 14px rgba(37, 211, 102, 0.45);
  transition: transform 0.2s, box-shadow 0.2s;
}

.floating-whatsapp:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 20px rgba(37, 211, 102, 0.55);
}

/* Scroll-top — derecha abajo */
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
  box-shadow: 0 4px 14px rgba(236, 107, 0, 0.35);
  transition: transform 0.2s, box-shadow 0.2s;
}

.scroll-top:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 20px rgba(236, 107, 0, 0.5);
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
