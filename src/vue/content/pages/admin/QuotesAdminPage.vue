<template>
  <AdminLayout title="Cotizaciones" subtitle="Tablero OT por estado">
    <section class="quotes-board-page">
      <header class="board-toolbar">
        <div class="toolbar-left">
          <h2 class="toolbar-title">Cotizaciones</h2>
          <p class="toolbar-subtitle">Borrador, enviadas y cerradas en una sola vista</p>
        </div>
        <div class="toolbar-right">
          <input
            v-model="searchQuery"
            type="search"
            class="form-control form-control-sm"
            data-testid="quotes-search"
            placeholder="Buscar COT, cliente o problema..."
            @keyup.enter="loadBoard"
          />
          <select v-model="statusFilter" class="form-select form-select-sm" data-testid="quotes-status-filter" @change="loadBoard">
            <option value="">Todos los estados</option>
            <option v-for="option in statusOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
          <button class="btn btn-sm btn-outline-primary" data-testid="quotes-refresh" :disabled="loading" @click="loadBoard">
            {{ loading ? 'Actualizando...' : 'Actualizar' }}
          </button>
        </div>
      </header>

      <div class="board-summary" data-testid="quotes-summary">
        <span class="summary-pill">En tablero: {{ counts.total }}</span>
        <span class="summary-pill">Abiertas: {{ metrics.open_total }}</span>
        <span class="summary-pill">Pendientes: {{ metrics.pending }}</span>
        <span class="summary-pill">Enviadas: {{ metrics.sent }}</span>
        <span class="summary-pill">Aprobadas: {{ metrics.approved }}</span>
        <span class="summary-pill is-warning">Vencen &lt; 3 días: {{ metrics.expiring_3d }}</span>
        <span class="summary-pill is-danger">Vencidas: {{ metrics.expired_open }}</span>
      </div>

      <div class="send-controls">
        <div class="form-check">
          <input id="sendWhatsapp" v-model="sendWhatsapp" class="form-check-input" type="checkbox" />
          <label class="form-check-label" for="sendWhatsapp">Enviar también por WhatsApp</label>
        </div>
        <input
          v-model="customMessage"
          type="text"
          class="form-control form-control-sm"
          placeholder="Mensaje opcional para envío de cotización"
        />
      </div>

      <div v-if="error" class="alert alert-warning mt-2">{{ error }}</div>

      <div class="board-columns" data-testid="quotes-board">
        <article
          v-for="column in columnDefs"
          :key="column.key"
          class="board-column"
        >
          <header class="column-header">
            <h3>{{ column.label }}</h3>
            <span class="badge text-bg-secondary">{{ getColumnCount(column.key) }}</span>
          </header>

          <div class="column-body">
            <article
              v-for="quote in getColumnItems(column.key)"
              :key="quote.id"
              class="quote-card"
              data-testid="quote-card"
              :class="{ highlighted: highlightedQuoteId === quote.id }"
            >
              <div class="quote-card-head">
                <strong>{{ quote.quote_number || ('COT-' + quote.id) }}</strong>
                <span class="status-pill">{{ quote.status || 'pending' }}</span>
              </div>

              <div class="quote-meta">
                <div><span>Cliente:</span> {{ quote.client?.name || quote.client_name || 'SIN_DATO' }}</div>
                <div><span>Total:</span> {{ formatCurrency(quote.estimated_total) }}</div>
                <div><span>Validez:</span> {{ formatDate(quote.valid_until) }}</div>
                <div v-if="quote.linked_repair_id">
                  <span>OT:</span> {{ quote.linked_repair_number || ('OT-' + quote.linked_repair_id) }}
                </div>
              </div>

              <p class="quote-problem">{{ quote.problem_description || 'Sin descripción' }}</p>

              <div class="quote-actions">
                <button
                  v-if="quote.status === 'pending'"
                  class="btn btn-sm btn-primary"
                  data-testid="quote-send"
                  :disabled="isBusy(quote.id)"
                  @click="sendQuote(quote)"
                >
                  {{ isBusy(quote.id) ? 'Enviando...' : 'Enviar' }}
                </button>

                <button
                  v-if="quote.status === 'sent'"
                  class="btn btn-sm btn-success"
                  data-testid="quote-approve"
                  :disabled="isBusy(quote.id)"
                  @click="changeStatus(quote, 'approved')"
                >
                  Aprobar
                </button>

                <button
                  v-if="quote.status === 'sent'"
                  class="btn btn-sm btn-outline-danger"
                  data-testid="quote-deny"
                  :disabled="isBusy(quote.id)"
                  @click="changeStatus(quote, 'denied')"
                >
                  Rechazar
                </button>

                <button
                  v-if="quote.status === 'approved' && !quote.linked_repair_id"
                  class="btn btn-sm btn-outline-primary"
                  data-testid="quote-create-repair"
                  :disabled="isBusy(quote.id)"
                  @click="createRepairFromQuote(quote)"
                >
                  {{ isBusy(quote.id) ? 'Creando OT...' : 'Crear OT' }}
                </button>

                <button
                  v-if="quote.linked_repair_id"
                  class="btn btn-sm btn-outline-secondary"
                  data-testid="quote-open-repair"
                  @click="openRepair(quote.linked_repair_id)"
                >
                  Ver OT
                </button>

                <button
                  v-if="!quote.linked_repair_id"
                  class="btn btn-sm btn-outline-danger"
                  data-testid="quote-delete"
                  :disabled="isBusy(quote.id)"
                  @click="deleteQuote(quote)"
                >
                  Eliminar
                </button>
              </div>
            </article>

            <p v-if="getColumnItems(column.key).length === 0" class="column-empty">
              Sin cotizaciones en esta columna.
            </p>
          </div>
        </article>
      </div>
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
@use '@/scss/core' as *;

.quotes-board-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.board-toolbar {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.toolbar-title {
  margin: 0;
  font-size: 1.2rem;
}

.toolbar-subtitle {
  margin: 0.25rem 0 0;
  color: $color-gray-600-legacy;
  font-size: 0.9rem;
}

.toolbar-right {
  display: grid;
  gap: 0.5rem;
}

.board-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.summary-pill {
  border-radius: 999px;
  padding: 0.2rem 0.55rem;
  font-size: 0.78rem;
  background: $color-gray-100-legacy;
  color: $color-gray-800-legacy;
}

.summary-pill.is-warning {
  background: rgba($color-warning, 0.2);
}

.summary-pill.is-danger {
  background: rgba($color-danger, 0.18);
}

.send-controls {
  display: grid;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 1px solid $color-gray-200-legacy;
  border-radius: 10px;
  background: $color-gray-50-legacy;
}

.board-columns {
  display: grid;
  gap: 0.75rem;
}

.board-column {
  border: 1px solid $color-gray-200-legacy;
  border-radius: 12px;
  background: $color-white;
  min-height: 220px;
  display: flex;
  flex-direction: column;
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.75rem;
  border-bottom: 1px solid $color-gray-200-legacy;
}

.column-header h3 {
  margin: 0;
  font-size: 0.95rem;
}

.column-body {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.quote-card {
  border: 1px solid $color-gray-200-legacy;
  border-radius: 10px;
  padding: 0.65rem;
  background: $color-gray-25-legacy;
}

.quote-card.highlighted {
  border-color: $color-primary;
  box-shadow: 0 0 0 2px rgba($color-primary, 0.2);
}

.quote-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.status-pill {
  font-size: 0.75rem;
  text-transform: uppercase;
  background: $color-gray-200-legacy;
  border-radius: 999px;
  padding: 0.15rem 0.45rem;
}

.quote-meta {
  margin-top: 0.45rem;
  display: grid;
  gap: 0.25rem;
  font-size: 0.82rem;
  color: $color-gray-700-legacy;
}

.quote-meta span {
  font-weight: 600;
}

.quote-problem {
  margin: 0.55rem 0;
  font-size: 0.85rem;
  color: $color-gray-800-legacy;
}

.quote-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.column-empty {
  margin: 0.2rem 0;
  font-size: 0.85rem;
  color: $color-gray-500-legacy;
}

@include media-breakpoint-up(md) {
  .board-toolbar {
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-end;
  }

  .toolbar-right {
    width: min(460px, 100%);
  }

  .board-columns {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@include media-breakpoint-up(lg) {
  .board-columns {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
