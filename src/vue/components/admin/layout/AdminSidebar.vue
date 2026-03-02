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
  { to: '/admin/quotes', label: 'Cotizaciones', icon: 'fa-solid fa-file-invoice-dollar' },
  { to: '/admin/clients', label: 'Clientes', icon: 'fa-solid fa-user-group' },
  { to: '/admin/inventory', label: 'Inventario', icon: 'fa-solid fa-boxes-stacked' },
  { to: '/admin/inventory/unified', label: 'Inventario Unificado', icon: 'fa-solid fa-layer-group' },
  { to: '/admin/categories', label: 'Categorías', icon: 'fa-solid fa-tags' },
  { to: '/admin/appointments', label: 'Citas', icon: 'fa-solid fa-calendar-check' },
  { to: '/admin/contact', label: 'Mensajes', icon: 'fa-solid fa-envelope' },
  { to: '/admin/newsletter', label: 'Newsletter', icon: 'fa-solid fa-paper-plane' },
  { to: '/admin/tickets', label: 'Tickets', icon: 'fa-solid fa-ticket' },
  { to: '/admin/purchase-requests', label: 'Compras', icon: 'fa-solid fa-cart-shopping' },
  { to: '/admin/manuals', label: 'Manuales', icon: 'fa-solid fa-book-open' },
  { to: '/admin/stats', label: 'Estadísticas', icon: 'fa-solid fa-chart-line' },
  { to: '/admin/wizards', label: 'Magos', icon: 'fa-solid fa-wand-magic-sparkles' },
  { to: '/admin/archive', label: 'Archivo', icon: 'fa-solid fa-box-archive' }
]

const brandLogo = `${import.meta.env.BASE_URL}images/logo/Logo%20Nuevo.webp`

const isActive = (item) => {
  if (item.to === '/admin') return route.path === '/admin'
  return route.path.startsWith(item.to)
}
</script>
