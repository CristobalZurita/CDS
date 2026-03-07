<template>
  <main class="ot-payments-page">
    <section class="page-header">
      <div>
        <h1>Pagos y solicitudes</h1>
        <p>Solicitudes de compra asociadas a ordenes de trabajo y tienda.</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" data-testid="ot-payments-refresh" :disabled="loading" @click="loadRequests">
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
        <router-link to="/dashboard" class="btn-secondary">Volver al panel</router-link>
      </div>
    </section>

    <p v-if="error" class="payments-error" data-testid="ot-payments-error">{{ error }}</p>

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
            <p class="request-subtitle">
              {{ request.repair_code || request.repair_number ? `OT: ${request.repair_code || request.repair_number}` : 'TIENDA / SIN_OT' }}
            </p>
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
              rel="noopener noreferrer"
              data-testid="ot-payment-proof-link"
            >
              Ver comprobante enviado
            </a>
          </div>
        </div>

        <div v-if="canSubmitProof(request.status)" class="proof-form">
          <h3>Subir comprobante de deposito</h3>
          <div class="form-grid">
            <input
              v-model.number="forms[request.id].amount"
              type="number"
              min="1"
              data-testid="ot-payment-amount"
              placeholder="Monto depositado (CLP)"
            />
            <input
              v-model="forms[request.id].deposit_reference"
              type="text"
              data-testid="ot-payment-reference"
              placeholder="Referencia de transferencia"
            />
          </div>

          <textarea
            v-model="forms[request.id].client_notes"
            rows="2"
            data-testid="ot-payment-notes"
            placeholder="Notas para administracion"
          />

          <input
            type="file"
            accept="image/*"
            data-testid="ot-payment-file"
            @change="onFileSelected(request.id, $event)"
          />

          <button
            class="btn-primary"
            data-testid="ot-payment-submit"
            :disabled="isBusy(request.id)"
            @click="submitProof(request)"
          >
            {{ isBusy(request.id) ? 'Enviando...' : 'Enviar comprobante' }}
          </button>
        </div>

        <div v-else class="proof-readonly">
          <small>Estado actual: {{ request.status }}. Si necesitas ayuda, abre un ticket.</small>
        </div>
      </article>
    </section>

    <section v-else class="empty-state" data-testid="ot-payments-empty">
      <p>No tienes solicitudes de pago OT pendientes por ahora.</p>
    </section>
  </main>
</template>

<script setup>
import { useOtPaymentsPage } from '@new/composables/useOtPaymentsPage'

const {
  requests,
  loading,
  error,
  forms,
  isBusy,
  canSubmitProof,
  toApiPath,
  formatCurrency,
  formatDate,
  onFileSelected,
  loadRequests,
  submitProof
} = useOtPaymentsPage()
</script>

<style scoped>
.ot-payments-page {
  padding: 1rem;
  display: grid;
  gap: 1rem;
}

.page-header,
.request-card,
.empty-state {
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 0.9rem;
  background: var(--cds-white);
}

.page-header,
.empty-state {
  padding: 0.9rem;
}

.page-header {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
}

.page-header p {
  margin: 0.3rem 0 0;
  color: var(--cds-text-muted);
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.btn-primary,
.btn-secondary {
  min-height: 44px;
  padding: 0.65rem 0.9rem;
  border-radius: 0.55rem;
  font-size: var(--cds-text-base);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  border: 1px solid var(--cds-primary);
  background: var(--cds-primary);
  color: var(--cds-white);
}

.btn-secondary {
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  background: var(--cds-white);
  color: var(--cds-text-normal);
}

.payments-error {
  margin: 0;
  border: 1px solid #f4c7c3;
  background: #fef3f2;
  color: #b42318;
  border-radius: 0.6rem;
  padding: 0.75rem;
}

.requests-list {
  display: grid;
  gap: 0.75rem;
}

.request-card {
  padding: 0.9rem;
  display: grid;
  gap: 0.6rem;
}

.request-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.5rem;
}

.request-head h2 {
  margin: 0;
  font-size: var(--cds-text-lg);
}

.request-subtitle,
.request-note,
.meta-label {
  margin: 0.25rem 0 0;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}

.status-pill {
  border-radius: 999px;
  padding: 0.3rem 0.7rem;
  font-size: var(--cds-text-sm);
  border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white);
  background: color-mix(in srgb, var(--cds-primary) 12%, white);
}

.request-body {
  display: grid;
  gap: 0.5rem;
}

.meta-grid {
  display: grid;
  gap: 0.5rem;
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.meta-grid strong {
  display: block;
  margin-top: 0.2rem;
}

.admin-note,
.proof-link,
.proof-readonly {
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  border-radius: 0.6rem;
  padding: 0.65rem;
}

.proof-link a {
  color: var(--cds-primary);
  text-decoration: none;
}

.proof-link a:hover {
  text-decoration: underline;
}

.proof-form {
  display: grid;
  gap: 0.55rem;
}

.proof-form h3 {
  margin: 0;
  font-size: var(--cds-text-base);
}

.form-grid {
  display: grid;
  gap: 0.5rem;
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.form-grid input,
.proof-form textarea,
.proof-form > input[type='file'] {
  min-height: 44px;
  padding: 0.65rem 0.75rem;
  border-radius: 0.55rem;
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  font-size: var(--cds-text-base);
}

.proof-form textarea {
  min-height: 96px;
  resize: vertical;
}

.empty-state {
  min-height: 180px;
  display: grid;
  place-items: center;
  text-align: center;
}

.empty-state p {
  margin: 0;
}

@media (min-width: 760px) {
  .meta-grid,
  .form-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
