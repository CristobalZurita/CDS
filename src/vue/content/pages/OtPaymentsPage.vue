<template>
  <div class="ot-payments-page">
    <div class="ot-payments-container">
      <header class="page-header">
        <div>
          <h1>Pagos OT</h1>
          <p>Solicitudes de compra asociadas a tus órdenes de trabajo</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-outline-primary btn-sm" :disabled="loading" @click="loadRequests">
            {{ loading ? 'Actualizando...' : 'Actualizar' }}
          </button>
          <router-link to="/dashboard" class="btn btn-outline-secondary btn-sm">
            Volver al panel
          </router-link>
        </div>
      </header>

      <div v-if="error" class="alert alert-warning">{{ error }}</div>

      <section v-if="requests.length > 0" class="requests-list">
        <article v-for="request in requests" :key="request.id" class="request-card">
          <header class="request-head">
            <div>
              <h2>Solicitud #{{ request.id }}</h2>
              <p class="request-subtitle">OT: {{ request.repair_number || 'SIN_OT' }}</p>
            </div>
            <span class="status-pill">{{ request.status }}</span>
          </header>

          <div class="request-body">
            <div class="meta-grid">
              <div>
                <span class="meta-label">Monto solicitado</span>
                <strong>{{ formatCurrency(request.requested_amount || request.total_items_amount || 0) }}</strong>
              </div>
              <div>
                <span class="meta-label">Vence</span>
                <strong>{{ formatDate(request.payment_due_date) }}</strong>
              </div>
              <div>
                <span class="meta-label">Items</span>
                <strong>{{ request.items_count || 0 }}</strong>
              </div>
            </div>

            <p v-if="request.notes" class="request-note">{{ request.notes }}</p>

            <div v-if="request.latest_payment?.admin_notes" class="admin-note">
              <strong>Indicaciones:</strong> {{ request.latest_payment.admin_notes }}
            </div>

            <div v-if="request.latest_payment?.proof_path" class="proof-link">
              <a :href="toApiPath(request.latest_payment.proof_path)" target="_blank" rel="noopener">
                Ver comprobante enviado
              </a>
            </div>
          </div>

          <div
            v-if="canSubmitProof(request.status)"
            class="proof-form"
          >
            <h3>Subir comprobante de depósito</h3>
            <div class="form-grid">
              <input
                v-model.number="forms[request.id].amount"
                type="number"
                min="1"
                class="form-control form-control-sm"
                placeholder="Monto depositado (CLP)"
              />
              <input
                v-model="forms[request.id].deposit_reference"
                type="text"
                class="form-control form-control-sm"
                placeholder="Referencia de transferencia"
              />
            </div>
            <textarea
              v-model="forms[request.id].client_notes"
              class="form-control form-control-sm"
              rows="2"
              placeholder="Notas para administración"
            />
            <input
              type="file"
              class="form-control form-control-sm"
              accept="image/*"
              @change="onFileSelected(request.id, $event)"
            />
            <button
              class="btn btn-sm btn-primary"
              :disabled="isBusy(request.id)"
              @click="submitProof(request)"
            >
              {{ isBusy(request.id) ? 'Enviando...' : 'Enviar comprobante' }}
            </button>
          </div>

          <div
            v-else
            class="proof-readonly"
          >
            <small>Estado actual: {{ request.status }}. Si necesitas ayuda, abre un ticket de soporte.</small>
          </div>
        </article>
      </section>

      <section v-else class="empty-state">
        <p>No tienes solicitudes de pago OT pendientes por ahora.</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '@/services/api'

const requests = ref([])
const loading = ref(false)
const error = ref('')
const busyIds = ref(new Set())
const forms = ref({})
const filesByRequest = ref({})

const isBusy = (requestId) => busyIds.value.has(Number(requestId))
const setBusy = (requestId, value) => {
  const id = Number(requestId)
  const next = new Set(busyIds.value)
  if (value) next.add(id)
  else next.delete(id)
  busyIds.value = next
}

const canSubmitProof = (status) => ['pending_payment', 'requested', 'proof_submitted'].includes(String(status || '').toLowerCase())

const ensureForm = (request) => {
  if (!forms.value[request.id]) {
    forms.value[request.id] = {
      amount: Number(request.requested_amount || request.total_items_amount || 0),
      deposit_reference: '',
      client_notes: ''
    }
  }
}

const toApiPath = (path) => {
  const value = String(path || '')
  if (!value) return '#'
  if (value.startsWith('http')) return value
  const base = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
  const host = base.includes('/api/') ? base.split('/api/')[0] : base
  return `${host}${value.startsWith('/') ? '' : '/'}${value}`
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

const formatDate = (value) => {
  if (!value) return 'SIN_FECHA'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'SIN_FECHA'
  return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium' }).format(date)
}

const onFileSelected = (requestId, event) => {
  const file = event?.target?.files?.[0] || null
  filesByRequest.value[requestId] = file
}

const uploadProofImage = async (file) => {
  if (!file) return null
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post('/uploads/images', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return res?.data?.path || null
}

const loadRequests = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get('/client/purchase-requests')
    requests.value = Array.isArray(res?.data) ? res.data : []
    requests.value.forEach(ensureForm)
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudieron cargar tus pagos OT'
    requests.value = []
  } finally {
    loading.value = false
  }
}

const submitProof = async (request) => {
  setBusy(request.id, true)
  error.value = ''
  try {
    ensureForm(request)
    const form = forms.value[request.id]
    const file = filesByRequest.value[request.id] || null
    const proofPath = await uploadProofImage(file)
    await api.post(`/client/purchase-requests/${request.id}/deposit-proof`, {
      amount: Number(form.amount || request.requested_amount || request.total_items_amount || 0),
      deposit_reference: form.deposit_reference || null,
      client_notes: form.client_notes || null,
      proof_path: proofPath || null,
      deposited_at: new Date().toISOString()
    })
    filesByRequest.value[request.id] = null
    forms.value[request.id].deposit_reference = ''
    forms.value[request.id].client_notes = ''
    await loadRequests()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudo enviar el comprobante'
  } finally {
    setBusy(request.id, false)
  }
}

loadRequests()
</script>

<style scoped lang="scss">
@import '@/scss/_core.scss';

.ot-payments-page {
  min-height: 100vh;
  background: $color-gray-50-legacy;
  padding: 1rem;
}

.ot-payments-container {
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  gap: 1rem;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.page-header h1 {
  margin: 0;
  font-size: 1.35rem;
}

.page-header p {
  margin: 0.2rem 0 0;
  color: $color-gray-600-legacy;
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.requests-list {
  display: grid;
  gap: 0.9rem;
}

.request-card {
  background: $color-white;
  border: 1px solid $color-gray-200-legacy;
  border-radius: 12px;
  padding: 0.95rem;
}

.request-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.request-head h2 {
  margin: 0;
  font-size: 1.02rem;
}

.request-subtitle {
  margin: 0.2rem 0 0;
  color: $color-gray-600-legacy;
  font-size: 0.85rem;
}

.status-pill {
  border-radius: 999px;
  background: $color-gray-200-legacy;
  padding: 0.2rem 0.55rem;
  font-size: 0.75rem;
  text-transform: uppercase;
}

.request-body {
  margin-top: 0.75rem;
  display: grid;
  gap: 0.6rem;
}

.meta-grid {
  display: grid;
  gap: 0.45rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.meta-label {
  display: block;
  font-size: 0.76rem;
  color: $color-gray-600-legacy;
}

.request-note,
.admin-note {
  margin: 0;
  font-size: 0.86rem;
}

.proof-link a {
  font-size: 0.82rem;
}

.proof-form {
  margin-top: 0.75rem;
  display: grid;
  gap: 0.45rem;
  border-top: 1px dashed $color-gray-300-legacy;
  padding-top: 0.75rem;
}

.proof-form h3 {
  margin: 0;
  font-size: 0.9rem;
}

.form-grid {
  display: grid;
  gap: 0.4rem;
}

.proof-readonly {
  margin-top: 0.65rem;
  color: $color-gray-600-legacy;
}

.empty-state {
  background: $color-white;
  border: 1px dashed $color-gray-300-legacy;
  border-radius: 12px;
  padding: 1.1rem;
  text-align: center;
  color: $color-gray-600-legacy;
}

@include media-breakpoint-up(md) {
  .ot-payments-page {
    padding: 1.25rem;
  }

  .page-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-end;
  }

  .meta-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
