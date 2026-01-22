<template>
  <aside class="admin-sidebar">
    <div class="brand">
      <img :src="brandLogo" alt="Cirujano de Sintetizadores" />
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
        <i :class="item.icon" />
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const items = [
  { to: '/admin', label: 'Dashboard', icon: 'fa-solid fa-gauge' },
  { to: '/admin/repairs', label: 'Reparaciones', icon: 'fa-solid fa-screwdriver-wrench' },
  { to: '/admin/clients', label: 'Clientes', icon: 'fa-solid fa-user-group' },
  { to: '/admin/inventory', label: 'Inventario', icon: 'fa-solid fa-boxes-stacked' },
  { to: '/admin/inventory/unified', label: 'Inventario Unificado', icon: 'fa-solid fa-layer-group' },
  { to: '/admin/categories', label: 'Categorías', icon: 'fa-solid fa-tags' },
  { to: '/admin/stats', label: 'Estadísticas', icon: 'fa-solid fa-chart-line' },
  { to: '/admin/appointments', label: 'Citas', icon: 'fa-solid fa-calendar-check' },
  { to: '/admin/contact', label: 'Mensajes', icon: 'fa-solid fa-envelope' },
  { to: '/admin/newsletter', label: 'Newsletter', icon: 'fa-solid fa-paper-plane' }
]

const brandLogo = `${import.meta.env.BASE_URL}images/logo/Logo%20Nuevo.jpg`

const isActive = (item) => {
  if (item.to === '/admin') return route.path === '/admin'
  return route.path.startsWith(item.to)
}
</script>

<style scoped lang="scss">
@import "/src/scss/_theming.scss";

.admin-sidebar {
  background: lighten($vintage-beige, 4%);
  color: $brand-text;
  padding: 1.5rem 1.25rem;
  border-right: 1px solid rgba(62, 60, 56, 0.18);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-family: $headings-font-family;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: $brand-text;
  font-size: 1.05rem;
}

.brand img {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid rgba(236, 107, 0, 0.6);
  background: $vintage-beige;
}

.menu {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.9rem 1rem;
  border-radius: 10px;
  text-decoration: none;
  color: $brand-text;
  font-weight: 600;
  font-size: 1.05rem;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.menu-item i {
  color: $orange-pastel;
  width: 20px;
  text-align: center;
}

.menu-item:hover {
  background: rgba(236, 107, 0, 0.12);
  border-color: rgba(236, 107, 0, 0.4);
  color: $brand-text;
}

.menu-item.active {
  background: rgba(236, 107, 0, 0.22);
  border-color: rgba(236, 107, 0, 0.6);
  color: $brand-text;
}

@include media-breakpoint-down(lg) {
  .admin-sidebar {
    flex-direction: row;
    overflow-x: auto;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .menu {
    flex-direction: row;
    flex-wrap: nowrap;
    gap: 0.5rem;
  }

  .menu-item {
    white-space: nowrap;
  }
}
</style>
