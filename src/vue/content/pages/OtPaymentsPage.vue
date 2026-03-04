<template>
  <div class="ot-payments-page">
    <div class="ot-payments-container">
      <header class="page-header">
        <div>
          <h1>Pagos y solicitudes</h1>
          <p>Solicitudes de compra asociadas a tus órdenes de trabajo y a la tienda</p>
        </div>
        <div class="header-actions">
          <button
            class="btn btn-outline-primary btn-sm"
            data-testid="ot-payments-refresh"
            :disabled="loading"
            @click="loadRequests"
          >
            {{ loading ? 'Actualizando...' : 'Actualizar' }}
          </button>
          <router-link to="/dashboard" class="btn btn-outline-secondary btn-sm">
            Volver al panel
          </router-link>
        </div>
      </header>

      <div v-if="error" class="alert alert-warning" data-testid="ot-payments-error">{{ error }}</div>

      <section v-if="requests.length > 0" class="requests-list">
        <article
          v-for="request in requests"
          :key="request.id"
          class="request-card"
          data-testid="ot-payment-row"
        >
          <header class="request-head">
            <div>
              <h2>Solicitud #{{ request.id }}</h2>
              <p class="request-subtitle">{{ request.repair_code || request.repair_number ? `OT: ${request.repair_code || request.repair_number}` : 'TIENDA / SIN_OT' }}</p>
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
              <a
                :href="toApiPath(request.latest_payment.proof_path)"
                target="_blank"
                rel="noopener"
                data-testid="ot-payment-proof-link"
              >
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
                data-testid="ot-payment-amount"
                placeholder="Monto depositado (CLP)"
              />
              <input
                v-model="forms[request.id].deposit_reference"
                type="text"
                class="form-control form-control-sm"
                data-testid="ot-payment-reference"
                placeholder="Referencia de transferencia"
              />
            </div>
            <textarea
              v-model="forms[request.id].client_notes"
              class="form-control form-control-sm"
              data-testid="ot-payment-notes"
              rows="2"
              placeholder="Notas para administración"
            />
            <input
              type="file"
              class="form-control form-control-sm"
              data-testid="ot-payment-file"
              accept="image/*"
              @change="onFileSelected(request.id, $event)"
            />
            <button
              class="btn btn-sm btn-primary"
              data-testid="ot-payment-submit"
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

      <section v-else class="empty-state" data-testid="ot-payments-empty">
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
@use "@/scss/_core.scss" as *;

.ot-payments-page {
  min-height: 100vh;
  padding: clamp(1rem, 3vw, 2rem);
  background:
    radial-gradient(circle at top right, color-mix(in srgb, var(--color-primary) 14%, transparent) 0, transparent 30%),
    linear-gradient(180deg, #f6f2ea 0%, #ece5d8 100%);
}

.ot-payments-container {
  width: min(100%, 1200px);
  margin: 0 auto;
  display: grid;
  gap: var(--spacer-md);
}

.page-header,
.header-actions,
.request-head {
  display: flex;
  gap: var(--spacer-sm);
  flex-wrap: wrap;
}

.page-header,
.request-head {
  align-items: center;
  justify-content: space-between;
}

.page-header,
.request-card,
.alert,
.empty-state {
  padding: var(--spacer-md);
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(211, 208, 195, 0.8);
  border-radius: 22px;
  box-shadow: var(--shadow-sm);
}

.page-header h1,
.request-head h2 {
  margin: 0;
  color: var(--color-dark);
  font-weight: 700;
}

.page-header h1 {
  font-size: clamp(1.8rem, 4vw, 2.6rem);
}

.page-header p,
.request-subtitle,
.request-note,
.proof-readonly,
.meta-label {
  margin: 0;
  color: var(--color-dark);
  opacity: 0.75;
  font-size: var(--text-sm);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0.65rem 0.95rem;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
  text-decoration: none;
}

.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.btn:disabled {
  opacity: 0.6;
  cursor: wait;
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-white);
}

.btn-outline-primary {
  border-color: var(--color-primary);
  background: transparent;
  color: var(--color-primary);
}

.btn-outline-secondary {
  border-color: var(--color-dark);
  background: transparent;
  color: var(--color-dark);
}

.alert {
  color: var(--color-dark);
  background: color-mix(in srgb, var(--color-white) 86%, var(--color-warning) 14%);
}

.requests-list {
  display: grid;
  gap: var(--spacer-md);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-primary) 15%, var(--color-white) 85%);
  color: var(--color-dark);
  font-size: var(--text-xs);
  font-weight: 700;
  text-transform: uppercase;
}

.request-body,
.proof-form,
.proof-readonly {
  display: grid;
  gap: var(--spacer-sm);
  margin-top: var(--spacer-sm);
}

.meta-grid,
.form-grid {
  display: grid;
  gap: var(--spacer-sm);
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.meta-grid strong,
.admin-note strong {
  color: var(--color-dark);
}

.admin-note,
.proof-link {
  padding: 0.8rem 0.9rem;
  border-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--color-white) 90%, var(--color-light) 10%);
}

.proof-link a {
  color: var(--color-primary);
  font-weight: 700;
  text-decoration: none;
}

.proof-link a:hover {
  text-decoration: underline;
}

.form-control {
  width: 100%;
  min-height: 44px;
  padding: 0.75rem 0.85rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-sm);
  background: var(--color-white);
  color: var(--color-dark);
  font-size: var(--text-sm);
}

textarea.form-control {
  min-height: 96px;
  resize: vertical;
}

.proof-readonly small {
  color: var(--color-dark);
  opacity: 0.72;
}

.empty-state {
  min-height: 240px;
  display: grid;
  place-items: center;
  text-align: center;
  color: var(--color-dark);
}

@include media-breakpoint-down(md) {
  .page-header,
  .header-actions,
  .request-head {
    flex-direction: column;
    align-items: stretch;
  }

  .meta-grid,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .btn {
    width: 100%;
  }
}
</style>
