<template>
	<div>
		<div class="d-flex justify-content-between align-items-center mb-3">
			<h1 class="h4">Inventario</h1>
			<div>
				<button class="btn btn-sm btn-success me-2" @click="onNew">Nuevo item</button>
				<button class="btn btn-sm btn-outline-secondary" @click="reload">Refrescar</button>
			</div>
		</div>

		<InventoryTable :items="items" @edit="onEdit" @delete="onDelete" />

		<div v-if="showForm" class="mt-3">
			<InventoryForm :item="selected" @save="onSave" @cancel="onCancel" />
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import InventoryTable from '@/vue/components/admin/InventoryTable.vue'
import InventoryForm from '@/vue/components/admin/InventoryForm.vue'
import { useInventoryStore } from '@/stores/inventory'

const store = useInventoryStore()
const route = useRoute()
const router = useRouter()

const items = ref([])
const showForm = ref(false)
const selected = ref(null)

async function load() {
	await store.fetchItems(1, 50)
	items.value = store.items
}

function reload() {
	load()
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
				const res = await fetch(`/api/v1/items/${val}`)
				if (res.ok) it = await res.json()
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
