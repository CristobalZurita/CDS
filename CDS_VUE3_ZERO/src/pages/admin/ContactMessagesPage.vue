<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Mensajes de contacto</h1>
        <p>Mensajes recibidos desde la landing.</p>
      </div>
      <div class="header-actions">
        <input v-model.trim="search" type="text" placeholder="Buscar nombre, email, asunto" />
        <button class="btn-secondary" data-testid="contact-refresh" :disabled="isLoading" @click="loadMessages">
          {{ isLoading ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section class="panel-card">
      <div v-if="isLoading" class="empty-state">Cargando mensajes...</div>
      <div v-else-if="filteredMessages.length === 0" class="empty-state">No hay mensajes registrados.</div>
      <div v-else class="table-wrap">
        <table data-testid="contact-table">
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
            <tr v-for="message in filteredMessages" :key="message.id">
              <td>{{ message.name }}</td>
              <td>{{ message.email }}</td>
              <td>{{ message.subject }}</td>
              <td>{{ message.message }}</td>
              <td>{{ formatDate(message.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useContactMessagesPage } from '@/composables/useContactMessagesPage'

const {
  isLoading,
  error,
  search,
  filteredMessages,
  formatDate,
  loadMessages
} = useContactMessagesPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
