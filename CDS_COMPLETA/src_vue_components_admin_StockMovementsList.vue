<template>
  <div>
    <h2>Movimientos de Stock</h2>
    <button @click="fetchMovements">Actualizar</button>
    <table>
      <thead>
        <tr>
          <th>Producto</th>
          <th>Tipo</th>
          <th>Cantidad</th>
          <th>Fecha</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="m in movements" :key="m.id">
          <td>{{ m.product_id }}</td>
          <td>{{ m.movement_type }}</td>
          <td>{{ m.quantity }}</td>
          <td>{{ m.created_at }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'
const movements = ref([])
async function fetchMovements() {
  movements.value = await useApi().get('/api/stock-movements')
}
fetchMovements()
</script>
