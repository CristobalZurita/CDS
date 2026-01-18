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

<style scoped>
.category-manager ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.5rem;
}
.category-manager li {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 0.75rem;
}
.category-manager span {
  display: block;
  color: #6b7280;
  font-size: 0.85rem;
}
</style>
