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

<style scoped src="./commonAdminPage.css"></style>
<style scoped>
.stat-card span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.stat-card strong { font-size: var(--cds-text-2xl); }
.stat-card { min-height: calc(7rem * var(--cds-type-scale, 1)); }
.panel-card h2 { margin: 0 0 .5rem; }
.panel-card ul { margin: 0; padding: 0; list-style: none; display: grid; gap: .35rem; }
.panel-card li {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: start;
  gap: .75rem;
  padding: .7rem .8rem;
  border: 1px solid var(--admin-neo-line, var(--cds-border-card));
  border-radius: var(--admin-neo-radius-sm, var(--cds-radius-md));
  background: var(--admin-neo-surface-soft, var(--cds-white));
}
.panel-card li span { min-width: 0; overflow-wrap: anywhere; }
.panel-card li strong { white-space: nowrap; }
.panel-card-wide { grid-column: 1 / -1; }
@media (min-width: 860px) {
  .cards-grid { grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr)); }
  .panel-grid { grid-template-columns: repeat(auto-fit, minmax(min(100%, 25rem), 1fr)); }
}
</style>
