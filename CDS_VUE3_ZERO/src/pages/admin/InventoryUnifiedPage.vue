<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Inventario unificado</h1>
        <p>Vista consolidada de alertas y distribución por familia.</p>
      </div>
      <button class="btn-secondary" :disabled="loading" @click="loadUnifiedInventory">
        {{ loading ? 'Actualizando...' : 'Actualizar' }}
      </button>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section class="cards-grid">
      <article class="stat-card">
        <span>Crítico (5)</span>
        <strong>{{ counts.critical_5 || 0 }}</strong>
      </article>
      <article class="stat-card">
        <span>Alto (20)</span>
        <strong>{{ counts.high_20 || 0 }}</strong>
      </article>
      <article class="stat-card">
        <span>Medio (50)</span>
        <strong>{{ counts.medium_50 || 0 }}</strong>
      </article>
      <article class="stat-card">
        <span>Bajo mínimo</span>
        <strong>{{ counts.low_min || 0 }}</strong>
      </article>
    </section>

    <section class="panel-grid">
      <article class="panel-card">
        <h2>Críticos (top 10)</h2>
        <ul v-if="topCritical.length > 0">
          <li v-for="item in topCritical" :key="item.id">
            <span>{{ item.sku }} · {{ item.name }}</span>
            <strong>{{ item.available_stock }}</strong>
          </li>
        </ul>
        <p v-else class="empty-state">Sin productos críticos.</p>
      </article>

      <article class="panel-card">
        <h2>Alta prioridad (top 10)</h2>
        <ul v-if="topHigh.length > 0">
          <li v-for="item in topHigh" :key="item.id">
            <span>{{ item.sku }} · {{ item.name }}</span>
            <strong>{{ item.available_stock }}</strong>
          </li>
        </ul>
        <p v-else class="empty-state">Sin productos en alta prioridad.</p>
      </article>

      <article class="panel-card panel-card-wide">
        <h2>Familias (distribución)</h2>
        <div v-if="familyBreakdown.length === 0" class="empty-state">Sin datos de inventario.</div>
        <div v-else class="table-wrap">
          <table>
            <thead><tr><th>Familia</th><th>Total</th></tr></thead>
            <tbody>
              <tr v-for="family in familyBreakdown" :key="family.family">
                <td>{{ family.family }}</td>
                <td>{{ family.total }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup>
import { useInventoryUnifiedPage } from '@/composables/useInventoryUnifiedPage'

const {
  loading,
  error,
  counts,
  topCritical,
  topHigh,
  familyBreakdown,
  loadUnifiedInventory
} = useInventoryUnifiedPage()
</script>

<style scoped>
.admin-page { padding: 1rem; display: grid; gap: 1rem; }
.admin-header, .stat-card, .panel-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); }
.admin-header { padding: .9rem; display: flex; flex-wrap: wrap; gap: .75rem; justify-content: space-between; align-items: center; }
.admin-header h1 { margin: 0; font-size: var(--cds-text-3xl); }
.admin-header p { margin: .3rem 0 0; color: var(--cds-text-muted); }
.btn-secondary { min-height: 44px; padding: .65rem .9rem; border-radius: .55rem; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); background: var(--cds-white); color: var(--cds-text-normal); font-size: var(--cds-text-base); }
.admin-error { margin: 0; border: 1px solid #f4c7c3; background: #fef3f2; color: #b42318; border-radius: .6rem; padding: .75rem; }
.cards-grid { display: grid; gap: .7rem; grid-template-columns: repeat(1,minmax(0,1fr)); }
.stat-card { padding: .8rem; display: grid; gap: .2rem; }
.stat-card span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.stat-card strong { font-size: var(--cds-text-2xl); }
.panel-grid { display: grid; gap: .7rem; grid-template-columns: repeat(1,minmax(0,1fr)); }
.panel-card { padding: .9rem; }
.panel-card h2 { margin: 0 0 .5rem; font-size: var(--cds-text-xl); }
.panel-card ul { margin: 0; padding: 0; list-style: none; display: grid; gap: .35rem; }
.panel-card li { display: flex; justify-content: space-between; gap: .5rem; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: .6rem; border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); }
th { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.empty-state { margin: 0; color: var(--cds-text-muted); }
@media (min-width: 860px) { .cards-grid { grid-template-columns: repeat(4,minmax(0,1fr)); } .panel-grid { grid-template-columns: repeat(2,minmax(0,1fr)); } .panel-card-wide { grid-column: 1 / -1; } }
</style>
