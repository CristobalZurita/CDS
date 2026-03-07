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
import { useTicketsPage } from '@new/composables/useTicketsPage'

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

<style scoped>
.admin-page { padding: 1rem; display: grid; gap: 1rem; }
.admin-header, .panel-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); }
.admin-header { padding: .9rem; display: flex; justify-content: space-between; align-items: center; gap: .75rem; flex-wrap: wrap; }
.admin-header h1 { margin: 0; font-size: var(--cds-text-3xl); }
.admin-header p { margin: .3rem 0 0; color: var(--cds-text-muted); }
.header-actions { display: flex; gap: .45rem; flex-wrap: wrap; }
.btn-primary, .btn-secondary, .btn-danger { min-height: 44px; padding: .65rem .9rem; border-radius: .55rem; border: 1px solid transparent; font-size: var(--cds-text-base); }
.btn-primary { background: var(--cds-primary); border-color: var(--cds-primary); color: var(--cds-white); }
.btn-secondary { background: var(--cds-white); border-color: color-mix(in srgb, var(--cds-light) 65%, white); color: var(--cds-text-normal); }
.btn-danger { background: #dc2626; border-color: #dc2626; color: #fff; }
.admin-error { margin: 0; border: 1px solid #fecaca; background: #fef2f2; color: #991b1b; border-radius: .65rem; padding: .75rem; }
.panel-card { padding: .9rem; display: grid; gap: .7rem; }
.panel-card h2 { margin: 0; font-size: var(--cds-text-xl); }
.filters-panel label, .form-grid label { display: grid; gap: .3rem; }
.filters-panel span, .form-grid span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.filters-panel input, .form-grid input, .form-grid textarea, .form-grid select, table select { min-height: 44px; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); border-radius: .55rem; padding: .65rem .75rem; font-size: var(--cds-text-base); }
.form-grid { display: grid; gap: .6rem; grid-template-columns: 1fr; }
.form-grid.two-cols { grid-template-columns: 1fr; }
.form-grid .full { grid-column: 1 / -1; }
.form-grid textarea { min-height: 92px; resize: vertical; }
.panel-actions { display: flex; justify-content: flex-end; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: .55rem; border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); vertical-align: top; }
th { color: var(--cds-text-muted); font-size: var(--cds-text-sm); }
.row-actions { display: flex; gap: .45rem; }
.inline-message { display: grid; gap: .45rem; grid-template-columns: 1fr; }
.message-row td { background: color-mix(in srgb, var(--cds-light) 7%, white); }
.empty-state { margin: 0; border: 1px dashed color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .65rem; padding: .8rem; color: var(--cds-text-muted); }
@media (min-width: 900px) {
  .form-grid.two-cols { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .inline-message { grid-template-columns: 1fr auto; }
}
</style>
