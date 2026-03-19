<template>
  <div
    class="admin-shell-layout"
    :class="{ 'admin-shell-layout--dashboard': isDashboardRoute }"
  >
    <!-- Sidebar fijo siempre visible -->
    <aside class="admin-sidebar">
      <div class="sidebar-brand">
        <span class="brand-icon">🎛️</span>
        <span class="brand-text">Admin</span>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
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
        <div class="breadcrumb">
          <h1 class="page-title">{{ pageTitle }}</h1>
          <p v-if="pageSubtitle" class="page-subtitle">{{ pageSubtitle }}</p>
        </div>
        <div class="topbar-actions">
          <AdminGlobalSearch />
          <span class="user-badge">👤 {{ userName }}</span>
        </div>
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
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AdminGlobalSearch from '@/components/admin/AdminGlobalSearch.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const userName = computed(() => authStore.user?.full_name || authStore.user?.email || 'Admin')

const pageTitle    = computed(() => route.meta.title    || 'Panel Admin')
const pageSubtitle = computed(() => route.meta.subtitle || '')
const isDashboardRoute = computed(() => route.path === '/admin')

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

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-shell-layout {
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
  --admin-list-mono-font-family: ui-monospace, monospace;
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
  --admin-nav-active-bg: rgba(236, 107, 0, 0.15);
  --admin-back-link-color: rgba(255, 255, 255, 0.6);
  --admin-logout-text: #f2b7b7;
  --admin-logout-hover-bg: rgba(220, 38, 38, 0.15);
  --admin-user-badge-bg: var(--cds-surface-1);
  display: flex;
  min-height: 100vh;
  background: var(--cds-background-color);
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

.sidebar-brand {
  padding: var(--admin-space-lg) var(--admin-space-xl);
  display: flex;
  align-items: center;
  gap: var(--admin-space-md);
  border-bottom: 1px solid var(--admin-sidebar-divider);
}

.brand-icon {
  font-size: var(--admin-text-3xl);
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

.nav-item:hover {
  background: var(--admin-nav-hover-bg);
  color: var(--cds-white);
}

.nav-item.active {
  background: var(--admin-nav-active-bg);
  color: var(--cds-primary);
  border-left-color: var(--cds-primary);
}

.nav-icon {
  font-size: var(--admin-text-xl);
  width: 2.4rem;
  text-align: center;
}

.nav-label {
  font-weight: var(--cds-font-medium);
}

.sidebar-footer {
  padding: var(--admin-space-md) 0;
  border-top: 1px solid var(--admin-sidebar-divider);
}

.back-link {
  color: var(--admin-back-link-color);
}

.back-link:hover {
  color: var(--cds-white);
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

.page-title {
  margin: 0;
  font-size: var(--admin-text-3xl);
  font-weight: var(--cds-font-bold);
  color: var(--cds-text-normal);
  line-height: 1;
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

.user-badge {
  background: var(--admin-user-badge-bg);
  padding: var(--admin-space-sm) var(--cds-space-lg);
  border-radius: var(--cds-radius-pill);
  font-size: var(--admin-text-sm);
  color: var(--cds-text-normal);
}

.admin-content {
  flex: 1;
  padding: var(--admin-space-2xl);
  overflow-y: auto;
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
}
</style>
