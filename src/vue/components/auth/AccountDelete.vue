<template>
  <div class="account-delete">
    <p>Eliminar cuenta es irreversible.</p>
    <button class="danger" type="button" @click="$emit('confirm')">Eliminar cuenta</button>
  </div>
</template>

<script setup>
defineEmits(['confirm'])
</script>
