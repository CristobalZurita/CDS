import { computed } from 'vue'
import { useInventoryStore } from '@/stores/inventory'

export function useInventory() {
  const store = useInventoryStore()

  const items = computed(() => store.items)
  const loading = computed(() => store.loading)
  const page = computed(() => store.page)
  const limit = computed(() => store.limit)

  const refresh = async (opts = {}) => {
    const nextPage = opts.page ?? store.page
    const nextLimit = opts.limit ?? store.limit
    return store.fetchItems(nextPage, nextLimit, opts.category ?? null)
  }

  return {
    items,
    loading,
    page,
    limit,
    refresh,
    deleteItem: store.deleteItem,
    updateItem: store.updateItem,
    createItem: store.createItem
  }
}
