<template>
  <div>
    <h2>Instrumentos</h2>
    <button @click="fetchInstruments">Actualizar</button>
    <table>
      <thead>
        <tr>
          <th>Marca</th>
          <th>Modelo</th>
          <th>Tipo</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="inst in instruments" :key="inst.id">
          <td>{{ inst.brand_id }}</td>
          <td>{{ inst.model }}</td>
          <td>{{ inst.type }}</td>
          <td>
            <button @click="editInstrument(inst)">Editar</button>
            <button @click="deleteInstrument(inst.id)">Borrar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
import { useInstruments } from '@/composables/useInstruments'
const { instruments, fetchInstruments, deleteInstrument } = useInstruments()
function editInstrument(inst) {
  // Implementar navegación o modal de edición
}
</script>
