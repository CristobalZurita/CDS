<template>
  <div
    class="admin-shell-layout"
    :class="{ 'admin-shell-layout--dashboard': isDashboardRoute }"
  >
    <!-- Sidebar fijo siempre visible -->
    <aside class="admin-sidebar" :class="{ 'admin-sidebar--dashboard': isDashboardRoute }">
      <div class="sidebar-brand">
        <span class="brand-icon">🎛️</span>
        <template v-if="isDashboardRoute">
          <span class="dashboard-brand-copy">
            <strong>Control</strong>
            <small>CDS Admin</small>
          </span>
        </template>
        <span v-else class="brand-text">Admin</span>
      </div>

      <nav class="sidebar-nav" :class="{ 'sidebar-nav--dashboard-grid': isDashboardRoute }">
        <router-link
          v-for="item in menuItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          :class="{ 'nav-item--dashboard-grid': isDashboardRoute }"
          :activeClass="item.exact ? '' : 'active'"
          exactActiveClass="active"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <router-link to="/" class="nav-item back-link">
          <span class="nav-icon">←</span>
          <span class="nav-label">Volver al Inicio</span>
        </router-link>
        <button class="nav-item logout-btn" @click="handleLogout">
          <span class="nav-icon">🚪</span>
          <span class="nav-label">Salir</span>
        </button>
      </div>
    </aside>

    <!-- Contenido principal -->
    <main class="admin-main">
      <!-- Top bar contextual -->
      <header class="admin-topbar">
        <template v-if="isDashboardRoute">
          <div class="admin-dashboard-topbar-clock">
            <strong class="admin-dashboard-topbar-time">{{ dashboardClockTime }}</strong>
            <div class="admin-dashboard-topbar-date">
              <span>{{ dashboardClockDay }}</span>
              <span>{{ dashboardClockDate }}</span>
            </div>
          </div>
          <div class="breadcrumb">
            <h1 class="page-title">{{ pageTitle }}</h1>
            <p v-if="pageSubtitle" class="page-subtitle">{{ pageSubtitle }}</p>
          </div>
          <div class="topbar-actions">
            <AdminGlobalSearch />
            <span class="user-badge">👤 {{ userName }}</span>
          </div>
        </template>
        <template v-else>
          <div class="breadcrumb">
            <h1 class="page-title">{{ pageTitle }}</h1>
            <p v-if="pageSubtitle" class="page-subtitle">{{ pageSubtitle }}</p>
          </div>
          <div class="topbar-actions">
            <AdminGlobalSearch />
            <span class="user-badge">👤 {{ userName }}</span>
          </div>
        </template>
      </header>

      <!-- Área de contenido -->
      <div class="admin-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <keep-alive :include="keepAlivePages">
              <component :is="Component" />
            </keep-alive>
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AdminGlobalSearch from '@/components/admin/AdminGlobalSearch.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const userName = computed(() => authStore.user?.full_name || authStore.user?.email || 'Admin')

const pageTitle    = computed(() => route.meta.title    || 'Panel Admin')
const pageSubtitle = computed(() => route.meta.subtitle || '')
const isDashboardRoute = computed(() => route.path.startsWith('/admin'))
const now = ref(new Date())

let clockTimer = null

const menuItems = [
  { to: '/admin', label: 'Dashboard',     icon: '📊', exact: true },
  { to: '/admin/intake',    label: 'Nuevo Ingreso', icon: '➕' },
  { to: '/admin/repairs',   label: 'Reparaciones',  icon: '🔧' },
  { to: '/admin/quotes',    label: 'Cotizaciones',  icon: '📄' },
  { to: '/admin/clients',   label: 'Clientes',      icon: '👥' },
  { to: '/admin/inventory', label: 'Inventario',    icon: '📦' },
  { to: '/admin/appointments', label: 'Citas',      icon: '📅' },
  { to: '/admin/tickets',   label: 'Tickets',       icon: '🎫' },
  { to: '/admin/stats',     label: 'Estadísticas',  icon: '📈' },
  { to: '/admin/media',     label: 'Medios',        icon: '🖼️' },
]

const keepAlivePages = ['RepairsAdminPage', 'ClientsPage', 'InventoryPage', 'QuotesAdminPage']

const dashboardClockTime = computed(() => {
  return new Intl.DateTimeFormat('es-CL', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(now.value)
})

const dashboardClockDay = computed(() => {
  return new Intl.DateTimeFormat('es-CL', {
    weekday: 'long',
  })
    .format(now.value)
    .replace(/^\p{L}/u, (letter) => letter.toUpperCase())
})

const dashboardClockDate = computed(() => {
  return new Intl.DateTimeFormat('es-CL', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(now.value)
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  clockTimer = window.setInterval(() => {
    now.value = new Date()
  }, 30000)
})

onUnmounted(() => {
  if (clockTimer) {
    window.clearInterval(clockTimer)
  }
})
</script>

<style scoped>
.admin-shell-layout {
  --admin-neo-line: rgba(79, 74, 69, 0.24);
  --admin-neo-line-strong: rgba(79, 74, 69, 0.38);
  --admin-neo-surface: var(--cds-surface-1);
  --admin-neo-surface-soft: var(--cds-surface-2);
  --admin-neo-surface-tint: var(--cds-surface-2);
  --admin-neo-ink: #464342;
  --admin-neo-muted: #6a6661;
  --admin-neo-shadow: 0 18px 40px rgba(39, 37, 34, 0.12);
  --admin-neo-shadow-sm: 0 8px 18px rgba(39, 37, 34, 0.08);
  --admin-neo-shadow-inset: inset 0 2px 3px rgba(17, 15, 13, 0.18);
  --admin-neo-radius: 1.65rem;
  --admin-neo-radius-sm: 1.2rem;
  --admin-neo-font: var(--cds-font-family-base);
  --admin-space-3xs: 0.35rem;
  --admin-space-2xs: 0.6rem;
  --admin-space-xs: 0.66rem;
  --admin-space-sm-compact: 0.7rem;
  --admin-space-sm: 0.96rem;
  --admin-space-md-compact: 0.9rem;
  --admin-space-md: 1.2rem;
  --admin-space-lg-compact: 1.25rem;
  --admin-space-lg: 1.8rem;
  --admin-space-xl: 2.4rem;
  --admin-space-2xl: 3.3rem;
  --admin-list-toolbar-gap: var(--admin-space-sm, 0.96rem);
  --admin-list-toolbar-margin-bottom: var(--admin-space-md, 1.2rem);
  --admin-list-pill-pad-block: var(--cds-space-xs);
  --admin-list-pill-pad-inline: var(--cds-space-md);
  --admin-list-search-min-width: 26rem;
  --admin-list-mono-font-family: var(--cds-font-family-mono);
  --admin-list-info-bg: rgba(14, 165, 233, 0.14);
  --admin-list-info-color: #0c4a6e;
  --admin-table-cell-padding: var(--admin-space-md, 1.2rem);
  --admin-table-refresh-pad-inline: 1.35rem;
  --admin-table-icon-padding: 0.5rem;
  --admin-sidebar-width: clamp(22rem, 20rem + 4vw, 26rem);
  --admin-sidebar-collapsed-width: 7.5rem;
  --admin-control-min-height-sm: 40px;
  --admin-control-min-height: 52px;
  --admin-text-xs: clamp(1.32rem, 1.26rem + 0.3vw, 1.44rem);
  --admin-text-sm: clamp(1.5rem, 1.44rem + 0.36vw, 1.68rem);
  --admin-text-base: clamp(1.68rem, 1.62rem + 0.54vw, 1.98rem);
  --admin-text-lg: clamp(1.8rem, 1.68rem + 0.72vw, 2.16rem);
  --admin-text-xl: clamp(1.92rem, 1.62rem + 1.5vw, 2.52rem);
  --admin-text-2xl: clamp(2.22rem, 1.74rem + 2.4vw, 3.06rem);
  --admin-text-3xl: clamp(2.58rem, 1.86rem + 3.6vw, 3.72rem);
  --admin-text-4xl: clamp(2.94rem, 1.98rem + 4.8vw, 4.32rem);
  --admin-sidebar-divider: rgba(255, 255, 255, 0.1);
  --admin-nav-text-muted: rgba(255, 255, 255, 0.72);
  --admin-nav-hover-bg: rgba(255, 255, 255, 0.05);
  --admin-nav-active-bg: var(--cds-surface-2);
  --admin-back-link-color: rgba(255, 255, 255, 0.6);
  --admin-logout-text: #f2b7b7;
  --admin-logout-hover-bg: rgba(220, 38, 38, 0.15);
  --admin-user-badge-bg: var(--cds-surface-1);
  display: flex;
  min-height: 100vh;
  background: var(--cds-background-color);
  font-family: var(--admin-neo-font);
}

.admin-shell-layout--dashboard {
  --admin-dashboard-scale: 0.65;
  --admin-space-3xs: calc(0.35rem * var(--admin-dashboard-scale));
  --admin-space-2xs: calc(0.6rem * var(--admin-dashboard-scale));
  --admin-space-xs: calc(0.66rem * var(--admin-dashboard-scale));
  --admin-space-sm-compact: calc(0.7rem * var(--admin-dashboard-scale));
  --admin-space-sm: calc(0.96rem * var(--admin-dashboard-scale));
  --admin-space-md-compact: calc(0.9rem * var(--admin-dashboard-scale));
  --admin-space-md: calc(1.2rem * var(--admin-dashboard-scale));
  --admin-space-lg-compact: calc(1.25rem * var(--admin-dashboard-scale));
  --admin-space-lg: calc(1.8rem * var(--admin-dashboard-scale));
  --admin-space-xl: calc(2.4rem * var(--admin-dashboard-scale));
  --admin-space-2xl: calc(3.3rem * var(--admin-dashboard-scale));
  --admin-sidebar-width: clamp(
    calc(22rem * var(--admin-dashboard-scale)),
    calc((20rem + 4vw) * var(--admin-dashboard-scale)),
    calc(26rem * var(--admin-dashboard-scale))
  );
  --admin-control-min-height-sm: calc(40px * var(--admin-dashboard-scale));
  --admin-control-min-height: calc(52px * var(--admin-dashboard-scale));
  --admin-text-xs: clamp(
    calc(1.32rem * var(--admin-dashboard-scale)),
    calc((1.26rem + 0.3vw) * var(--admin-dashboard-scale)),
    calc(1.44rem * var(--admin-dashboard-scale))
  );
  --admin-text-sm: clamp(
    calc(1.5rem * var(--admin-dashboard-scale)),
    calc((1.44rem + 0.36vw) * var(--admin-dashboard-scale)),
    calc(1.68rem * var(--admin-dashboard-scale))
  );
  --admin-text-base: clamp(
    calc(1.68rem * var(--admin-dashboard-scale)),
    calc((1.62rem + 0.54vw) * var(--admin-dashboard-scale)),
    calc(1.98rem * var(--admin-dashboard-scale))
  );
  --admin-text-lg: clamp(
    calc(1.8rem * var(--admin-dashboard-scale)),
    calc((1.68rem + 0.72vw) * var(--admin-dashboard-scale)),
    calc(2.16rem * var(--admin-dashboard-scale))
  );
  --admin-text-xl: clamp(
    calc(1.92rem * var(--admin-dashboard-scale)),
    calc((1.62rem + 1.5vw) * var(--admin-dashboard-scale)),
    calc(2.52rem * var(--admin-dashboard-scale))
  );
  --admin-text-2xl: clamp(
    calc(2.22rem * var(--admin-dashboard-scale)),
    calc((1.74rem + 2.4vw) * var(--admin-dashboard-scale)),
    calc(3.06rem * var(--admin-dashboard-scale))
  );
  --admin-text-3xl: clamp(
    calc(2.58rem * var(--admin-dashboard-scale)),
    calc((1.86rem + 3.6vw) * var(--admin-dashboard-scale)),
    calc(3.72rem * var(--admin-dashboard-scale))
  );
  --admin-text-4xl: clamp(
    calc(2.94rem * var(--admin-dashboard-scale)),
    calc((1.98rem + 4.8vw) * var(--admin-dashboard-scale)),
    calc(4.32rem * var(--admin-dashboard-scale))
  );
  background: var(--cds-background-color);
  --admin-user-badge-bg: rgba(255, 255, 255, 0.92);
}

.admin-sidebar {
  width: var(--admin-sidebar-width);
  background: var(--cds-nav-background-color);
  color: var(--cds-white);
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  z-index: 100;
}

.admin-shell-layout--dashboard .admin-sidebar {
  width: clamp(16rem, 14rem + 3vw, 19rem);
  background: transparent;
  padding: var(--admin-space-lg) var(--admin-space-md);
  gap: var(--admin-space-md);
}

.sidebar-brand {
  padding: var(--admin-space-lg) var(--admin-space-xl);
  display: flex;
  align-items: center;
  gap: var(--admin-space-md);
  border-bottom: 1px solid var(--admin-sidebar-divider);
}

.admin-shell-layout--dashboard .sidebar-brand,
.admin-shell-layout--dashboard .sidebar-nav,
.admin-shell-layout--dashboard .sidebar-footer {
  border: 1px solid var(--admin-neo-line);
  border-radius: var(--admin-neo-radius);
  background: var(--admin-neo-surface);
  box-shadow: var(--admin-neo-shadow);
  backdrop-filter: blur(14px);
}

.admin-shell-layout--dashboard .sidebar-brand {
  border-bottom: none;
  color: var(--cds-dark);
  padding: var(--admin-space-lg) var(--admin-space-lg);
}

.dashboard-brand-copy {
  display: grid;
  gap: 0.1rem;
  line-height: 1;
}

.dashboard-brand-copy strong {
  font-size: var(--admin-text-2xl);
  letter-spacing: -0.05em;
  color: var(--cds-dark);
}

.dashboard-brand-copy small {
  font-size: var(--admin-text-sm);
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: var(--cds-text-muted);
}

.brand-icon {
  font-size: var(--admin-text-3xl);
}

.admin-shell-layout--dashboard .brand-icon {
  width: 3.6rem;
  height: 3.6rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: var(--cds-surface-2);
}

.brand-text {
  font-size: var(--admin-text-2xl);
  font-weight: var(--cds-font-bold);
  letter-spacing: -0.5px;
}

.sidebar-nav {
  flex: 1;
  padding: var(--admin-space-md) 0;
  overflow-y: auto;
}

.admin-shell-layout--dashboard .sidebar-nav {
  display: grid;
  gap: var(--admin-space-sm);
  padding: var(--admin-space-sm);
  overflow: visible;
}

.sidebar-nav--dashboard-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--admin-space-md);
  padding: var(--admin-space-md) var(--admin-space-xl);
  color: var(--admin-nav-text-muted);
  text-decoration: none;
  transition: all 0.2s;
  border-left: 3px solid transparent;
  cursor: pointer;
  background: none;
  border: none;
  width: 100%;
  font-size: var(--admin-text-base);
  line-height: 1.2;
}

.admin-shell-layout--dashboard .nav-item {
  border-left: none;
  border-radius: var(--admin-neo-radius-sm);
  padding: var(--admin-space-sm) var(--admin-space-md);
  color: var(--admin-neo-ink);
  background: transparent;
}

.nav-item--dashboard-grid {
  min-height: 5rem;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: var(--admin-space-xs);
  padding: var(--admin-space-md);
  text-align: center;
  border: 1px solid var(--admin-neo-line);
  background: var(--cds-surface-1);
  box-shadow: var(--admin-neo-shadow-sm);
}

.nav-item:hover {
  background: var(--admin-nav-hover-bg);
  color: var(--cds-white);
}

.admin-shell-layout--dashboard .nav-item:hover {
  background: rgba(79, 74, 69, 0.06);
  color: var(--cds-dark);
}

.nav-item.active {
  background: var(--admin-nav-active-bg);
  color: var(--cds-primary);
  border-left-color: var(--cds-primary);
}

.admin-shell-layout--dashboard .nav-item.active {
  background: var(--cds-dark);
  color: var(--cds-white);
  box-shadow: var(--admin-neo-shadow);
}

.nav-icon {
  font-size: var(--admin-text-xl);
  width: 2.4rem;
  text-align: center;
}

.admin-shell-layout--dashboard .nav-icon {
  width: 3.6rem;
  height: 3.6rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid var(--admin-neo-line);
  box-shadow: var(--admin-neo-shadow-sm);
}

.nav-label {
  font-weight: var(--cds-font-medium);
}

.admin-shell-layout--dashboard .nav-label {
  font-weight: var(--cds-font-semibold);
  font-size: var(--admin-text-sm);
  line-height: 1.25;
}

.admin-shell-layout--dashboard .nav-item.active .nav-icon {
  background: var(--cds-surface-2);
  border-color: var(--cds-border-card);
}

.sidebar-footer {
  padding: var(--admin-space-md) 0;
  border-top: 1px solid var(--admin-sidebar-divider);
}

.admin-shell-layout--dashboard .sidebar-footer {
  border-top: none;
  padding: var(--admin-space-sm);
  display: grid;
  gap: var(--admin-space-sm);
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.admin-shell-layout--dashboard .sidebar-footer .nav-item {
  min-height: 5.4rem;
  flex-direction: row;
  justify-content: flex-start;
  text-align: left;
}

.back-link {
  color: var(--admin-back-link-color);
}

.admin-shell-layout--dashboard .back-link,
.admin-shell-layout--dashboard .logout-btn {
  color: var(--cds-text-normal);
}

.back-link:hover {
  color: var(--cds-white);
}

.admin-shell-layout--dashboard .back-link:hover,
.admin-shell-layout--dashboard .logout-btn:hover {
  color: var(--cds-dark);
}

.logout-btn {
  color: var(--admin-logout-text);
}

.logout-btn:hover {
  background: var(--admin-logout-hover-bg);
  color: var(--cds-danger);
}

.admin-main {
  flex: 1;
  margin-left: var(--admin-sidebar-width);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.admin-shell-layout--dashboard .admin-main {
  margin-left: clamp(16rem, 14rem + 3vw, 19rem);
}

.admin-topbar {
  background: var(--cds-white);
  padding: var(--admin-space-lg) var(--admin-space-2xl);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--cds-border-card);
  position: sticky;
  top: 0;
  z-index: 50;
}

.admin-shell-layout--dashboard .admin-topbar {
  background: var(--admin-neo-surface);
  border: 1px solid var(--admin-neo-line);
  border-radius: var(--admin-neo-radius);
  margin: var(--admin-space-lg) var(--admin-space-lg) 0;
  padding: var(--admin-space-md) var(--admin-space-lg);
  box-shadow: var(--admin-neo-shadow);
  backdrop-filter: blur(14px);
  display: grid;
  grid-template-columns: minmax(17rem, 0.78fr) minmax(0, 1fr) auto;
  gap: var(--admin-space-md);
  align-items: center;
}

.admin-dashboard-topbar-clock {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: var(--admin-space-md);
  padding: var(--admin-space-md);
  border-radius: calc(var(--cds-radius-lg) * 0.95);
  background: var(--cds-surface-2);
  color: var(--cds-dark);
  min-height: 100%;
}

.admin-dashboard-topbar-time {
  font-size: calc(var(--admin-text-4xl) * 1.08);
  letter-spacing: -0.06em;
  line-height: 0.9;
}

.admin-dashboard-topbar-date {
  display: grid;
  gap: 0.12rem;
  font-size: var(--admin-text-sm);
  text-transform: uppercase;
  letter-spacing: 0.13em;
  color: var(--cds-text-muted);
}

.admin-shell-layout--dashboard .breadcrumb {
  min-width: 0;
}

.page-title {
  margin: 0;
  font-size: var(--admin-text-3xl);
  font-weight: var(--cds-font-bold);
  color: var(--cds-text-normal);
  line-height: 1;
}

.admin-shell-layout--dashboard .page-title {
  letter-spacing: -0.04em;
}

.page-subtitle {
  margin: var(--admin-space-xs) 0 0;
  font-size: var(--admin-text-base);
  color: var(--cds-text-muted);
  line-height: 1.35;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: var(--admin-space-sm);
  min-width: min(42rem, 100%);
}

.admin-shell-layout--dashboard .topbar-actions {
  justify-content: flex-end;
  gap: var(--admin-space-md);
}

.user-badge {
  background: var(--admin-user-badge-bg);
  padding: var(--admin-space-sm) var(--cds-space-lg);
  border-radius: var(--cds-radius-pill);
  font-size: var(--admin-text-sm);
  color: var(--cds-text-normal);
}

.admin-shell-layout--dashboard .user-badge {
  border: 1px solid var(--admin-neo-line);
  box-shadow: var(--admin-neo-shadow-sm);
}

.admin-content {
  flex: 1;
  padding: var(--admin-space-2xl);
  overflow-y: auto;
}

.admin-shell-layout--dashboard .admin-content {
  padding: var(--admin-space-lg);
}

.admin-content :deep(.admin-page),
.admin-content :deep(.admin-dashboard-page) {
  font-size: var(--admin-text-base);
}

.admin-content :deep(.admin-success),
.admin-content :deep(.admin-error),
.admin-content :deep(.empty-state) {
  padding: var(--admin-space-sm) var(--cds-space-md);
  font-size: var(--admin-text-sm);
}

.admin-content :deep(.panel-card),
.admin-content :deep(.summary-card),
.admin-content :deep(.stat-card),
.admin-content :deep(.wizard-card),
.admin-content :deep(.appointment-card),
.admin-content :deep(.panel-nested),
.admin-content :deep(.quote-card),
.admin-content :deep(.binding-form),
.admin-content :deep(.note-card),
.admin-content :deep(.filter-row) {
  padding: var(--admin-space-md);
  gap: var(--admin-space-sm);
}

.admin-content :deep(.cards-grid),
.admin-content :deep(.panel-grid),
.admin-content :deep(.summary-grid),
.admin-content :deep(.detail-grid),
.admin-content :deep(.columns-grid),
.admin-content :deep(.photos-grid),
.admin-content :deep(.toolbar),
.admin-content :deep(.filters-panel),
.admin-content :deep(.catalog-filters),
.admin-content :deep(.upload-extra-actions),
.admin-content :deep(.binding-form-fields),
.admin-content :deep(.inline-message),
.admin-content :deep(.payment-box),
.admin-content :deep(.row-actions) {
  gap: var(--admin-space-sm);
}

.admin-content :deep(.panel-head),
.admin-content :deep(.column-head),
.admin-content :deep(.appointment-head),
.admin-content :deep(.detail-head),
.admin-content :deep(.item-head) {
  gap: var(--admin-space-sm);
}

.admin-content :deep(.panel-card h2),
.admin-content :deep(.section-header h2),
.admin-content :deep(.panel-head h2),
.admin-content :deep(.panel-head h3),
.admin-content :deep(.column-head h3),
.admin-content :deep(.alerts-header h3) {
  font-size: var(--admin-text-2xl);
  line-height: 1.1;
}

.admin-content :deep(.panel-card p),
.admin-content :deep(.summary-card span),
.admin-content :deep(.summary-card small),
.admin-content :deep(.quote-meta),
.admin-content :deep(.quote-problem),
.admin-content :deep(.photo-meta),
.admin-content :deep(.cell-stack small),
.admin-content :deep(.list-count) {
  font-size: var(--admin-text-sm);
}

.admin-content :deep(th),
.admin-content :deep(td),
.admin-content :deep(li),
.admin-content :deep(.alert-text),
.admin-content :deep(.binding-row),
.admin-content :deep(.queue-item) {
  font-size: var(--admin-text-base);
  line-height: 1.45;
}

.admin-content :deep(input:not([type="checkbox"]):not([type="radio"]):not([type="file"])),
.admin-content :deep(select),
.admin-content :deep(textarea) {
  min-height: var(--admin-control-min-height);
  font-size: var(--admin-text-base);
}

.admin-content :deep(textarea) {
  min-height: 120px;
}

.admin-content :deep(.btn-primary),
.admin-content :deep(.btn-secondary),
.admin-content :deep(.btn-danger),
.admin-content :deep(.btn-success),
.admin-content :deep(.btn-refresh),
.admin-content :deep(.btn-submit),
.admin-content :deep(.chip),
.admin-content :deep(.status-chip),
.admin-content :deep(.status-badge),
.admin-content :deep(.role-pill),
.admin-content :deep(.status-pill),
.admin-content :deep(.flag-list span) {
  font-size: var(--admin-text-sm);
}

.admin-content :deep(.btn-primary),
.admin-content :deep(.btn-secondary),
.admin-content :deep(.btn-danger),
.admin-content :deep(.btn-success),
.admin-content :deep(.btn-refresh),
.admin-content :deep(.btn-submit) {
  min-height: var(--admin-control-min-height);
}

.admin-content :deep(.btn-icon) {
  min-width: 2.75rem;
  min-height: 2.75rem;
  font-size: var(--admin-text-xl);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .admin-sidebar {
    width: var(--admin-sidebar-collapsed-width);
  }

  .brand-text,
  .nav-label {
    display: none;
  }

  .sidebar-brand {
    justify-content: center;
    padding: var(--admin-space-md);
  }

  .nav-item {
    justify-content: center;
    padding: var(--admin-space-md);
  }

  .nav-icon {
    width: auto;
  }

  .admin-main {
    margin-left: var(--admin-sidebar-collapsed-width);
  }

  .admin-content {
    padding: var(--admin-space-xl);
  }

  .admin-topbar {
    flex-wrap: wrap;
  }

  .admin-shell-layout--dashboard .admin-sidebar {
    width: var(--admin-sidebar-collapsed-width);
  }

  .admin-shell-layout--dashboard .admin-main {
    margin-left: var(--admin-sidebar-collapsed-width);
  }

  .admin-shell-layout--dashboard .sidebar-nav--dashboard-grid,
  .admin-shell-layout--dashboard .sidebar-footer {
    grid-template-columns: 1fr;
  }

  .admin-shell-layout--dashboard .dashboard-brand-copy,
  .admin-shell-layout--dashboard .nav-label {
    display: none;
  }

  .admin-shell-layout--dashboard .nav-item--dashboard-grid,
  .admin-shell-layout--dashboard .sidebar-footer .nav-item {
    min-height: 4.8rem;
    padding: var(--admin-space-sm);
    justify-content: center;
  }

  .admin-shell-layout--dashboard .admin-topbar {
    grid-template-columns: 1fr;
  }

  .topbar-actions {
    width: 100%;
    min-width: 0;
  }
}

@media (max-width: 640px) {
  .admin-sidebar {
    width: 100%;
    height: auto;
    position: relative;
    flex-direction: row;
    flex-wrap: wrap;
    padding: var(--admin-space-xs);
  }

  .sidebar-brand {
    border-bottom: none;
    padding: var(--admin-space-xs) var(--admin-space-md);
  }

  .sidebar-nav {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    padding: 0;
    flex: none;
  }

  .nav-item {
    padding: var(--admin-space-xs) var(--admin-space-md);
    border-left: none;
    border-bottom: 2px solid transparent;
  }

  .nav-item.active {
    border-left-color: transparent;
    border-bottom-color: var(--cds-primary);
  }

  .sidebar-footer {
    display: flex;
    border-top: none;
    padding: 0;
  }

  .admin-main {
    margin-left: 0;
  }

  .admin-topbar {
    padding: var(--admin-space-md);
  }

  .page-title {
    font-size: var(--admin-text-2xl);
  }

  .admin-shell-layout--dashboard .admin-sidebar {
    width: 100%;
    padding: var(--admin-space-xs);
  }

  .admin-shell-layout--dashboard .admin-main {
    margin-left: 0;
  }

  .admin-shell-layout--dashboard .sidebar-nav--dashboard-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .admin-shell-layout--dashboard .sidebar-footer {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
