<template>
  <div class="master-layout">
    <SiteHeaderNav
      :logo-src="logoSrc"
      :menu-open="menuOpen"
      :is-home="isHome"
      :nav-sections="navSections"
      :is-authenticated="isAuthenticated"
      :cart-items-count="shopCart.totals.itemsCount"
      @toggle-menu="menuOpen = !menuOpen"
      @close-menu="menuOpen = false"
      @cart-click="onCartClick"
    />

    <main class="site-body">
      <router-view />
    </main>

    <SiteFooter :logo-src="logoSrc" />

    <SiteFloatingActions
      :show-scroll-top="showScrollTop"
      :cart-open="shopCart.cartOpen"
      @scroll-top="scrollToTop"
    />

  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import SiteFloatingActions from '@/components/layout/SiteFloatingActions.vue'
import SiteFooter from '@/components/layout/SiteFooter.vue'
import SiteHeaderNav from '@/components/layout/SiteHeaderNav.vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useHomePage } from '@/composables/useHomePage'
import { useShopCartStore } from '@/stores/shopCart'
import { useCloudinaryImage } from '@/composables/useCloudinary'
import { useMediaBinding } from '@/composables/useMediaBinding'

const { resolveSlotOr } = useMediaBinding()
const { isAuthenticated } = useAuth()
const { sections } = useHomePage()
const route = useRoute()
const router = useRouter()
const shopCart = useShopCartStore()
const logoSrc = computed(() => resolveSlotOr(
  'site.logo.square',
  useCloudinaryImage('/images/logo/logo_square_004.webp')
))

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

/* ─── MAIN ─── */
.site-body {
  min-height: 0;
}
</style>
