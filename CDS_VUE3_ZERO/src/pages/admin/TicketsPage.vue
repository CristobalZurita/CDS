<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Tickets</h1>
        <p>Consultas internas y seguimiento con mensajes.</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" :disabled="loading" @click="loadTickets">
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
        <button class="btn-primary" :disabled="loading" @click="toggleForm">
          {{ showForm ? 'Cancelar' : 'Nuevo ticket' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section v-if="showForm" class="panel-card">
      <h2>Crear ticket</h2>
      <div class="form-grid two-cols">
        <label>
          <span>Cliente</span>
          <select v-model="form.client_id">
            <option value="">Sin cliente</option>
            <option v-for="client in clients" :key="client.id" :value="client.id">
              {{ client.client_code || `#${client.id}` }} - {{ client.name }}
            </option>
          </select>
        </label>
        <label>
          <span>OT relacionada</span>
          <select v-model="form.repair_id">
            <option value="">Sin OT</option>
            <option v-for="repair in repairs" :key="repair.id" :value="repair.id">
              {{ repair.repair_code || `OT #${repair.id}` }}
            </option>
          </select>
        </label>
        <label class="full"><span>Asunto *</span><input v-model.trim="form.subject" type="text" /></label>
        <label class="full"><span>Mensaje *</span><textarea v-model.trim="form.message" rows="3"></textarea></label>
        <label>
          <span>Prioridad</span>
          <select v-model="form.priority">
            <option v-for="option in priorityOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
          </select>
        </label>
      </div>
      <div class="panel-actions">
        <button class="btn-primary" :disabled="loading" @click="createTicket">
          {{ loading ? 'Guardando...' : 'Crear ticket' }}
        </button>
      </div>
    </section>

    <section class="panel-card filters-panel">
      <label>
        <span>Buscar ticket</span>
        <input v-model.trim="searchQuery" type="search" placeholder="ID, asunto, estado o prioridad" />
      </label>
    </section>

    <section class="panel-card">
      <h2>Listado ({{ tickets.length }})</h2>
      <p v-if="tickets.length === 0" class="empty-state">No hay tickets registrados.</p>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Asunto</th>
              <th>Estado</th>
              <th>Prioridad</th>
              <th>Mensajes</th>
              <th>Actualizado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ticket in tickets" :key="ticket.id">
              <td>#{{ ticket.id }}</td>
              <td>{{ ticket.subject }}</td>
              <td>
                <select :value="ticket.status" @change="updateTicketStatus(ticket, $event.target.value)">
                  <option v-for="option in statusOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
                </select>
              </td>
              <td>{{ ticket.priority }}</td>
              <td>{{ ticket.messages.length }}</td>
              <td>{{ formatDate(ticket.updated_at) }}</td>
              <td>
                <div class="row-actions">
                  <button class="btn-danger" :disabled="loading" @click="deleteTicket(ticket)">Eliminar</button>
                </div>
              </td>
            </tr>
            <tr v-for="ticket in tickets" :key="`msg-${ticket.id}`" class="message-row">
              <td colspan="7">
                <div class="inline-message">
                  <input v-model.trim="messageDrafts[ticket.id]" type="text" placeholder="Agregar mensaje rapido al ticket" />
                  <button class="btn-secondary" :disabled="loading" @click="submitMessage(ticket)">Agregar mensaje</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useTicketsPage } from '@/composables/useTicketsPage'

const {
  tickets,
  clients,
  repairs,
  loading,
  error,
  showForm,
  form,
  searchQuery,
  statusOptions,
  priorityOptions,
  formatDate,
  toggleForm,
  loadTickets,
  createTicket,
  updateTicketStatus,
  deleteTicket,
  addMessage
} = useTicketsPage()

const messageDrafts = ref({})

async function submitMessage(ticket) {
  const value = String(messageDrafts.value[ticket.id] || '').trim()
  if (!value) return
  await addMessage(ticket, value)
  messageDrafts.value[ticket.id] = ''
}
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped>
/* Filtro inline en filters-panel */
/* Mensaje rápido inline */
.inline-message { display: grid; gap: .45rem; grid-template-columns: 1fr; }
.message-row td { background: color-mix(in srgb, var(--cds-light) 7%, white); }
@media (min-width: 900px) { .inline-message { grid-template-columns: 1fr auto; } }
</style>
