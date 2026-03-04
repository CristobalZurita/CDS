<template>
  <AdminLayout title="Inventario" subtitle="Gestión de stock y componentes">
    <section class="inventory-page">
      <header class="inventory-page__header">
        <h1 class="inventory-page__title">Inventario</h1>

        <div class="inventory-page__actions">
          <button
            type="button"
            class="inventory-page__button"
            :class="{ 'inventory-page__button--active': activeView === 'sheet' }"
            data-testid="inventory-view-sheet"
            @click="activeView = 'sheet'"
          >
            Planilla simple
          </button>
          <button
            type="button"
            class="inventory-page__button"
            :class="{ 'inventory-page__button--active': activeView === 'states' }"
            data-testid="inventory-view-states"
            @click="activeView = 'states'"
          >
            Estados stock
          </button>
          <button
            type="button"
            class="inventory-page__button inventory-page__button--secondary"
            :class="{ 'inventory-page__button--active inventory-page__button--secondary-active': activeView === 'manage' }"
            data-testid="inventory-view-manage"
            @click="activeView = 'manage'"
          >
            Administrar items
          </button>
          <button
            type="button"
            class="inventory-page__button inventory-page__button--success"
            data-testid="inventory-new"
            @click="onNew"
          >
            Nuevo item
          </button>
          <button
            type="button"
            class="inventory-page__button inventory-page__button--outline-success"
            data-testid="inventory-sync-catalog"
            :disabled="syncingCatalog"
            @click="syncCatalog"
          >
            {{ syncingCatalog ? 'Sincronizando...' : 'Sincronizar tienda' }}
          </button>
          <button
            type="button"
            class="inventory-page__button inventory-page__button--secondary"
            data-testid="inventory-refresh"
            @click="reload"
          >
            Refrescar
          </button>
        </div>
      </header>

      <section v-if="catalogStatus" class="inventory-page__panel" data-testid="inventory-catalog-status">
        <div class="inventory-page__panel-head">
          <div class="inventory-page__panel-copy">
            <h2 class="inventory-page__panel-title">Estado catálogo tienda</h2>
            <p class="inventory-page__panel-text">
              Las fotos que agregas en <code>public/images/INVENTARIO</code> se publican en tienda mediante esta sincronización.
            </p>
          </div>

          <div class="inventory-page__headline-metrics">
            <div>
              <strong data-testid="inventory-catalog-files">{{ catalogStatus.files_count }}</strong> fotos detectadas
            </div>
            <div>
              <strong data-testid="inventory-catalog-linked">{{ catalogStatus.linked_products_count }}</strong> productos vinculados
            </div>
            <div>
              <strong data-testid="inventory-catalog-sellable">{{ catalogStatus.sellable_now_count }}</strong> vendibles ahora
            </div>
          </div>
        </div>

        <div class="inventory-page__stats-grid">
          <article class="inventory-page__stat-card">
            <span class="inventory-page__stat-label">Publicados</span>
            <strong class="inventory-page__stat-value">{{ catalogStatus.explicit_store_visible_count }}</strong>
          </article>
          <article class="inventory-page__stat-card">
            <span class="inventory-page__stat-label">Con stock bruto</span>
            <strong class="inventory-page__stat-value">{{ catalogStatus.with_nonzero_stock_count }}</strong>
          </article>
          <article class="inventory-page__stat-card">
            <span class="inventory-page__stat-label">Pendientes por vincular</span>
            <strong class="inventory-page__stat-value" data-testid="inventory-catalog-pending">
              {{ catalogStatus.pending_images_count }}
            </strong>
          </article>
          <article class="inventory-page__stat-card">
            <span class="inventory-page__stat-label">Registros huérfanos</span>
            <strong class="inventory-page__stat-value">{{ catalogStatus.orphan_rows_count }}</strong>
          </article>
        </div>

        <div v-if="catalogStatus.pending_images_count" class="inventory-page__pending">
          <span class="inventory-page__pending-label">Pendientes</span>
          <div class="inventory-page__chips">
            <span
              v-for="imageName in catalogStatus.pending_images.slice(0, 8)"
              :key="imageName"
              class="inventory-page__chip"
            >
              {{ imageName }}
            </span>
          </div>
        </div>
      </section>

      <section class="inventory-page__panel">
        <div class="inventory-page__filters">
          <label class="inventory-page__field inventory-page__field--wide" for="inventory-search-input">
            <span class="inventory-page__label">Buscar</span>
            <input
              id="inventory-search-input"
              v-model.trim="searchTerm"
              class="inventory-page__input"
              data-testid="inventory-search-input"
              placeholder="SKU, nombre, familia o descripción"
              type="text"
            />
          </label>

          <label class="inventory-page__field" for="inventory-filter-category">
            <span class="inventory-page__label">Categoría</span>
            <select
              id="inventory-filter-category"
              v-model="selectedCategoryId"
              class="inventory-page__select"
              data-testid="inventory-filter-category"
            >
              <option value="">Todas</option>
              <option v-for="category in categories" :key="category.id" :value="String(category.id)">
                {{ category.name }}
              </option>
            </select>
          </label>

          <label class="inventory-page__field" for="inventory-filter-scope">
            <span class="inventory-page__label">Vista</span>
            <select
              id="inventory-filter-scope"
              v-model="storeScope"
              class="inventory-page__select"
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
          </label>

          <div class="inventory-page__field inventory-page__field--action">
            <button
              type="button"
              class="inventory-page__button inventory-page__button--secondary inventory-page__button--block"
              data-testid="inventory-clear-filters"
              @click="clearFilters"
            >
              Limpiar
            </button>
          </div>
        </div>

        <p class="inventory-page__results" data-testid="inventory-results-count">
          Mostrando {{ filteredItems.length }} de {{ items.length }} items.
        </p>

        <div class="inventory-page__summary-grid" data-testid="inventory-scope-summary">
          <article class="inventory-page__summary-card">
            <span class="inventory-page__summary-label">Interno sólo</span>
            <strong class="inventory-page__summary-value">{{ scopeSummary.internalOnly }}</strong>
          </article>
          <article class="inventory-page__summary-card">
            <span class="inventory-page__summary-label">Publicado tienda</span>
            <strong class="inventory-page__summary-value">{{ scopeSummary.published }}</strong>
          </article>
          <article class="inventory-page__summary-card">
            <span class="inventory-page__summary-label">Con stock 0</span>
            <strong class="inventory-page__summary-value">{{ scopeSummary.zeroStock }}</strong>
          </article>
          <article class="inventory-page__summary-card">
            <span class="inventory-page__summary-label">Precio base 1000</span>
            <strong class="inventory-page__summary-value">{{ scopeSummary.basePrice }}</strong>
          </article>
          <article class="inventory-page__summary-card">
            <span class="inventory-page__summary-label">Reservados / OT</span>
            <strong class="inventory-page__summary-value">{{ scopeSummary.otLinked }}</strong>
          </article>
          <article class="inventory-page__summary-card">
            <span class="inventory-page__summary-label">Consumo interno</span>
            <strong class="inventory-page__summary-value">{{ scopeSummary.internalUse }}</strong>
          </article>
        </div>
      </section>

      <InventoryAlerts :items="filteredItems" />

      <InventoryStockSheet
        v-if="activeView === 'sheet'"
        :items="filteredItems"
        @save="onQuickSave"
        @save-many="onQuickSaveMany"
      />
      <InventoryStockStates v-else-if="activeView === 'states'" :items="filteredItems" @save="onStateSave" />
      <InventoryTable v-else :items="filteredItems" @edit="onEdit" @delete="onDelete" />

      <section v-if="showForm" class="inventory-page__form-panel">
        <InventoryForm :item="selected" @save="onSave" @cancel="onCancel" />
      </section>
    </section>
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

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.inventory-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
}

.inventory-page__header,
.inventory-page__panel-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacer-md);
  flex-wrap: wrap;
}

.inventory-page__title,
.inventory-page__panel-title {
  margin: 0;
  color: var(--color-dark);
  font-weight: 700;
}

.inventory-page__title {
  font-size: var(--text-xl);
}

.inventory-page__panel-title {
  font-size: var(--text-lg);
}

.inventory-page__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacer-sm);
}

.inventory-page__panel,
.inventory-page__form-panel {
  padding: var(--spacer-md);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.inventory-page__panel-copy {
  max-width: 44rem;
}

.inventory-page__panel-text,
.inventory-page__results,
.inventory-page__stat-label,
.inventory-page__summary-label,
.inventory-page__pending-label,
.inventory-page__label {
  color: var(--color-dark);
  opacity: 0.72;
}

.inventory-page__panel-text,
.inventory-page__results {
  margin: 0;
  font-size: var(--text-sm);
}

.inventory-page__headline-metrics {
  display: grid;
  gap: 0.35rem;
  text-align: right;
  color: var(--color-dark);
  font-size: var(--text-sm);
}

.inventory-page__stats-grid,
.inventory-page__summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--spacer-sm);
}

.inventory-page__stats-grid {
  margin-top: var(--spacer-md);
}

.inventory-page__summary-grid {
  margin-top: var(--spacer-sm);
}

.inventory-page__stat-card,
.inventory-page__summary-card {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-height: 100%;
  padding: 0.85rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--color-white) 88%, var(--color-light) 12%);
}

.inventory-page__stat-value,
.inventory-page__summary-value {
  color: var(--color-dark);
  font-size: var(--text-lg);
  font-weight: 700;
}

.inventory-page__pending {
  margin-top: var(--spacer-md);
}

.inventory-page__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.inventory-page__chip {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-white) 80%, var(--color-light) 20%);
  color: var(--color-dark);
  font-size: var(--text-xs);
  font-weight: 600;
}

.inventory-page__filters {
  display: grid;
  grid-template-columns: minmax(0, 2fr) repeat(2, minmax(180px, 1fr)) minmax(120px, auto);
  gap: var(--spacer-sm);
  align-items: end;
}

.inventory-page__field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.inventory-page__field--action {
  justify-content: flex-end;
}

.inventory-page__input,
.inventory-page__select {
  width: 100%;
  min-height: 44px;
  padding: 0.7rem 0.85rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-sm);
  background: var(--color-white);
  color: var(--color-dark);
  font-size: var(--text-sm);
}

.inventory-page__button {
  min-height: 40px;
  padding: 0.65rem 0.95rem;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-primary);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
}

.inventory-page__button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.inventory-page__button:disabled {
  opacity: 0.6;
  cursor: wait;
}

.inventory-page__button--active,
.inventory-page__button--success {
  background: var(--color-primary);
  color: var(--color-white);
}

.inventory-page__button--secondary {
  border-color: var(--color-dark);
  color: var(--color-dark);
}

.inventory-page__button--secondary-active {
  background: var(--color-dark);
  color: var(--color-white);
}

.inventory-page__button--outline-success {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.inventory-page__button--block {
  width: 100%;
}

.inventory-page code {
  padding: 0.15rem 0.35rem;
  border-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--color-white) 70%, var(--color-light) 30%);
  color: var(--color-dark);
  font-size: 0.9em;
}

@include media-breakpoint-down(lg) {
  .inventory-page__filters {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@include media-breakpoint-down(md) {
  .inventory-page__header,
  .inventory-page__panel-head,
  .inventory-page__actions {
    flex-direction: column;
    align-items: stretch;
  }

  .inventory-page__headline-metrics {
    text-align: left;
  }

  .inventory-page__filters {
    grid-template-columns: 1fr;
  }

  .inventory-page__button {
    width: 100%;
  }
}
</style>
