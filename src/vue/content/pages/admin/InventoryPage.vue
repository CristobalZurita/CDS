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

		<InventoryAlerts :items="items" />

		<InventoryStockSheet v-if="activeView === 'sheet'" :items="items" @save="onQuickSave" />
		<InventoryStockStates v-else-if="activeView === 'states'" :items="items" @save="onStateSave" />

		<InventoryTable v-else :items="items" @edit="onEdit" @delete="onDelete" />

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
import { api } from '@/services/api'
import { showError, showSuccess } from '@/services/toastService'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const store = useInventoryStore()
const route = useRoute()
const router = useRouter()

const items = computed(() => store.items)
const showForm = ref(false)
const selected = ref(null)
const activeView = ref('sheet')
const catalogStatus = ref(null)
const syncingCatalog = ref(false)

async function load() {
	await store.fetchItems(1, 50)
}

async function loadCatalogStatus() {
	try {
		const res = await api.get('/inventory/store-catalog/status')
		catalogStatus.value = res?.data || null
	} catch (e) {
		console.error(e)
		showError('No se pudo leer el estado del catálogo tienda.')
	}
}

function reload() {
	Promise.all([load(), loadCatalogStatus()])
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
			price: payload.price ?? 0
		})
		await load()
		await loadCatalogStatus()
	} catch (e) {
		console.error(e)
		showError('No se pudo guardar el stock.')
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
	if (syncingCatalog.value) return
	syncingCatalog.value = true
	try {
		const res = await api.post('/inventory/store-catalog/sync')
		const result = res?.data?.result || {}
		catalogStatus.value = res?.data?.status || null
		await load()
		showSuccess(`Catálogo sincronizado. ${result.matched || 0} vinculados, ${result.created || 0} creados.`)
	} catch (e) {
		console.error(e)
		showError('No se pudo sincronizar el catálogo tienda.')
	} finally {
		syncingCatalog.value = false
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
	await Promise.all([load(), loadCatalogStatus()])
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
			// fetch item detail from API
			try {
				const res = await api.get(`/inventory/${val}`)
				if (res?.data) it = res.data
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
