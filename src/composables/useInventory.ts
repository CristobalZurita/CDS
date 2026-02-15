import { computed } from 'vue'
import { useInventoryStore } from '@/stores/inventory'
import type { ComputedRef, Ref } from 'vue'

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
  items: ComputedRef<InventoryItem[]>
  loading: ComputedRef<boolean>
  page: ComputedRef<number>
  limit: ComputedRef<number>
  refresh: (opts?: { page?: number; limit?: number; category?: string | null }) => Promise<InventoryItem[]>
  deleteItem: (id: string) => Promise<boolean>
  updateItem: (id: string, data: any) => Promise<InventoryItem>
  createItem: (data: any) => Promise<InventoryItem>
}

export function useInventory(): UseInventoryComposable {
  const store = useInventoryStore()

  const items = computed(() => store.items)
  const loading = computed(() => store.loading)
  const page = computed(() => store.page)
  const limit = computed(() => store.limit)

  const refresh = async (opts: { page?: number; limit?: number; category?: string | null } = {}): Promise<InventoryItem[]> => {
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
