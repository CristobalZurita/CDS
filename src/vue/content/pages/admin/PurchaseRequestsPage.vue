<template>
  <AdminLayout title="Compras sugeridas" subtitle="Carrito interno por cliente/OT">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1 class="h4">Solicitudes de compra</h1>
      <div>
        <button class="btn btn-sm btn-success me-2" data-testid="purchase-requests-new" @click="showWizard = !showWizard">
          {{ showWizard ? 'Cerrar' : 'Nueva solicitud' }}
        </button>
        <button class="btn btn-sm btn-outline-secondary" data-testid="purchase-requests-refresh" @click="loadRequests">Actualizar</button>
      </div>
    </div>

    <div v-if="activeRepairFilter" class="alert alert-info d-flex flex-wrap justify-content-between align-items-center gap-2">
      <span>Filtro activo por OT ID: <strong>#{{ activeRepairFilter }}</strong></span>
      <button class="btn btn-sm btn-outline-secondary" data-testid="purchase-requests-clear-filter" @click="clearRepairFilter">Quitar filtro</button>
    </div>

    <div v-if="showWizard" class="card p-3 mb-3" data-testid="purchase-requests-wizard">
      <WizardPurchaseRequest @completed="onCompleted" />
    </div>

    <div v-if="error" class="alert alert-warning">{{ error }}</div>

    <div class="card p-3">
      <table class="table table-sm align-middle">
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
              <div><strong>{{ req.client_name || 'SIN_CLIENTE' }}</strong></div>
              <small class="text-muted">{{ req.repair_code || req.repair_number || 'SIN_OT' }}</small>
            </td>
            <td>
              <span class="badge text-bg-secondary">{{ req.status }}</span>
            </td>
            <td>{{ req.items_count || req.items?.length || 0 }}</td>
            <td>{{ formatCurrency(req.total_items_amount || req.requested_amount || 0) }}</td>
            <td>
              <div class="payment-box">
                <input
                  v-model.number="paymentDraft[req.id].amount"
                  type="number"
                  min="1"
                  class="form-control form-control-sm"
                  placeholder="Monto CLP"
                />
                <input
                  v-model.number="paymentDraft[req.id].dueDays"
                  type="number"
                  min="1"
                  max="30"
                  class="form-control form-control-sm"
                  placeholder="Días"
                />
                <input
                  v-model="paymentDraft[req.id].instruction"
                  type="text"
                  class="form-control form-control-sm"
                  placeholder="Instrucción depósito"
                />
                <button
                  class="btn btn-sm btn-outline-primary"
                  data-testid="purchase-request-request-payment"
                  :disabled="isBusy(req.id)"
                  @click="requestPayment(req)"
                >
                  {{ isBusy(req.id) ? 'Enviando...' : 'Solicitar pago' }}
                </button>
              </div>
            </td>
            <td>
              <div v-if="req.latest_payment">
                <div><strong>{{ req.latest_payment.status }}</strong></div>
                <small class="text-muted">
                  {{ formatCurrency(req.latest_payment.amount || req.requested_amount || 0) }}
                </small>
                <small v-if="req.latest_payment.deposit_reference" class="d-block text-muted">
                  Ref: {{ req.latest_payment.deposit_reference }}
                </small>
                <small v-if="req.latest_payment.proof_path" class="d-block">
                  <a :href="toApiPath(req.latest_payment.proof_path)" target="_blank" rel="noopener">
                    Ver comprobante
                  </a>
                </small>
              </div>
              <span v-else class="text-muted">Sin pago</span>
            </td>
            <td>
              <div class="actions-col">
                <button
                  class="btn btn-sm btn-success"
                  data-testid="purchase-request-confirm-payment"
                  :disabled="isBusy(req.id)"
                  @click="confirmPayment(req)"
                >
                  Confirmar pago
                </button>
                <select
                  class="form-select form-select-sm"
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
                  class="btn btn-sm btn-outline-danger"
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
            <td colspan="8" class="text-muted">Sin solicitudes registradas.</td>
          </tr>
        </tbody>
      </table>
    </div>
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
@use '@/scss/core' as *;

.payment-box {
  display: grid;
  gap: 0.35rem;
  min-width: 230px;
}

.actions-col {
  display: grid;
  gap: 0.35rem;
  min-width: 170px;
}
</style>
