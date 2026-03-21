<template>
  <div class="admin-dashboard-page">
    <p v-if="error" class="admin-error">{{ error }}</p>
    <section v-if="isLoading" class="panel-card"><p class="empty-state">Cargando indicadores...</p></section>
    <template v-else>
      <section class="admin-dashboard-hero">
        <div class="admin-dashboard-hero-main">
          <p class="admin-dashboard-eyebrow">Centro de control</p>
          <h2 class="admin-dashboard-title">Operación general del taller</h2>
          <p class="admin-dashboard-copy">
            Vista ejecutiva para revisar pulso, prioridades y accesos rápidos del sistema administrativo.
          </p>

          <div class="admin-dashboard-chip-row">
            <span class="admin-dashboard-chip admin-dashboard-chip--ink">
              <i class="fa-solid fa-calendar-day"></i>
              {{ dashboardDate }}
            </span>
            <span class="admin-dashboard-chip admin-dashboard-chip--accent">
              <i class="fa-solid fa-triangle-exclamation"></i>
              {{ normalizedAlerts.length }} alerta{{ normalizedAlerts.length === 1 ? '' : 's' }}
            </span>
            <span class="admin-dashboard-chip admin-dashboard-chip--muted">
              <i class="fa-solid fa-layer-group"></i>
              {{ zoneCards.length }} zonas activas
            </span>
          </div>

          <div class="admin-dashboard-actions">
            <router-link class="btn-primary admin-dashboard-btn" to="/admin/intake">
              <i class="fa-solid fa-plus"></i>
              Nuevo ingreso
            </router-link>
            <router-link class="btn-secondary admin-dashboard-btn" to="/admin/repairs">
              <i class="fa-solid fa-screwdriver-wrench"></i>
              Reparaciones
            </router-link>
            <router-link class="btn-secondary admin-dashboard-btn" to="/admin/clients">
              <i class="fa-solid fa-users"></i>
              Clientes
            </router-link>
            <button class="btn-secondary admin-dashboard-btn" type="button" @click="loadDashboard">
              <i class="fa-solid fa-rotate-right"></i>
              Refrescar
            </button>
          </div>
        </div>

        <aside class="admin-dashboard-focus">
          <p class="admin-dashboard-eyebrow">Foco inmediato</p>
          <h3 class="admin-dashboard-focus-title">{{ focusTitle }}</h3>
          <p class="admin-dashboard-focus-copy">{{ focusCopy }}</p>
          <div class="admin-dashboard-focus-metrics">
            <article class="admin-dashboard-focus-card">
              <span>Usuarios</span>
              <strong>{{ formatNumber(stats?.users) }}</strong>
            </article>
            <article class="admin-dashboard-focus-card">
              <span>Clientes</span>
              <strong>{{ formatNumber(stats?.clients) }}</strong>
            </article>
            <article class="admin-dashboard-focus-card">
              <span>Reparaciones</span>
              <strong>{{ formatNumber(stats?.repairs) }}</strong>
            </article>
          </div>
        </aside>
      </section>

      <section class="admin-dashboard-command-grid">
        <article class="admin-dashboard-command-card">
          <span class="admin-dashboard-command-icon">📦</span>
          <div>
            <h3>Inventario</h3>
            <p>Stock, disponibilidad y salud operativa del catálogo interno.</p>
          </div>
          <router-link class="btn-link" to="/admin/inventory">Abrir inventario →</router-link>
        </article>

        <article class="admin-dashboard-command-card">
          <span class="admin-dashboard-command-icon">📄</span>
          <div>
            <h3>Cotizaciones</h3>
            <p>Seguimiento de solicitudes, márgenes y aprobación del flujo comercial.</p>
          </div>
          <router-link class="btn-link" to="/admin/quotes">Abrir cotizaciones →</router-link>
        </article>

        <article class="admin-dashboard-command-card">
          <span class="admin-dashboard-command-icon">📈</span>
          <div>
            <h3>Estadísticas</h3>
            <p>Indicadores históricos, tendencias y lectura extendida del desempeño.</p>
          </div>
          <router-link class="btn-link" to="/admin/stats">Abrir estadísticas →</router-link>
        </article>
      </section>

      <StatsCards :stats="stats" />

      <section class="admin-dashboard-zones">
        <KpiZones
          :zone-cards="zoneCards"
          :alerts="normalizedAlerts"
        />
      </section>
    </template>

    <section class="admin-dashboard-bottom-grid">
      <AdminDashboardRepairsPanel />
      <AdminDashboardUsersPanel />
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AdminDashboardRepairsPanel from '@/components/admin/AdminDashboardRepairsPanel.vue'
import AdminDashboardUsersPanel from '@/components/admin/AdminDashboardUsersPanel.vue'
import KpiZones from '@/components/admin/KpiZones.vue'
import StatsCards from '@/components/admin/StatsCards.vue'
import { useAdminDashboardPage } from '@/composables/useAdminDashboardPage'

const {
  isLoading,
  error,
  stats,
  zoneCards,
  normalizedAlerts,
  loadDashboard,
} = useAdminDashboardPage()

const dashboardDate = computed(() => {
  return new Intl.DateTimeFormat('es-CL', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  }).format(new Date())
})

const focusTitle = computed(() => {
  if (normalizedAlerts.value.length > 0) return 'Hay frentes que requieren atención hoy'
  if (Number(stats.value?.repairs || 0) > 0) return 'El taller tiene carga operativa activa'
  if (Number(stats.value?.clients || 0) > 0) return 'La base de clientes está viva y en movimiento'
  return 'El tablero está estable'
})

const focusCopy = computed(() => {
  if (normalizedAlerts.value.length > 0) {
    return normalizedAlerts.value[0]?.text || 'Revisa las alertas del sistema para priorizar la operación.'
  }
  if (Number(stats.value?.repairs || 0) > 0) {
    return 'Usa este panel como entrada ejecutiva para navegar entre reparaciones, inventario y clientes sin perder contexto.'
  }
  return 'Puedes usar esta portada como centro de mando para abrir los módulos administrativos principales.'
})

function formatNumber(val) {
  const num = Number(val)
  return Number.isFinite(num) ? num.toLocaleString('es-CL') : '0'
}
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped src="./adminDashboardShared.css"></style>
