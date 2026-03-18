<template>
  <article class="alerts-box">
    <header class="alerts-header">
      <span class="alerts-icon" aria-hidden="true">🚨</span>
      <div>
        <h3>Alertas que requieren atención</h3>
        <p class="alerts-subtitle">Incidencias activas para revisión operativa</p>
      </div>
    </header>

    <ul class="alerts-list">
      <li
        v-for="alert in alerts"
        :key="alert.key"
        :class="['alert-item', alert.tone ? `alert-${alert.tone}` : null]"
      >
        <span class="alert-text">{{ alert.text }}</span>
        <span class="alert-badge">{{ alert.count }}</span>
      </li>
    </ul>
  </article>
</template>

<script setup>
defineProps({
  alerts: { type: Array, default: () => [] }
})
</script>

<style scoped src="../../pages/admin/adminDashboardShared.css"></style>
