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

		<div class="table-responsive">
			<table class="table table-sm align-middle">
				<thead>
					<tr>
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
						<td colspan="7" class="text-muted">Sin resultados.</td>
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

const emit = defineEmits(['save'])
const query = ref('')
const rows = ref([])

const normalizeRow = (item) => ({
	id: item.id,
	name: item.name,
	sku: item.sku,
	category: item.category,
	stock: Number(item.stock ?? item.quantity ?? 0),
	min_stock: Number(item.min_stock ?? item.min_quantity ?? 0),
	price: Number(item.price ?? 0)
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

const saveRow = (row) => {
	emit('save', {
		id: row.id,
		stock: row.stock,
		min_stock: row.min_stock,
		price: row.price
	})
}
</script>
