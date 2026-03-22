<template>
  <main class="store-verify-page">
    <div class="verify-card">

      <div v-if="loading" class="verify-state">
        <i class="fas fa-spinner fa-spin verify-icon verify-icon--loading"></i>
        <p>Verificando tu pedido...</p>
      </div>

      <div v-else-if="error" class="verify-state">
        <i class="fas fa-times-circle verify-icon verify-icon--error"></i>
        <h1 class="verify-title">Link inválido o vencido</h1>
        <p class="verify-body">{{ error }}</p>
        <router-link to="/tienda" class="btn-verify">
          <i class="fas fa-store"></i> Ir a la tienda
        </router-link>
      </div>

      <div v-else class="verify-state">
        <i class="fas fa-check-circle verify-icon verify-icon--success"></i>
        <h1 class="verify-title">
          {{ alreadyVerified ? 'Pedido ya confirmado' : '¡Pedido confirmado!' }}
        </h1>
        <p class="verify-body">{{ message }}</p>
        <p v-if="requestId" class="verify-ref">Pedido <strong>#{{ requestId }}</strong></p>
        <router-link to="/tienda" class="btn-verify">
          <i class="fas fa-store"></i> Seguir comprando
        </router-link>
      </div>

    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'

const route = useRoute()

const loading = ref(true)
const error = ref('')
const message = ref('')
const requestId = ref(null)
const alreadyVerified = ref(false)

onMounted(async () => {
  const token = route.params.token
  if (!token) {
    error.value = 'Token no encontrado en la URL.'
    loading.value = false
    return
  }
  try {
    const res = await api.get(`/store/verify/${token}`)
    message.value = res.data?.message || 'Pedido confirmado.'
    requestId.value = res.data?.request_id || null
    alreadyVerified.value = Boolean(res.data?.already_verified)
  } catch (err) {
    error.value = err?.response?.data?.detail || err?.message || 'No se pudo verificar el pedido.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.store-verify-page {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--cds-space-2xl) var(--cds-space-md);
}

.verify-card {
  width: 100%;
  max-width: 480px;
  padding: var(--cds-space-2xl) var(--cds-space-xl);
  background: var(--cds-surface-1);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-lg);
  box-shadow: var(--cds-shadow-md);
}

.verify-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--cds-space-md);
  text-align: center;
}

.verify-icon {
  font-size: 3.5rem;
  line-height: 1;
}

.verify-icon--loading { color: var(--cds-text-muted); }
.verify-icon--success { color: var(--cds-valid-text); }
.verify-icon--error   { color: var(--cds-invalid-text); }

.verify-title {
  margin: 0;
  font-size: var(--cds-text-2xl);
  color: var(--cds-dark);
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.verify-body {
  margin: 0;
  font-size: var(--cds-text-base);
  color: var(--cds-text-muted);
  line-height: 1.6;
}

.verify-ref {
  margin: 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.btn-verify {
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

.btn-verify:hover {
  background: var(--cds-primary-hover);
}
</style>
