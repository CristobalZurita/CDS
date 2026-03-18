<template>
  <section class="kpi-section">
    <div class="kpi-grid">
      <AdminDashboardZoneCard
        v-for="zone in zoneCards"
        :key="zone.key"
        :icon="zone.icon"
        :title="zone.title"
        :description="zone.description"
        :metrics="zone.metrics"
      />
    </div>

    <AdminDashboardAlertsPanel v-if="alerts.length" :alerts="alerts" />
  </section>
</template>

<script setup>
import AdminDashboardAlertsPanel from '@/components/admin/AdminDashboardAlertsPanel.vue'
import AdminDashboardZoneCard from '@/components/admin/AdminDashboardZoneCard.vue'

defineProps({
  zoneCards: { type: Array, default: () => [] },
  alerts: { type: Array, default: () => [] }
})
</script>

<style scoped src="../../pages/admin/adminDashboardShared.css"></style>
