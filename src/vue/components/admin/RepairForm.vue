<template>
  <form class="repair-form" @submit.prevent="onSubmit">
    <div class="mb-2">
      <label class="form-label">Cliente</label>
      <select v-model.number="form.client_id" class="form-select" required>
        <option :value="null">Selecciona cliente</option>
        <option v-for="client in clients" :key="client.id" :value="client.id">
          {{ client.client_code || client.id }} - {{ client.name }}
        </option>
      </select>
    </div>
    <div class="mb-2">
      <label class="form-label">Modelo/Instrumento</label>
      <input v-model="form.model" class="form-control" placeholder="Ej: Korg MS-20" required />
    </div>
    <div class="mb-2">
      <label class="form-label">Problema reportado</label>
      <textarea v-model="form.problem_reported" class="form-control" rows="2" required></textarea>
    </div>
    <div class="row g-2">
      <div class="col-md-6">
        <label class="form-label">Abono (CLP)</label>
        <input v-model.number="form.paid_amount" type="number" min="0" class="form-control" />
      </div>
      <div class="col-md-6">
        <label class="form-label">Medio de pago</label>
        <select v-model="form.payment_method" class="form-select">
          <option value="cash">Efectivo</option>
          <option value="web">Web</option>
          <option value="transfer">Transferencia</option>
        </select>
      </div>
    </div>
    <div class="mt-3 d-flex justify-content-end gap-2">
      <button type="submit" class="btn btn-primary btn-sm">Guardar</button>
    </div>
  </form>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import { useRepairs } from '@/composables/useRepairs'
const { createRepair, updateRepair } = useRepairs()
const emit = defineEmits(['saved'])
const clients = ref([])
const form = ref({
  client_id: null,
  model: '',
  problem_reported: '',
  paid_amount: 20000,
  payment_method: 'cash'
})

const loadClients = async () => {
  try {
    const res = await api.get('/clients/')
    clients.value = res.data || []
  } catch (e) {
    clients.value = []
  }
}

async function onSubmit() {
  try {
    // Si es edición, usar updateRepair, si es nuevo, usar createRepair
    await createRepair(form.value)
    emit('saved')
  } catch (e) {
    console.error('Error guardando reparación:', e)
    alert('Error guardando reparación')
  }
}

onMounted(loadClients)
</script>
