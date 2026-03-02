<template>
	<div class="stock-sheet">
		<div class="sheet-help">
			<h5 class="mb-2">Planilla de stock (modo simple)</h5>
			<p class="mb-0">
				Completa los campos y presiona <strong>Guardar</strong> por fila. Si no tienes stock real,
				deja <strong>0</strong> y actualiza cuando lo tengas. No puede quedar vacío.
			</p>
		</div>

		<div class="sheet-controls">
			<input v-model="query" class="form-control" placeholder="Buscar por nombre, SKU o categoría..." />
		</div>

		<div class="sheet-bulk card card-body mb-3">
			<div class="d-flex flex-wrap justify-content-between align-items-start gap-3">
				<div>
					<h6 class="mb-1">Edición masiva</h6>
					<p class="mb-0 text-muted">
						Selecciona filas visibles, aplica stock/mínimo/precio y guarda todo junto.
					</p>
				</div>
				<div class="small text-muted" data-testid="inventory-sheet-selected-count">
					{{ selectedCount }} seleccionados
				</div>
			</div>

			<div class="row g-2 mt-1 align-items-end">
				<div class="col-sm-4 col-lg-2">
					<label class="form-label mb-1">Stock</label>
					<input v-model="bulk.stock" type="number" min="0" class="form-control form-control-sm" data-testid="inventory-sheet-bulk-stock" />
				</div>
				<div class="col-sm-4 col-lg-2">
					<label class="form-label mb-1">Mínimo</label>
					<input v-model="bulk.min_stock" type="number" min="0" class="form-control form-control-sm" data-testid="inventory-sheet-bulk-min-stock" />
				</div>
				<div class="col-sm-4 col-lg-2">
					<label class="form-label mb-1">Precio</label>
					<input v-model="bulk.price" type="number" min="0" class="form-control form-control-sm" data-testid="inventory-sheet-bulk-price" />
				</div>
				<div class="col-sm-6 col-lg-2">
					<label class="form-label mb-1">Habilitado</label>
					<select v-model="bulk.enabled" class="form-select form-select-sm" data-testid="inventory-sheet-bulk-enabled">
						<option value="">Mantener</option>
						<option value="true">Sí</option>
						<option value="false">No</option>
					</select>
				</div>
				<div class="col-sm-6 col-lg-2">
					<label class="form-label mb-1">Visible tienda</label>
					<select v-model="bulk.store_visible" class="form-select form-select-sm" data-testid="inventory-sheet-bulk-store-visible">
						<option value="">Mantener</option>
						<option value="true">Sí</option>
						<option value="false">No</option>
					</select>
				</div>
				<div class="col-lg-4">
					<div class="d-flex flex-wrap gap-2">
						<button class="btn btn-sm btn-outline-secondary" data-testid="inventory-sheet-select-visible" @click="selectVisible">
							Seleccionar visibles
						</button>
						<button class="btn btn-sm btn-outline-secondary" data-testid="inventory-sheet-clear-selection" @click="clearSelection">
							Limpiar selección
						</button>
						<button class="btn btn-sm btn-outline-primary" data-testid="inventory-sheet-apply-bulk" @click="applyBulkValues">
							Aplicar a selección
						</button>
						<button class="btn btn-sm btn-primary" data-testid="inventory-sheet-save-selected" :disabled="selectedCount === 0" @click="saveSelected">
							Guardar selección
						</button>
					</div>
				</div>
			</div>
		</div>

		<div class="table-responsive">
			<table class="table table-sm align-middle">
				<thead>
					<tr>
						<th>
							<input type="checkbox" :checked="allVisibleSelected" @change="toggleVisibleSelection($event.target.checked)" />
						</th>
						<th>Nombre</th>
						<th>SKU / Código</th>
						<th>Categoría</th>
						<th>Stock</th>
						<th>Mínimo</th>
						<th>Precio</th>
						<th></th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="row in filteredRows" :key="row.id">
						<td>
							<input v-model="row.selected" type="checkbox" data-testid="inventory-sheet-row-select" />
						</td>
						<td class="name-cell">{{ row.name || '—' }}</td>
						<td>{{ row.sku || '—' }}</td>
						<td>{{ row.category || '—' }}</td>
						<td>
							<input v-model.number="row.stock" type="number" min="0" class="form-control form-control-sm" />
						</td>
						<td>
							<input v-model.number="row.min_stock" type="number" min="0" class="form-control form-control-sm" />
						</td>
						<td>
							<input v-model.number="row.price" type="number" min="0" class="form-control form-control-sm" />
						</td>
						<td class="text-end">
							<button class="btn btn-sm btn-outline-primary" @click="saveRow(row)">Guardar</button>
						</td>
					</tr>
					<tr v-if="filteredRows.length === 0">
						<td colspan="8" class="text-muted">Sin resultados.</td>
					</tr>
				</tbody>
			</table>
		</div>
	</div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
	items: {
		type: Array,
		default: () => []
	}
})

const emit = defineEmits(['save', 'save-many'])
const query = ref('')
const rows = ref([])
const bulk = ref({
	stock: '',
	min_stock: '',
	price: '',
	enabled: '',
	store_visible: '',
})

const normalizeRow = (item) => ({
	id: item.id,
	name: item.name,
	sku: item.sku,
	category: item.category,
	stock: Number(item.stock ?? item.quantity ?? 0),
	min_stock: Number(item.min_stock ?? item.min_quantity ?? 0),
	price: Number(item.price ?? 0),
	enabled: item.enabled ?? true,
	store_visible: item.store_visible ?? false,
	selected: false,
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
		const hay = [row.name, row.sku, row.category].filter(Boolean).join(' ').toLowerCase()
		return hay.includes(q)
	})
})

const selectedRows = computed(() => rows.value.filter((row) => row.selected))
const selectedCount = computed(() => selectedRows.value.length)
const allVisibleSelected = computed(() => filteredRows.value.length > 0 && filteredRows.value.every((row) => row.selected))

const toggleVisibleSelection = (checked) => {
	filteredRows.value.forEach((row) => {
		row.selected = Boolean(checked)
	})
}

const selectVisible = () => toggleVisibleSelection(true)

const clearSelection = () => {
	rows.value.forEach((row) => {
		row.selected = false
	})
}

const applyBulkValues = () => {
	const stockValue = bulk.value.stock === '' ? null : Number(bulk.value.stock)
	const minValue = bulk.value.min_stock === '' ? null : Number(bulk.value.min_stock)
	const priceValue = bulk.value.price === '' ? null : Number(bulk.value.price)
	const enabledValue = bulk.value.enabled === '' ? null : bulk.value.enabled === 'true'
	const storeVisibleValue = bulk.value.store_visible === '' ? null : bulk.value.store_visible === 'true'

	selectedRows.value.forEach((row) => {
		if (stockValue !== null && Number.isFinite(stockValue)) row.stock = stockValue
		if (minValue !== null && Number.isFinite(minValue)) row.min_stock = minValue
		if (priceValue !== null && Number.isFinite(priceValue)) row.price = priceValue
		if (enabledValue !== null) row.enabled = enabledValue
		if (storeVisibleValue !== null) row.store_visible = storeVisibleValue
	})
}

const saveRow = (row) => {
	emit('save', {
		id: row.id,
		stock: row.stock,
		min_stock: row.min_stock,
		price: row.price,
		enabled: row.enabled,
		store_visible: row.store_visible,
	})
}

const saveSelected = () => {
	if (!selectedRows.value.length) return
	emit('save-many', selectedRows.value.map((row) => ({
		id: row.id,
		stock: row.stock,
		min_stock: row.min_stock,
		price: row.price,
		enabled: row.enabled,
		store_visible: row.store_visible,
	})))
}
</script>
