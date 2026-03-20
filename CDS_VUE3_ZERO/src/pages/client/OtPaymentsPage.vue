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

        <div v-if="canSubmitProof(request)" class="proof-form">
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
import { useOtPaymentsPage } from '@/composables/useOtPaymentsPage'

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

<style scoped src="./commonClientPage.css"></style>
