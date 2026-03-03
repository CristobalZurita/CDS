<template>
  <AdminLayout title="Inventario Unificado" subtitle="POC y operación de importaciones">
    <div class="p-6">
      <h1 class="text-2xl font-bold mb-4">Inventario Unificado (POC)</h1>
      <div class="mb-4">
        <input v-model="filter" data-testid="inventory-unified-filter" @keyup.enter="load" placeholder="Filtrar por categoría" class="input" />
        <button data-testid="inventory-unified-search" @click="load" class="btn btn-primary ml-2">Buscar</button>
        <button @click="triggerImport" class="btn btn-secondary ml-4" :disabled="importing">{{ importing ? 'Importando...' : 'Iniciar importación' }}</button>
      </div>

      <div v-if="loading">Cargando...</div>
      <div v-if="lastRunId" class="mt-4">Última importación: <strong>{{ lastRunId }}</strong> <em v-if="runStatus">({{ runStatus }})</em></div>
      <div v-else class="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        <InventoryCard
          v-for="it in items"
          :key="it.id"
          :item="it"
          @request-edit="onRequestEdit"
          @request-delete="onRequestDelete"
        />
      </div>
    </div>
  </AdminLayout>
</template>

<script>
import { useInventoryStore } from '@/stores/inventory'
import InventoryCard from '@/components/prototypes/InventoryCard.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'InventoryUnified',
  components: { InventoryCard, AdminLayout },
  setup() {
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
      } catch (e) {
        console.error(e)
        alert('Error eliminando item')
      }
    }

    function onRequestEdit(item) {
      // Navigate to admin inventory edit page; InventoryPage can read query param `edit`
      router.push({ name: 'admin-inventory', query: { edit: item.id } })
    }

    async function triggerImport() {
      try {
        const data = await store.triggerImport()
        runStatus.value = data?.status || 'started'
      } catch (e) {
        const detail = e?.response?.data?.detail || e?.message || e
        if (String(detail).includes('Not Found')) {
          alert('Importación no disponible en este entorno.')
        } else {
          alert('Error iniciando importación: ' + detail)
        }
      }
    }
    onMounted(() => load())
    return { filter, items, loading, load, importing, triggerImport, lastRunId, runStatus, onRequestDelete, onRequestEdit }
  }
}
</script>
