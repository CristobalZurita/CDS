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
