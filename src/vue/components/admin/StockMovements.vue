<template>
  <table class="table">
    <thead>
      <tr>
        <th>Item</th>
        <th>Cantidad</th>
        <th>Fecha</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="move in movements" :key="move.id">
        <td>{{ move.item_name || move.item_id }}</td>
        <td>{{ move.quantity }}</td>
        <td>{{ formatDate(move.created_at) }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script setup>
defineProps({
  movements: { type: Array, default: () => [] }
})

const formatDate = (value) => {
  if (!value) return '—'
  return new Intl.DateTimeFormat('es-CL').format(new Date(value))
}
</script>
