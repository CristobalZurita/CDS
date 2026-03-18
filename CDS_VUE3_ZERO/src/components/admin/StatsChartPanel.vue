<template>
  <article class="panel-card chart-card">
    <h2 class="stats-panel-title">{{ title }}</h2>
    <VueApexCharts
      :type="type"
      height="220"
      :options="options"
      :series="series"
    />
  </article>
</template>

<script setup>
import VueApexCharts from 'vue3-apexcharts'

defineProps({
  title: { type: String, default: '' },
  type: { type: String, default: 'line' },
  options: { type: Object, default: () => ({}) },
  series: { type: Array, default: () => [] }
})
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/statsPageShared.css"></style>
