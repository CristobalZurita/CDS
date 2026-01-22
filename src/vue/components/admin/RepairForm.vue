<template>
  <form @submit.prevent="onSubmit">
    <div>
      <label>Título</label>
      <input v-model="form.title" required />
    </div>
    <div>
      <label>Cliente</label>
      <select v-model.number="form.client_id" required>
        <option :value="null">Selecciona cliente</option>
        <option v-for="client in clients" :key="client.id" :value="client.id">
          {{ client.name }} ({{ client.email }})
        </option>
      </select>
    </div>
    <div>
      <label>Modelo/Instrumento</label>
      <input v-model="form.model" placeholder="Ej: Korg MS-20" required />
    </div>
    <div>
      <label>Problema reportado</label>
      <textarea v-model="form.problem_reported" required></textarea>
    </div>
    <button type="submit">Guardar</button>
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
  title: '',
  client_id: null,
  model: '',
  problem_reported: ''
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
