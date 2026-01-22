<template>
  <AdminLayout title="Tickets" subtitle="Consultas internas y seguimiento">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1 class="h4">Tickets</h1>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="showWizard = !showWizard">
          {{ showWizard ? 'Cerrar' : 'Nuevo ticket' }}
        </button>
        <button class="btn btn-sm btn-outline-secondary" @click="loadTickets">Actualizar</button>
      </div>
    </div>

    <div v-if="showWizard" class="card p-3 mb-3">
      <WizardTicket @completed="onCompleted" />
    </div>

    <div class="card p-3">
      <table class="table table-sm">
        <thead>
          <tr>
            <th>ID</th>
            <th>Asunto</th>
            <th>Estado</th>
            <th>Prioridad</th>
            <th>Mensajes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ticket in tickets" :key="ticket.id">
            <td>#{{ ticket.id }}</td>
            <td>{{ ticket.subject }}</td>
            <td>{{ ticket.status }}</td>
            <td>{{ ticket.priority }}</td>
            <td>{{ ticket.messages?.length || 0 }}</td>
          </tr>
          <tr v-if="tickets.length === 0">
            <td colspan="5" class="text-muted">Sin tickets registrados.</td>
          </tr>
        </tbody>
      </table>
    </div>
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

const onCompleted = () => {
  showWizard.value = false
  loadTickets()
}

onMounted(loadTickets)
</script>
