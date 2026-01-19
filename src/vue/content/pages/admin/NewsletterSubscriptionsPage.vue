<template>
  <AdminLayout title="Newsletter" subtitle="Suscripciones activas">
    <section class="admin-section">
      <div class="admin-section-header">
        <h2 class="admin-section-title">Suscripciones</h2>
        <button class="admin-btn admin-btn-outline" @click="fetchSubscriptions">
          <i class="fa-solid fa-rotate" />
          Actualizar
        </button>
      </div>

      <p v-if="error" class="admin-status admin-status-error">{{ error }}</p>
      <p v-else-if="isLoading" class="admin-status">Cargando suscripciones...</p>

      <div v-else-if="subscriptions.length === 0" class="admin-empty">
        No hay suscripciones registradas.
      </div>

      <table v-else class="admin-table">
        <thead>
          <tr>
            <th>Email</th>
            <th>Estado</th>
            <th>Origen</th>
            <th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="subscription in subscriptions" :key="subscription.id">
            <td>{{ subscription.email }}</td>
            <td>{{ subscription.is_active ? 'Activa' : 'Inactiva' }}</td>
            <td>{{ subscription.source_url || '-' }}</td>
            <td>{{ formatDate(subscription.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </AdminLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'
import { useApi } from '@/composables/useApi.js'

const api = useApi()
const subscriptions = ref([])
const isLoading = ref(false)
const error = ref('')

const fetchSubscriptions = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const data = await api.get('/newsletter/subscriptions')
    subscriptions.value = Array.isArray(data) ? data : []
  } catch (err) {
    error.value = err.message || 'No se pudieron cargar las suscripciones.'
  } finally {
    isLoading.value = false
  }
}

const formatDate = (value) => {
  if (!value) return ''
  try {
    return new Date(value).toLocaleString()
  } catch (err) {
    return value
  }
}

onMounted(fetchSubscriptions)
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

.admin-status {
  margin: 0 0 1rem;
  font-weight: 600;
  color: $brand-text;
}

.admin-status-error {
  color: $danger;
}

.admin-empty {
  padding: 1rem 0;
  font-weight: 600;
  color: $brand-text;
}
</style>
