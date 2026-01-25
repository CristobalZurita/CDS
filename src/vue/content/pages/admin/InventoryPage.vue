<template>
	<AdminLayout title="Inventario" subtitle="Gestión de stock y componentes">
		<div class="d-flex justify-content-between align-items-center mb-3">
			<h1 class="h4">Inventario</h1>
			<div>
				<button class="btn btn-sm btn-outline-primary me-2" @click="activeView = 'sheet'">Planilla simple</button>
				<button class="btn btn-sm btn-outline-primary me-2" @click="activeView = 'states'">Estados stock</button>
				<button class="btn btn-sm btn-outline-secondary me-2" @click="activeView = 'manage'">Administrar items</button>
				<button class="btn btn-sm btn-success me-2" @click="onNew">Nuevo item</button>
				<button class="btn btn-sm btn-outline-secondary" @click="reload">Refrescar</button>
			</div>
		</div>

		<InventoryStockSheet v-if="activeView === 'sheet'" :items="items" @save="onQuickSave" />
		<InventoryStockStates v-else-if="activeView === 'states'" :items="items" @save="onStateSave" />

		<InventoryTable v-else :items="items" @edit="onEdit" @delete="onDelete" />

		<div v-if="showForm" class="mt-3">
			<InventoryForm :item="selected" @save="onSave" @cancel="onCancel" />
		</div>
	</AdminLayout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/services/api'
import InventoryTable from '@/vue/components/admin/InventoryTable.vue'
import InventoryForm from '@/vue/components/admin/InventoryForm.vue'
import InventoryStockSheet from '@/vue/components/admin/InventoryStockSheet.vue'
import InventoryStockStates from '@/vue/components/admin/InventoryStockStates.vue'
import { useInventoryStore } from '@/stores/inventory'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const store = useInventoryStore()
const route = useRoute()
const router = useRouter()

const items = ref([])
const warnedSkus = new Set()
const showForm = ref(false)
const selected = ref(null)
const activeView = ref('sheet')

async function load() {
	await store.fetchItems(1, 50)
	items.value = store.items
	checkLowStockAlerts()
}

function reload() {
	load()
}

function checkLowStockAlerts() {
	if (!items.value?.length) return
	const alerts = []
	for (const item of items.value) {
		const stock = Number(item.stock ?? 0)
		const minStock = Number(item.min_stock ?? 0)
		if (minStock <= 0) continue
		if (warnedSkus.has(item.sku)) continue
		if (stock <= Math.ceil(minStock * 0.25)) {
			alerts.push({ level: '5%', item })
		} else if (stock <= Math.ceil(minStock * 0.5)) {
			alerts.push({ level: '10%', item })
		} else if (stock <= minStock) {
			alerts.push({ level: '20%', item })
		}
	}
	if (!alerts.length) return
	const top = alerts[0]
	const lines = alerts.slice(0, 5).map(a => `${a.item.sku} (${a.item.name}) - ${a.level}`)
	alert(
		`Alerta de stock bajo (aprox.):\\n${lines.join('\\n')}\\n\\nReponer cuando sea posible.`
	)
	for (const a of alerts) {
		warnedSkus.add(a.item.sku)
	}
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
		await load()
	} catch (e) {
		console.error(e)
		alert('No fue posible eliminar el item')
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
		await load()
	} catch (e) {
		console.error(e)
		alert('Error guardando item: ' + (e.message || e))
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
	} catch (e) {
		console.error(e)
		alert('No se pudo guardar el stock.')
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
	} catch (e) {
		console.error(e)
		alert('No se pudo guardar estados de stock.')
	}
}

function onCancel() {
	showForm.value = false
	selected.value = null
	const q = { ...route.query }
	delete q.edit
	router.replace({ query: q })
}

onMounted(() => load())

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

<style scoped>
</style>
