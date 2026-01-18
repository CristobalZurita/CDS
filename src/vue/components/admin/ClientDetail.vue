<template>
  <section class="client-detail">
    <h4>{{ client.name || 'Cliente' }}</h4>
    <p>{{ client.email || 'sin correo' }}</p>
    <p>{{ client.phone || 'sin telefono' }}</p>
    <p>{{ client.notes || 'sin notas' }}</p>
  </section>
</template>

<script setup>
defineProps({
  client: { type: Object, default: () => ({}) }
})
</script>

<style scoped>
.client-detail {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem;
}
</style>
