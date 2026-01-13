import { useInventoryStore } from '@/stores/inventory'

export function useInventory() {
  const store = useInventoryStore()
  return {
    items: store.items,
    loading: store.loading,
    page: store.page,
    limit: store.limit,
    fetchItems: store.fetchItems,
    deleteItem: store.deleteItem,
    updateItem: store.updateItem,
    createItem: store.createItem
  }
}
