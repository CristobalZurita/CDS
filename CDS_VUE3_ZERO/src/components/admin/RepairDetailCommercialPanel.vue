<template>
  <section class="panel-card">
    <h2>Garantia y comprobante</h2>

    <div class="detail-grid commercial-grid">
      <article class="panel-nested commercial-card">
        <div class="panel-head">
          <h3>Garantia</h3>
          <div class="action-grid">
            <button
              v-if="canCreateWarranty"
              class="btn-secondary"
              :disabled="performingAction"
              @click="emit('create-warranty')"
            >
              Crear garantia
            </button>
            <button
              v-if="canSubmitWarrantyClaim"
              class="btn-secondary"
              :disabled="performingAction"
              @click="emit('toggle-claim-form')"
            >
              {{ showClaimForm ? 'Cerrar reclamo' : 'Registrar reclamo' }}
            </button>
          </div>
        </div>

        <template v-if="warranty">
          <p><strong>Tipo:</strong> {{ formatWarrantyType(warranty.warranty_type) }}</p>
          <p><strong>Estado:</strong> <span :class="resolveWarrantyStatusClass(warranty.status)">{{ formatWarrantyStatus(warranty.status) }}</span></p>
          <p><strong>Inicio:</strong> {{ formatDate(warranty.start_date) }}</p>
          <p><strong>Fin:</strong> {{ formatDate(warranty.end_date) }}</p>
          <p><strong>Reclamos:</strong> {{ warranty.claims_used }} / {{ warranty.max_claims }}</p>

          <div class="commercial-subsection">
            <h4>Historial de reclamos</h4>
            <div v-if="showClaimForm" class="commercial-form">
              <label>
                Problema reportado
                <textarea
                  class="admin-textarea"
                  rows="3"
                  :value="claimProblemDescription"
                  :disabled="performingAction"
                  @input="emit('update-claim-field', { field: 'problemDescription', value: $event.target.value })"
                ></textarea>
              </label>
              <label>
                Tipo de falla
                <input
                  class="admin-input"
                  type="text"
                  :value="claimFaultType"
                  :disabled="performingAction"
                  @input="emit('update-claim-field', { field: 'faultType', value: $event.target.value })"
                >
              </label>
              <div class="field-actions">
                <button
                  class="btn-primary"
                  :disabled="performingAction"
                  @click="emit('submit-warranty-claim')"
                >
                  Guardar reclamo
                </button>
              </div>
            </div>
            <div v-if="claims.length" class="commercial-list">
              <article
                v-for="claim in claims"
                :key="claim.id || claim.claim_number"
                class="commercial-entry"
              >
                <header>
                  <strong>{{ claim.claim_number || `Reclamo #${claim.id}` }}</strong>
                  <span :class="resolveClaimStatusClass(claim.status)">{{ formatClaimStatus(claim.status) }}</span>
                </header>
                <p>{{ claim.problem_description || 'Sin descripcion' }}</p>
                <div class="commercial-meta">
                  <span v-if="claim.fault_type">Falla: {{ claim.fault_type }}</span>
                  <span v-if="claim.submitted_at">Ingreso: {{ formatDate(claim.submitted_at) }}</span>
                  <span v-if="claim.resolved_at">Cierre: {{ formatDate(claim.resolved_at) }}</span>
                </div>
              </article>
            </div>
            <p v-else class="empty-state compact-empty">Sin reclamos registrados.</p>
          </div>
        </template>
        <p v-else class="empty-state">No hay garantia registrada para esta OT.</p>
      </article>

      <article class="panel-nested commercial-card">
        <div class="panel-head">
          <h3>Comprobante</h3>
          <div class="action-grid">
            <button
              v-if="canCreateInvoice"
              class="btn-secondary"
              :disabled="performingAction"
              @click="emit('create-invoice')"
            >
              Generar comprobante
            </button>
            <button
              v-if="canRecordInvoicePayment"
              class="btn-secondary"
              :disabled="performingAction"
              @click="emit('toggle-payment-form')"
            >
              {{ showPaymentForm ? 'Cerrar pago' : 'Registrar pago' }}
            </button>
          </div>
        </div>

        <template v-if="invoice">
          <p><strong>Numero:</strong> {{ invoice.invoice_number || `Factura #${invoice.id}` }}</p>
          <p><strong>Estado:</strong> <span :class="resolveInvoiceStatusClass(invoice.status)">{{ formatInvoiceStatus(invoice.status) }}</span></p>
          <p><strong>Emision:</strong> {{ formatDate(invoice.issue_date) }}</p>
          <p><strong>Vencimiento:</strong> {{ formatDate(invoice.due_date) }}</p>
          <p><strong>Total:</strong> {{ formatCurrency(invoice.total) }}</p>
          <p><strong>Pendiente:</strong> {{ formatCurrency(invoice.amount_due) }}</p>

          <div class="commercial-subsection">
            <h4>Pagos registrados</h4>
            <div v-if="showPaymentForm" class="commercial-form commercial-form-grid">
              <label>
                Monto
                <input
                  class="admin-input"
                  type="number"
                  min="1"
                  step="1"
                  :value="paymentAmount"
                  :disabled="performingAction"
                  @input="emit('update-payment-field', { field: 'amount', value: $event.target.value })"
                >
              </label>
              <label>
                Metodo
                <select
                  class="admin-select"
                  :value="paymentMethod"
                  :disabled="performingAction"
                  @change="emit('update-payment-field', { field: 'paymentMethod', value: $event.target.value })"
                >
                  <option value="cash">Efectivo</option>
                  <option value="card">Tarjeta</option>
                  <option value="transfer">Transferencia</option>
                  <option value="paypal">PayPal</option>
                </select>
              </label>
              <label>
                ID transaccion
                <input
                  class="admin-input"
                  type="text"
                  :value="paymentTransactionId"
                  :disabled="performingAction"
                  @input="emit('update-payment-field', { field: 'transactionId', value: $event.target.value })"
                >
              </label>
              <div class="field-actions">
                <button
                  class="btn-primary"
                  :disabled="performingAction"
                  @click="emit('submit-invoice-payment')"
                >
                  Guardar pago
                </button>
              </div>
            </div>
            <div v-if="payments.length" class="commercial-list">
              <article
                v-for="payment in payments"
                :key="payment.id"
                class="commercial-entry"
              >
                <header>
                  <strong>{{ formatCurrency(payment.amount) }}</strong>
                  <span :class="resolvePaymentStatusClass(payment.status)">{{ formatPaymentStatus(payment.status) }}</span>
                </header>
                <div class="commercial-meta">
                  <span>{{ formatPaymentMethod(payment.payment_method) }}</span>
                  <span v-if="payment.created_at">{{ formatDate(payment.created_at) }}</span>
                  <span v-if="payment.transaction_id">TX: {{ payment.transaction_id }}</span>
                </div>
                <p v-if="payment.notes">{{ payment.notes }}</p>
              </article>
            </div>
            <p v-else class="empty-state compact-empty">Sin pagos registrados para esta OT.</p>
          </div>
        </template>
        <p v-else class="empty-state">No hay comprobante generado para esta OT.</p>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  warranty: {
    type: Object,
    default: null
  },
  invoice: {
    type: Object,
    default: null
  },
  claims: {
    type: Array,
    default: () => []
  },
  payments: {
    type: Array,
    default: () => []
  },
  canSubmitWarrantyClaim: {
    type: Boolean,
    default: false
  },
  canRecordInvoicePayment: {
    type: Boolean,
    default: false
  },
  showClaimForm: {
    type: Boolean,
    default: false
  },
  claimProblemDescription: {
    type: String,
    default: ''
  },
  claimFaultType: {
    type: String,
    default: ''
  },
  showPaymentForm: {
    type: Boolean,
    default: false
  },
  paymentAmount: {
    type: [Number, String],
    default: ''
  },
  paymentMethod: {
    type: String,
    default: 'cash'
  },
  paymentTransactionId: {
    type: String,
    default: ''
  },
  performingAction: {
    type: Boolean,
    default: false
  },
  canCreateWarranty: {
    type: Boolean,
    default: false
  },
  canCreateInvoice: {
    type: Boolean,
    default: false
  },
  formatDate: {
    type: Function,
    required: true
  },
  formatCurrency: {
    type: Function,
    required: true
  }
})

const emit = defineEmits([
  'create-warranty',
  'create-invoice',
  'toggle-claim-form',
  'update-claim-field',
  'submit-warranty-claim',
  'toggle-payment-form',
  'update-payment-field',
  'submit-invoice-payment'
])

function formatWarrantyType(value) {
  const map = {
    labor: 'Mano de obra',
    parts: 'Repuestos',
    full: 'Completa',
    limited: 'Limitada',
    extended: 'Extendida'
  }
  return map[String(value || '').toLowerCase()] || 'Sin tipo'
}

function formatWarrantyStatus(value) {
  const map = {
    active: 'Activa',
    expired: 'Vencida',
    voided: 'Anulada',
    claimed: 'Con reclamo',
    used: 'Usada'
  }
  return map[String(value || '').toLowerCase()] || 'Sin estado'
}

function formatInvoiceStatus(value) {
  const map = {
    draft: 'Borrador',
    sent: 'Enviada',
    viewed: 'Vista',
    paid: 'Pagada',
    partial: 'Pago parcial',
    overdue: 'Vencida',
    void: 'Anulada',
    refunded: 'Reembolsada'
  }
  return map[String(value || '').toLowerCase()] || 'Sin estado'
}

function formatClaimStatus(value) {
  const map = {
    submitted: 'Ingresado',
    under_review: 'En revision',
    approved: 'Aprobado',
    rejected: 'Rechazado',
    in_progress: 'En proceso',
    completed: 'Completado'
  }
  return map[String(value || '').toLowerCase()] || 'Sin estado'
}

function formatPaymentStatus(value) {
  const map = {
    pending: 'Pendiente',
    success: 'Confirmado',
    failed: 'Fallido',
    refunded: 'Reembolsado'
  }
  return map[String(value || '').toLowerCase()] || 'Sin estado'
}

function formatPaymentMethod(value) {
  const map = {
    cash: 'Efectivo',
    card: 'Tarjeta',
    transfer: 'Transferencia',
    paypal: 'PayPal'
  }
  return map[String(value || '').toLowerCase()] || 'Sin metodo'
}

function resolveWarrantyStatusClass(status) {
  const key = String(status || '').toLowerCase()
  if (key === 'active') return 'status-success'
  if (['claimed', 'used'].includes(key)) return 'status-progress'
  if (['expired', 'voided'].includes(key)) return 'status-archived'
  return 'status-neutral'
}

function resolveInvoiceStatusClass(status) {
  const key = String(status || '').toLowerCase()
  if (key === 'paid') return 'status-success'
  if (['sent', 'viewed', 'partial'].includes(key)) return 'status-progress'
  if (['overdue', 'void', 'refunded'].includes(key)) return 'status-archived'
  return 'status-neutral'
}

function resolveClaimStatusClass(status) {
  const key = String(status || '').toLowerCase()
  if (['approved', 'completed'].includes(key)) return 'status-success'
  if (['under_review', 'in_progress'].includes(key)) return 'status-progress'
  if (key === 'rejected') return 'status-rejected'
  return 'status-neutral'
}

function resolvePaymentStatusClass(status) {
  const key = String(status || '').toLowerCase()
  if (key === 'success') return 'status-success'
  if (key === 'pending') return 'status-progress'
  if (['failed', 'refunded'].includes(key)) return 'status-rejected'
  return 'status-neutral'
}
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/repairDetailAdminShared.css"></style>
