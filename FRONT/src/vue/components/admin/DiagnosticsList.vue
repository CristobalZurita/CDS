<template>
  <div>
    <h2>Diagnósticos</h2>
    <button @click="fetchDiagnostics">Actualizar</button>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Reparación</th>
          <th>Costo estimado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="d in diagnostics" :key="d.id">
          <td>{{ d.id }}</td>
          <td>{{ d.repair_id }}</td>
          <td>{{ d.quote_total }}</td>
          <td>
            <button @click="editDiagnostic(d)">Editar</button>
            <button @click="deleteDiagnostic(d.id)">Borrar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
import { useDiagnostics } from '@/composables/useDiagnostics'
const { diagnostics, fetchDiagnostics, deleteDiagnostic } = useDiagnostics()
function editDiagnostic(d) {
  // Implementar edición
}
</script>
