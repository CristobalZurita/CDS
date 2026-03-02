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
        <h4>Selecciona la OT</h4>
        <div class="form-grid">
          <div>
            <label>OT</label>
            <select v-model="form.repair_id" class="form-select">
              <option :value="null">Selecciona</option>
              <option v-for="repair in repairs" :key="repair.id" :value="repair.id">
                {{ repair.repair_code || repair.repair_number }}
              </option>
            </select>
          </div>
          <div>
            <label>Tipo de firma</label>
            <select v-model="form.request_type" class="form-select">
              <option value="ingreso">Ingreso</option>
              <option value="retiro">Retiro</option>
            </select>
          </div>
          <div>
            <label>Expira (min)</label>
            <input v-model.number="form.expires_minutes" type="number" min="1" max="5" class="form-control" />
          </div>
        </div>
      </div>

      <div v-else class="wizard-section">
        <h4>Enlace de firma</h4>
        <div v-if="result">
          <p>Comparte este enlace o QR con el cliente:</p>
          <input class="form-control" :value="signatureLink" readonly />
          <p class="mt-2"><strong>Estado:</strong> {{ result.status }}</p>
        </div>
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
  { key: 'select', title: 'OT y tipo' },
  { key: 'link', title: 'Enlace' }
]

const currentStep = ref(0)
const repairs = ref([])
const result = ref(null)

const form = ref({
  repair_id: null,
  request_type: 'ingreso',
  expires_minutes: 5
})

const canContinue = computed(() => {
  return currentStep.value === 0 ? !!form.value.repair_id : true
})

const signatureLink = computed(() => {
  if (!result.value?.token) return ''
  return `${window.location.origin}/signature/${result.value.token}`
})

const loadRepairs = async () => {
  const res = await api.get('/repairs/').catch(() => ({ data: [] }))
  repairs.value = res.data || res || []
}

const handleNext = async () => {
  if (currentStep.value === steps.length - 1) {
    emit('completed')
    return
  }
  if (currentStep.value === 0) {
    const res = await api.post('/signatures/requests', form.value)
    result.value = res.data || res
  }
  currentStep.value += 1
}

const handlePrev = () => {
  if (currentStep.value > 0) currentStep.value -= 1
}

onMounted(loadRepairs)
</script>
