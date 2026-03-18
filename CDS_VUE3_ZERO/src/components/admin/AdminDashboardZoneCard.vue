<template>
  <article class="kpi-box">
    <header class="kpi-header">
      <span class="kpi-icon" aria-hidden="true">{{ icon }}</span>
      <div>
        <h3 class="kpi-title">{{ title }}</h3>
        <p class="kpi-desc">{{ description }}</p>
      </div>
    </header>

    <div class="kpi-metrics">
      <div
        v-for="metric in metrics"
        :key="metric.key"
        :class="['metric', metric.tone ? `metric-${metric.tone}` : null]"
      >
        <span class="metric-value">{{ metric.value }}</span>
        <span class="metric-label">{{ metric.label }}</span>
      </div>
    </div>
  </article>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '' },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  metrics: { type: Array, default: () => [] }
})
</script>

<style scoped src="../../pages/admin/adminDashboardShared.css"></style>
