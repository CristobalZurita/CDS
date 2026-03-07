<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Cotizaciones</h1>
        <p>Tablero de estados para pendientes, enviadas y cerradas.</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" :disabled="loading" @click="loadBoard">
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section class="panel-card toolbar-grid">
      <label>
        <span>Buscar</span>
        <input
          v-model.trim="searchQuery"
          type="search"
          placeholder="COT, cliente o problema"
          @keyup.enter="loadBoard"
        />
      </label>
      <label>
        <span>Estado</span>
        <select v-model="statusFilter" @change="loadBoard">
          <option value="">Todos</option>
          <option v-for="option in statusOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
        </select>
      </label>
      <label class="checkbox-row">
        <input v-model="sendWhatsapp" type="checkbox" />
        <span>Enviar tambien por WhatsApp</span>
      </label>
      <label class="full">
        <span>Mensaje opcional de envio</span>
        <input v-model.trim="customMessage" type="text" placeholder="Mensaje para cliente" />
      </label>
    </section>

    <section class="summary-grid">
      <article class="summary-card"><span>En tablero</span><strong>{{ counts.total }}</strong></article>
      <article class="summary-card"><span>Abiertas</span><strong>{{ metrics.open_total }}</strong></article>
      <article class="summary-card"><span>Pendientes</span><strong>{{ metrics.pending }}</strong></article>
      <article class="summary-card"><span>Enviadas</span><strong>{{ metrics.sent }}</strong></article>
      <article class="summary-card"><span>Aprobadas</span><strong>{{ metrics.approved }}</strong></article>
      <article class="summary-card warning"><span>Vencen &lt; 3 dias</span><strong>{{ metrics.expiring_3d }}</strong></article>
      <article class="summary-card danger"><span>Vencidas</span><strong>{{ metrics.expired_open }}</strong></article>
    </section>

    <section class="columns-grid">
      <article v-for="column in columnDefs" :key="column.key" class="column-card">
        <header class="column-head">
          <h2>{{ column.label }}</h2>
          <span class="chip">{{ getColumnCount(column.key) }}</span>
        </header>

        <div class="column-body">
          <article
            v-for="quote in getColumnItems(column.key)"
            :key="quote.id"
            class="quote-card"
            :class="{ highlighted: highlightedQuoteId === quote.id }"
          >
            <div class="quote-head">
              <strong>{{ quote.quote_number || `COT-${quote.id}` }}</strong>
              <span class="status-chip">{{ quote.status || 'pending' }}</span>
            </div>

            <div class="quote-meta">
              <div><span>Cliente:</span> {{ quote.client?.name || quote.client_name || 'SIN_DATO' }}</div>
              <div><span>Total:</span> {{ formatCurrency(quote.estimated_total) }}</div>
              <div><span>Validez:</span> {{ formatDate(quote.valid_until) }}</div>
              <div v-if="quote.linked_repair_id"><span>OT:</span> {{ quote.linked_repair_number || `OT-${quote.linked_repair_id}` }}</div>
            </div>

            <p class="quote-problem">{{ quote.problem_description || 'Sin descripcion' }}</p>

            <div class="row-actions">
              <button
                v-if="quote.status === 'pending'"
                class="btn-primary"
                :disabled="isBusy(quote.id)"
                @click="sendQuote(quote)"
              >
                {{ isBusy(quote.id) ? 'Enviando...' : 'Enviar' }}
              </button>

              <button
                v-if="quote.status === 'sent'"
                class="btn-success"
                :disabled="isBusy(quote.id)"
                @click="changeStatus(quote, 'approved')"
              >
                Aprobar
              </button>

              <button
                v-if="quote.status === 'sent'"
                class="btn-danger"
                :disabled="isBusy(quote.id)"
                @click="changeStatus(quote, 'denied')"
              >
                Rechazar
              </button>

              <button
                v-if="quote.status === 'approved' && !quote.linked_repair_id"
                class="btn-secondary"
                :disabled="isBusy(quote.id)"
                @click="createRepairFromQuote(quote)"
              >
                {{ isBusy(quote.id) ? 'Creando OT...' : 'Crear OT' }}
              </button>

              <button
                v-if="quote.linked_repair_id"
                class="btn-secondary"
                @click="openRepair(quote.linked_repair_id)"
              >
                Ver OT
              </button>

              <button
                v-if="!quote.linked_repair_id"
                class="btn-danger"
                :disabled="isBusy(quote.id)"
                @click="deleteQuote(quote)"
              >
                Eliminar
              </button>
            </div>
          </article>

          <p v-if="getColumnItems(column.key).length === 0" class="empty-state">Sin cotizaciones en esta columna.</p>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup>
import { useQuotesAdminPage } from '@new/composables/useQuotesAdminPage'

const {
  loading,
  error,
  searchQuery,
  statusFilter,
  customMessage,
  sendWhatsapp,
  statusOptions,
  columnDefs,
  counts,
  metrics,
  highlightedQuoteId,
  isBusy,
  getColumnItems,
  getColumnCount,
  formatCurrency,
  formatDate,
  loadBoard,
  sendQuote,
  changeStatus,
  createRepairFromQuote,
  openRepair,
  deleteQuote
} = useQuotesAdminPage()
</script>

<style scoped>
.admin-page { padding: 1rem; display: grid; gap: 1rem; }
.admin-header, .panel-card, .summary-card, .column-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); }
.admin-header { padding: .9rem; display: flex; justify-content: space-between; align-items: center; gap: .75rem; flex-wrap: wrap; }
.admin-header h1 { margin: 0; font-size: var(--cds-text-3xl); }
.admin-header p { margin: .3rem 0 0; color: var(--cds-text-muted); }
.header-actions { display: flex; gap: .45rem; }
.btn-primary, .btn-secondary, .btn-danger, .btn-success { min-height: 40px; border-radius: .55rem; padding: .6rem .9rem; border: 1px solid transparent; font-size: var(--cds-text-sm); }
.btn-primary { background: var(--cds-primary); border-color: var(--cds-primary); color: var(--cds-white); }
.btn-secondary { background: var(--cds-white); border-color: color-mix(in srgb, var(--cds-light) 65%, white); color: var(--cds-text-normal); }
.btn-success { background: #16a34a; border-color: #16a34a; color: #fff; }
.btn-danger { background: #dc2626; border-color: #dc2626; color: #fff; }
.admin-error { margin: 0; border: 1px solid #fecaca; background: #fef2f2; color: #991b1b; border-radius: .65rem; padding: .75rem; }
.panel-card { padding: .9rem; display: grid; gap: .6rem; }
.toolbar-grid { grid-template-columns: repeat(1, minmax(0, 1fr)); }
.toolbar-grid label { display: grid; gap: .3rem; }
.toolbar-grid span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.toolbar-grid input, .toolbar-grid select { min-height: 44px; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); border-radius: .55rem; padding: .65rem .75rem; font-size: var(--cds-text-base); }
.toolbar-grid .full { grid-column: 1 / -1; }
.checkbox-row { display: flex !important; align-items: center; gap: .5rem !important; }
.summary-grid { display: grid; gap: .65rem; grid-template-columns: repeat(1, minmax(0, 1fr)); }
.summary-card { padding: .7rem; display: grid; gap: .2rem; }
.summary-card span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.summary-card strong { font-size: var(--cds-text-xl); }
.summary-card.warning { background: #fef9c3; }
.summary-card.danger { background: #fee2e2; }
.columns-grid { display: grid; gap: .8rem; grid-template-columns: repeat(1, minmax(0, 1fr)); }
.column-card { display: grid; align-content: start; }
.column-head { display: flex; justify-content: space-between; align-items: center; gap: .45rem; padding: .75rem .85rem; border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); }
.column-head h2 { margin: 0; font-size: var(--cds-text-lg); }
.chip { border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); border-radius: 999px; padding: .2rem .55rem; font-size: var(--cds-text-sm); }
.column-body { padding: .75rem; display: grid; gap: .55rem; }
.quote-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .7rem; background: color-mix(in srgb, var(--cds-light) 9%, white); padding: .7rem; display: grid; gap: .45rem; }
.quote-card.highlighted { border-color: color-mix(in srgb, var(--cds-primary) 45%, white); box-shadow: 0 0 0 2px color-mix(in srgb, var(--cds-primary) 14%, transparent); }
.quote-head { display: flex; justify-content: space-between; gap: .45rem; align-items: center; }
.status-chip { border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); border-radius: 999px; padding: .15rem .55rem; font-size: var(--cds-text-xs); text-transform: uppercase; }
.quote-meta { display: grid; gap: .25rem; font-size: var(--cds-text-sm); }
.quote-meta span { color: var(--cds-text-muted); }
.quote-problem { margin: 0; font-size: var(--cds-text-sm); line-height: 1.5; }
.row-actions { display: flex; gap: .4rem; flex-wrap: wrap; }
.empty-state { margin: 0; border: 1px dashed color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .65rem; padding: .7rem; color: var(--cds-text-muted); }
@media (min-width: 900px) {
  .toolbar-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .summary-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .columns-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
</style>
