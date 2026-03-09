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

<style scoped>
.admin-page { padding: 1rem; display: grid; gap: 1rem; }
.admin-header, .panel-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); }
.admin-header { padding: .9rem; display: flex; flex-wrap: wrap; justify-content: space-between; gap: .75rem; align-items: center; }
.admin-header h1 { margin: 0; font-size: var(--cds-text-3xl); }
.admin-header p { margin: .3rem 0 0; color: var(--cds-text-muted); }
.header-actions { display: flex; flex-wrap: wrap; gap: .5rem; }
.header-actions input { min-height: 44px; min-width: 260px; padding: .65rem .75rem; border-radius: .55rem; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); font-size: var(--cds-text-base); }
.btn-secondary { min-height: 44px; padding: .65rem .9rem; border-radius: .55rem; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); background: var(--cds-white); color: var(--cds-text-normal); font-size: var(--cds-text-base); }
.admin-error { margin: 0; border: 1px solid #f4c7c3; background: #fef3f2; color: #b42318; border-radius: .6rem; padding: .75rem; }
.panel-card { padding: .9rem; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: .6rem; border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); vertical-align: top; }
th { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.empty-state { border: 1px dashed color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .7rem; padding: .9rem; }
</style>
