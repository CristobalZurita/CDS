<template>
  <aside class="admin-sidebar">
    <div class="brand">
      <span class="brand-logo">🎛️</span>
      <span>Admin</span>
    </div>

    <nav class="menu">
      <router-link
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="menu-item"
        :class="{ active: isActive(item) }"
      >
        <span class="menu-icon">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const items = [
  { to: '/admin', label: 'Dashboard', icon: '📊' },
  { to: '/admin/repairs', label: 'Reparaciones', icon: '🔧' },
  { to: '/admin/quotes', label: 'Cotizaciones', icon: '📄' },
  { to: '/admin/clients', label: 'Clientes', icon: '👥' },
  { to: '/admin/inventory', label: 'Inventario', icon: '📦' },
  { to: '/admin/intake', label: 'Nuevo Ingreso', icon: '➕' },
  { to: '/admin/appointments', label: 'Citas', icon: '📅' },
  { to: '/dashboard', label: '← Volver al Panel', icon: '🏠' }
]

const isActive = (item) => {
  if (item.to === '/admin') return route.path === '/admin'
  return route.path.startsWith(item.to)
}
</script>

<style scoped>
.admin-sidebar {
  width: 260px;
  min-height: 100vh;
  background: var(--color-dark, #1a1a2e);
  color: var(--color-white, #fff);
  position: fixed;
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.brand {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-weight: 700;
  font-size: 1.25rem;
}

.brand-logo {
  font-size: 1.5rem;
}

.menu {
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-white, #fff);
}

.menu-item.active {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-primary, #ff6b35);
  border-left-color: var(--color-primary, #ff6b35);
}

.menu-icon {
  font-size: 1.25rem;
  width: 1.5rem;
  text-align: center;
}

@media (max-width: 768px) {
  .admin-sidebar {
    width: 100%;
    position: relative;
    min-height: auto;
  }
  
  .menu {
    flex-direction: row;
    flex-wrap: wrap;
    padding: 0.5rem;
  }
  
  .menu-item {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }
}
</style>
