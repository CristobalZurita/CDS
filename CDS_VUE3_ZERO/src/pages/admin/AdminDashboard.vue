<template>
  <div class="admin-dashboard-page">
    <p v-if="error" class="admin-error">{{ error }}</p>
    <section v-if="isLoading" class="panel-card"><p class="empty-state">Cargando indicadores...</p></section>
    <template v-else>
      <StatsCards :stats="stats" />

      <KpiZones
        :zone-cards="zoneCards"
        :alerts="normalizedAlerts"
      />
    </template>

    <AdminDashboardRepairsPanel />
    <AdminDashboardUsersPanel />
  </div>
</template>

<script setup>
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
} = useAdminDashboardPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped src="./adminDashboardShared.css"></style>
