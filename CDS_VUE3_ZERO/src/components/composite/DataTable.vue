<template>
  <BaseCard class="data-table-card" :padding="'none'">
    <!-- Toolbar -->
    <div v-if="showToolbar" class="table-toolbar">
      <!-- Búsqueda -->
      <div v-if="searchable" class="toolbar-search">
        <BaseInput
          v-model="searchQuery"
          type="search"
          :placeholder="searchPlaceholder"
          size="sm"
          @input="handleSearch"
        >
          <template #rightIcon>🔍</template>
        </BaseInput>
      </div>
      
      <!-- Filtros -->
      <div v-if="$slots.filters" class="toolbar-filters">
        <slot name="filters" :filters="activeFilters"></slot>
      </div>
      
      <!-- Acciones -->
      <div v-if="$slots.actions" class="toolbar-actions">
        <slot name="actions"></slot>
      </div>
    </div>

    <!-- Tabla -->
    <BaseTable
      :rows="filteredRows"
      :columns="columns"
      :loading="loading"
      :empty-text="emptyText"
      :clickable="clickable"
      :striped="striped"
      :compact="compact"
      @row-click="$emit('row-click', $event)"
    >
      <template v-for="slot in columnSlots" :key="slot" #[slot]="{ row, value, column, index }">
        <slot :name="slot" :row="row" :value="value" :column="column" :index="index"></slot>
      </template>
      
      <template #loading>
        <slot name="loading"></slot>
      </template>
      
      <template #empty>
        <slot name="empty"></slot>
      </template>
    </BaseTable>

    <!-- Paginación mejorada -->
    <div v-if="pagination && totalPages > 1" class="table-pagination-enhanced">
      <div class="pagination-info">
        Mostrando {{ startItem }}-{{ endItem }} de {{ totalItems }} resultados
      </div>
      
      <div class="pagination-controls">
        <BaseButton
          variant="ghost"
          size="sm"
          :disabled="currentPage === 1"
          @click="goToPage(1)"
        >
          «
        </BaseButton>
        <BaseButton
          variant="ghost"
          size="sm"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          ←
        </BaseButton>
        
        <span class="page-numbers">
          <button
            v-for="page in visiblePages"
            :key="page"
            class="page-number"
            :class="{ 'is-active': page === currentPage }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
        </span>
        
        <BaseButton
          variant="ghost"
          size="sm"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          →
        </BaseButton>
        <BaseButton
          variant="ghost"
          size="sm"
          :disabled="currentPage === totalPages"
          @click="goToPage(totalPages)"
        >
          »
        </BaseButton>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import BaseCard from '../base/BaseCard.vue'
import BaseTable from '../base/BaseTable.vue'
import BaseInput from '../base/BaseInput.vue'
import BaseButton from '../base/BaseButton.vue'

const props = defineProps({
  // Datos
  rows: { type: Array, required: true },
  columns: { type: Array, required: true },
  
  // Loading y vacío
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: 'No hay datos' },
  
  // Toolbar
  showToolbar: { type: Boolean, default: true },
  searchable: { type: Boolean, default: true },
  searchPlaceholder: { type: String, default: 'Buscar...' },
  searchFields: { type: Array, default: () => [] }, // Campos a buscar
  
  // Filtros
  activeFilters: { type: Object, default: () => ({}) },
  
  // Tabla
  clickable: { type: Boolean, default: false },
  striped: { type: Boolean, default: true },
  compact: { type: Boolean, default: false },
  
  // Paginación
  pagination: { type: Boolean, default: true },
  pageSize: { type: Number, default: 10 },
  currentPage: { type: Number, default: 1 }
})

const emit = defineEmits(['row-click', 'search', 'page-change', 'filter-change'])

// Estado
const searchQuery = ref('')
const internalPage = ref(props.currentPage)

// Columnas con slots personalizados
const columnSlots = computed(() => {
  return props.columns
    .filter(col => col.customSlot)
    .map(col => `cell-${col.key}`)
})

// Filtrado
const filteredRows = computed(() => {
  let result = [...props.rows]
  
  // Búsqueda
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    const fields = props.searchFields.length > 0 
      ? props.searchFields 
      : props.columns.map(c => c.key)
    
    result = result.filter(row => {
      return fields.some(field => {
        const value = getNestedValue(row, field)
        return String(value || '').toLowerCase().includes(query)
      })
    })
  }
  
  // Filtros activos
  for (const [key, value] of Object.entries(props.activeFilters)) {
    if (value !== undefined && value !== null && value !== '') {
      result = result.filter(row => {
        const rowValue = getNestedValue(row, key)
        return String(rowValue) === String(value)
      })
    }
  }
  
  return result
})

// Paginación
const totalItems = computed(() => filteredRows.value.length)
const totalPages = computed(() => Math.ceil(totalItems.value / props.pageSize))

const startItem = computed(() => {
  if (totalItems.value === 0) return 0
  return (internalPage.value - 1) * props.pageSize + 1
})

const endItem = computed(() => {
  return Math.min(internalPage.value * props.pageSize, totalItems.value)
})

// Páginas visibles (máximo 5)
const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, internalPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  
  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// Obtener valor anidado (ej: 'client.name')
function getNestedValue(obj, path) {
  return path.split('.').reduce((acc, part) => acc?.[part], obj)
}

// Handlers
function handleSearch() {
  internalPage.value = 1 // Reset a página 1 al buscar
  emit('search', searchQuery.value)
}

function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  internalPage.value = page
  emit('page-change', page)
}

// Sincronizar página externa
watch(() => props.currentPage, (newPage) => {
  internalPage.value = newPage
})
</script>

<style scoped>
.data-table-card {
  overflow: hidden;
}

/* Toolbar */
.table-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--cds-border-card);
  background: var(--cds-surface-2);
}

.toolbar-search {
  flex: 1;
  min-width: 250px;
  max-width: 400px;
}

.toolbar-search :deep(.base-input) {
  min-height: 38px;
}

.toolbar-filters {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.toolbar-actions {
  margin-left: auto;
  display: flex;
  gap: 0.5rem;
}

/* Paginación mejorada */
.table-pagination-enhanced {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid var(--cds-border-card);
  background: var(--cds-surface-1);
}

.pagination-info {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
  margin: 0 0.5rem;
}

.page-number {
  min-width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 0.5rem;
  border: 1px solid transparent;
  border-radius: var(--cds-radius-sm);
  background: transparent;
  color: var(--cds-text-normal);
  font-size: var(--cds-text-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-number:hover:not(.is-active) {
  background: var(--cds-surface-2);
}

.page-number.is-active {
  background: var(--cds-primary);
  color: var(--cds-white);
}

@media (max-width: 640px) {
  .table-toolbar {
    flex-direction: column;
  }
  
  .toolbar-search {
    max-width: none;
  }
  
  .toolbar-actions {
    margin-left: 0;
    width: 100%;
    justify-content: flex-end;
  }
  
  .table-pagination-enhanced {
    flex-direction: column;
    align-items: stretch;
  }
  
  .pagination-controls {
    justify-content: center;
  }
}
</style>
