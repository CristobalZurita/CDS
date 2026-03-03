import { storeToRefs } from 'pinia'
import { useInventoryStore } from '@/stores/inventory'

export function useInventory() {
  const store = useInventoryStore()
  const refs = storeToRefs(store)

  const items = refs.items
  const loading = refs.loading || refs.isLoading
  const error = refs.error
  const page = refs.page
  const limit = refs.limit
  const catalogStatus = refs.catalogStatus
  const syncingCatalog = refs.syncingCatalog
  const importing = refs.importing
  const lastRunId = refs.lastRunId
  const runStatus = refs.runStatus

  const refresh = async (opts = {}) => {
    const nextPage = opts.page ?? store.page
    const nextLimit = opts.limit ?? store.limit
    return store.fetchItems(nextPage, nextLimit, opts.category ?? null)
  }

  return {
    items,
    loading,
    error,
    page,
    limit,
    catalogStatus,
    syncingCatalog,
    importing,
    lastRunId,
    runStatus,
    refresh,
    deleteItem: store.deleteItem,
    updateItem: store.updateItem,
    createItem: store.createItem,
    fetchCatalogStatus: store.fetchCatalogStatus,
    fetchItemById: store.fetchItemById,
    syncCatalog: store.syncCatalog,
    triggerImport: store.triggerImport,
  }
}
