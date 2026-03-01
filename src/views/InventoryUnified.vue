<template>
  <AdminLayout title="Inventario Unificado" subtitle="POC y operación de importaciones">
    <div class="p-6">
      <h1 class="text-2xl font-bold mb-4">Inventario Unificado (POC)</h1>
      <div class="mb-4">
        <input v-model="filter" data-testid="inventory-unified-filter" @keyup.enter="load" placeholder="Filtrar por categoría" class="input" />
        <button data-testid="inventory-unified-search" @click="load" class="btn btn-primary ml-2">Buscar</button>
        <button @click="triggerImport" class="btn btn-secondary ml-4" :disabled="importing">{{ importing ? 'Importando...' : 'Iniciar importación' }}</button>
      </div>

      <div v-if="store.loading">Cargando...</div>
      <div v-if="lastRunId" class="mt-4">Última importación: <strong>{{ lastRunId }}</strong> <em v-if="runStatus">({{ runStatus }})</em></div>
      <div v-else class="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        <InventoryCard
          v-for="it in store.items"
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'

export default {
  name: 'InventoryUnified',
  components: { InventoryCard, AdminLayout },
  setup() {
    const filter = ref('')
    const store = useInventoryStore()
    const importing = ref(false)
    const lastRunId = ref(null)
    const runStatus = ref(null)
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
      importing.value = true
      runStatus.value = null
      try {
        const res = await api.post('/imports/run')
        const data = res.data || {}
        lastRunId.value = data.run_id || null
        runStatus.value = data.status || 'started'
      } catch (e) {
        const detail = e?.response?.data?.detail || e?.message || e
        if (String(detail).includes('Not Found')) {
          alert('Importación no disponible en este entorno.')
        } else {
          alert('Error iniciando importación: ' + detail)
        }
      } finally {
        importing.value = false
      }
    }
    onMounted(() => load())
    return { filter, store, load, importing, triggerImport, lastRunId, runStatus, onRequestDelete, onRequestEdit }
  }
}
</script>

<style scoped lang="scss">
@import "@/scss/_core.scss";

.input { padding: 0.5rem; border: 1px solid $color-gray-180-legacy; border-radius: 4px }
.btn { padding: 0.5rem 0.75rem }
</style>
