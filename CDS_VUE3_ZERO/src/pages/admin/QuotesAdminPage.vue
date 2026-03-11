<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Cotizaciones</h1>
        <p>Tablero de estados para pendientes, enviadas y cerradas.</p>
      </div>
      <div class="header-actions">
        <button class="btn-primary" @click="showNewQuoteModal = true">
          + Nueva Cotización
        </button>
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

    <!-- Modal Nueva Cotización -->
    <div v-if="showNewQuoteModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <header class="modal-header">
          <h2>Nueva Cotización</h2>
          <button class="modal-close" @click="closeModal">×</button>
        </header>

        <form class="modal-form" @submit.prevent="handleCreateQuote">
          <div class="form-grid">
            <div class="form-group full">
              <label>Nombre del cliente *</label>
              <input 
                v-model="newQuote.client_name" 
                type="text" 
                placeholder="Ej: Juan Pérez"
                required
              />
            </div>

            <div class="form-group">
              <label>Email *</label>
              <input 
                v-model="newQuote.client_email" 
                type="email" 
                placeholder="ejemplo@correo.com"
                required
              />
            </div>

            <div class="form-group">
              <label>Teléfono</label>
              <input 
                v-model="newQuote.client_phone" 
                type="tel" 
                placeholder="+56912345678"
              />
            </div>

            <div class="form-group full">
              <label>Descripción del problema *</label>
              <textarea 
                v-model="newQuote.problem_description" 
                placeholder="Describa el problema del equipo..."
                rows="3"
                required
              ></textarea>
            </div>

            <div class="form-group full">
              <label>Diagnóstico (opcional)</label>
              <textarea 
                v-model="newQuote.diagnosis" 
                placeholder="Su diagnóstico técnico preliminar..."
                rows="2"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Costo repuestos (CLP)</label>
              <input 
                v-model.number="newQuote.estimated_parts_cost" 
                type="number" 
                min="0"
                step="1000"
                placeholder="0"
              />
            </div>

            <div class="form-group">
              <label>Costo mano de obra (CLP)</label>
              <input 
                v-model.number="newQuote.estimated_labor_cost" 
                type="number" 
                min="0"
                step="1000"
                placeholder="0"
              />
            </div>

            <div class="form-group">
              <label>Total estimado * (CLP)</label>
              <input 
                v-model.number="newQuote.estimated_total" 
                type="number" 
                min="0"
                step="1000"
                placeholder="0"
                required
              />
            </div>

            <div class="form-group">
              <label>Válida hasta</label>
              <input 
                v-model="newQuote.valid_until" 
                type="date"
              />
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeModal">
              Cancelar
            </button>
            <button 
              type="submit" 
              class="btn-primary"
              :disabled="isCreating"
            >
              {{ isCreating ? 'Creando...' : 'Crear Cotización' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useQuotesAdminPage } from '@/composables/useQuotesAdminPage'

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
  deleteQuote,
  createQuote
} = useQuotesAdminPage()

// Modal state
const showNewQuoteModal = ref(false)
const isCreating = ref(false)

// Default valid until (30 days)
const defaultValidUntil = () => {
  const date = new Date()
  date.setDate(date.getDate() + 30)
  return date.toISOString().split('T')[0]
}

const newQuote = reactive({
  client_name: '',
  client_email: '',
  client_phone: '',
  problem_description: '',
  diagnosis: '',
  estimated_parts_cost: 0,
  estimated_labor_cost: 0,
  estimated_total: 0,
  valid_until: defaultValidUntil()
})

function closeModal() {
  showNewQuoteModal.value = false
  resetForm()
}

function resetForm() {
  newQuote.client_name = ''
  newQuote.client_email = ''
  newQuote.client_phone = ''
  newQuote.problem_description = ''
  newQuote.diagnosis = ''
  newQuote.estimated_parts_cost = 0
  newQuote.estimated_labor_cost = 0
  newQuote.estimated_total = 0
  newQuote.valid_until = defaultValidUntil()
}

async function handleCreateQuote() {
  isCreating.value = true
  
  const result = await createQuote(newQuote)
  
  if (result.success) {
    closeModal()
  }
  
  isCreating.value = false
}
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

/* Modal styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: var(--cds-white);
  border-radius: var(--cds-radius-lg);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--cds-shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
}

.modal-header h2 {
  margin: 0;
  font-size: var(--cds-text-xl);
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--cds-text-muted);
  padding: 0.25rem;
}

.modal-close:hover {
  color: var(--cds-text-normal);
}

.modal-form {
  padding: 1.25rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-group.full {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: var(--cds-text-sm);
  font-weight: 500;
  color: var(--cds-text-normal);
}

.form-group input,
.form-group textarea {
  min-height: 44px;
  padding: 0.65rem 0.9rem;
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  border-radius: var(--cds-radius-sm);
  font-size: var(--cds-text-base);
  font-family: inherit;
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--cds-primary);
  box-shadow: var(--cds-focus-ring);
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .modal-actions button {
    width: 100%;
  }
}
</style>
