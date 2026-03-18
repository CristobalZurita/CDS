<template>
  <div class="calculators-toolbar">
    <div class="calculators-tabs" role="tablist">
      <button
        v-for="cat in categories"
        :key="cat"
        class="calc-tab"
        :class="{ 'calc-tab--active': activeCategory === cat }"
        type="button"
        role="tab"
        :aria-selected="activeCategory === cat"
        @click="$emit('update:active-category', cat)"
      >
        {{ cat }}
      </button>
    </div>

    <form class="calculators-search" @submit.prevent="$emit('search-submit')">
      <i class="fa-solid fa-magnifying-glass search-icon"></i>
      <input
        :value="search"
        type="search"
        class="search-input"
        placeholder="Buscar por nombre"
        autocomplete="off"
        @input="$emit('update:search', $event.target.value)"
      />
      <button type="submit" class="search-button">Buscar</button>
    </form>
  </div>
</template>

<script setup>
defineProps({
  categories: { type: Array, default: () => [] },
  activeCategory: { type: String, default: 'Todas' },
  search: { type: String, default: '' }
})

defineEmits(['update:active-category', 'update:search', 'search-submit'])
</script>

<style scoped src="./calculatorsPageShared.css"></style>
