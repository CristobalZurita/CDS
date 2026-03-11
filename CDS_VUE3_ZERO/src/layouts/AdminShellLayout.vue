<template>
  <div class="admin-shell-layout">
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
          :class="{ active: isActive(item) }"
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
          <span class="user-badge">👤 {{ userName }}</span>
        </div>
      </header>

      <!-- Área de contenido -->
      <div class="admin-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const userName = computed(() => authStore.user?.full_name || authStore.user?.email || 'Admin')

const pageTitle = computed(() => {
  const titles = {
    'admin-dashboard': 'Dashboard',
    'admin-repairs': 'Reparaciones',
    'admin-repair-detail': 'Detalle de Reparación',
    'admin-quotes': 'Cotizaciones',
    'admin-clients': 'Clientes',
    'admin-inventory': 'Inventario',
    'admin-inventory-unified': 'Inventario Unificado',
    'admin-categories': 'Categorías',
    'admin-appointments': 'Citas',
    'admin-contact': 'Mensajes',
    'admin-newsletter': 'Newsletter',
    'admin-tickets': 'Tickets',
    'admin-purchase-requests': 'Solicitudes de Compra',
    'admin-manuals': 'Manuales',
    'admin-stats': 'Estadísticas',
    'admin-wizards': 'Magos',
    'admin-intake': 'Nuevo Ingreso',
    'admin-archive': 'Archivo'
  }
  return titles[route.name] || 'Panel Admin'
})

const pageSubtitle = computed(() => {
  const subtitles = {
    'admin-dashboard': 'Panel de control administrativo',
    'admin-repairs': 'Gestión de órdenes de trabajo',
    'admin-quotes': 'Cotizaciones y presupuestos',
    'admin-clients': 'Base de datos de clientes',
    'admin-inventory': 'Control de stock y materiales',
    'admin-intake': 'Ingreso unificado de equipos'
  }
  return subtitles[route.name] || ''
})

const menuItems = [
  { to: '/admin', label: 'Dashboard', icon: '📊' },
  { to: '/admin/intake', label: 'Nuevo Ingreso', icon: '➕' },
  { to: '/admin/repairs', label: 'Reparaciones', icon: '🔧' },
  { to: '/admin/quotes', label: 'Cotizaciones', icon: '📄' },
  { to: '/admin/clients', label: 'Clientes', icon: '👥' },
  { to: '/admin/inventory', label: 'Inventario', icon: '📦' },
  { to: '/admin/appointments', label: 'Citas', icon: '📅' },
  { to: '/admin/tickets', label: 'Tickets', icon: '🎫' },
  { to: '/admin/stats', label: 'Estadísticas', icon: '📈' }
]

const isActive = (item) => {
  if (item.to === '/admin') return route.path === '/admin'
  return route.path.startsWith(item.to)
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* Layout principal - 35% larger */
.admin-shell-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
  font-size: 1.35rem;
}

/* Sidebar - 35% larger */
.admin-sidebar {
  width: 351px;
  background: #1a1f36;
  color: #fff;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  z-index: 100;
}

.sidebar-brand {
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.brand-icon {
  font-size: 2.4rem;
}

.brand-text {
  font-size: 1.7rem;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.sidebar-nav {
  flex: 1;
  padding: 1.35rem 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  padding: 1.2rem 2rem;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.2s;
  border-left: 3px solid transparent;
  cursor: pointer;
  background: none;
  border: none;
  width: 100%;
  font-size: 1.25rem;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.nav-item.active {
  background: rgba(255, 107, 53, 0.15);
  color: #ff6b35;
  border-left-color: #ff6b35;
}

.nav-icon {
  font-size: 1.7rem;
  width: 2rem;
  text-align: center;
}

.nav-label {
  font-weight: 500;
}

.sidebar-footer {
  padding: 1.35rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.back-link {
  color: rgba(255, 255, 255, 0.6);
}

.back-link:hover {
  color: #fff;
}

.logout-btn {
  color: rgba(255, 100, 100, 0.8);
}

.logout-btn:hover {
  background: rgba(255, 100, 100, 0.15);
  color: #ff6464;
}

/* Main content - 35% larger */
.admin-main {
  flex: 1;
  margin-left: 351px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Topbar - 35% larger */
.admin-topbar {
  background: #fff;
  padding: 1.7rem 2.7rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e8ecf1;
  position: sticky;
  top: 0;
  z-index: 50;
}

.page-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #1a1f36;
}

.page-subtitle {
  margin: 0.35rem 0 0;
  font-size: 1.2rem;
  color: #6b7280;
}

.user-badge {
  background: #f3f4f6;
  padding: 0.7rem 1.35rem;
  border-radius: 999px;
  font-size: 1.2rem;
  color: #374151;
}

/* Content area - 35% larger */
.admin-content {
  flex: 1;
  padding: 2.7rem;
  overflow-y: auto;
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
    width: 95px;
  }
  
  .brand-text,
  .nav-label {
    display: none;
  }
  
  .sidebar-brand {
    justify-content: center;
    padding: 1.35rem;
  }
  
  .nav-item {
    justify-content: center;
    padding: 1.35rem;
  }
  
  .nav-icon {
    width: auto;
  }
  
  .admin-main {
    margin-left: 95px;
  }
  
  .admin-content {
    padding: 2rem;
  }
}

@media (max-width: 640px) {
  .admin-sidebar {
    width: 100%;
    height: auto;
    position: relative;
    flex-direction: row;
    flex-wrap: wrap;
    padding: 0.7rem;
  }
  
  .sidebar-brand {
    border-bottom: none;
    padding: 0.7rem 1.35rem;
  }
  
  .sidebar-nav {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    padding: 0;
    flex: none;
  }
  
  .nav-item {
    padding: 0.7rem 1.35rem;
    border-left: none;
    border-bottom: 2px solid transparent;
  }
  
  .nav-item.active {
    border-left-color: transparent;
    border-bottom-color: #ff6b35;
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
    padding: 1.35rem;
  }
  
  .page-title {
    font-size: 1.7rem;
  }
}
</style>
