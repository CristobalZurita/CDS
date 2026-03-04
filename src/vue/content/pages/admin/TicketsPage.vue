<template>
  <AdminLayout title="Tickets" subtitle="Consultas internas y seguimiento">
    <section class="admin-page">
      <header class="admin-page__header">
        <h1 class="admin-page__title">Tickets</h1>

        <div class="admin-page__actions">
          <button
            type="button"
            class="admin-page__button admin-page__button--success"
            data-testid="tickets-new"
            @click="showWizard = !showWizard"
          >
            {{ showWizard ? 'Cerrar' : 'Nuevo ticket' }}
          </button>
          <button
            type="button"
            class="admin-page__button admin-page__button--secondary"
            data-testid="tickets-refresh"
            @click="loadTickets"
          >
            Actualizar
          </button>
        </div>
      </header>

      <section v-if="showWizard" class="admin-page__panel" data-testid="tickets-wizard">
        <WizardTicket @completed="onCompleted" />
      </section>

      <section class="admin-page__panel">
        <div class="admin-page__table-wrap">
          <table class="admin-page__table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Asunto</th>
                <th>Estado</th>
                <th>Prioridad</th>
                <th>Mensajes</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ticket in tickets" :key="ticket.id" data-testid="ticket-row">
                <td>#{{ ticket.id }}</td>
                <td>{{ ticket.subject }}</td>
                <td>{{ ticket.status }}</td>
                <td>{{ ticket.priority }}</td>
                <td data-testid="ticket-message-count">{{ ticket.messages?.length || 0 }}</td>
                <td>
                  <div class="admin-page__cell-actions">
                    <select
                      class="admin-page__select"
                      data-testid="ticket-status-select"
                      :value="ticket.status"
                      @change="updateTicketStatus(ticket, $event.target.value)"
                    >
                      <option value="open">open</option>
                      <option value="in_progress">in_progress</option>
                      <option value="closed">closed</option>
                    </select>
                    <button
                      type="button"
                      class="admin-page__button admin-page__button--danger"
                      data-testid="ticket-delete"
                      @click="deleteTicket(ticket)"
                    >
                      Eliminar
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="tickets.length === 0">
                <td colspan="6" class="admin-page__empty">Sin tickets registrados.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'
import WizardTicket from '@/vue/components/admin/wizard/WizardTicket.vue'

const tickets = ref([])
const showWizard = ref(false)

const loadTickets = async () => {
  const res = await api.get('/tickets/').catch(() => ({ data: [] }))
  tickets.value = res.data || res || []
}

const updateTicketStatus = async (ticket, status) => {
  await api.patch(`/tickets/${ticket.id}?status=${encodeURIComponent(status)}`).catch(() => null)
  loadTickets()
}

const deleteTicket = async (ticket) => {
  if (!confirm(`¿Eliminar ticket #${ticket.id}?`)) return
  await api.delete(`/tickets/${ticket.id}`).catch(() => null)
  loadTickets()
}

const onCompleted = () => {
  showWizard.value = false
  loadTickets()
}

onMounted(loadTickets)
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.admin-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
}

.admin-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacer-md);
  flex-wrap: wrap;
}

.admin-page__title {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--text-xl);
  font-weight: 700;
}

.admin-page__actions,
.admin-page__cell-actions {
  display: flex;
  gap: var(--spacer-sm);
  flex-wrap: wrap;
}

.admin-page__panel {
  padding: var(--spacer-md);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.admin-page__table-wrap {
  width: 100%;
  overflow-x: auto;
}

.admin-page__table {
  width: 100%;
  border-collapse: collapse;
}

.admin-page__table th,
.admin-page__table td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-light);
  text-align: left;
  vertical-align: middle;
  color: var(--color-dark);
  font-size: var(--text-sm);
}

.admin-page__table th {
  font-weight: 700;
}

.admin-page__empty {
  color: var(--color-dark);
  opacity: 0.7;
}

.admin-page__select {
  min-height: 40px;
  min-width: 160px;
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-sm);
  background: var(--color-white);
  color: var(--color-dark);
  font-size: var(--text-sm);
}

.admin-page__button {
  min-height: 40px;
  padding: 0.65rem 0.9rem;
  border: 0;
  border-radius: var(--radius-sm);
  color: var(--color-white);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
}

.admin-page__button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.admin-page__button--success {
  background: var(--color-primary);
}

.admin-page__button--secondary {
  background: var(--color-dark);
}

.admin-page__button--danger {
  background: var(--color-danger);
}

@include media-breakpoint-down(md) {
  .admin-page__header,
  .admin-page__actions,
  .admin-page__cell-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .admin-page__select,
  .admin-page__button {
    width: 100%;
  }
}
</style>
