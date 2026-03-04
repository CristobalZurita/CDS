<template>
  <AdminLayout title="Cotizaciones" subtitle="Tablero OT por estado">
    <section class="quotes-board-page">
      <header class="quotes-board-page__toolbar">
        <div class="quotes-board-page__toolbar-copy">
          <h1 class="quotes-board-page__title">Cotizaciones</h1>
          <p class="quotes-board-page__subtitle">Borrador, enviadas y cerradas en una sola vista</p>
        </div>

        <div class="quotes-board-page__toolbar-actions">
          <input
            v-model="searchQuery"
            type="search"
            class="quotes-board-page__input"
            data-testid="quotes-search"
            placeholder="Buscar COT, cliente o problema..."
            @keyup.enter="loadBoard"
          />
          <select
            v-model="statusFilter"
            class="quotes-board-page__select"
            data-testid="quotes-status-filter"
            @change="loadBoard"
          >
            <option value="">Todos los estados</option>
            <option v-for="option in statusOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
          <button
            type="button"
            class="quotes-board-page__button quotes-board-page__button--secondary"
            data-testid="quotes-refresh"
            :disabled="loading"
            @click="loadBoard"
          >
            {{ loading ? 'Actualizando...' : 'Actualizar' }}
          </button>
        </div>
      </header>

      <section class="quotes-board-page__summary" data-testid="quotes-summary">
        <span class="quotes-board-page__pill">En tablero: {{ counts.total }}</span>
        <span class="quotes-board-page__pill">Abiertas: {{ metrics.open_total }}</span>
        <span class="quotes-board-page__pill">Pendientes: {{ metrics.pending }}</span>
        <span class="quotes-board-page__pill">Enviadas: {{ metrics.sent }}</span>
        <span class="quotes-board-page__pill">Aprobadas: {{ metrics.approved }}</span>
        <span class="quotes-board-page__pill quotes-board-page__pill--warning">Vencen &lt; 3 días: {{ metrics.expiring_3d }}</span>
        <span class="quotes-board-page__pill quotes-board-page__pill--danger">Vencidas: {{ metrics.expired_open }}</span>
      </section>

      <section class="quotes-board-page__send-controls">
        <label class="quotes-board-page__checkbox" for="sendWhatsapp">
          <input id="sendWhatsapp" v-model="sendWhatsapp" class="quotes-board-page__checkbox-input" type="checkbox" />
          <span>Enviar también por WhatsApp</span>
        </label>
        <input
          v-model="customMessage"
          type="text"
          class="quotes-board-page__input"
          placeholder="Mensaje opcional para envío de cotización"
        />
      </section>

      <section v-if="error" class="quotes-board-page__alert">{{ error }}</section>

      <section class="quotes-board-page__columns" data-testid="quotes-board">
        <article
          v-for="column in columnDefs"
          :key="column.key"
          class="quotes-board-page__column"
        >
          <header class="quotes-board-page__column-header">
            <h2 class="quotes-board-page__column-title">{{ column.label }}</h2>
            <span class="quotes-board-page__badge">{{ getColumnCount(column.key) }}</span>
          </header>

          <div class="quotes-board-page__column-body">
            <article
              v-for="quote in getColumnItems(column.key)"
              :key="quote.id"
              class="quotes-board-page__card"
              data-testid="quote-card"
              :class="{ 'quotes-board-page__card--highlighted': highlightedQuoteId === quote.id }"
            >
              <div class="quotes-board-page__card-head">
                <strong>{{ quote.quote_number || ('COT-' + quote.id) }}</strong>
                <span class="quotes-board-page__status-pill">{{ quote.status || 'pending' }}</span>
              </div>

              <div class="quotes-board-page__meta">
                <div><span>Cliente:</span> {{ quote.client?.name || quote.client_name || 'SIN_DATO' }}</div>
                <div><span>Total:</span> {{ formatCurrency(quote.estimated_total) }}</div>
                <div><span>Validez:</span> {{ formatDate(quote.valid_until) }}</div>
                <div v-if="quote.linked_repair_id">
                  <span>OT:</span> {{ quote.linked_repair_number || ('OT-' + quote.linked_repair_id) }}
                </div>
              </div>

              <p class="quotes-board-page__problem">{{ quote.problem_description || 'Sin descripción' }}</p>

              <div class="quotes-board-page__card-actions">
                <button
                  v-if="quote.status === 'pending'"
                  type="button"
                  class="quotes-board-page__button quotes-board-page__button--primary"
                  data-testid="quote-send"
                  :disabled="isBusy(quote.id)"
                  @click="sendQuote(quote)"
                >
                  {{ isBusy(quote.id) ? 'Enviando...' : 'Enviar' }}
                </button>

                <button
                  v-if="quote.status === 'sent'"
                  type="button"
                  class="quotes-board-page__button quotes-board-page__button--success"
                  data-testid="quote-approve"
                  :disabled="isBusy(quote.id)"
                  @click="changeStatus(quote, 'approved')"
                >
                  Aprobar
                </button>

                <button
                  v-if="quote.status === 'sent'"
                  type="button"
                  class="quotes-board-page__button quotes-board-page__button--danger"
                  data-testid="quote-deny"
                  :disabled="isBusy(quote.id)"
                  @click="changeStatus(quote, 'denied')"
                >
                  Rechazar
                </button>

                <button
                  v-if="quote.status === 'approved' && !quote.linked_repair_id"
                  type="button"
                  class="quotes-board-page__button quotes-board-page__button--secondary"
                  data-testid="quote-create-repair"
                  :disabled="isBusy(quote.id)"
                  @click="createRepairFromQuote(quote)"
                >
                  {{ isBusy(quote.id) ? 'Creando OT...' : 'Crear OT' }}
                </button>

                <button
                  v-if="quote.linked_repair_id"
                  type="button"
                  class="quotes-board-page__button quotes-board-page__button--ghost"
                  data-testid="quote-open-repair"
                  @click="openRepair(quote.linked_repair_id)"
                >
                  Ver OT
                </button>

                <button
                  v-if="!quote.linked_repair_id"
                  type="button"
                  class="quotes-board-page__button quotes-board-page__button--danger"
                  data-testid="quote-delete"
                  :disabled="isBusy(quote.id)"
                  @click="deleteQuote(quote)"
                >
                  Eliminar
                </button>
              </div>
            </article>

            <p v-if="getColumnItems(column.key).length === 0" class="quotes-board-page__empty">
              Sin cotizaciones en esta columna.
            </p>
          </div>
        </article>
      </section>
    </section>
  </AdminLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/services/api'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const statusFilter = ref('')
const customMessage = ref('')
const sendWhatsapp = ref(true)
const busyIds = ref(new Set())

const statusOptions = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'sent', label: 'Enviada' },
  { value: 'approved', label: 'Aprobada' },
  { value: 'denied', label: 'Rechazada' },
  { value: 'canceled', label: 'Cancelada' }
]

const board = ref({
  draft_pending: [],
  waiting_response: [],
  closed: []
})
const counts = ref({
  draft_pending: 0,
  waiting_response: 0,
  closed: 0,
  total: 0
})
const metrics = ref({
  pending: 0,
  sent: 0,
  approved: 0,
  denied: 0,
  canceled: 0,
  expired_open: 0,
  expiring_3d: 0,
  open_total: 0
})

const columnDefs = [
  { key: 'draft_pending', label: 'Borrador / Pendiente' },
  { key: 'waiting_response', label: 'En espera de respuesta' },
  { key: 'closed', label: 'Cerradas' }
]

const highlightedQuoteId = computed(() => {
  const value = Number(route.query.quote_id || 0)
  return Number.isFinite(value) && value > 0 ? value : null
})

const isBusy = (quoteId) => busyIds.value.has(Number(quoteId))

const setBusy = (quoteId, value) => {
  const id = Number(quoteId)
  const next = new Set(busyIds.value)
  if (value) next.add(id)
  else next.delete(id)
  busyIds.value = next
}

const toPayload = (res) => {
  if (!res) return {}
  if (res.data?.data) return res.data.data
  if (res.data) return res.data
  return res
}

const normalizeBoard = (payload) => {
  const incoming = payload?.board || {}
  return {
    draft_pending: Array.isArray(incoming.draft_pending) ? incoming.draft_pending : [],
    waiting_response: Array.isArray(incoming.waiting_response) ? incoming.waiting_response : [],
    closed: Array.isArray(incoming.closed) ? incoming.closed : []
  }
}

const normalizeCounts = (payload) => {
  const incoming = payload?.counts || {}
  return {
    draft_pending: Number(incoming.draft_pending || 0),
    waiting_response: Number(incoming.waiting_response || 0),
    closed: Number(incoming.closed || 0),
    total: Number(incoming.total || 0)
  }
}

const normalizeMetrics = (payload) => {
  const incoming = payload?.metrics || {}
  return {
    pending: Number(incoming.pending || 0),
    sent: Number(incoming.sent || 0),
    approved: Number(incoming.approved || 0),
    denied: Number(incoming.denied || 0),
    canceled: Number(incoming.canceled || 0),
    expired_open: Number(incoming.expired_open || 0),
    expiring_3d: Number(incoming.expiring_3d || 0),
    open_total: Number(incoming.open_total || 0)
  }
}

const filterByQuery = (items) => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return items
  return items.filter((quote) => {
    const text = [
      quote.quote_number,
      quote.client?.name,
      quote.client_name,
      quote.problem_description,
      quote.status
    ].filter(Boolean).join(' ').toLowerCase()
    return text.includes(q)
  })
}

const getColumnItems = (key) => filterByQuery(board.value[key] || [])

const getColumnCount = (key) => getColumnItems(key).length

const formatCurrency = (value) => {
  const amount = Number(value || 0)
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

const formatDate = (value) => {
  if (!value) return 'SIN_DATO'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'SIN_DATO'
  return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium' }).format(date)
}

const loadBoard = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = { limit: 300 }
    const q = searchQuery.value.trim()
    if (q) {
      params.q = q
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    const res = await api.get('/diagnostic/quotes/board', { params })
    const payload = toPayload(res)
    board.value = normalizeBoard(payload)
    counts.value = normalizeCounts(payload)
    metrics.value = normalizeMetrics(payload)
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudo cargar el tablero de cotizaciones'
  } finally {
    loading.value = false
  }
}

const sendQuote = async (quote) => {
  setBusy(quote.id, true)
  try {
    await api.post(`/diagnostic/quotes/${quote.id}/send`, {
      send_whatsapp: sendWhatsapp.value,
      message: customMessage.value || null
    })
    await loadBoard()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudo enviar la cotización'
  } finally {
    setBusy(quote.id, false)
  }
}

const changeStatus = async (quote, status) => {
  setBusy(quote.id, true)
  try {
    await api.post(`/diagnostic/quotes/${quote.id}/status`, {
      status,
      client_response: status === 'approved'
        ? 'Aprobada por administración'
        : 'Rechazada por administración'
    })
    await loadBoard()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudo actualizar estado de cotización'
  } finally {
    setBusy(quote.id, false)
  }
}

const createRepairFromQuote = async (quote) => {
  if (!quote?.id || !quote?.client_id) {
    error.value = 'No se pudo crear OT: faltan datos de cliente o cotización'
    return
  }

  setBusy(quote.id, true)
  try {
    const payload = {
      client_id: quote.client_id,
      quote_id: quote.id,
      title: quote.quote_number ? `OT ${quote.quote_number}` : `OT ${quote.id}`,
      description: quote.problem_description || 'Sin descripción',
      model: quote.device_model || quote.device?.model || quote.client?.name || 'SIN_MODELO',
      diagnosis: quote.diagnosis || null,
      parts_cost: Number(quote.estimated_parts_cost || 0),
      labor_cost: Number(quote.estimated_labor_cost || 0),
      total_cost: Number(quote.estimated_total || 0)
    }
    const res = await api.post('/repairs', payload)
    const repairId = Number(res?.data?.id || 0)
    await loadBoard()
    if (repairId > 0) {
      router.push(`/admin/repairs/${repairId}`)
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudo crear la OT desde esta cotización'
  } finally {
    setBusy(quote.id, false)
  }
}

const openRepair = (repairId) => {
  const id = Number(repairId || 0)
  if (id > 0) {
    router.push(`/admin/repairs/${id}`)
  }
}

const deleteQuote = async (quote) => {
  if (!quote?.id) return
  if (!confirm(`¿Eliminar la cotización ${quote.quote_number || quote.id}?`)) return

  setBusy(quote.id, true)
  try {
    await api.delete(`/diagnostic/quotes/${quote.id}`)
    await loadBoard()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudo eliminar la cotización'
  } finally {
    setBusy(quote.id, false)
  }
}

onMounted(loadBoard)
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.quotes-board-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
}

.quotes-board-page__toolbar,
.quotes-board-page__toolbar-actions,
.quotes-board-page__summary,
.quotes-board-page__card-actions {
  display: flex;
  gap: var(--spacer-sm);
  flex-wrap: wrap;
}

.quotes-board-page__toolbar {
  align-items: center;
  justify-content: space-between;
}

.quotes-board-page__toolbar-copy {
  display: grid;
  gap: 0.35rem;
}

.quotes-board-page__title {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--text-xl);
  font-weight: 700;
}

.quotes-board-page__subtitle {
  margin: 0;
  color: var(--color-dark);
  opacity: 0.72;
  font-size: var(--text-sm);
}

.quotes-board-page__input,
.quotes-board-page__select {
  min-height: 42px;
  padding: 0.7rem 0.85rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-sm);
  background: var(--color-white);
  color: var(--color-dark);
  font-size: var(--text-sm);
}

.quotes-board-page__input {
  min-width: 260px;
}

.quotes-board-page__select {
  min-width: 220px;
}

.quotes-board-page__button {
  min-height: 40px;
  padding: 0.65rem 0.95rem;
  border: 0;
  border-radius: var(--radius-sm);
  color: var(--color-white);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
}

.quotes-board-page__button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.quotes-board-page__button:disabled {
  opacity: 0.6;
  cursor: wait;
}

.quotes-board-page__button--primary,
.quotes-board-page__button--success {
  background: var(--color-primary);
}

.quotes-board-page__button--secondary {
  background: var(--color-dark);
}

.quotes-board-page__button--ghost {
  background: var(--color-light);
  color: var(--color-dark);
}

.quotes-board-page__button--danger {
  background: var(--color-danger);
}

.quotes-board-page__summary,
.quotes-board-page__send-controls,
.quotes-board-page__alert {
  padding: var(--spacer-md);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.quotes-board-page__send-controls {
  display: grid;
  gap: var(--spacer-sm);
}

.quotes-board-page__pill {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-white) 82%, var(--color-light) 18%);
  color: var(--color-dark);
  font-size: var(--text-xs);
  font-weight: 700;
}

.quotes-board-page__pill--warning {
  background: var(--color-warning);
}

.quotes-board-page__pill--danger {
  background: var(--color-danger);
  color: var(--color-white);
}

.quotes-board-page__checkbox {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  color: var(--color-dark);
  font-size: var(--text-sm);
  font-weight: 600;
}

.quotes-board-page__checkbox-input {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
}

.quotes-board-page__alert {
  color: var(--color-dark);
  background: color-mix(in srgb, var(--color-white) 86%, var(--color-warning) 14%);
}

.quotes-board-page__columns {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--spacer-md);
  align-items: start;
}

.quotes-board-page__column {
  min-width: 0;
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.quotes-board-page__column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacer-sm);
  padding: var(--spacer-md);
  border-bottom: 1px solid var(--color-light);
}

.quotes-board-page__column-title {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--text-lg);
  font-weight: 700;
}

.quotes-board-page__badge {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  background: var(--color-dark);
  color: var(--color-white);
  font-size: var(--text-xs);
  font-weight: 700;
}

.quotes-board-page__column-body {
  display: grid;
  gap: var(--spacer-sm);
  padding: var(--spacer-md);
}

.quotes-board-page__card {
  padding: 0.9rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--color-white) 92%, var(--color-light) 8%);
  transition: var(--transition-base);
}

.quotes-board-page__card--highlighted {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-primary) 18%, transparent);
}

.quotes-board-page__card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  color: var(--color-dark);
}

.quotes-board-page__status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-primary) 16%, var(--color-white) 84%);
  color: var(--color-dark);
  font-size: var(--text-xs);
  font-weight: 700;
  text-transform: uppercase;
}

.quotes-board-page__meta {
  display: grid;
  gap: 0.35rem;
  color: var(--color-dark);
  font-size: var(--text-sm);
}

.quotes-board-page__meta span {
  font-weight: 700;
}

.quotes-board-page__problem {
  margin: 0.85rem 0 0;
  color: var(--color-dark);
  font-size: var(--text-sm);
  line-height: 1.55;
}

.quotes-board-page__card-actions {
  margin-top: var(--spacer-md);
}

.quotes-board-page__empty {
  margin: 0;
  color: var(--color-dark);
  opacity: 0.68;
  font-size: var(--text-sm);
}

@include media-breakpoint-down(xl) {
  .quotes-board-page__columns {
    grid-template-columns: 1fr;
  }
}

@include media-breakpoint-down(md) {
  .quotes-board-page__toolbar,
  .quotes-board-page__toolbar-actions,
  .quotes-board-page__card-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .quotes-board-page__input,
  .quotes-board-page__select,
  .quotes-board-page__button {
    width: 100%;
    min-width: 0;
  }
}
</style>
