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
        <h4>Contexto de compra</h4>
        <div class="form-grid">
          <div>
            <label>Cliente (opcional)</label>
            <select v-model="form.client_id" class="form-select">
              <option :value="null">Sin cliente</option>
              <option v-for="client in clients" :key="client.id" :value="client.id">
                {{ client.client_code || `CDS-${client.id}` }} - {{ client.name }}
              </option>
            </select>
          </div>
          <div>
            <label>OT (opcional)</label>
            <select v-model="form.repair_id" class="form-select">
              <option :value="null">Sin OT</option>
              <option v-for="repair in repairs" :key="repair.id" :value="repair.id">
                {{ repair.repair_code || repair.repair_number }}
              </option>
            </select>
          </div>
        </div>
        <div class="mt-3">
          <label>Notas</label>
          <textarea v-model="form.notes" rows="3" class="form-control" />
        </div>
      </div>

      <div v-else-if="currentStep === 1" class="wizard-section">
        <h4>Items sugeridos</h4>
        <div v-for="(item, index) in form.items" :key="index" class="item-row">
          <input v-model="item.sku" class="form-control" placeholder="SKU" />
          <input v-model="item.name" class="form-control" placeholder="Nombre" />
          <input v-model.number="item.quantity" type="number" class="form-control" min="1" />
          <input v-model.number="item.unit_price" type="number" class="form-control" min="0" />
          <button class="btn btn-outline-danger" @click="removeItem(index)">Quitar</button>
        </div>
        <button class="btn btn-outline-primary mt-2" @click="addItem">Agregar item</button>
      </div>

      <div v-else class="wizard-section">
        <h4>Confirmación</h4>
        <div class="summary-grid">
          <div><strong>Cliente:</strong> {{ selectedClientLabel }}</div>
          <div><strong>OT:</strong> {{ selectedRepairLabel }}</div>
          <div><strong>Items:</strong> {{ form.items.length }}</div>
        </div>
        <div v-if="result" class="alert alert-success mt-3">Solicitud creada: #{{ result.id }}</div>
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
  { key: 'items', title: 'Items' },
  { key: 'confirm', title: 'Confirmación' }
]

const currentStep = ref(0)
const clients = ref([])
const repairs = ref([])
const result = ref(null)

const form = ref({
  client_id: null,
  repair_id: null,
  notes: '',
  items: [
    { sku: '', name: '', quantity: 1, unit_price: 0 }
  ]
})

const canContinue = computed(() => {
  if (currentStep.value === 1) {
    return form.value.items.length > 0
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

const addItem = () => {
  form.value.items.push({ sku: '', name: '', quantity: 1, unit_price: 0 })
}

const removeItem = (index) => {
  form.value.items.splice(index, 1)
}

const handleNext = async () => {
  if (currentStep.value === steps.length - 1) {
    emit('completed')
    return
  }
  if (currentStep.value === steps.length - 2) {
    const res = await api.post('/purchase-requests/', form.value)
    result.value = res.data || res
  }
  currentStep.value += 1
}

const handlePrev = () => {
  if (currentStep.value > 0) currentStep.value -= 1
}

onMounted(loadData)
</script>

<style scoped>
.wizard-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}
.item-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem;
  align-items: center;
}
.summary-grid {
  display: grid;
  gap: 0.5rem;
}
</style>
