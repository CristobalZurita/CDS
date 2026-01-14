<template>
  <div>
    <h2>Reparaciones</h2>
    <button @click="fetchRepairs">Actualizar</button>
    <table>
      <thead>
        <tr>
          <th>Título</th>
          <th>Cliente</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="repair in repairs" :key="repair.id">
          <td>{{ repair.title }}</td>
          <td>{{ repair.client_id }}</td>
          <td>{{ repair.status }}</td>
          <td>
            <button @click="editRepair(repair)">Editar</button>
            <button @click="deleteRepair(repair.id)">Borrar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
import { useRepairs } from '@/composables/useRepairs'
const { repairs, fetchRepairs, deleteRepair } = useRepairs()
function editRepair(repair) {
  // Implementar navegación o modal de edición
}
</script>
