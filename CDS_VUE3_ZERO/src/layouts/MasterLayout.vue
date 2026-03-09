<template>
  <div class="master-layout">

    <header class="site-header">
      <div class="site-header-inner">

        <router-link to="/" class="brand-link" @click="menuOpen = false">
          <img
            src="/images/logo/logo_square_004.webp"
            alt="Cirujano de Sintetizadores"
            class="brand-logo"
            width="80"
            height="80"
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

          <router-link to="/calculadoras" class="site-nav-link" @click="menuOpen = false">Calculadoras</router-link>
          <router-link to="/tienda" class="site-nav-link" @click="menuOpen = false">Tienda</router-link>

          <router-link
            v-if="isAuthenticated"
            to="/dashboard"
            class="site-nav-link"
            @click="menuOpen = false"
          >Dashboard</router-link>
          <router-link
            v-else
            to="/login"
            class="site-nav-link"
            @click="menuOpen = false"
          >Iniciar Sesión</router-link>

        </nav>

        <!-- Acciones fijas derecha: Cotizar, Carrito, Hamburger -->
        <div class="nav-actions">

          <router-link to="/cotizador-ia" class="nav-cotizar" aria-label="Ir al cotizador IA">
            <i class="fas fa-file-invoice-dollar"></i>
            <span class="nav-cotizar-label">Cotizar</span>
          </router-link>

          <button
            class="nav-cart-btn"
            type="button"
            aria-label="Carrito de compras"
            @click="onCartClick"
          >
            <i class="fas fa-shopping-cart"></i>
            <span class="nav-cart-label">Carrito</span>
            <span v-if="shopCart.totals.itemsCount > 0" class="nav-cart-badge">
              {{ shopCart.totals.itemsCount }}
            </span>
          </button>

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

    <!-- Volver arriba — derecha abajo, se desplaza si el carrito está abierto -->
    <button
      v-show="showScrollTop"
      class="scroll-top"
      :class="{ 'scroll-top--cart-open': shopCart.cartOpen }"
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
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useHomePage } from '@/composables/useHomePage'
import { useShopCartStore } from '@/stores/shopCart'

const { isAuthenticated } = useAuth()
const { sections } = useHomePage()
const route = useRoute()
const router = useRouter()
const shopCart = useShopCartStore()

function onCartClick() {
  if (route.path === '/tienda') {
    shopCart.openCart()
  } else {
    router.push('/tienda')
  }
}

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
  --cds-header-height: 96px;
  --cds-anchor-gap: 12px;
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
  --nav-font-size: clamp(1.8rem, 0.28vw + 1.1rem, 1.34rem);
  --nav-link-pad-y: clamp(0.72rem, 0.18vw + 0.66rem, 0.86rem);
  --nav-link-pad-x: clamp(1rem, 0.22vw + 0.92rem, 1.22rem);
}

.site-header-inner {
  width: 100%;
  max-width: none;
  padding: 0 1rem;
  min-height: var(--cds-header-height);
  display: flex;
  align-items: center;
  justify-content: flex-start;
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
  width: 80px;
  height: 80px;
  border-radius: 0.35rem;
  flex-shrink: 0;
}

.brand-name {
  font-size: var(--cds-text-base);
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
  flex-wrap: nowrap;
  gap: 0.2rem;
  align-items: center;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

/* Grupo derecho: Cotizar + Carrito + Hamburger */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  margin-left: auto;
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
  min-height: clamp(56px, 3vw, 62px);
  padding: var(--nav-link-pad-y) var(--nav-link-pad-x);
  border-radius: 0.45rem;
  font-size: var(--nav-font-size);
  font-family: var(--cds-font-family-base), sans-serif;
  font-weight: var(--cds-font-medium);
  text-transform: lowercase;
  letter-spacing: 0.01em;
  display: inline-flex;
  align-items: center;
  transition: background 0.15s, font-size 0.2s ease, letter-spacing 0.2s ease;
  white-space: nowrap;
}

.site-nav-link:hover,
.site-nav-link.router-link-active:hover {
  background: color-mix(in srgb, var(--cds-primary) 22%, transparent);
  text-transform: uppercase;
  font-size: calc(var(--nav-font-size) * 1.5);
  letter-spacing: 0.03em;
}

.site-nav-link.router-link-active {
  background: transparent;
}

/* ─── COTIZAR (navbar derecha, siempre visible) ─── */
.nav-cotizar {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1.1rem;
  border-radius: 0.45rem;
  background: var(--cds-primary);
  color: var(--cds-white);
  text-decoration: none;
  font-size: var(--cds-text-base);
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

/* ─── CARRITO (navbar) ─── */
.nav-cart-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 52px;
  padding: 0.55rem 1.1rem;
  border: none;
  border-radius: 0.45rem;
  background: color-mix(in srgb, var(--cds-white) 14%, transparent);
  color: var(--cds-white);
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.02em;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s, transform 0.12s;
  white-space: nowrap;
}

.nav-cart-btn:hover {
  background: color-mix(in srgb, var(--cds-white) 24%, transparent);
  transform: translateY(-1px);
}

.nav-cart-label {
  display: none;
}

@media (min-width: 480px) {
  .nav-cart-label {
    display: inline;
  }
}

.nav-cart-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 17px;
  height: 17px;
  padding: 0 4px;
  border-radius: 999px;
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: 0.65rem;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  pointer-events: none;
}

/* ─── HAMBURGER ─── */
.nav-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border: none;
  border-radius: 0.4rem;
  background: transparent;
  color: var(--cds-white);
  font-size: 1.55rem;
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
    justify-content: center;
    overflow: visible;
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
  --footer-safe-left: clamp(1rem, 12vw, calc(1rem + 50px + 0.75rem));
  --footer-safe-right: clamp(1rem, 12vw, calc(1rem + 46px + 0.75rem));
  padding-top: clamp(3rem, 3vw, 4rem);
  padding-right: var(--footer-safe-right);
  padding-bottom: clamp(1.4rem, 1.8vw, 2rem);
  padding-left: var(--footer-safe-left);
}

.site-footer-grid {
  width: 100%;
  max-width: none;
  margin: 0;
  display: grid;
  gap: clamp(2rem, 2.2vw, 2.8rem);
  grid-template-columns: 1fr;
}

.site-footer h2 {
  margin: 0 0 0.75rem;
  font-size: clamp(1.08rem, 0.22vw + 1.02rem, 1.24rem);
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: color-mix(in srgb, var(--cds-white) 60%, transparent);
}

.site-footer p {
  margin: 0;
  font-size: clamp(1rem, 0.18vw + 0.95rem, 1.12rem);
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
  width: 66px;
  height: 66px;
  border-radius: 0.4rem;
}

.footer-brand-name {
  font-size: clamp(1.2rem, 0.26vw + 1.12rem, 1.36rem);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-white);
  margin: 0;
  line-height: 1.2;
}

.footer-brand-tagline {
  font-size: clamp(1rem, 0.18vw + 0.95rem, 1.12rem);
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
  font-size: clamp(1rem, 0.18vw + 0.95rem, 1.12rem);
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
  font-size: clamp(1rem, 0.18vw + 0.95rem, 1.12rem);
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.site-footer-legal {
  width: 100%;
  max-width: none;
  margin: clamp(2rem, 2.3vw, 2.8rem) 0 0;
  padding-top: 1.2rem;
  border-top: 1px solid color-mix(in srgb, var(--cds-white) 12%, transparent);
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
  align-items: center;
  font-size: clamp(0.96rem, 0.14vw + 0.92rem, 1.04rem);
  color: color-mix(in srgb, var(--cds-white) 50%, transparent);
}

.site-footer-legal a {
  color: color-mix(in srgb, var(--cds-white) 50%, transparent);
  font-size: inherit;
}

.site-footer-legal a:hover {
  color: var(--cds-white);
}

@media (min-width: 600px) {
  .site-footer-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 768px) {
  .site-footer {
    --footer-safe-left: clamp(1.5rem, 8vw, calc(1.5rem + 54px + 0.9rem));
    --footer-safe-right: clamp(1.5rem, 8vw, calc(1.5rem + 50px + 0.9rem));
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
  transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1), transform 0.2s, box-shadow 0.2s;
}

.scroll-top:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 20px rgba(236, 107, 0, 0.5);
}

/* Carrito abierto: mover la flecha a la izquierda del drawer */
.scroll-top.scroll-top--cart-open {
  right: calc(min(420px, 100vw) + 1rem);
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

  .scroll-top.scroll-top--cart-open {
    right: calc(min(420px, 100vw) + 1.5rem);
  }
}
</style>
