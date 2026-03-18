<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Estadisticas</h1>
        <p>Indicadores y metricas del sistema.</p>
      </div>
      <button class="btn-secondary" :disabled="isLoading" @click="load">
        {{ isLoading ? 'Actualizando...' : 'Actualizar' }}
      </button>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section class="cards-grid">
      <article v-for="card in cards" :key="card.id" class="stat-card">
        <span class="stat-label">{{ card.label }}</span>
        <strong class="stat-value">{{ card.value }}</strong>
      </article>
    </section>

    <section class="panel-grid">
      <StatsMetricPanel
        v-for="panel in summaryPanels"
        :key="panel.key"
        :title="panel.title"
        :items="panel.items"
      />
    </section>

    <section class="charts-grid">
      <StatsChartPanel
        v-for="chart in chartPanels"
        :key="chart.key"
        :title="chart.title"
        :type="chart.type"
        :options="chart.options"
        :series="chart.series"
      />
    </section>
  </main>
</template>

<script setup>
import { defineAsyncComponent } from 'vue'
import StatsMetricPanel from '@/components/admin/StatsMetricPanel.vue'
import { useStatsPage } from '@/composables/useStatsPage'

const StatsChartPanel = defineAsyncComponent(() => import('@/components/admin/StatsChartPanel.vue'))

const {
  isLoading,
  error,
  cards,
  summaryPanels,
  chartPanels,
  load
} = useStatsPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped src="./statsPageShared.css"></style>
