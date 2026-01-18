<template>
  <section class="profile">
    <div>
      <h3>{{ user.full_name || user.name || 'Usuario' }}</h3>
      <p>{{ user.email || 'sin correo' }}</p>
    </div>
    <div class="meta">
      <span>{{ user.phone || 'sin telefono' }}</span>
      <span>{{ user.role || 'cliente' }}</span>
    </div>
  </section>
</template>

<script setup>
defineProps({
  user: { type: Object, default: () => ({}) }
})
</script>

<style scoped>
.profile {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem;
  display: grid;
  gap: 0.5rem;
}
.meta {
  display: flex;
  gap: 1rem;
  color: #6b7280;
  font-size: 0.85rem;
}
</style>
