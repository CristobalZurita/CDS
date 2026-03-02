<template>
  <div class="stock-states">
    <div class="sheet-help">
      <h5 class="mb-2">Estados de stock (detalle)</h5>
      <p class="mb-0">
        Ajusta estados por componente. Estos estados se descuentan del stock disponible.
      </p>
    </div>

    <div class="sheet-controls">
      <input v-model="query" class="form-control" placeholder="Buscar por SKU o nombre..." />
    </div>

    <div class="table-responsive">
      <table class="table table-sm align-middle">
        <thead>
          <tr>
            <th>SKU</th>
            <th>Nombre</th>
            <th>Stock</th>
            <th>Reservado</th>
            <th>En trabajo</th>
            <th>En tránsito</th>
            <th>En revisión</th>
            <th>Dañado</th>
            <th>Consumo interno</th>
            <th>Disponible</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in filteredRows" :key="row.id">
            <td>{{ row.sku }}</td>
            <td>{{ row.name }}</td>
            <td>
              <input v-model.number="row.stock" type="number" min="0" class="form-control form-control-sm" />
            </td>
            <td>
              <input v-model.number="row.quantity_reserved" type="number" min="0" class="form-control form-control-sm" />
            </td>
            <td>
              <input v-model.number="row.quantity_in_work" type="number" min="0" class="form-control form-control-sm" />
            </td>
            <td>
              <input v-model.number="row.quantity_in_transit" type="number" min="0" class="form-control form-control-sm" />
            </td>
            <td>
              <input v-model.number="row.quantity_under_review" type="number" min="0" class="form-control form-control-sm" />
            </td>
            <td>
              <input v-model.number="row.quantity_damaged" type="number" min="0" class="form-control form-control-sm" />
            </td>
            <td>
              <input v-model.number="row.quantity_internal_use" type="number" min="0" class="form-control form-control-sm" />
            </td>
            <td class="fw-bold">{{ available(row) }}</td>
            <td class="text-end">
              <button class="btn btn-sm btn-outline-primary" @click="saveRow(row)">Guardar</button>
            </td>
          </tr>
          <tr v-if="filteredRows.length === 0">
            <td colspan="11" class="text-muted">Sin resultados.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] }
})
const emit = defineEmits(['save'])
const query = ref('')
const rows = ref([])

const normalizeRow = (item) => ({
  id: item.id,
  sku: item.sku,
  name: item.name,
  stock: Number(item.stock ?? 0),
  quantity_reserved: Number(item.quantity_reserved ?? 0),
  quantity_in_work: Number(item.quantity_in_work ?? 0),
  quantity_in_transit: Number(item.quantity_in_transit ?? 0),
  quantity_under_review: Number(item.quantity_under_review ?? 0),
  quantity_damaged: Number(item.quantity_damaged ?? 0),
  quantity_internal_use: Number(item.quantity_internal_use ?? 0)
})

watch(
  () => props.items,
  (val) => {
    rows.value = Array.isArray(val) ? val.map(normalizeRow) : []
  },
  { immediate: true }
)

const filteredRows = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((row) => {
    const hay = [row.sku, row.name].filter(Boolean).join(' ').toLowerCase()
    return hay.includes(q)
  })
})

const available = (row) => {
  const blocked = row.quantity_reserved + row.quantity_in_work + row.quantity_in_transit + row.quantity_under_review + row.quantity_damaged + row.quantity_internal_use
  return Math.max(row.stock - blocked, 0)
}

const saveRow = (row) => {
  emit('save', { ...row })
}
</script>
