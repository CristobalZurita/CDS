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
