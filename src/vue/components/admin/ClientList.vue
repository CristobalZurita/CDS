<template>
  <ul class="client-list">
    <li v-for="client in clients" :key="client.id" @click="$emit('select', client)">
      <div class="client-header">
        <strong>{{ client.name }}</strong>
        <span v-if="client.client_code" class="client-code">{{ client.client_code }}</span>
      </div>
      <span>{{ client.email || 'Sin correo' }}</span>
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
.client-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem;
}
.client-code {
  font-size: 0.85rem;
  font-weight: 700;
  color: #ec6b00;
}
.client-list span {
  display: block;
  color: #6b7280;
  font-size: 0.95rem;
}
</style>
