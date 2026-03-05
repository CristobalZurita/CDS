import { storeToRefs } from 'pinia'
import { useInventoryStore } from '@/stores/inventory'
import type { Ref } from 'vue'

interface InventoryItem {
  id: string
  name: string
  sku: string
  quantity: number
  minQuantity?: number
  unitPrice?: number
  category?: string
  createdAt?: string
  updatedAt?: string
}

export interface UseInventoryComposable {
  items: Ref<InventoryItem[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  page: Ref<number>
  limit: Ref<number>
  catalogStatus: Ref<Record<string, any> | null>
  syncingCatalog: Ref<boolean>
  importing: Ref<boolean>
  lastRunId: Ref<string | null>
  runStatus: Ref<string | null>
  refresh: (opts?: { page?: number; limit?: number; category?: string | null }) => Promise<InventoryItem[]>
  fetchCatalogStatus: () => Promise<Record<string, any> | null>
  fetchItemById: (id: string) => Promise<Record<string, any> | null>
  syncCatalog: () => Promise<Record<string, any> | null>
  triggerImport: () => Promise<Record<string, any>>
  deleteItem: (id: string) => Promise<boolean>
  updateItem: (id: string, data: any) => Promise<InventoryItem>
  createItem: (data: any) => Promise<InventoryItem>
}

export function useInventory(): UseInventoryComposable {
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

  const refresh = async (opts: { page?: number; limit?: number; category?: string | null } = {}): Promise<InventoryItem[]> => {
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
    fetchCatalogStatus: store.fetchCatalogStatus,
    fetchItemById: store.fetchItemById,
    syncCatalog: store.syncCatalog,
    triggerImport: store.triggerImport,
    deleteItem: store.deleteItem,
    updateItem: store.updateItem,
    createItem: store.createItem
  }
}
