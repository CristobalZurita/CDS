<template>
  <ul class="client-list">
    <li v-for="client in clients" :key="client.id" @click="$emit('select', client)">
      <strong>{{ client.name }}</strong>
      <span>{{ client.email }}</span>
    </li>
  </ul>
</template>

<script setup>
defineProps({
  clients: { type: Array, default: () => [] }
})

defineEmits(['select'])
</script>

<style scoped>
.client-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.5rem;
}
.client-list li {
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
}
.client-list span {
  display: block;
  color: #6b7280;
  font-size: 0.85rem;
}
</style>
