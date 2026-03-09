<template>
  <section class="calculators-page">
    <section class="calculators-container">
      <header class="calculators-header">
        <h1>{{ title }}</h1>
        <p>{{ subtitle }}</p>
      </header>

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
            @click="activeCategory = cat"
          >
            {{ cat }}
          </button>
        </div>

        <form class="calculators-search" @submit.prevent="applySearch">
          <i class="fa-solid fa-magnifying-glass search-icon"></i>
          <input
            v-model="search"
            type="search"
            class="search-input"
            placeholder="Buscar por nombre"
            autocomplete="off"
          />
          <button type="submit" class="search-button">Buscar</button>
        </form>
      </div>

      <template v-if="showPopular">
        <h2 class="section-label">Más populares</h2>
        <div class="calculators-grid">
          <router-link
            v-for="item in popularItems"
            :key="item.path"
            :to="item.path"
            class="calculator-card"
          >
            <div class="calculator-card-icon">
              <i :class="item.icon"></i>
            </div>
            <div class="calculator-card-content">
              <h3>{{ item.label }}</h3>
              <p>{{ item.description }}</p>
            </div>
          </router-link>
        </div>

        <h2 class="section-label">Todas</h2>
      </template>

      <div class="calculators-grid">
        <router-link
          v-for="item in filteredItems"
          :key="item.path"
          :to="item.path"
          class="calculator-card"
        >
          <div class="calculator-card-icon">
            <i :class="item.icon"></i>
          </div>
          <div class="calculator-card-content">
            <h3>{{ item.label }}</h3>
            <p>{{ item.description }}</p>
          </div>
        </router-link>
      </div>

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

<style scoped>
.calculators-page {
  min-height: 100vh;
  padding: var(--cds-space-xl) var(--cds-space-md) var(--cds-space-2xl);
  background-color: var(--cds-background-color);
}

.calculators-container {
  max-width: var(--cds-content-max);
  margin: 0 auto;
}

.calculators-header h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
  line-height: var(--cds-leading-tight);
  text-transform: uppercase;
}

.calculators-header p {
  margin: var(--cds-space-xs) 0 0;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-base);
}

.calculators-toolbar {
  margin-top: var(--cds-space-lg);
  display: grid;
  gap: var(--cds-space-md);
}

.calculators-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
  border-bottom: 1px solid rgba(62, 60, 56, 0.3);
}

.calc-tab {
  border: none;
  background: transparent;
  color: var(--cds-dark);
  padding: 0.55rem 0.9rem 0.6rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
  border-bottom: 3px solid transparent;
}

.calc-tab--active {
  color: var(--cds-primary);
  border-bottom-color: var(--cds-primary);
}

.calculators-search {
  position: relative;
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 0.55rem;
}

.search-icon {
  position: absolute;
  left: 0.9rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--cds-text-muted);
  pointer-events: none;
  font-size: 0.95rem;
}

.search-input {
  width: 100%;
  border: 1px solid rgba(62, 60, 56, 0.25);
  border-radius: 999px;
  padding: 0.72rem 1rem 0.72rem 2.45rem;
  font-size: var(--cds-text-base);
  background: rgba(255, 255, 255, 0.75);
  color: var(--cds-dark);
  outline: none;
  box-sizing: border-box;
}

.search-input:focus {
  border-color: var(--cds-primary);
}

.search-button {
  border: none;
  border-radius: 999px;
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  padding: 0.7rem 1.2rem;
  cursor: pointer;
}

.section-label {
  margin: var(--cds-space-md) 0 var(--cds-space-sm);
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-dark);
}

.calculators-grid {
  display: grid;
  gap: var(--cds-space-md);
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
}

.calculator-card {
  border: 1px solid rgba(62, 60, 56, 0.25);
  border-radius: var(--cds-radius-md);
  background: rgba(255, 255, 255, 0.22);
  text-decoration: none;
  color: inherit;
  padding: var(--cds-space-md);
  min-height: 260px;
  display: grid;
  align-content: start;
  gap: 0.75rem;
  transition: border-color 0.15s ease, transform 0.15s ease;
}

.calculator-card:hover {
  border-color: var(--cds-primary);
  transform: translateY(-2px);
}

.calculator-card-icon {
  width: 74px;
  height: 60px;
  border: 1px solid color-mix(in srgb, var(--cds-primary) 75%, white);
  border-radius: 0.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--cds-primary);
  font-size: 1.65rem;
  margin: 0 auto;
}

.calculator-card-content {
  text-align: center;
}

.calculator-card-content h3 {
  margin: 0;
  font-size: var(--cds-text-base);
  line-height: 1.3;
  color: var(--cds-dark);
}

.calculator-card-content p {
  margin: 0.55rem 0 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  line-height: 1.45;
}

.no-results {
  margin-top: var(--cds-space-xl);
  text-align: center;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-base);
}

.calculators-actions {
  margin-top: var(--cds-space-xl);
  display: flex;
  justify-content: center;
}

.back-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.7rem 1.1rem;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--cds-primary) 45%, transparent);
  color: color-mix(in srgb, var(--cds-primary) 85%, #6b3000);
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
}

@media (min-width: 960px) {
  .calculators-toolbar {
    grid-template-columns: minmax(0, 1fr) minmax(280px, 430px);
    align-items: end;
  }

  .calculators-search {
    margin-left: var(--cds-space-md);
  }
}
</style>
