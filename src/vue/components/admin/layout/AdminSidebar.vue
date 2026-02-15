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
  { to: '/admin/appointments', label: 'Citas', icon: 'fa-solid fa-calendar-check' },
  { to: '/admin/contact', label: 'Mensajes', icon: 'fa-solid fa-envelope' },
  { to: '/admin/newsletter', label: 'Newsletter', icon: 'fa-solid fa-paper-plane' },
  { to: '/admin/tickets', label: 'Tickets', icon: 'fa-solid fa-ticket' },
  { to: '/admin/purchase-requests', label: 'Compras', icon: 'fa-solid fa-cart-shopping' },
  { to: '/admin/archive', label: 'Archivo', icon: 'fa-solid fa-box-archive' }
]

const brandLogo = `${import.meta.env.BASE_URL}images/logo/Logo%20Nuevo.webp`

const isActive = (item) => {
  if (item.to === '/admin') return route.path === '/admin'
  return route.path.startsWith(item.to)
}
</script>

<style lang="scss" scoped>
@import '@/scss/_core.scss';

.admin-sidebar {
  background: lighten($vintage-beige, 4%);
  color: $color-dark;
  padding: $spacer-lg $spacer-md;
  border-right: 1px solid rgba($color-dark, 0.18);
  display: flex;
  flex-direction: column;
  gap: $spacer-lg;
}

.brand {
  display: flex;
  align-items: center;
  gap: $spacer-sm;
  font-family: $font-family-heading;
  text-transform: uppercase;
  letter-spacing: $ls-wide;
  color: $color-dark;
  font-size: $text-md;
}

.brand img {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: $border-radius-md;
  border: 2px solid rgba($color-primary, 0.6);
  background: $vintage-beige;
}

.menu {
  display: flex;
  flex-direction: column;
  gap: $spacer-xs;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: $spacer-sm;
  padding: $spacer-sm $spacer-md;
  border-radius: $border-radius-lg;
  text-decoration: none;
  color: $color-dark;
  font-weight: $fw-semibold;
  font-size: $text-md;
  transition: $transition-fast;
  border: 1px solid transparent;
}

.menu-item i {
  color: $orange-pastel;
  width: 20px;
  text-align: center;
}

.menu-item:hover {
  background: rgba($color-primary, 0.12);
  border-color: rgba($color-primary, 0.4);
  color: $color-dark;
}

.menu-item.active {
  background: rgba($color-primary, 0.22);
  border-color: rgba($color-primary, 0.6);
  color: $color-dark;
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
    gap: $spacer-sm;
  }

  .menu-item {
    white-space: nowrap;
  }
}
</style>
