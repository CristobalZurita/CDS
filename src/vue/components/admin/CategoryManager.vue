<template>
  <section class="category-manager">
    <ul>
      <li v-for="cat in categories" :key="cat.id">
        <strong>{{ cat.name }}</strong>
        <span>{{ cat.description }}</span>
      </li>
    </ul>
    <p v-if="!categories.length">Sin categorias.</p>
  </section>
</template>

<script setup>
defineProps({
  categories: { type: Array, default: () => [] }
})
</script>

<style scoped lang="scss">
@import '@/scss/_core.scss';

.category-manager ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.5rem;
}
.category-manager li {
  border: 1px solid $color-gray-200-legacy;
  border-radius: 10px;
  padding: 0.75rem;
}
.category-manager span {
  display: block;
  color: $color-gray-500-legacy;
  font-size: 0.85rem;
}
</style>
