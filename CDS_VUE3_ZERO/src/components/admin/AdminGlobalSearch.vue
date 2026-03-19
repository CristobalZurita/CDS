<template>
  <div ref="rootRef" class="admin-global-search">
    <input
      v-model.trim="query"
      type="search"
      class="admin-global-search__input"
      placeholder="Buscar cliente, OT, cotizacion, inventario..."
      @focus="handleFocus"
      @input="handleInput"
      @keydown.esc="closeResults"
    />

    <div v-if="showResults" class="admin-global-search__results">
      <p v-if="loading" class="admin-global-search__empty">Buscando...</p>
      <p v-else-if="!results.length" class="admin-global-search__empty">Sin resultados.</p>

      <button
        v-for="result in results"
        :key="`${result.type}-${result.id}`"
        type="button"
        class="admin-global-search__item"
        @click="openResult(result)"
      >
        <strong>{{ result.label }}</strong>
        <span>{{ formatAdminSearchType(result.type) }}<template v-if="result.subtitle"> · {{ result.subtitle }}</template></span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  formatAdminSearchType,
  resolveAdminSearchRoute,
  searchAdminRecords
} from '@/services/adminSearchService'

const router = useRouter()
const rootRef = ref(null)
const query = ref('')
const loading = ref(false)
const results = ref([])
const isOpen = ref(false)
let searchTimer = 0

const showResults = computed(() => isOpen.value && query.value.trim().length >= 2)

function clearSearchTimer() {
  if (searchTimer) {
    window.clearTimeout(searchTimer)
    searchTimer = 0
  }
}

function closeResults() {
  isOpen.value = false
}

function resetResults() {
  results.value = []
  loading.value = false
}

async function runSearch(nextQuery) {
  const trimmedQuery = String(nextQuery || '').trim()
  if (trimmedQuery.length < 2) {
    resetResults()
    return
  }

  loading.value = true
  try {
    results.value = await searchAdminRecords(trimmedQuery)
  } catch {
    results.value = []
  } finally {
    loading.value = false
  }
}

function handleInput() {
  isOpen.value = true
  clearSearchTimer()
  searchTimer = window.setTimeout(() => {
    runSearch(query.value)
  }, 180)
}

function handleFocus() {
  if (query.value.trim().length >= 2) {
    isOpen.value = true
  }
}

function handleDocumentClick(event) {
  if (!rootRef.value) return
  if (!rootRef.value.contains(event.target)) {
    closeResults()
  }
}

async function openResult(result) {
  closeResults()
  query.value = String(result?.label || '')
  await router.push(resolveAdminSearchRoute(result))
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

onBeforeUnmount(() => {
  clearSearchTimer()
  document.removeEventListener('click', handleDocumentClick)
})
</script>

<style scoped>
.admin-global-search {
  position: relative;
  min-width: 24rem;
}

.admin-global-search__input {
  min-height: 44px;
  width: 100%;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  padding: 0.7rem 0.9rem;
  font: inherit;
  background: var(--cds-white);
}

.admin-global-search__results {
  position: absolute;
  top: calc(100% + 0.35rem);
  left: 0;
  right: 0;
  z-index: 30;
  display: grid;
  gap: 0.2rem;
  padding: 0.45rem;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  background: var(--cds-white);
  box-shadow: var(--cds-shadow-md);
}

.admin-global-search__item {
  display: grid;
  gap: 0.15rem;
  border: none;
  background: transparent;
  text-align: left;
  padding: 0.65rem 0.7rem;
  border-radius: var(--cds-radius-sm);
  cursor: pointer;
}

.admin-global-search__item:hover {
  background: var(--cds-surface-1);
}

.admin-global-search__item strong {
  font-size: var(--cds-text-sm);
}

.admin-global-search__item span,
.admin-global-search__empty {
  font-size: var(--cds-text-xs);
  color: var(--cds-text-soft);
}

@media (max-width: 900px) {
  .admin-global-search {
    min-width: 100%;
  }
}
</style>
