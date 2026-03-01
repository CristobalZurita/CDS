<template>
	<div class="components-manager">
		<div class="section-header">
			<h5 class="section-title">
				<i class="fa-solid fa-microchip me-2"></i>Materiales Utilizados
			</h5>
			<button class="btn btn-sm btn-primary" @click="showAddForm = !showAddForm" :disabled="isReadOnly">
				<i class="fa-solid fa-plus me-1"></i> Agregar Material
			</button>
		</div>

		<!-- Formulario para agregar componente -->
		<div v-if="showAddForm && !isReadOnly" class="add-form">
			<div class="row g-2">
				<div class="col-md-4">
					<div class="filters-grid">
						<div>
							<label class="form-label">Familia</label>
							<select v-model="familyFilter" class="form-select" @change="onFiltersChanged">
								<option value="ALL">Todas</option>
								<option value="RES">RES</option>
								<option value="CAPC">CAPC</option>
								<option value="CAPE">CAPE</option>
								<option value="DIO">DIO</option>
								<option value="Q">Q</option>
								<option value="IC">IC</option>
							</select>
						</div>
						<div>
							<label class="form-label">Origen</label>
							<select v-model="originFilter" class="form-select" @change="onFiltersChanged">
								<option value="REAL">Solo reales</option>
								<option value="ALL">Todos</option>
								<option value="CATALOGO_ONLY">Solo catálogo</option>
							</select>
						</div>
					</div>
					<div class="form-check mb-2 mt-2">
						<input id="enabledOnly" v-model="enabledOnly" class="form-check-input" type="checkbox" @change="onFiltersChanged" />
						<label class="form-check-label" for="enabledOnly">Solo habilitados</label>
					</div>
					<label class="form-label">Buscar en inventario</label>
					<input
						v-model="searchQuery"
						type="text"
						class="form-control"
						placeholder="Nombre, SKU o categoría..."
						@input="searchInventory"
					/>
					<!-- Resultados de búsqueda -->
					<div v-if="searchResults.length > 0" class="search-results">
						<div
							v-for="item in searchResults"
							:key="item.id"
							class="search-item"
							@click="selectItem(item)"
						>
							<div class="search-item-main">
								<span class="item-name">{{ item.name }}</span>
								<div class="item-meta">
									<span class="badge bg-secondary me-1">{{ item.family || 'NA' }}</span>
									<span class="badge bg-info text-dark">{{ item.origin_status || 'LEGACY' }}</span>
								</div>
							</div>
							<span class="item-stock">Stock: {{ item.available_stock ?? item.stock }} {{ item.stock_unit || 'u' }}</span>
							<span class="item-price">${{ formatNumber(item.price) }}</span>
						</div>
					</div>
				</div>
				<div class="col-md-2">
					<label class="form-label">Cantidad</label>
					<input
						v-model.number="newComponent.quantity"
						type="number"
						class="form-control"
						min="1"
						:max="selectedItem?.available_stock || selectedItem?.stock || 999"
					/>
				</div>
				<div class="col-md-3">
					<label class="form-label">Componente seleccionado</label>
					<input
						:value="selectedItem?.name || '—'"
						type="text"
						class="form-control"
						readonly
					/>
				</div>
				<div class="col-md-3 d-flex align-items-end gap-2">
					<button
						class="btn btn-success flex-grow-1"
						:disabled="!canAddComponent || adding"
						@click="addComponent"
					>
						<i class="fa-solid fa-check me-1"></i>
						{{ adding ? 'Agregando...' : 'Agregar' }}
					</button>
					<button class="btn btn-outline-secondary" @click="cancelAdd">
						<i class="fa-solid fa-times"></i>
					</button>
				</div>
			</div>
			<div v-if="selectedItem" class="selected-preview">
				<span class="badge bg-info me-2">{{ selectedItem.category || 'Sin categoría' }}</span>
				<span>Precio unitario: <strong>${{ formatNumber(selectedItem.price) }}</strong></span>
				<span class="ms-3">Subtotal: <strong>${{ formatNumber((selectedItem.price || 0) * (newComponent.quantity || 0)) }}</strong></span>
			</div>
		</div>

		<!-- Tabla de componentes usados -->
		<div class="components-table-wrapper">
			<table class="components-table" v-if="components.length > 0">
				<thead>
					<tr>
						<th>Componente</th>
						<th>Categoría</th>
						<th class="text-center">Cantidad</th>
						<th class="text-end">P. Unitario</th>
						<th class="text-end">Subtotal</th>
						<th class="text-center" v-if="!isReadOnly">Acciones</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="comp in components" :key="comp.id">
						<td>
							<span class="component-name">{{ comp.component_name || `ID: ${comp.component_id}` }}</span>
							<small class="text-muted d-block" v-if="comp.notes">{{ comp.notes }}</small>
						</td>
						<td>
							<span class="badge bg-secondary">{{ comp.component_table || '—' }}</span>
						</td>
						<td class="text-center">{{ comp.quantity }}</td>
						<td class="text-end">${{ formatNumber(comp.unit_cost || 0) }}</td>
						<td class="text-end fw-bold">${{ formatNumber((comp.unit_cost || 0) * comp.quantity) }}</td>
						<td class="text-center" v-if="!isReadOnly">
							<button
								class="btn btn-sm btn-outline-danger"
								@click="removeComponent(comp)"
								:disabled="removing === comp.id"
							>
								<i class="fa-solid fa-trash"></i>
							</button>
						</td>
					</tr>
				</tbody>
				<tfoot>
					<tr class="total-row">
						<td colspan="4" class="text-end"><strong>Total Materiales:</strong></td>
						<td class="text-end total-amount">${{ formatNumber(totalMaterials) }}</td>
						<td v-if="!isReadOnly"></td>
					</tr>
				</tfoot>
			</table>
			<div v-else class="empty-state">
				<i class="fa-solid fa-box-open fa-2x text-muted mb-2"></i>
				<p class="text-muted mb-0">No hay materiales registrados</p>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { api } from '@/services/api'

const props = defineProps({
	repairId: { type: [Number, String], required: true },
	isReadOnly: { type: Boolean, default: false }
})

const emit = defineEmits(['update:totalCost', 'componentsChanged'])

// State
const components = ref([])
const inventory = ref([])
const searchQuery = ref('')
const searchResults = ref([])
const selectedItem = ref(null)
const familyFilter = ref('ALL')
const originFilter = ref('REAL')
const enabledOnly = ref(true)
const showAddForm = ref(false)
const adding = ref(false)
const removing = ref(null)
const newComponent = ref({
	quantity: 1,
	notes: ''
})

// Computed
const totalMaterials = computed(() => {
	return components.value.reduce((sum, c) => sum + (c.unit_cost || 0) * c.quantity, 0)
})

const canAddComponent = computed(() => {
	const available = Number(selectedItem.value?.available_stock ?? selectedItem.value?.stock ?? 0)
	return selectedItem.value && newComponent.value.quantity > 0 && newComponent.value.quantity <= available
})

// Watch totalMaterials and emit to parent
watch(totalMaterials, (val) => {
	emit('update:totalCost', val)
})

// Methods
const formatNumber = (num) => {
	return new Intl.NumberFormat('es-CL').format(num || 0)
}

const loadComponents = async () => {
	try {
		const res = await api.get(`/repairs/${props.repairId}/components`)
		components.value = res.data || res || []
		emit('componentsChanged', components.value)
	} catch (error) {
		console.error('Error cargando componentes:', error)
		components.value = []
	}
}

const loadInventory = async () => {
	try {
		const params = new URLSearchParams()
		if (familyFilter.value && familyFilter.value !== 'ALL') {
			params.set('family', familyFilter.value)
		}
		if (originFilter.value && originFilter.value !== 'ALL') {
			params.set('origin_status', originFilter.value)
		}
		if (enabledOnly.value) {
			params.set('enabled_only', 'true')
		}
		const suffix = params.toString() ? `?${params.toString()}` : ''
		const res = await api.get(`/inventory/${suffix}`)
		inventory.value = res.data || res || []
		searchInventory()
	} catch (error) {
		console.error('Error cargando inventario:', error)
		inventory.value = []
	}
}

const searchInventory = () => {
	if (!searchQuery.value || searchQuery.value.length < 2) {
		searchResults.value = []
		return
	}

	const query = searchQuery.value.toLowerCase()
	searchResults.value = inventory.value
		.filter(item =>
			(item.name?.toLowerCase().includes(query) ||
			item.sku?.toLowerCase().includes(query) ||
			item.category?.toLowerCase().includes(query)) &&
			Number(item.available_stock ?? item.stock ?? 0) > 0
		)
		.slice(0, 10)
}

const onFiltersChanged = async () => {
	await loadInventory()
	if (selectedItem.value) {
		const stillAvailable = inventory.value.find((item) => item.id === selectedItem.value.id)
		if (!stillAvailable) {
			selectedItem.value = null
			newComponent.value.quantity = 1
		}
	}
}

const selectItem = (item) => {
	selectedItem.value = item
	searchQuery.value = item.name
	searchResults.value = []
	newComponent.value.quantity = 1
}

const addComponent = async () => {
	if (!canAddComponent.value) return

	adding.value = true
	try {
		await api.post(`/repairs/${props.repairId}/components`, {
			component_table: 'products',
			component_id: selectedItem.value.id,
			quantity: newComponent.value.quantity,
			notes: newComponent.value.notes || null
		})

		// Recargar componentes e inventario (stock actualizado)
		await Promise.all([loadComponents(), loadInventory()])

		// Reset form
		cancelAdd()
	} catch (error) {
		console.error('Error agregando componente:', error)
		alert(error.response?.data?.detail || 'Error al agregar componente')
	} finally {
		adding.value = false
	}
}

const removeComponent = async (comp) => {
	if (!confirm(`¿Eliminar ${comp.component_name || 'este componente'} y devolver al stock?`)) return

	removing.value = comp.id
	try {
		await api.delete(`/repairs/${props.repairId}/components/${comp.id}`)
		await Promise.all([loadComponents(), loadInventory()])
	} catch (error) {
		console.error('Error eliminando componente:', error)
		alert(error.response?.data?.detail || 'Error al eliminar componente')
	} finally {
		removing.value = null
	}
}

const cancelAdd = () => {
	showAddForm.value = false
	selectedItem.value = null
	searchQuery.value = ''
	searchResults.value = []
	newComponent.value = { quantity: 1, notes: '' }
}

// Lifecycle
onMounted(async () => {
	await Promise.all([loadComponents(), loadInventory()])
})

// Expose for parent
defineExpose({ loadComponents, totalMaterials })
</script>

<style scoped lang="scss">
@use '@/scss/theming' as *;

.components-manager {
	background: $vintage-beige;
	border-radius: 12px;
	padding: 1.25rem;
	box-shadow: 0 2px 8px rgba($color-black, 0.08);
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 1rem;
}

.section-title {
	color: $brand-text;
	font-weight: 600;
	margin: 0;
}

.add-form {
	background: rgba($color-white, 0.7);
	border-radius: 8px;
	padding: 1rem;
	margin-bottom: 1rem;
	border: 1px solid rgba($brand-primary, 0.2);
}

.filters-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 0.5rem;
}

.search-results {
	position: absolute;
	z-index: 100;
	background: $color-white;
	border: 1px solid $color-gray-180-legacy;
	border-radius: 8px;
	max-height: 200px;
	overflow-y: auto;
	width: calc(100% - 1rem);
	box-shadow: 0 4px 12px rgba($color-black, 0.15);
}

.search-item {
	padding: 0.5rem 0.75rem;
	cursor: pointer;
	display: flex;
	justify-content: space-between;
	align-items: center;
	border-bottom: 1px solid $color-gray-190-legacy;
	gap: 0.5rem;

	&:hover {
		background: lighten($brand-primary, 45%);
	}

	&:last-child {
		border-bottom: none;
	}

	.item-name {
		font-weight: 500;
		flex: 1;
	}

	.search-item-main {
		flex: 1;
		min-width: 0;
	}

	.item-meta {
		margin-top: 0.25rem;
	}

	.item-stock {
		color: $color-gray-666-legacy;
		font-size: 0.85em;
		margin: 0 0.5rem;
	}

	.item-price {
		color: $brand-primary;
		font-weight: 600;
	}
}

.selected-preview {
	margin-top: 0.75rem;
	padding: 0.5rem;
	background: rgba($brand-primary, 0.1);
	border-radius: 6px;
	font-size: 0.9em;
}

.components-table-wrapper {
	overflow-x: auto;
}

.components-table {
	width: 100%;
	border-collapse: collapse;
	background: $color-white;
	border-radius: 8px;
	overflow: hidden;

	th, td {
		padding: 0.75rem;
		border-bottom: 1px solid $color-gray-190-legacy;
	}

	th {
		background: $brand-text;
		color: $color-white;
		font-weight: 600;
		font-size: 0.85em;
		text-transform: uppercase;
	}

	tbody tr:hover {
		background: rgba($brand-primary, 0.05);
	}

	.component-name {
		font-weight: 500;
	}

	.total-row {
		background: lighten($brand-primary, 40%);

		td {
			border-bottom: none;
			padding: 1rem 0.75rem;
		}

		.total-amount {
			font-size: 1.1em;
			color: $brand-primary;
		}
	}
}

.empty-state {
	text-align: center;
	padding: 2rem;
	background: $color-white;
	border-radius: 8px;
}
</style>
