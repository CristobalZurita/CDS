<template>
  <section class="panel-card">
    <div class="panel-header">
      <h2>Materiales y herramientas</h2>
    </div>

    <!-- Filtro por tipo -->
    <div class="type-tabs">
      <button
        v-for="tab in typeTabs"
        :key="tab.key"
        type="button"
        class="type-tab"
        :class="{ 'is-active': activeType === tab.key }"
        @click="activeType = tab.key"
      >
        {{ tab.label }}
        <span class="tab-count">{{ tab.count }}</span>
      </button>
    </div>

    <!-- Formulario de adición -->
    <div class="add-form">
      <div class="add-fields">
        <div class="field-wrap field-product">
          <label class="field-label">
            {{ activeType === 'herramienta' ? 'Herramienta' : activeType === 'insumo' ? 'Insumo' : 'Componente' }}
          </label>
          <select v-model="selectedProductId" class="field-select" :disabled="loadingInventory">
            <option value="">{{ loadingInventory ? 'Cargando...' : 'Seleccionar...' }}</option>
            <option
              v-for="item in filteredItems"
              :key="item.id"
              :value="item.id"
              :disabled="!isHerramienta(item) && (item.available_stock ?? 0) <= 0"
            >
              {{ item.name }}{{ item.sku ? ` · ${item.sku}` : '' }}
              <template v-if="!isHerramienta(item)"> — stock: {{ item.available_stock ?? item.stock_quantity ?? 0 }}</template>
            </option>
          </select>
        </div>

        <div class="field-wrap field-qty">
          <label class="field-label">{{ isHerramientaSelected ? 'Usos' : 'Cant.' }}</label>
          <input
            v-model.number="selectedQty"
            type="number"
            class="field-input"
            :min="1"
            :max="isHerramientaSelected ? 999 : (selectedItem?.available_stock ?? 999)"
          />
        </div>

        <button
          type="button"
          class="btn-add"
          :disabled="!canAdd || adding"
          @click="addComponent"
        >
          {{ adding ? '...' : '+ Agregar' }}
        </button>
      </div>
      <p v-if="addError" class="field-error">{{ addError }}</p>
    </div>

    <!-- Lista registrada -->
    <div v-if="loadingComponents" class="empty-state">Cargando...</div>
    <div v-else-if="components.length === 0" class="empty-state">
      No hay ítems registrados en esta OT.
    </div>
    <table v-else class="components-table">
      <thead>
        <tr>
          <th>Ítem</th>
          <th class="col-type">Tipo</th>
          <th class="col-qty">Cant.</th>
          <th class="col-action"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="comp in components" :key="comp.id">
          <td>{{ comp.component_name || `#${comp.component_id}` }}</td>
          <td class="col-type">
            <span class="type-badge" :class="compTypeBadge(comp)">
              {{ compTypeLabel(comp) }}
            </span>
          </td>
          <td class="col-qty">{{ comp.quantity }}</td>
          <td class="col-action">
            <button
              type="button"
              class="btn-remove"
              :disabled="removing === comp.id"
              @click="removeComponent(comp.id)"
            >
              Quitar
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '@/services/api'

const props = defineProps({
  repairId: { type: Number, required: true }
})

const inventoryItems = ref([])
const components = ref([])
const loadingInventory = ref(false)
const loadingComponents = ref(false)
const adding = ref(false)
const removing = ref(null)
const addError = ref('')
const activeType = ref('componente')
const selectedProductId = ref('')
const selectedQty = ref(1)

// Clasificación por nombre de categoría
function isHerramienta(item) {
  return String(item.category ?? '').toLowerCase().includes('herramienta')
}
function isInsumo(item) {
  return String(item.category ?? '').toLowerCase().includes('insumo')
}
function typeOf(item) {
  if (isHerramienta(item)) return 'herramienta'
  if (isInsumo(item)) return 'insumo'
  return 'componente'
}

const typeTabs = computed(() => [
  { key: 'componente', label: 'Componentes', count: inventoryItems.value.filter(i => typeOf(i) === 'componente').length },
  { key: 'insumo',     label: 'Insumos',     count: inventoryItems.value.filter(i => typeOf(i) === 'insumo').length },
  { key: 'herramienta',label: 'Herramientas',count: inventoryItems.value.filter(i => typeOf(i) === 'herramienta').length },
])

const filteredItems = computed(() =>
  inventoryItems.value.filter(i => typeOf(i) === activeType.value)
)

const selectedItem = computed(() =>
  inventoryItems.value.find(i => i.id === selectedProductId.value) ?? null
)
const isHerramientaSelected = computed(() =>
  selectedItem.value ? isHerramienta(selectedItem.value) : false
)
const canAdd = computed(() => selectedProductId.value !== '' && selectedQty.value >= 1)

// Badges en tabla
function compTypeLabel(comp) {
  const name = String(comp.component_name ?? '').toLowerCase()
  const notes = String(comp.notes ?? '').toLowerCase()
  if (notes.includes('herramienta') || name.includes('cautín') || name.includes('osciloscopio')) return 'Herramienta'
  if (notes.includes('insumo') || name.includes('soldadura') || name.includes('alcohol')) return 'Insumo'
  return 'Componente'
}
function compTypeBadge(comp) {
  const label = compTypeLabel(comp)
  if (label === 'Herramienta') return 'badge-tool'
  if (label === 'Insumo') return 'badge-supply'
  return 'badge-component'
}

// API
async function fetchInventory() {
  loadingInventory.value = true
  try {
    const res = await api.get('/inventory/')
    inventoryItems.value = res.data ?? res
  } finally {
    loadingInventory.value = false
  }
}

async function fetchComponents() {
  loadingComponents.value = true
  try {
    const res = await api.get(`/repairs/${props.repairId}/components`)
    components.value = res.data ?? res
  } finally {
    loadingComponents.value = false
  }
}

async function addComponent() {
  if (!canAdd.value) return
  adding.value = true
  addError.value = ''
  try {
    await api.post(`/repairs/${props.repairId}/components`, {
      component_table: 'products',
      component_id: selectedProductId.value,
      quantity: selectedQty.value,
      skip_stock_check: isHerramientaSelected.value
    })
    selectedProductId.value = ''
    selectedQty.value = 1
    await fetchComponents()
  } catch (err) {
    addError.value = err?.response?.data?.detail || 'Error al agregar'
  } finally {
    adding.value = false
  }
}

async function removeComponent(usageId) {
  removing.value = usageId
  try {
    await api.delete(`/repairs/${props.repairId}/components/${usageId}`)
    await fetchComponents()
  } finally {
    removing.value = null
  }
}

watch(activeType, () => {
  selectedProductId.value = ''
  selectedQty.value = 1
  addError.value = ''
})

onMounted(() => {
  fetchInventory()
  fetchComponents()
})
</script>

<style scoped>
.panel-header {
  margin-bottom: 1rem;
}
.panel-header h2 {
  font-size: var(--cds-text-lg);
  font-weight: 700;
  color: var(--cds-text-normal);
  margin: 0;
}

/* Tabs */
.type-tabs {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--cds-border-card);
  padding-bottom: 0.75rem;
}
.type-tab {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.85rem;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-sm);
  background: transparent;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  cursor: pointer;
  font-weight: 500;
  transition: all 0.15s;
}
.type-tab:hover {
  border-color: var(--cds-primary);
  color: var(--cds-primary);
}
.type-tab.is-active {
  background: var(--cds-primary);
  border-color: var(--cds-primary);
  color: var(--cds-white);
}
.tab-count {
  font-size: var(--cds-text-xs);
  opacity: 0.75;
}

/* Form */
.add-form { margin-bottom: 1.5rem; }
.add-fields {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
  flex-wrap: wrap;
}
.field-wrap { display: flex; flex-direction: column; gap: 0.3rem; }
.field-product { flex: 1; min-width: 180px; }
.field-qty { width: 5rem; }
.field-label {
  font-size: var(--cds-text-sm);
  font-weight: 600;
  color: var(--cds-text-muted);
}
.field-select,
.field-input {
  height: 2.5rem;
  padding: 0 0.75rem;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  font-size: var(--cds-text-sm);
  color: var(--cds-text-normal);
  background: var(--cds-white);
  width: 100%;
}
.field-select:focus,
.field-input:focus {
  outline: none;
  border-color: var(--cds-primary);
}
.btn-add {
  height: 2.5rem;
  padding: 0 1.25rem;
  background: var(--cds-primary);
  color: var(--cds-white);
  border: none;
  border-radius: var(--cds-radius-md);
  font-size: var(--cds-text-sm);
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  align-self: flex-end;
}
.btn-add:disabled { opacity: 0.5; cursor: not-allowed; }
.field-error {
  margin-top: 0.4rem;
  font-size: var(--cds-text-sm);
  color: var(--cds-error, #dc2626);
}

/* Table */
.empty-state {
  text-align: center;
  padding: 1.5rem;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}
.components-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--cds-text-sm);
}
.components-table th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  font-weight: 600;
  color: var(--cds-text-muted);
  border-bottom: 1px solid var(--cds-border-card);
}
.components-table td {
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid var(--cds-light-2);
  color: var(--cds-text-normal);
}
.col-type { width: 7rem; }
.col-qty  { width: 4rem; text-align: center; }
.col-action { width: 5rem; text-align: right; }

.type-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: var(--cds-radius-sm);
  font-size: var(--cds-text-xs);
  font-weight: 600;
}
.badge-component { background: rgba(236, 107, 0, 0.1); color: var(--cds-primary); }
.badge-supply    { background: #fef3c7; color: #92400e; }
.badge-tool      { background: #dbeafe; color: #1e40af; }

.btn-remove {
  background: none;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-sm);
  padding: 0.2rem 0.6rem;
  font-size: var(--cds-text-xs);
  color: var(--cds-text-muted);
  cursor: pointer;
}
.btn-remove:hover { border-color: var(--cds-error, #dc2626); color: var(--cds-error, #dc2626); }
.btn-remove:disabled { opacity: 0.4; cursor: not-allowed; }

@media (max-width: 768px) {
  .add-fields { flex-direction: column; }
  .field-qty { width: 100%; }
  .btn-add { width: 100%; }
}
</style>
