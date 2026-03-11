<template>
  <div class="base-table-wrapper">
    <!-- Loading state -->
    <div v-if="loading" class="table-loading">
      <slot name="loading">
        <div class="loading-spinner"></div>
        <span>Cargando...</span>
      </slot>
    </div>

    <!-- Empty state -->
    <div v-else-if="!rows.length" class="table-empty">
      <slot name="empty">
        <p>{{ emptyText }}</p>
      </slot>
    </div>

    <!-- Table -->
    <div v-else class="table-container" :class="{ 'has-sticky-header': stickyHeader }">
      <table class="base-table" :class="tableClasses">
        <thead>
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              :class="{
                'is-sortable': column.sortable,
                'is-sorted': sortKey === column.key,
                [`align-${column.align || 'left'}`]: true
              }"
              :style="{ width: column.width }"
              @click="column.sortable && handleSort(column.key)"
            >
              <span class="th-content">
                {{ column.label }}
                <span v-if="column.sortable" class="sort-icon">
                  <template v-if="sortKey === column.key">
                    {{ sortOrder === 'asc' ? '↑' : '↓' }}
                  </template>
                  <template v-else>⇅</template>
                </span>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, rowIndex) in sortedRows"
            :key="getRowKey(row, rowIndex)"
            :class="{
              'is-clickable': clickable,
              'is-selected': selectedKey === getRowKey(row, rowIndex)
            }"
            @click="handleRowClick(row, rowIndex)"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              :class="[`align-${column.align || 'left'}`]"
            >
              <slot
                :name="`cell-${column.key}`"
                :row="row"
                :value="getCellValue(row, column.key)"
                :column="column"
                :index="rowIndex"
              >
                {{ formatCellValue(getCellValue(row, column.key), column.format) }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="pagination && totalPages > 1" class="table-pagination">
      <button
        class="pagination-btn"
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
      >
        ← Anterior
      </button>
      
      <span class="pagination-info">
        Página {{ currentPage }} de {{ totalPages }}
      </span>
      
      <button
        class="pagination-btn"
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
      >
        Siguiente →
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  rows: { type: Array, required: true },
  columns: { 
    type: Array, 
    required: true,
    // Cada columna: { key, label, sortable?, width?, align?, format? }
  },
  rowKey: { type: [String, Function], default: 'id' },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: 'No hay datos para mostrar' },
  clickable: { type: Boolean, default: false },
  stickyHeader: { type: Boolean, default: false },
  compact: { type: Boolean, default: false },
  striped: { type: Boolean, default: false },
  bordered: { type: Boolean, default: false },
  // Paginación
  pagination: { type: Boolean, default: false },
  pageSize: { type: Number, default: 10 },
  currentPage: { type: Number, default: 1 }
})

const emit = defineEmits(['row-click', 'sort', 'page-change'])

// Sorting interno
const sortKey = ref('')
const sortOrder = ref('asc')

const tableClasses = computed(() => ({
  'is-compact': props.compact,
  'is-striped': props.striped,
  'is-bordered': props.bordered
}))

// Obtener key única de fila
function getRowKey(row, index) {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(row)
  }
  return row[props.rowKey] || index
}

// Obtener valor de celda (soporta nested keys como 'client.name')
function getCellValue(row, key) {
  const keys = key.split('.')
  let value = row
  for (const k of keys) {
    value = value?.[k]
    if (value === undefined || value === null) break
  }
  return value
}

// Formatear valor de celda
function formatCellValue(value, format) {
  if (value === undefined || value === null) return '—'
  
  switch (format) {
    case 'date':
      return new Date(value).toLocaleDateString('es-CL')
    case 'datetime':
      return new Date(value).toLocaleString('es-CL')
    case 'currency':
      return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP'
      }).format(value)
    case 'number':
      return new Intl.NumberFormat('es-CL').format(value)
    case 'boolean':
      return value ? 'Sí' : 'No'
    default:
      return String(value)
  }
}

// Filas ordenadas
const sortedRows = computed(() => {
  let data = [...props.rows]
  
  if (props.pagination) {
    const start = (props.currentPage - 1) * props.pageSize
    const end = start + props.pageSize
    data = data.slice(start, end)
  }
  
  if (!sortKey.value) return data
  
  return data.sort((a, b) => {
    const aVal = getCellValue(a, sortKey.value)
    const bVal = getCellValue(b, sortKey.value)
    
    if (aVal === bVal) return 0
    
    const comparison = aVal > bVal ? 1 : -1
    return sortOrder.value === 'asc' ? comparison : -comparison
  })
})

// Paginación
const totalPages = computed(() => Math.ceil(props.rows.length / props.pageSize))

function handleSort(key) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
  emit('sort', { key: sortKey.value, order: sortOrder.value })
}

function handleRowClick(row, index) {
  if (props.clickable) {
    emit('row-click', row, index)
  }
}

function goToPage(page) {
  emit('page-change', page)
}
</script>

<style scoped>
.base-table-wrapper {
  width: 100%;
}

/* Loading state */
.table-loading,
.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: var(--cds-text-muted);
  gap: 1rem;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--cds-light-3);
  border-top-color: var(--cds-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Table container */
.table-container {
  overflow-x: auto;
  border-radius: var(--cds-radius-md);
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
}

.table-container.has-sticky-header {
  max-height: 500px;
  overflow-y: auto;
}

/* Table base */
.base-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--cds-text-base);
  background: var(--cds-white);
}

/* Header */
.base-table thead {
  background: color-mix(in srgb, var(--cds-light) 10%, white);
}

.table-container.has-sticky-header .base-table thead {
  position: sticky;
  top: 0;
  z-index: 10;
}

.base-table th {
  padding: 0.875rem 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--cds-text-normal);
  border-bottom: 2px solid color-mix(in srgb, var(--cds-light) 50%, white);
  white-space: nowrap;
}

.base-table th.is-sortable {
  cursor: pointer;
  user-select: none;
}

.base-table th.is-sortable:hover {
  background: color-mix(in srgb, var(--cds-light) 20%, white);
}

.base-table th.is-sorted {
  color: var(--cds-primary);
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-icon {
  font-size: 0.75rem;
  opacity: 0.5;
}

.base-table th.is-sorted .sort-icon {
  opacity: 1;
}

/* Body */
.base-table td {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  color: var(--cds-text-normal);
}

.base-table tbody tr:last-child td {
  border-bottom: none;
}

.base-table tbody tr:hover {
  background: color-mix(in srgb, var(--cds-light) 5%, white);
}

.base-table tbody tr.is-clickable {
  cursor: pointer;
}

.base-table tbody tr.is-selected {
  background: color-mix(in srgb, var(--cds-primary) 8%, white);
}

/* Alineaciones */
.align-left { text-align: left; }
.align-center { text-align: center; }
.align-right { text-align: right; }

/* Variantes */
.base-table.is-compact th,
.base-table.is-compact td {
  padding: 0.5rem 0.75rem;
}

.base-table.is-striped tbody tr:nth-child(even) {
  background: color-mix(in srgb, var(--cds-light) 5%, white);
}

.base-table.is-bordered th,
.base-table.is-bordered td {
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
}

/* Paginación */
.table-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 1px solid color-mix(in srgb, var(--cds-light) 50%, white);
  border-radius: var(--cds-radius-sm);
  background: var(--cds-white);
  color: var(--cds-text-normal);
  font-size: var(--cds-text-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  border-color: var(--cds-primary);
  color: var(--cds-primary);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}
</style>
