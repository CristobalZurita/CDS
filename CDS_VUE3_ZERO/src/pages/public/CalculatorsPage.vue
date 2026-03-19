<template>
  <section class="calculators-page">
    <section class="calculators-container">
      <header class="calculators-header">
        <h1>{{ title }}</h1>
        <p>{{ subtitle }}</p>
      </header>

      <CalculatorsToolbar
        :categories="categories"
        :active-category="activeCategory"
        :search="search"
        @update:active-category="activeCategory = $event"
        @update:search="search = $event"
        @search-submit="applySearch"
      />


      <CalculatorsGrid :items="filteredItems" />

      <p v-if="filteredItems.length === 0" class="no-results">
        No hay calculadoras que coincidan con tu búsqueda.
      </p>

      <div class="calculators-actions">
        <router-link to="/" class="back-link">Volver al inicio</router-link>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import CalculatorsGrid from '@/components/business/CalculatorsGrid.vue'
import CalculatorsToolbar from '@/components/business/CalculatorsToolbar.vue'
import { useCalculatorsPage } from '@/composables/useCalculatorsPage'

const { title, subtitle, categories, calculatorItems, popularItems } = useCalculatorsPage()

const search = ref('')
const activeCategory = ref('Todas')

const showPopular = computed(() =>
  activeCategory.value === 'Todas' && search.value.trim() === ''
)

const filteredItems = computed(() => {
  const q = search.value.trim().toLowerCase()
  return calculatorItems.value.filter((item) => {
    const matchCategory = activeCategory.value === 'Todas' || item.category === activeCategory.value
    const matchSearch = !q || item.label.toLowerCase().includes(q) || item.description.toLowerCase().includes(q)
    return matchCategory && matchSearch
  })
})

function applySearch() {
  search.value = search.value.trim()
}
</script>
<style scoped src="../../components/business/calculatorsPageShared.css"></style>
