<template>
  <WizardShell
    :steps="steps"
    :current-index="currentStep"
    :can-continue="canContinue"
    @next="handleNext"
    @prev="handlePrev"
  >
    <template #default>
      <div v-if="currentStep === 0" class="wizard-section">
        <h4>Contexto del ticket</h4>
        <div class="form-grid">
          <div>
            <label>Cliente (opcional)</label>
            <select v-model="form.client_id" class="form-select" data-testid="ticket-client">
              <option :value="null">Sin cliente</option>
              <option v-for="client in clients" :key="client.id" :value="client.id">
                {{ client.client_code || `CDS-${client.id}` }} - {{ client.name }}
              </option>
            </select>
          </div>
          <div>
            <label>OT (opcional)</label>
            <select v-model="form.repair_id" class="form-select" data-testid="ticket-repair">
              <option :value="null">Sin OT</option>
              <option v-for="repair in repairs" :key="repair.id" :value="repair.id">
                {{ repair.repair_code || repair.repair_number }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div v-else-if="currentStep === 1" class="wizard-section">
        <h4>Detalle del ticket</h4>
        <div class="form-grid">
          <div>
            <label>Asunto</label>
            <input v-model="form.subject" class="form-control" data-testid="ticket-subject" placeholder="Ej: Consulta de reparación" />
          </div>
          <div>
            <label>Prioridad</label>
            <select v-model="form.priority" class="form-select" data-testid="ticket-priority">
              <option value="low">Baja</option>
              <option value="normal">Normal</option>
              <option value="high">Alta</option>
            </select>
          </div>
        </div>
        <div class="mt-3">
          <label>Mensaje</label>
          <textarea v-model="form.message" rows="5" class="form-control" data-testid="ticket-message" />
        </div>
      </div>

      <div v-else class="wizard-section">
        <h4>Confirmación</h4>
        <div class="summary-grid">
          <div><strong>Cliente:</strong> {{ selectedClientLabel }}</div>
          <div><strong>OT:</strong> {{ selectedRepairLabel }}</div>
          <div><strong>Asunto:</strong> {{ form.subject }}</div>
          <div><strong>Prioridad:</strong> {{ form.priority }}</div>
        </div>
        <p class="mt-3">{{ form.message }}</p>
        <div v-if="result" class="alert alert-success" data-testid="ticket-result">Ticket creado: #{{ result.id }}</div>
      </div>
    </template>
  </WizardShell>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/services/api'
import WizardShell from './WizardShell.vue'

const emit = defineEmits(['completed'])

const steps = [
  { key: 'context', title: 'Contexto' },
  { key: 'detail', title: 'Detalle' },
  { key: 'confirm', title: 'Confirmación' }
]

const currentStep = ref(0)
const clients = ref([])
const repairs = ref([])
const result = ref(null)

const form = ref({
  client_id: null,
  repair_id: null,
  subject: '',
  priority: 'normal',
  message: ''
})

const canContinue = computed(() => {
  if (currentStep.value === 1) {
    return form.value.subject.trim().length > 2 && form.value.message.trim().length > 0
  }
  return true
})

const selectedClientLabel = computed(() => {
  const client = clients.value.find(c => c.id === form.value.client_id)
  return client ? `${client.client_code || `CDS-${client.id}`} - ${client.name}` : 'Sin cliente'
})

const selectedRepairLabel = computed(() => {
  const repair = repairs.value.find(r => r.id === form.value.repair_id)
  return repair ? (repair.repair_code || repair.repair_number) : 'Sin OT'
})

const loadData = async () => {
  const [clientsRes, repairsRes] = await Promise.all([
    api.get('/clients/').catch(() => ({ data: [] })),
    api.get('/repairs/').catch(() => ({ data: [] }))
  ])
  clients.value = clientsRes.data || clientsRes || []
  repairs.value = repairsRes.data || repairsRes || []
}

const handleNext = async () => {
  if (currentStep.value === steps.length - 1) {
    emit('completed')
    return
  }
  if (currentStep.value === steps.length - 2) {
    const payload = { ...form.value }
    const res = await api.post('/tickets/', payload)
    result.value = res.data || res
  }
  currentStep.value += 1
}

const handlePrev = () => {
  if (currentStep.value > 0) currentStep.value -= 1
}

onMounted(loadData)
</script>
