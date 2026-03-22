<template>
  <main class="payment-result-page">
    <div class="result-card">

      <div class="result-icon" :class="iconClass">
        <i :class="iconFa"></i>
      </div>

      <h1 class="result-title">{{ title }}</h1>
      <p class="result-message">{{ message }}</p>

      <p v-if="externalReference" class="result-ref">
        Referencia: <strong>{{ externalReference }}</strong>
      </p>

      <div class="result-actions">
        <router-link to="/ot-payments" class="btn-primary">
          <i class="fas fa-list-alt"></i> Ver mis pagos
        </router-link>
      </div>

    </div>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const status = computed(() => String(route.query.status || '').toLowerCase())
const externalReference = computed(() => route.query.external_reference || '')

const isApproved = computed(() => status.value === 'approved')
const isPending  = computed(() => status.value === 'pending' || status.value === 'in_process')

const iconClass = computed(() => ({
  'result-icon--success': isApproved.value,
  'result-icon--pending': isPending.value,
  'result-icon--error':   !isApproved.value && !isPending.value,
}))

const iconFa = computed(() => {
  if (isApproved.value) return 'fas fa-check-circle'
  if (isPending.value)  return 'fas fa-clock'
  return 'fas fa-times-circle'
})

const title = computed(() => {
  if (isApproved.value) return 'Pago aprobado'
  if (isPending.value)  return 'Pago en proceso'
  return 'Pago no completado'
})

const message = computed(() => {
  if (isApproved.value) return 'Tu pago fue recibido correctamente. El taller procesará tu solicitud a la brevedad.'
  if (isPending.value)  return 'Tu pago está siendo procesado. Te notificaremos cuando se confirme.'
  return 'El pago no pudo completarse o fue rechazado. Puedes intentarlo nuevamente desde tu lista de pagos.'
})
</script>

<style scoped>
.payment-result-page {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--cds-space-2xl) var(--cds-space-md);
}

.result-card {
  width: 100%;
  max-width: 480px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--cds-space-md);
  padding: var(--cds-space-2xl) var(--cds-space-xl);
  background: var(--cds-surface-1);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-lg);
  box-shadow: var(--cds-shadow-md);
  text-align: center;
}

.result-icon {
  font-size: 3.5rem;
  line-height: 1;
}

.result-icon--success { color: var(--cds-valid-text); }
.result-icon--pending  { color: var(--cds-primary); }
.result-icon--error    { color: var(--cds-invalid-text); }

.result-title {
  margin: 0;
  font-size: var(--cds-text-2xl);
  color: var(--cds-dark);
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.result-message {
  margin: 0;
  font-size: var(--cds-text-base);
  color: var(--cds-text-muted);
  line-height: 1.6;
}

.result-ref {
  margin: 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.result-actions {
  margin-top: var(--cds-space-sm);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: var(--cds-space-xs);
  min-height: 44px;
  padding: var(--cds-space-sm) var(--cds-space-xl);
  border: none;
  border-radius: var(--cds-radius-pill);
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  text-decoration: none;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-primary:hover {
  background: var(--cds-primary-hover);
}
</style>
