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

<style lang="scss" scoped>
@import '@/scss/_core.scss';

.client-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: $spacer-sm;
}

.client-list li {
  padding: 0.75rem;
  border: 1px solid $color-gray-200-legacy;
  border-radius: $border-radius-md;
  cursor: pointer;
}

.client-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem;
}

.client-code {
  font-size: $text-sm;
  font-weight: $fw-bold;
  color: $color-primary;
}

.client-list span {
  display: block;
  color: $color-gray-500-legacy;
  font-size: $text-base;
}
</style>
