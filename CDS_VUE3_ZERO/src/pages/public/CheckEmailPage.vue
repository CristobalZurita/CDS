<template>
  <main class="check-email-page">
    <div class="check-email-card">

      <div v-if="!emailWarning">
        <div class="check-email-icon">
          <i class="fas fa-envelope-open-text"></i>
        </div>
        <h1 class="check-email-title">Revisa tu email</h1>
        <p class="check-email-body">
          Te enviamos un link de confirmación a <strong>{{ email }}</strong>.
        </p>
        <p class="check-email-body">
          Haz click en ese link para confirmar tu pedido. El link vence en 24 horas.
        </p>
        <p class="check-email-hint">
          <i class="fas fa-info-circle"></i>
          Si no lo ves, revisa tu carpeta de spam o correo no deseado.
        </p>
      </div>

      <div v-else>
        <div class="check-email-icon check-email-icon--warning">
          <i class="fas fa-check-circle"></i>
        </div>
        <h1 class="check-email-title">Pedido recibido</h1>
        <p class="check-email-body">
          Tu solicitud fue registrada correctamente.
        </p>
        <p class="check-email-warning">
          <i class="fas fa-exclamation-triangle"></i>
          No pudimos enviar el email de confirmación en este momento.
          El taller revisará tu solicitud y se comunicará contigo por teléfono.
        </p>
      </div>

      <router-link to="/tienda" class="btn-back-store">
        <i class="fas fa-store"></i> Volver a la tienda
      </router-link>

    </div>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const email = computed(() => route.query.email || 'tu correo')
const emailWarning = computed(() => route.query.warn === '1')
</script>

<style scoped>
.check-email-page {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--cds-space-2xl) var(--cds-space-md);
}

.check-email-card {
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

.check-email-icon {
  font-size: 3.5rem;
  color: var(--cds-primary);
  line-height: 1;
}

.check-email-title {
  margin: 0;
  font-size: var(--cds-text-2xl);
  color: var(--cds-dark);
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.check-email-body {
  margin: 0;
  font-size: var(--cds-text-base);
  color: var(--cds-text-muted);
  line-height: 1.6;
}

.check-email-hint {
  margin: 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  display: flex;
  align-items: center;
  gap: var(--cds-space-xs);
}

.btn-back-store {
  display: inline-flex;
  align-items: center;
  gap: var(--cds-space-xs);
  min-height: 44px;
  padding: var(--cds-space-sm) var(--cds-space-xl);
  border-radius: var(--cds-radius-pill);
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  text-decoration: none;
  margin-top: var(--cds-space-sm);
  transition: background 0.15s;
}

.btn-back-store:hover {
  background: var(--cds-primary-hover);
}

.check-email-icon--warning {
  color: var(--cds-valid-text, #1a7f4b);
}

.check-email-warning {
  margin: 0;
  padding: 0.7rem 0.9rem;
  border-radius: var(--cds-radius-sm);
  border: 1px solid var(--cds-warning, #d97706);
  background: rgba(217, 119, 6, 0.08);
  color: var(--cds-dark);
  font-size: var(--cds-text-sm);
  line-height: 1.6;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  text-align: left;
}
</style>
