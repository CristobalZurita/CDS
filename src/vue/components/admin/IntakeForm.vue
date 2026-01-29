<template>
  <div class="card p-3">
    <h5 class="mb-3">Ingreso completo (cliente + instrumento + reparación)</h5>

    <div class="section-title">Cliente</div>
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

    <div class="section-title mt-3">Instrumento</div>
    <div class="row g-2">
      <div class="col-md-6">
        <label class="form-label">Marca (texto)</label>
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
        <label class="form-label">Descripción</label>
        <input v-model="device.description" class="form-control" />
      </div>
      <div class="col-12">
        <label class="form-label">Condición / Observaciones</label>
        <textarea v-model="device.condition_notes" class="form-control" rows="2"></textarea>
      </div>
    </div>

    <div class="section-title mt-3">Reparación</div>
    <div class="row g-2">
      <div class="col-12">
        <label class="form-label">Problema reportado *</label>
        <textarea v-model="repair.problem_reported" class="form-control" rows="3"></textarea>
      </div>
      <div class="col-md-4">
        <label class="form-label">Prioridad</label>
        <select v-model.number="repair.priority" class="form-select">
          <option :value="1">Alta</option>
          <option :value="2">Media</option>
          <option :value="3">Baja</option>
        </select>
      </div>
      <div class="col-md-8">
        <label class="form-label">Notas internas</label>
        <input v-model="repair.notes" class="form-control" />
      </div>
    </div>

    <div class="section-title mt-3">Foto inicial (opcional)</div>
    <div class="row g-2">
      <div class="col-md-6">
        <input type="file" class="form-control" accept="image/*" @change="onFileSelected" />
      </div>
      <div class="col-md-6">
        <input v-model="photo.caption" class="form-control" placeholder="Descripción de la foto" />
      </div>
    </div>

    <div class="mt-3 d-flex gap-2 justify-content-end">
      <button class="btn btn-secondary btn-sm" @click="resetForm" :disabled="saving">Limpiar</button>
      <button class="btn btn-primary btn-sm" @click="submit" :disabled="saving">
        {{ saving ? 'Guardando...' : 'Guardar ingreso' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '@/services/api'

const emit = defineEmits(['completed'])

const client = ref({
  name: '',
  email: '',
  phone: '',
  address: '',
  notes: ''
})

const device = ref({
  brand_other: '',
  model: '',
  serial_number: '',
  description: '',
  condition_notes: ''
})

const repair = ref({
  problem_reported: '',
  priority: 2,
  notes: ''
})

const photo = ref({
  file: null,
  caption: ''
})

const saving = ref(false)

const onFileSelected = (e) => {
  photo.value.file = e.target.files?.[0] || null
}

const resetForm = () => {
  client.value = { name: '', email: '', phone: '', address: '', notes: '' }
  device.value = { brand_other: '', model: '', serial_number: '', description: '', condition_notes: '' }
  repair.value = { problem_reported: '', priority: 2, notes: '' }
  photo.value = { file: null, caption: '' }
}

const submit = async () => {
  if (!client.value.name || !client.value.email || !device.value.model || !repair.value.problem_reported) {
    alert('Completa los campos obligatorios (cliente, email, modelo, problema).')
    return
  }

  saving.value = true
  try {
    const clientRes = await api.post('/clients', client.value)
    const clientId = clientRes.data?.id
    if (!clientId) throw new Error('No se pudo crear cliente')

    const deviceRes = await api.post('/devices/', {
      client_id: clientId,
      model: device.value.model,
      brand_other: device.value.brand_other || null,
      serial_number: device.value.serial_number || null,
      description: device.value.description || null,
      condition_notes: device.value.condition_notes || null
    })
    const deviceId = deviceRes.data?.id
    if (!deviceId) throw new Error('No se pudo crear instrumento')

    const repairRes = await api.post('/repairs', {
      device_id: deviceId,
      problem_reported: repair.value.problem_reported,
      priority: repair.value.priority
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
    alert('Error en ingreso completo')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped lang="scss">
@import '@/scss/_core.scss';

.section-title {
  font-weight: 600;
  margin-top: 0.5rem;
}
</style>
