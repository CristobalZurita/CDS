<template>
  <AdminLayout title="Contacto" subtitle="Mensajes recibidos desde la landing">
    <section class="admin-section">
      <div class="admin-section-header">
        <h2 class="admin-section-title">Mensajes</h2>
        <button class="admin-btn admin-btn-outline" @click="fetchMessages">
          <i class="fa-solid fa-rotate" />
          Actualizar
        </button>
      </div>

      <p v-if="error" class="admin-status admin-status-error">{{ error }}</p>
      <p v-else-if="isLoading" class="admin-status">Cargando mensajes...</p>

      <div v-else-if="messages.length === 0" class="admin-empty">
      No hay mensajes registrados.
      </div>

      <table v-else class="admin-table">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Email</th>
            <th>Asunto</th>
            <th>Mensaje</th>
            <th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="message in messages" :key="message.id">
            <td>{{ message.name }}</td>
            <td>{{ message.email }}</td>
            <td>{{ message.subject }}</td>
            <td>{{ message.message }}</td>
            <td>{{ formatDate(message.created_at) }}</td>
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
const messages = ref([])
const isLoading = ref(false)
const error = ref('')

const fetchMessages = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const data = await api.get('/contact/messages')
    messages.value = Array.isArray(data) ? data : []
  } catch (err) {
    error.value = err.message || 'No se pudieron cargar los mensajes.'
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

onMounted(fetchMessages)
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
