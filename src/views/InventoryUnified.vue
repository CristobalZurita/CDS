<template>
  <AdminLayout title="Inventario Unificado" subtitle="POC y operación de importaciones">
    <section class="inventory-unified">
      <header class="inventory-unified__header">
        <h1 class="inventory-unified__title">Inventario Unificado (POC)</h1>

        <div class="inventory-unified__toolbar">
          <input
            v-model="filter"
            data-testid="inventory-unified-filter"
            class="inventory-unified__input"
            placeholder="Filtrar por categoría"
            @keyup.enter="load"
          />

          <div class="inventory-unified__actions">
            <button
              data-testid="inventory-unified-search"
              class="inventory-unified__button inventory-unified__button--primary"
              type="button"
              @click="load"
            >
              Buscar
            </button>
            <button
              class="inventory-unified__button inventory-unified__button--secondary"
              type="button"
              :disabled="importing"
              @click="triggerImport"
            >
              {{ importing ? 'Importando...' : 'Iniciar importación' }}
            </button>
          </div>
        </div>
      </header>

      <div v-if="loading" class="inventory-unified__feedback">Cargando...</div>
      <div v-if="lastRunId" class="inventory-unified__status">
        Última importación: <strong>{{ lastRunId }}</strong>
        <em v-if="runStatus">({{ runStatus }})</em>
      </div>
      <div v-else class="inventory-unified__grid">
        <InventoryCard
          v-for="it in items"
          :key="it.id"
          :item="it"
          @request-edit="onRequestEdit"
          @request-delete="onRequestDelete"
        />
      </div>
    </section>
  </AdminLayout>
</template>

<script setup>
import { useInventoryStore } from '@/stores/inventory'
import InventoryCard from '@/components/prototypes/InventoryCard.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const filter = ref('')
const store = useInventoryStore()
const items = computed(() => store.items || [])
const loading = computed(() => store.loading ?? store.isLoading)
const importing = computed(() => store.importing)
const lastRunId = computed(() => store.lastRunId)
const runStatus = computed(() => store.runStatus)
const router = useRouter()

const load = () => store.fetchItems(1, 20, filter.value || null, null)

async function onRequestDelete(item) {
  const ok = confirm(`Eliminar item "${item.name || item.id}"?`)
  if (!ok) return

  try {
    const success = await store.deleteItem(item.id)
    if (!success) alert('No se pudo eliminar el item')
  } catch (error) {
    console.error(error)
    alert('Error eliminando item')
  }
}

function onRequestEdit(item) {
  router.push({ name: 'admin-inventory', query: { edit: item.id } })
}

async function triggerImport() {
  try {
    await store.triggerImport()
  } catch (error) {
    const detail = error?.response?.data?.detail || error?.message || error
    if (String(detail).includes('Not Found')) {
      alert('Importación no disponible en este entorno.')
    } else {
      alert('Error iniciando importación: ' + detail)
    }
  }
}

onMounted(() => load())
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.inventory-unified {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-lg);
  padding: var(--spacer-lg);
}

.inventory-unified__header {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
}

.inventory-unified__title {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--text-xl);
  font-weight: 700;
}

.inventory-unified__toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacer-md);
  align-items: center;
}

.inventory-unified__input {
  width: 100%;
  max-width: 320px;
  flex: 1 1 320px;
  min-height: 44px;
  padding: 0.75rem 0.875rem;
  color: var(--color-dark);
  font-size: var(--text-base);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.inventory-unified__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacer-sm);
}

.inventory-unified__button {
  min-height: 44px;
  padding: 0.75rem 1rem;
  border: 0;
  border-radius: var(--radius-md);
  color: var(--color-white);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
}

.inventory-unified__button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.inventory-unified__button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.inventory-unified__button--primary {
  background: var(--color-primary);
}

.inventory-unified__button--secondary {
  background: var(--color-dark);
}

.inventory-unified__feedback,
.inventory-unified__status {
  padding: var(--spacer-md);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  color: var(--color-dark);
}

.inventory-unified__grid {
  display: grid;
  gap: var(--spacer-md);
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

@include media-breakpoint-down(md) {
  .inventory-unified {
    padding: var(--spacer-md);
  }

  .inventory-unified__toolbar,
  .inventory-unified__actions {
    flex-direction: column;
    align-items: stretch;
  }

  .inventory-unified__input {
    min-width: 100%;
  }

  .inventory-unified__grid {
    grid-template-columns: 1fr;
  }
}
</style>
