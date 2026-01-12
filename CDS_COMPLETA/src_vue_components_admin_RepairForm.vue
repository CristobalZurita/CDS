<template>
  <form @submit.prevent="onSubmit">
    <div>
      <label>Título</label>
      <input v-model="form.title" required />
    </div>
    <div>
      <label>Cliente</label>
      <input v-model="form.client_id" required />
    </div>
    <div>
      <label>Estado</label>
      <select v-model="form.status">
        <option value="pending">Pendiente</option>
        <option value="in_progress">En Proceso</option>
        <option value="waiting_parts">Esperando Repuestos</option>
        <option value="completed">Completada</option>
        <option value="ready_pickup">Lista para Retiro</option>
        <option value="delivered">Entregada</option>
        <option value="cancelled">Cancelada</option>
      </select>
    </div>
    <div>
      <label>Descripción</label>
      <textarea v-model="form.description"></textarea>
    </div>
    <button type="submit">Guardar</button>
  </form>
</template>
<script setup>
import { ref } from 'vue'
import { useRepairs } from '@/composables/useRepairs'
const { createRepair, updateRepair } = useRepairs()
const form = ref({ title: '', client_id: '', status: 'pending', description: '' })
function onSubmit() {
  // Si es edición, usar updateRepair, si es nuevo, usar createRepair
  createRepair(form.value)
}
</script>
