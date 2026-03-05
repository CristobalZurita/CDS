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
        <h4>Instrumento</h4>
        <div class="form-grid">
          <div>
            <label>Instrumento</label>
            <select v-model="form.instrument_id" class="form-select" data-testid="manual-instrument">
              <option :value="null">Selecciona</option>
              <option v-for="inst in instruments" :key="inst.id" :value="inst.id">
                {{ inst.brand?.name || '' }} {{ inst.model }}
              </option>
            </select>
          </div>
          <div>
            <label>Título</label>
            <input v-model="form.title" class="form-control" data-testid="manual-title" placeholder="Manual de servicio" />
          </div>
        </div>
      </div>

      <div v-else-if="currentStep === 1" class="wizard-section">
        <h4>Fuente del manual</h4>
        <div class="form-grid">
          <div>
            <label>URL externa (opcional)</label>
            <input v-model="form.url" class="form-control" data-testid="manual-url" placeholder="https://..." />
          </div>
          <div>
            <label>Archivo (PDF/Imagen)</label>
            <input type="file" class="form-control" data-testid="manual-file" @change="onFileChange" />
          </div>
        </div>
      </div>

      <div v-else class="wizard-section">
        <h4>Confirmación</h4>
        <div class="summary-grid">
          <div><strong>Instrumento:</strong> {{ selectedInstrumentLabel }}</div>
          <div><strong>Título:</strong> {{ form.title }}</div>
          <div><strong>Fuente:</strong> {{ form.url ? 'URL' : file ? 'Archivo' : 'Sin fuente' }}</div>
        </div>
        <div v-if="result" class="alert alert-success mt-3" data-testid="manual-result">Manual creado: #{{ result.id }}</div>
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
  { key: 'instrument', title: 'Instrumento' },
  { key: 'source', title: 'Fuente' },
  { key: 'confirm', title: 'Confirmación' }
]

const currentStep = ref(0)
const instruments = ref([])
const file = ref(null)
const result = ref(null)

const form = ref({
  instrument_id: null,
  title: '',
  url: ''
})

const canContinue = computed(() => {
  if (currentStep.value === 0) {
    return !!form.value.instrument_id && form.value.title.trim().length > 1
  }
  return true
})

const selectedInstrumentLabel = computed(() => {
  const inst = instruments.value.find(i => i.id === form.value.instrument_id)
  if (!inst) return 'Sin instrumento'
  return `${inst.brand?.name || ''} ${inst.model}`.trim()
})

const loadInstruments = async () => {
  const res = await api.get('/instruments/').catch(() => ({ data: [] }))
  instruments.value = res.data || res || []
}

const onFileChange = (event) => {
  const files = event.target.files
  file.value = files && files.length ? files[0] : null
}

const handleNext = async () => {
  if (currentStep.value === steps.length - 1) {
    emit('completed')
    return
  }
  if (currentStep.value === steps.length - 2) {
    if (file.value) {
      const formData = new FormData()
      formData.append('file', file.value)
      const uploadRes = await api.post(`/manuals/upload/${form.value.instrument_id}?title=${encodeURIComponent(form.value.title)}`, formData)
      result.value = uploadRes.data || uploadRes
    } else {
      const res = await api.post('/manuals/', {
        instrument_id: form.value.instrument_id,
        title: form.value.title,
        url: form.value.url,
        source: form.value.url ? 'external' : 'internal'
      })
      result.value = res.data || res
    }
  }
  currentStep.value += 1
}

const handlePrev = () => {
  if (currentStep.value > 0) currentStep.value -= 1
}

onMounted(loadInstruments)
</script>
