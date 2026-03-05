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
