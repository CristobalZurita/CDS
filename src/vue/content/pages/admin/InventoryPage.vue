<template>
	<AdminLayout title="Inventario" subtitle="Gestión de stock y componentes">
		<div class="d-flex justify-content-between align-items-center mb-3">
			<h1 class="h4">Inventario</h1>
			<div>
				<button class="btn btn-sm btn-outline-primary me-2" data-testid="inventory-view-sheet" @click="activeView = 'sheet'">Planilla simple</button>
				<button class="btn btn-sm btn-outline-primary me-2" data-testid="inventory-view-states" @click="activeView = 'states'">Estados stock</button>
				<button class="btn btn-sm btn-outline-secondary me-2" data-testid="inventory-view-manage" @click="activeView = 'manage'">Administrar items</button>
				<button class="btn btn-sm btn-success me-2" data-testid="inventory-new" @click="onNew">Nuevo item</button>
				<button class="btn btn-sm btn-outline-success me-2" data-testid="inventory-sync-catalog" :disabled="syncingCatalog" @click="syncCatalog">
					{{ syncingCatalog ? 'Sincronizando...' : 'Sincronizar tienda' }}
				</button>
				<button class="btn btn-sm btn-outline-secondary" data-testid="inventory-refresh" @click="reload">Refrescar</button>
			</div>
		</div>

		<div v-if="catalogStatus" class="card mb-3" data-testid="inventory-catalog-status">
			<div class="card-body">
				<div class="d-flex justify-content-between align-items-start gap-3 flex-wrap">
					<div>
						<h2 class="h6 mb-2">Estado catálogo tienda</h2>
						<p class="text-muted mb-0">
							Las fotos que agregas en <code>public/images/INVENTARIO</code> se publican en tienda mediante esta sincronización.
						</p>
					</div>
					<div class="text-end">
						<div><strong data-testid="inventory-catalog-files">{{ catalogStatus.files_count }}</strong> fotos detectadas</div>
						<div><strong data-testid="inventory-catalog-linked">{{ catalogStatus.linked_products_count }}</strong> productos vinculados</div>
						<div><strong data-testid="inventory-catalog-sellable">{{ catalogStatus.sellable_now_count }}</strong> vendibles ahora</div>
					</div>
				</div>
				<div class="row mt-3 g-2">
					<div class="col-sm-6 col-lg-3">
						<div class="border rounded p-2 h-100">
							<div class="small text-muted">Publicados</div>
							<div class="fw-semibold">{{ catalogStatus.explicit_store_visible_count }}</div>
						</div>
					</div>
					<div class="col-sm-6 col-lg-3">
						<div class="border rounded p-2 h-100">
							<div class="small text-muted">Con stock bruto</div>
							<div class="fw-semibold">{{ catalogStatus.with_nonzero_stock_count }}</div>
						</div>
					</div>
					<div class="col-sm-6 col-lg-3">
						<div class="border rounded p-2 h-100">
							<div class="small text-muted">Pendientes por vincular</div>
							<div class="fw-semibold" data-testid="inventory-catalog-pending">{{ catalogStatus.pending_images_count }}</div>
						</div>
					</div>
					<div class="col-sm-6 col-lg-3">
						<div class="border rounded p-2 h-100">
							<div class="small text-muted">Registros huérfanos</div>
							<div class="fw-semibold">{{ catalogStatus.orphan_rows_count }}</div>
						</div>
					</div>
				</div>
				<div v-if="catalogStatus.pending_images_count" class="mt-3">
					<div class="small text-muted mb-1">Pendientes</div>
					<div class="d-flex flex-wrap gap-2">
						<span
							v-for="imageName in catalogStatus.pending_images.slice(0, 8)"
							:key="imageName"
							class="badge text-bg-light"
						>
							{{ imageName }}
						</span>
					</div>
				</div>
			</div>
		</div>

		<div class="card mb-3">
			<div class="card-body">
				<div class="row g-2 align-items-end">
					<div class="col-lg-5">
						<label class="form-label mb-1" for="inventory-search-input">Buscar</label>
						<input
							id="inventory-search-input"
							v-model.trim="searchTerm"
							class="form-control"
							data-testid="inventory-search-input"
							placeholder="SKU, nombre, familia o descripción"
							type="text"
						/>
					</div>
					<div class="col-sm-6 col-lg-3">
						<label class="form-label mb-1" for="inventory-filter-category">Categoría</label>
						<select
							id="inventory-filter-category"
							v-model="selectedCategoryId"
							class="form-select"
							data-testid="inventory-filter-category"
						>
							<option value="">Todas</option>
							<option v-for="category in categories" :key="category.id" :value="String(category.id)">
								{{ category.name }}
							</option>
						</select>
					</div>
					<div class="col-sm-6 col-lg-3">
						<label class="form-label mb-1" for="inventory-filter-scope">Vista</label>
						<select
							id="inventory-filter-scope"
							v-model="storeScope"
							class="form-select"
							data-testid="inventory-filter-scope"
						>
							<option value="all">Todo</option>
							<option value="published">Publicados en tienda</option>
							<option value="hidden">No publicados</option>
							<option value="with-image">Con foto</option>
							<option value="without-image">Sin foto</option>
							<option value="sellable">Vendibles ahora</option>
							<option value="low-stock">Stock bajo</option>
							<option value="zero-stock">Stock en 0</option>
							<option value="base-price">Precio base 1000</option>
							<option value="reserved">Reservados</option>
							<option value="in-work">En trabajo</option>
							<option value="internal-use">Consumo interno</option>
							<option value="ot-active">Vinculados a OT</option>
						</select>
					</div>
					<div class="col-lg-1 text-lg-end">
						<button class="btn btn-outline-secondary w-100" data-testid="inventory-clear-filters" @click="clearFilters">
							Limpiar
						</button>
					</div>
				</div>
				<div class="mt-2 small text-muted" data-testid="inventory-results-count">
					Mostrando {{ filteredItems.length }} de {{ items.length }} items.
				</div>
				<div class="row g-2 mt-2" data-testid="inventory-scope-summary">
					<div class="col-sm-6 col-xl-2">
						<div class="border rounded p-2 h-100">
							<div class="small text-muted">Interno sólo</div>
							<div class="fw-semibold">{{ scopeSummary.internalOnly }}</div>
						</div>
					</div>
					<div class="col-sm-6 col-xl-2">
						<div class="border rounded p-2 h-100">
							<div class="small text-muted">Publicado tienda</div>
							<div class="fw-semibold">{{ scopeSummary.published }}</div>
						</div>
					</div>
					<div class="col-sm-6 col-xl-2">
						<div class="border rounded p-2 h-100">
							<div class="small text-muted">Con stock 0</div>
							<div class="fw-semibold">{{ scopeSummary.zeroStock }}</div>
						</div>
					</div>
					<div class="col-sm-6 col-xl-2">
						<div class="border rounded p-2 h-100">
							<div class="small text-muted">Precio base 1000</div>
							<div class="fw-semibold">{{ scopeSummary.basePrice }}</div>
						</div>
					</div>
					<div class="col-sm-6 col-xl-2">
						<div class="border rounded p-2 h-100">
							<div class="small text-muted">Reservados / OT</div>
							<div class="fw-semibold">{{ scopeSummary.otLinked }}</div>
						</div>
					</div>
					<div class="col-sm-6 col-xl-2">
						<div class="border rounded p-2 h-100">
							<div class="small text-muted">Consumo interno</div>
							<div class="fw-semibold">{{ scopeSummary.internalUse }}</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<InventoryAlerts :items="filteredItems" />

		<InventoryStockSheet v-if="activeView === 'sheet'" :items="filteredItems" @save="onQuickSave" @save-many="onQuickSaveMany" />
		<InventoryStockStates v-else-if="activeView === 'states'" :items="filteredItems" @save="onStateSave" />

		<InventoryTable v-else :items="filteredItems" @edit="onEdit" @delete="onDelete" />

		<div v-if="showForm" class="mt-3">
			<InventoryForm :item="selected" @save="onSave" @cancel="onCancel" />
		</div>
	</AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import InventoryTable from '@/vue/components/admin/InventoryTable.vue'
import InventoryForm from '@/vue/components/admin/InventoryForm.vue'
import InventoryStockSheet from '@/vue/components/admin/InventoryStockSheet.vue'
import InventoryStockStates from '@/vue/components/admin/InventoryStockStates.vue'
import InventoryAlerts from '@/vue/components/admin/InventoryAlerts.vue'
import { useInventoryStore } from '@/stores/inventory'
import { useCategoriesStore } from '@/stores/categories'
import { showError, showSuccess } from '@/services/toastService'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const store = useInventoryStore()
const categoriesStore = useCategoriesStore()
const route = useRoute()
const router = useRouter()

const items = computed(() => store.items || [])
const catalogStatus = computed(() => store.catalogStatus)
const syncingCatalog = computed(() => store.syncingCatalog)
const categories = computed(() => categoriesStore.categories || [])
const showForm = ref(false)
const selected = ref(null)
const activeView = ref('sheet')
const searchTerm = ref('')
const selectedCategoryId = ref('')
const storeScope = ref('all')

function normalizeSearchText(value) {
	return String(value || '')
		.normalize('NFD')
		.replace(/[\u0300-\u036f]/g, '')
		.toLowerCase()
		.replace(/[_-]+/g, ' ')
		.trim()
}

const filteredItems = computed(() => {
	const normalizedSearch = normalizeSearchText(searchTerm.value)
	return items.value.filter((item) => {
		if (selectedCategoryId.value && String(item.category_id ?? '') !== String(selectedCategoryId.value)) {
			return false
		}

		if (storeScope.value === 'published' && item.store_visible !== true) {
			return false
		}
		if (storeScope.value === 'hidden' && item.store_visible === true) {
			return false
		}
		if (storeScope.value === 'with-image' && !item.image_url) {
			return false
		}
		if (storeScope.value === 'without-image' && item.image_url) {
			return false
		}
		if (storeScope.value === 'sellable' && Number(item.sellable_stock || 0) <= 0) {
			return false
		}
		if (storeScope.value === 'low-stock' && item.is_low_stock !== true) {
			return false
		}
		if (storeScope.value === 'zero-stock' && Number(item.stock || 0) > 0) {
			return false
		}
		if (storeScope.value === 'base-price' && Number(item.price || 0) !== 1000) {
			return false
		}
		if (storeScope.value === 'reserved' && Number(item.quantity_reserved || 0) <= 0) {
			return false
		}
		if (storeScope.value === 'in-work' && Number(item.quantity_in_work || 0) <= 0) {
			return false
		}
		if (storeScope.value === 'internal-use' && Number(item.quantity_internal_use || 0) <= 0) {
			return false
		}
		if (storeScope.value === 'ot-active' && (Number(item.quantity_reserved || 0) + Number(item.quantity_in_work || 0)) <= 0) {
			return false
		}

		if (!normalizedSearch) {
			return true
		}

		const haystack = normalizeSearchText([
			item.name,
			item.sku,
			item.family,
			item.category,
			item.description,
			item.origin_status,
		].filter(Boolean).join(' '))

		return haystack.includes(normalizedSearch)
	})
})

const scopeSummary = computed(() => {
	return items.value.reduce((acc, item) => {
		if (item.store_visible === true) acc.published += 1
		else acc.internalOnly += 1
		if (Number(item.stock || 0) <= 0) acc.zeroStock += 1
		if (Number(item.price || 0) === 1000) acc.basePrice += 1
		if ((Number(item.quantity_reserved || 0) + Number(item.quantity_in_work || 0)) > 0) acc.otLinked += 1
		if (Number(item.quantity_internal_use || 0) > 0) acc.internalUse += 1
		return acc
	}, { internalOnly: 0, published: 0, zeroStock: 0, basePrice: 0, otLinked: 0, internalUse: 0 })
})

async function load() {
	await store.fetchItems(1, 50)
}

async function loadCatalogStatus() {
	try {
		await store.fetchCatalogStatus()
	} catch (e) {
		console.error(e)
		showError('No se pudo leer el estado del catálogo tienda.')
	}
}

function reload() {
	Promise.all([load(), loadCatalogStatus()])
}

function clearFilters() {
	searchTerm.value = ''
	selectedCategoryId.value = ''
	storeScope.value = 'all'
}

function onNew() {
	selected.value = null
	showForm.value = true
	router.replace({ query: { ...route.query, edit: 'new' } })
}

function onEdit(item) {
	selected.value = item
	showForm.value = true
	router.replace({ query: { ...route.query, edit: item.id } })
}

async function onDelete(item) {
	if (!confirm(`Eliminar item "${item.name || item.id}"?`)) return
	try {
		await store.deleteItem(item.id)
		showSuccess('Item eliminado correctamente.')
	} catch (e) {
		console.error(e)
		showError('No fue posible eliminar el item.')
	}
}

async function onSave(payload) {
	try {
		if (payload.id) {
			await store.updateItem(payload.id, payload)
		} else {
			await store.createItem(payload)
		}
		showForm.value = false
		selected.value = null
		// remove edit query
		const q = { ...route.query }
		delete q.edit
		router.replace({ query: q })
		await loadCatalogStatus()
	} catch (e) {
		console.error(e)
		showError('Error guardando item: ' + (e.message || e))
	}
}

async function onQuickSave(payload) {
	if (!payload?.id) return
	try {
		await store.updateItem(payload.id, {
			stock: payload.stock ?? 0,
			min_quantity: payload.min_stock ?? 0,
			price: payload.price ?? 0,
			enabled: payload.enabled,
			store_visible: payload.store_visible,
		})
		await load()
		await loadCatalogStatus()
	} catch (e) {
		console.error(e)
		showError('No se pudo guardar el stock.')
	}
}

async function onQuickSaveMany(payloads) {
	if (!Array.isArray(payloads) || !payloads.length) return
	try {
		for (const payload of payloads) {
			if (!payload?.id) continue
			await store.updateItem(payload.id, {
				stock: payload.stock ?? 0,
				min_quantity: payload.min_stock ?? 0,
				price: payload.price ?? 0,
				enabled: payload.enabled,
				store_visible: payload.store_visible,
			})
		}
		await load()
		await loadCatalogStatus()
		showSuccess(`${payloads.length} items actualizados correctamente.`)
	} catch (e) {
		console.error(e)
		showError('No se pudo guardar la selección masiva.')
	}
}

async function onStateSave(payload) {
	if (!payload?.id) return
	try {
		await store.updateItem(payload.id, {
			stock: payload.stock ?? 0,
			quantity_reserved: payload.quantity_reserved ?? 0,
			quantity_in_work: payload.quantity_in_work ?? 0,
			quantity_in_transit: payload.quantity_in_transit ?? 0,
			quantity_under_review: payload.quantity_under_review ?? 0,
			quantity_damaged: payload.quantity_damaged ?? 0,
			quantity_internal_use: payload.quantity_internal_use ?? 0
		})
		await load()
		await loadCatalogStatus()
	} catch (e) {
		console.error(e)
		showError('No se pudo guardar estados de stock.')
	}
}

async function syncCatalog() {
	try {
		const data = await store.syncCatalog()
		const result = data?.result || {}
		showSuccess(`Catálogo sincronizado. ${result.matched || 0} vinculados, ${result.created || 0} creados.`)
	} catch (e) {
		console.error(e)
		showError('No se pudo sincronizar el catálogo tienda.')
	}
}

function onCancel() {
	showForm.value = false
	selected.value = null
	const q = { ...route.query }
	delete q.edit
	router.replace({ query: q })
}

onMounted(async () => {
	await Promise.all([load(), loadCatalogStatus(), categoriesStore.fetchCategories()])
})

// react to ?edit= query param (e.g., when InventoryUnified navigates to admin page)
watch(
	() => route.query.edit,
	async (val) => {
		if (!val) return
		if (val === 'new') {
			onNew()
			return
		}
		// try find in loaded items
		let it = store.items?.find((x) => String(x.id) === String(val))
		if (!it) {
			try {
				it = await store.fetchItemById(String(val))
			} catch (e) {
				console.error('Failed to fetch item detail', e)
			}
		}
		if (it) {
			onEdit(it)
		}
	},
	{ immediate: true }
)
</script>
