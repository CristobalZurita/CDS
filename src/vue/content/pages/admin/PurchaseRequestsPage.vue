<template>
  <AdminLayout title="Compras sugeridas" subtitle="Carrito interno por cliente/OT">
    <section class="purchase-page">
      <header class="purchase-page__header">
        <h1 class="purchase-page__title">Solicitudes de compra</h1>

        <div class="purchase-page__actions">
          <button
            type="button"
            class="purchase-page__button purchase-page__button--success"
            data-testid="purchase-requests-new"
            @click="showWizard = !showWizard"
          >
            {{ showWizard ? 'Cerrar' : 'Nueva solicitud' }}
          </button>
          <button
            type="button"
            class="purchase-page__button purchase-page__button--secondary"
            data-testid="purchase-requests-refresh"
            @click="loadRequests"
          >
            Actualizar
          </button>
        </div>
      </header>

      <section v-if="activeRepairFilter" class="purchase-page__notice">
        <span>Filtro activo por OT ID: <strong>#{{ activeRepairFilter }}</strong></span>
        <button
          type="button"
          class="purchase-page__button purchase-page__button--secondary"
          data-testid="purchase-requests-clear-filter"
          @click="clearRepairFilter"
        >
          Quitar filtro
        </button>
      </section>

      <section v-if="showWizard" class="purchase-page__panel" data-testid="purchase-requests-wizard">
        <WizardPurchaseRequest @completed="onCompleted" />
      </section>

      <section v-if="error" class="purchase-page__alert">{{ error }}</section>

      <section class="purchase-page__panel">
        <div class="purchase-page__table-wrap">
          <table class="purchase-page__table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Cliente / OT</th>
                <th>Estado</th>
                <th>Items</th>
                <th>Total</th>
                <th>Cobro cliente</th>
                <th>Último pago</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="req in requests" :key="req.id" data-testid="purchase-request-row">
                <td>#{{ req.id }}</td>
                <td>
                  <div class="purchase-page__client-name">{{ req.client_name || 'SIN_CLIENTE' }}</div>
                  <span class="purchase-page__muted">{{ req.repair_code || req.repair_number || 'SIN_OT' }}</span>
                </td>
                <td>
                  <span class="purchase-page__badge">{{ req.status }}</span>
                </td>
                <td>{{ req.items_count || req.items?.length || 0 }}</td>
                <td>{{ formatCurrency(req.total_items_amount || req.requested_amount || 0) }}</td>
                <td>
                  <div class="purchase-page__payment-box">
                    <input
                      v-model.number="paymentDraft[req.id].amount"
                      type="number"
                      min="1"
                      class="purchase-page__input"
                      placeholder="Monto CLP"
                    />
                    <input
                      v-model.number="paymentDraft[req.id].dueDays"
                      type="number"
                      min="1"
                      max="30"
                      class="purchase-page__input"
                      placeholder="Días"
                    />
                    <input
                      v-model="paymentDraft[req.id].instruction"
                      type="text"
                      class="purchase-page__input"
                      placeholder="Instrucción depósito"
                    />
                    <button
                      type="button"
                      class="purchase-page__button purchase-page__button--primary"
                      data-testid="purchase-request-request-payment"
                      :disabled="isBusy(req.id)"
                      @click="requestPayment(req)"
                    >
                      {{ isBusy(req.id) ? 'Enviando...' : 'Solicitar pago' }}
                    </button>
                  </div>
                </td>
                <td>
                  <div v-if="req.latest_payment" class="purchase-page__payment-status">
                    <div class="purchase-page__client-name">{{ req.latest_payment.status }}</div>
                    <span class="purchase-page__muted">
                      {{ formatCurrency(req.latest_payment.amount || req.requested_amount || 0) }}
                    </span>
                    <span v-if="req.latest_payment.deposit_reference" class="purchase-page__muted">
                      Ref: {{ req.latest_payment.deposit_reference }}
                    </span>
                    <a
                      v-if="req.latest_payment.proof_path"
                      class="purchase-page__link"
                      :href="toApiPath(req.latest_payment.proof_path)"
                      target="_blank"
                      rel="noopener"
                    >
                      Ver comprobante
                    </a>
                  </div>
                  <span v-else class="purchase-page__muted">Sin pago</span>
                </td>
                <td>
                  <div class="purchase-page__row-actions">
                    <button
                      type="button"
                      class="purchase-page__button purchase-page__button--success"
                      data-testid="purchase-request-confirm-payment"
                      :disabled="isBusy(req.id)"
                      @click="confirmPayment(req)"
                    >
                      Confirmar pago
                    </button>
                    <select
                      class="purchase-page__select"
                      data-testid="purchase-request-status-select"
                      :disabled="isBusy(req.id)"
                      :value="req.status"
                      @change="setStatus(req, $event.target.value)"
                    >
                      <option v-for="status in statusOptions" :key="status" :value="status">
                        {{ status }}
                      </option>
                    </select>
                    <button
                      type="button"
                      class="purchase-page__button purchase-page__button--danger"
                      data-testid="purchase-request-delete"
                      :disabled="isBusy(req.id)"
                      @click="deleteRequest(req)"
                    >
                      Eliminar
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="requests.length === 0">
                <td colspan="8" class="purchase-page__empty">Sin solicitudes registradas.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>
  </AdminLayout>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/services/api'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'
import WizardPurchaseRequest from '@/vue/components/admin/wizard/WizardPurchaseRequest.vue'

const route = useRoute()
const router = useRouter()
const requests = ref([])
const showWizard = ref(false)
const error = ref('')
const busyIds = ref(new Set())
const paymentDraft = ref({})
const activeRepairFilter = computed(() => {
  const raw = route.query?.repair_id
  const value = Number(raw)
  return Number.isFinite(value) && value > 0 ? value : null
})

const statusOptions = [
  'draft',
  'suggested',
  'approved',
  'requested',
  'pending_payment',
  'proof_submitted',
  'paid_client',
  'purchased_admin',
  'received',
  'applied_ot',
  'cancelled'
]

const isBusy = (requestId) => busyIds.value.has(Number(requestId))
const setBusy = (requestId, value) => {
  const id = Number(requestId)
  const next = new Set(busyIds.value)
  if (value) next.add(id)
  else next.delete(id)
  busyIds.value = next
}

const ensureDraft = (req) => {
  if (!paymentDraft.value[req.id]) {
    paymentDraft.value[req.id] = {
      amount: Math.max(1, Number(req.requested_amount || req.total_items_amount || 1)),
      dueDays: 3,
      instruction: 'Deposita el monto solicitado y sube comprobante en tu panel.'
    }
  }
}

const formatCurrency = (value) => {
  const amount = Number(value || 0)
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

const toApiPath = (path) => {
  const value = String(path || '')
  if (!value) return '#'
  if (value.startsWith('http')) return value
  const base = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
  const host = base.includes('/api/') ? base.split('/api/')[0] : base
  return `${host}${value.startsWith('/') ? '' : '/'}${value}`
}

const loadRequests = async () => {
  error.value = ''
  try {
    const params = {}
    if (activeRepairFilter.value) params.repair_id = activeRepairFilter.value
    const res = await api.get('/purchase-requests/board', { params })
    const list = res?.data?.requests || []
    requests.value = Array.isArray(list) ? list : []
    requests.value.forEach(ensureDraft)
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudieron cargar las solicitudes de compra'
    requests.value = []
  }
}

const requestPayment = async (req) => {
  setBusy(req.id, true)
  error.value = ''
  try {
    ensureDraft(req)
    const draft = paymentDraft.value[req.id]
    await api.post(`/purchase-requests/${req.id}/request-payment`, {
      amount: Number(draft.amount || req.requested_amount || req.total_items_amount || 1),
      due_days: Number(draft.dueDays || 3),
      instruction: draft.instruction || null
    })
    await loadRequests()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudo solicitar pago al cliente'
  } finally {
    setBusy(req.id, false)
  }
}

const confirmPayment = async (req) => {
  setBusy(req.id, true)
  error.value = ''
  try {
    await api.post(`/purchase-requests/${req.id}/confirm-payment`, {
      admin_notes: 'Pago validado por administración'
    })
    await loadRequests()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudo confirmar el pago'
  } finally {
    setBusy(req.id, false)
  }
}

const setStatus = async (req, status) => {
  setBusy(req.id, true)
  error.value = ''
  try {
    await api.patch(`/purchase-requests/${req.id}`, { status })
    await loadRequests()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudo actualizar estado'
  } finally {
    setBusy(req.id, false)
  }
}

const onCompleted = () => {
  showWizard.value = false
  loadRequests()
}

const deleteRequest = async (req) => {
  if (!confirm(`¿Eliminar la solicitud #${req.id}?`)) return
  setBusy(req.id, true)
  error.value = ''
  try {
    await api.delete(`/purchase-requests/${req.id}`)
    await loadRequests()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudo eliminar la solicitud'
  } finally {
    setBusy(req.id, false)
  }
}

const clearRepairFilter = async () => {
  const nextQuery = { ...route.query }
  delete nextQuery.repair_id
  await router.replace({ name: 'admin-purchase-requests', query: nextQuery })
}

watch(
  () => route.query?.repair_id,
  () => {
    loadRequests()
  }
)

onMounted(loadRequests)
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.purchase-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
}

.purchase-page__header,
.purchase-page__actions,
.purchase-page__notice,
.purchase-page__row-actions {
  display: flex;
  gap: var(--spacer-sm);
  flex-wrap: wrap;
}

.purchase-page__header,
.purchase-page__notice {
  align-items: center;
  justify-content: space-between;
}

.purchase-page__title {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--text-xl);
  font-weight: 700;
}

.purchase-page__panel,
.purchase-page__notice,
.purchase-page__alert {
  padding: var(--spacer-md);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.purchase-page__notice {
  background: color-mix(in srgb, var(--color-white) 85%, var(--color-info) 15%);
}

.purchase-page__alert {
  color: var(--color-dark);
  background: color-mix(in srgb, var(--color-white) 86%, var(--color-warning) 14%);
}

.purchase-page__table-wrap {
  width: 100%;
  overflow-x: auto;
}

.purchase-page__table {
  width: 100%;
  border-collapse: collapse;
}

.purchase-page__table th,
.purchase-page__table td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-light);
  text-align: left;
  vertical-align: top;
  color: var(--color-dark);
  font-size: var(--text-sm);
}

.purchase-page__table th {
  font-weight: 700;
}

.purchase-page__client-name {
  font-weight: 700;
  color: var(--color-dark);
}

.purchase-page__muted,
.purchase-page__empty {
  color: var(--color-dark);
  opacity: 0.72;
}

.purchase-page__badge {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-dark) 15%, var(--color-white) 85%);
  color: var(--color-dark);
  font-size: var(--text-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.purchase-page__payment-box,
.purchase-page__payment-status {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.purchase-page__input,
.purchase-page__select {
  width: 100%;
  min-height: 40px;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-sm);
  background: var(--color-white);
  color: var(--color-dark);
  font-size: var(--text-sm);
}

.purchase-page__button {
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

.purchase-page__button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.purchase-page__button:disabled {
  opacity: 0.6;
  cursor: wait;
}

.purchase-page__button--primary,
.purchase-page__button--success {
  background: var(--color-primary);
}

.purchase-page__button--secondary {
  background: var(--color-dark);
}

.purchase-page__button--danger {
  background: var(--color-danger);
}

.purchase-page__link {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
}

.purchase-page__link:hover {
  text-decoration: underline;
}

@include media-breakpoint-down(md) {
  .purchase-page__header,
  .purchase-page__actions,
  .purchase-page__notice,
  .purchase-page__row-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .purchase-page__button {
    width: 100%;
  }
}
</style>
