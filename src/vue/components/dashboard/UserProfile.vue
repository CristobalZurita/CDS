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

<style lang="scss" scoped>
@import '@/scss/_core.scss';

.profile {
  border: 1px solid $color-gray-200-legacy;
  border-radius: $border-radius-lg;
  padding: $spacer-md;
  display: grid;
  gap: $spacer-sm;
}

.meta {
  display: flex;
  gap: $spacer-md;
  color: $color-gray-500-legacy;
  font-size: $text-sm;
}
</style>
