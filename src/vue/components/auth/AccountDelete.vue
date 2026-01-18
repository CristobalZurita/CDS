<template>
  <div class="account-delete">
    <p>Eliminar cuenta es irreversible.</p>
    <button class="danger" type="button" @click="$emit('confirm')">Eliminar cuenta</button>
  </div>
</template>

<script setup>
defineEmits(['confirm'])
</script>

<style scoped>
.account-delete {
  padding: 1rem;
  border: 1px solid #fecaca;
  border-radius: 12px;
  background: #fff1f2;
}
.danger {
  margin-top: 0.5rem;
  background: #dc2626;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 0.9rem;
  cursor: pointer;
}
</style>
