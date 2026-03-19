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
  --layout-header-height: 96px;
  --layout-anchor-gap: 12px;
  --layout-content-max: 1440px;
  --layout-section-scroll-margin-top: calc(
    var(--layout-header-height) +
    var(--layout-anchor-gap)
  );
  --layout-section-padding-block: clamp(3.4rem, 6vw, 6rem);
  --layout-section-padding-block-mobile: clamp(2.6rem, 8vw, 4rem);
  --layout-section-content-gap: clamp(1.45rem, 2.8vw, 2.4rem);
  --layout-footer-padding-top: clamp(3rem, 3vw, 4rem);
  --layout-footer-padding-inline: clamp(0.75rem, 2vw, 1.5rem);
  --layout-footer-padding-bottom: clamp(1.4rem, 1.8vw, 2rem);
  --layout-footer-grid-row-gap: clamp(2rem, 2.2vw, 2.8rem);
  --layout-footer-grid-column-gap: clamp(2.4rem, 3vw, 4rem);
  --layout-footer-grid-template-columns: repeat(auto-fit, minmax(min(100%, 13.5rem), 1fr));
  --layout-footer-brand-width: min(100%, 16rem);
  --layout-footer-brand-summary-margin-top: clamp(1.5rem, 2vw, 2.2rem);
  --layout-footer-logo-size: clamp(96px, 12vw, 130px);
  --layout-footer-map-max-width: 18rem;
  --layout-footer-map-offset-inline: 70px;
  --layout-footer-legal-margin-top: clamp(2rem, 2.3vw, 2.8rem);
  --layout-calculator-page-padding: var(--cds-space-xl) var(--cds-space-md) var(--cds-space-2xl);
  --layout-calculator-container-max: 1160px;
  --layout-calculator-content-gap: 1.2rem;
  --layout-calculator-layout-gap: 1rem;
  --layout-calculator-layout-columns-desktop: minmax(320px, 1fr) minmax(360px, 1.2fr);
  --layout-catalog-page-padding: var(--cds-space-xl) var(--cds-space-md) var(--cds-space-2xl);
  --layout-catalog-container-max: var(--layout-content-max, var(--cds-content-max));
  --layout-store-page-padding: var(--cds-space-xl) var(--cds-space-md) var(--cds-space-2xl);
  --layout-store-shell-max: min(1440px, 98vw);
  --layout-schedule-page-padding: 1rem;
  --layout-schedule-container-max: 1040px;
  --layout-schedule-container-gap: 1rem;
  --layout-schedule-card-padding: 1rem;
  --layout-schedule-header-copy-margin-top: 0.4rem;
  --layout-schedule-progress-gap: 0.5rem;
  --layout-schedule-progress-step-min-height: 64px;
  --layout-schedule-step-gap: 0.9rem;
  --layout-schedule-calendar-header-gap: 0.5rem;
  --layout-schedule-calendar-grid-gap: 0.35rem;
  --layout-schedule-weekday-min-height: 32px;
  --layout-schedule-day-min-height: 40px;
  --layout-schedule-timeslot-heading-margin-bottom: 0.45rem;
  --layout-schedule-timeslot-list-gap: 0.45rem;
  --layout-schedule-control-min-height: 44px;
  --layout-schedule-control-pad-block: 0.65rem;
  --layout-schedule-control-pad-inline: 0.9rem;
  --layout-schedule-confirmation-gap: 0.7rem;
  --layout-schedule-confirmation-padding: 0.9rem;
  --layout-schedule-confirmation-section-gap: 0.75rem;
  --layout-schedule-confirmation-section-padding-bottom: 0.5rem;
  --layout-schedule-info-copy-margin-block: 0.3rem;
  --layout-schedule-feedback-padding: 0.7rem;
  --layout-schedule-success-icon-size: 64px;
  --layout-schedule-action-gap: 0.6rem;
  --layout-legal-page-padding: 1rem;
  --layout-legal-container-max: 980px;
  --layout-legal-card-padding: 1rem;
  --layout-token-page-padding: 1rem;
  --layout-token-card-padding: 1rem;
  --layout-token-card-narrow-width: min(640px, 100%);
  --layout-token-card-wide-width: min(760px, 100%);
  --layout-quotation-page-padding: 0.5rem 1rem 2rem;
  --layout-quotation-page-padding-md: 1rem 1.5rem 2.5rem;
  --layout-quotation-shell-max: 920px;
  --layout-quotation-page-gap: 1rem;
  --layout-quotation-progress-height: 4px;
  --layout-quotation-progress-radius: 4px;
  --layout-quotation-alert-padding-block: 0.75rem;
  --layout-quotation-alert-padding-inline: 1rem;
  --layout-quotation-card-padding-mobile: 1.25rem 1rem;
  --layout-quotation-card-padding-desktop: 1.75rem 1.5rem;
  --layout-quotation-card-gap: 1rem;
  --layout-quotation-form-gap: 0.75rem;
  --layout-quotation-field-gap: 0.4rem;
  --layout-quotation-control-min-height: 44px;
  --layout-quotation-control-pad-block: 0.65rem;
  --layout-quotation-control-pad-inline: 0.8rem;
  --layout-quotation-loading-gap: 0.5rem;
  --layout-quotation-spinner-size: 18px;
  --layout-quotation-spinner-size-sm: 14px;
  --layout-quotation-action-gap: 0.6rem;
  --layout-quotation-button-pad-block: 0.65rem;
  --layout-quotation-button-pad-inline: 1.1rem;
  --layout-quotation-button-icon-gap: 0.4rem;
  --layout-quotation-checkbox-gap: 0.6rem;
  --layout-quotation-checkbox-size: 18px;
  --layout-quotation-summary-radius: 0.7rem;
  --layout-quotation-summary-padding: 0.9rem;
  --layout-quotation-summary-gap: 0.75rem;
  --layout-quotation-summary-divider-padding-top: 0.65rem;
  --layout-quotation-tag-gap: 0.4rem;
  --layout-quotation-tag-pad-block: 0.2rem;
  --layout-quotation-tag-pad-inline: 0.5rem;
  --layout-quotation-chip-radius: 0.35rem;
  --layout-quotation-disclaimer-padding: 0.75rem;
  --layout-quotation-fault-card-pad-block: 0.7rem;
  --layout-quotation-fault-card-pad-inline: 0.85rem;
  --layout-quotation-fault-card-column-gap: 0.6rem;
  --layout-quotation-fault-card-row-gap: 0.1rem;
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr auto;
}

/* ─── MAIN ─── */
.site-body {
  min-height: 0;
}
</style>
