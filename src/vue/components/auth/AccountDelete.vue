<template>
  <div class="account-delete">
    <p>Eliminar cuenta es irreversible.</p>
    <button class="danger" type="button" @click="$emit('confirm')">Eliminar cuenta</button>
  </div>
</template>

<script setup>
defineEmits(['confirm'])
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.account-delete {
  padding: 1rem;
  border: 1px solid $color-red-150-legacy;
  border-radius: 12px;
  background: $color-red-25-legacy;
}
.danger {
  margin-top: 0.5rem;
  background: $color-red-600-legacy;
  color: $color-white;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 0.9rem;
  cursor: pointer;
}
</style>
