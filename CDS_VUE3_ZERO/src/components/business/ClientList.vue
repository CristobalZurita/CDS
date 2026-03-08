<template>
  <ul class="client-list">
    <slot />
  </ul>
</template>

<style scoped>
.client-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.5rem;
}
</style>
