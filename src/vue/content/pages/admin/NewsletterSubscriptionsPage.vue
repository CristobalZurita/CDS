<template>
  <AdminLayout title="Newsletter" subtitle="Suscripciones activas">
    <section class="admin-section">
      <div class="admin-section-header">
        <h2 class="admin-section-title">Suscripciones</h2>
        <button class="admin-btn admin-btn-outline" data-testid="newsletter-refresh" @click="fetchSubscriptions">
          <i class="fa-solid fa-rotate" />
          Actualizar
        </button>
      </div>

      <p v-if="error" class="admin-status admin-status-error">{{ error }}</p>
      <p v-else-if="isLoading" class="admin-status">Cargando suscripciones...</p>

      <div v-else-if="subscriptions.length === 0" class="admin-empty">
        No hay suscripciones registradas.
      </div>

      <table v-else class="admin-table admin-table--stack" data-testid="newsletter-table">
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
            <td data-label="Email">{{ subscription.email }}</td>
            <td data-label="Estado">{{ subscription.is_active ? 'Activa' : 'Inactiva' }}</td>
            <td data-label="Origen">{{ subscription.source_url || '-' }}</td>
            <td data-label="Fecha">{{ formatDate(subscription.created_at) }}</td>
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

@include media-breakpoint-down(md) {
  .admin-table--stack,
  .admin-table--stack thead,
  .admin-table--stack tbody,
  .admin-table--stack tr,
  .admin-table--stack th,
  .admin-table--stack td {
    display: block;
    width: 100%;
  }

  .admin-table--stack thead {
    display: none;
  }

  .admin-table--stack tr {
    padding: $spacer-md;
    margin-bottom: 0.75rem;
    background: $color-white;
    border-radius: $border-radius-lg;
    box-shadow: 0 8px 16px rgba($color-dark, 0.12);
  }

  .admin-table--stack td {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.35rem 0;
    font-size: 1rem;
  }

  .admin-table--stack td::before {
    content: attr(data-label);
    font-weight: 600;
    color: $text-muted;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    font-size: 0.8rem;
  }
}
</style>
