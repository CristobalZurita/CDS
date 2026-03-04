<template>
  <WizardShell
    :steps="steps"
    :current-index="stepIndex"
    :can-continue="canContinue"
    @next="onNext"
    @prev="onPrev"
  >
    <template #default>
      <div v-if="errorMessage" class="alert alert-danger mb-3">
        {{ errorMessage }}
      </div>
      <div v-if="stepIndex === 0" class="wizard-step-body">
        <h4>Cliente</h4>
        <div class="row g-2">
          <div class="col-md-6">
            <label class="form-label">Nombre *</label>
            <input v-model="client.name" class="form-control" />
          </div>
          <div class="col-md-6">
            <label class="form-label">Email *</label>
            <input v-model="client.email" type="email" class="form-control" />
          </div>
          <div class="col-md-6">
            <label class="form-label">Teléfono</label>
            <input v-model="client.phone" class="form-control" />
          </div>
          <div class="col-md-6">
            <label class="form-label">Dirección</label>
            <input v-model="client.address" class="form-control" />
          </div>
          <div class="col-12">
            <label class="form-label">Notas</label>
            <textarea v-model="client.notes" class="form-control" rows="2"></textarea>
          </div>
        </div>
      </div>

      <div v-else-if="stepIndex === 1" class="wizard-step-body">
        <h4>Instrumento</h4>
        <div class="row g-2">
          <div class="col-md-6">
            <label class="form-label">Marca</label>
            <input v-model="device.brand_other" class="form-control" placeholder="Ej: Korg" />
          </div>
          <div class="col-md-6">
            <label class="form-label">Modelo *</label>
            <input v-model="device.model" class="form-control" placeholder="Ej: MS-20" />
          </div>
          <div class="col-md-6">
            <label class="form-label">Número de serie</label>
            <input v-model="device.serial_number" class="form-control" />
          </div>
          <div class="col-md-6">
            <label class="form-label">Accesorios / Detalles de entrada</label>
            <input v-model="device.description" class="form-control" placeholder="Fundas, cables, fuente..." />
          </div>
          <div class="col-12">
            <label class="form-label">Estado visual / condición</label>
            <textarea v-model="device.condition_notes" class="form-control" rows="2"></textarea>
          </div>
        </div>
      </div>

      <div v-else-if="stepIndex === 2" class="wizard-step-body">
        <h4>Orden de trabajo</h4>
        <div class="row g-2">
          <div class="col-12">
            <label class="form-label">Problema reportado *</label>
            <textarea v-model="repair.problem_reported" class="form-control" rows="3"></textarea>
          </div>
          <div class="col-md-4">
            <label class="form-label">Prioridad</label>
            <select v-model.number="repair.priority" class="form-select">
              <option :value="1">Alta</option>
              <option :value="2">Normal</option>
              <option :value="3">Baja</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label">Abono (CLP)</label>
            <input v-model.number="repair.paid_amount" type="number" min="0" class="form-control" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Medio de pago</label>
            <select v-model="repair.payment_method" class="form-select">
              <option value="cash">Efectivo</option>
              <option value="web">Web</option>
              <option value="transfer">Transferencia</option>
            </select>
          </div>
        </div>
      </div>

      <div v-else-if="stepIndex === 3" class="wizard-step-body">
        <h4>Foto inicial (opcional)</h4>
        <div class="row g-2">
          <div class="col-md-6">
            <input type="file" class="form-control" accept="image/*" @change="onFileSelected" />
          </div>
          <div class="col-md-6">
            <input v-model="photo.caption" class="form-control" placeholder="Descripción de la foto" />
          </div>
        </div>
        <div class="mt-3 d-flex justify-content-end">
          <button class="btn btn-primary btn-sm" :disabled="saving" @click="submit">
            {{ saving ? 'Guardando...' : 'Finalizar ingreso' }}
          </button>
        </div>
      </div>
    </template>
  </WizardShell>
</template>

<script setup>
import { ref, computed } from 'vue'
import { api } from '@/services/api'
import WizardShell from '@/vue/components/admin/wizard/WizardShell.vue'

const emit = defineEmits(['completed'])

const steps = [
  { key: 'client', title: 'Cliente' },
  { key: 'device', title: 'Instrumento' },
  { key: 'repair', title: 'OT' },
  { key: 'photo', title: 'Foto' }
]

const stepIndex = ref(0)
const saving = ref(false)
const errorMessage = ref('')

const client = ref({ name: '', email: '', phone: '', address: '', notes: '' })
const device = ref({ brand_other: '', model: '', serial_number: '', description: '', condition_notes: '' })
const repair = ref({ problem_reported: '', priority: 2, paid_amount: 20000, payment_method: 'cash' })
const photo = ref({ file: null, caption: '' })

const onFileSelected = (e) => {
  photo.value.file = e.target.files?.[0] || null
}

const canContinue = computed(() => {
  if (stepIndex.value === 0) return !!client.value.name && !!client.value.email
  if (stepIndex.value === 1) return !!device.value.model
  if (stepIndex.value === 2) return !!repair.value.problem_reported
  return true
})

const onNext = () => {
  if (stepIndex.value < steps.length - 1) {
    stepIndex.value += 1
  }
}

const onPrev = () => {
  if (stepIndex.value > 0) {
    stepIndex.value -= 1
  }
}

const resetForm = () => {
  client.value = { name: '', email: '', phone: '', address: '', notes: '' }
  device.value = { brand_other: '', model: '', serial_number: '', description: '', condition_notes: '' }
  repair.value = { problem_reported: '', priority: 2, paid_amount: 20000, payment_method: 'cash' }
  photo.value = { file: null, caption: '' }
  stepIndex.value = 0
}

const submit = async () => {
  if (!client.value.name || !client.value.email || !device.value.model || !repair.value.problem_reported) {
    alert('Completa los campos obligatorios.')
    return
  }
  saving.value = true
  errorMessage.value = ''
  try {
    const clientRes = await api.post('/clients', client.value)
    const clientId = clientRes.data?.id
    const deviceRes = await api.post('/devices/', {
      client_id: clientId,
      model: device.value.model,
      brand_other: device.value.brand_other || null,
      serial_number: device.value.serial_number || null,
      description: device.value.description || null,
      condition_notes: device.value.condition_notes || null
    })
    const deviceId = deviceRes.data?.id
    const repairRes = await api.post('/repairs', {
      device_id: deviceId,
      problem_reported: repair.value.problem_reported,
      priority: repair.value.priority,
      paid_amount: repair.value.paid_amount,
      payment_method: repair.value.payment_method,
      payment_status: 'deposit'
    })
    const repairId = repairRes.data?.id
    if (repairId && photo.value.file) {
      const formData = new FormData()
      formData.append('file', photo.value.file)
      const uploadRes = await api.post('/uploads/images', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const path = uploadRes.data?.path
      if (path) {
        await api.post(`/repairs/${repairId}/photos`, {
          photo_url: path,
          caption: photo.value.caption || null,
          photo_type: 'general'
        })
      }
    }
    emit('completed', { client_id: clientId, device_id: deviceId, repair_id: repairId })
    resetForm()
  } catch (e) {
    console.error(e)
    errorMessage.value = e?.response?.data?.detail || e?.message || 'Error en ingreso completo'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.wizard-step-body {
  display: grid;
  gap: var(--spacer-md);
}

.wizard-step-body h4 {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--text-lg);
  font-weight: 700;
}

.row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacer-sm);
}

.row > [class*="col-"] {
  min-width: 0;
}

.col-12 {
  flex: 1 1 100%;
}

.col-md-6 {
  flex: 1 1 calc(50% - var(--spacer-sm));
}

.col-md-4 {
  flex: 1 1 calc(33.333% - var(--spacer-sm));
}

.form-label {
  display: block;
  margin-bottom: 0.35rem;
  color: var(--color-dark);
  font-size: var(--text-sm);
  font-weight: 700;
}

.form-control,
.form-select {
  width: 100%;
  min-height: 44px;
  padding: 0.7rem 0.85rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-sm);
  background: var(--color-white);
  color: var(--color-dark);
  font-size: var(--text-sm);
}

textarea.form-control {
  min-height: 90px;
  resize: vertical;
}

.alert {
  padding: 0.85rem 1rem;
  border-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--color-white) 86%, var(--color-danger) 14%);
  color: var(--color-dark);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0.65rem 0.95rem;
  border: 0;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
}

.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.btn:disabled {
  opacity: 0.6;
  cursor: wait;
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-white);
}

.d-flex {
  display: flex;
}

.justify-content-end {
  justify-content: flex-end;
}

.mt-3 {
  margin-top: var(--spacer-md);
}

@include media-breakpoint-down(md) {
  .col-md-6,
  .col-md-4 {
    flex-basis: 100%;
  }

  .d-flex {
    display: block;
  }

  .btn {
    width: 100%;
  }
}
</style>
