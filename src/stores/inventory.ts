/**
 * Store Pinia - inventory.ts (TypeScript)
 * Gestiona el estado de inventario con tipos completos
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { InventoryItem, CreateInventoryItemData, UpdateInventoryItemData } from '@/types/stores';
import api from '@/services/api';

function extractApiData<T>(response: any, fallback: T): T {
  return (response?.data?.data ?? response?.data ?? fallback) as T;
}

export const useInventoryStore = defineStore('inventory', () => {
  // State
  const items = ref<InventoryItem[]>([]);
  const isLoading = ref(false);
  const error = ref<any | null>(null);
  const searchQuery = ref('');
  const page = ref(1);
  const limit = ref(20);
  const catalogStatus = ref<Record<string, any> | null>(null);
  const syncingCatalog = ref(false);
  const importing = ref(false);
  const lastRunId = ref<string | null>(null);
  const runStatus = ref<string | null>(null);

  /**
   * Fetch inventory items with pagination and filters
   */
  async function fetchItems(
    pageNum: number = 1,
    limitNum: number = 20,
    search: string | null = null,
    categoryId: string | null = null
  ): Promise<InventoryItem[]> {
    isLoading.value = true;
    error.value = null;
    page.value = pageNum;
    limit.value = limitNum;

    try {
      const params = new URLSearchParams({
        limit: String(limitNum),
        page: String(pageNum),
      });

      if (search) {
        params.set('search', search);
      }
      if (categoryId) {
        params.set('category_id', categoryId);
      }

      const response = await api.get(`/inventory/?${params.toString()}`);
      items.value = extractApiData<InventoryItem[]>(response, []);
    } catch (err: any) {
      error.value = err;
      items.value = [];
    } finally {
      isLoading.value = false;
    }
    return items.value;
  }

  /**
   * Search inventory items
   */
  async function searchItems(query: string): Promise<InventoryItem[]> {
    searchQuery.value = query;
    return fetchItems(1, limit.value, query);
  }

  /**
   * Update stock for item
   */
  async function updateStock(id: string, quantity: number): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const payload = { stock: quantity };
      await api.put(`/inventory/${id}`, payload);
      await fetchItems(page.value, limit.value);
    } catch (err: any) {
      error.value = err;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Get low stock items
   */
  async function getLowStockItems(): Promise<InventoryItem[]> {
    try {
      const response = await api.get('/inventory/low-stock');
      return extractApiData<InventoryItem[]>(response, []);
    } catch (err: any) {
      error.value = err;
      return [];
    }
  }

  /**
   * Create inventory item
   */
  async function addItem(data: CreateInventoryItemData): Promise<InventoryItem | null> {
    isLoading.value = true;
    error.value = null;
    try {
      const payload: Record<string, any> = { ...data };
      // Normalize: handle both quantity and stock
      if (payload.quantity !== undefined && !('stock' in payload)) {
        payload.stock = payload.quantity;
      }
      delete payload.quantity;

      const response = await api.post('/inventory/', payload);
      const created = extractApiData<InventoryItem | null>(response, null);
      if (created) {
        items.value = [created, ...items.value.filter((item) => String(item.id) !== String(created.id))];
      }
      return created;
    } catch (err: any) {
      error.value = err;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update inventory item
   */
  async function updateItem(id: string, data: UpdateInventoryItemData): Promise<InventoryItem | null> {
    isLoading.value = true;
    error.value = null;
    try {
      const payload: Record<string, any> = { ...data };
      // Normalize: handle both quantity and stock
      if (payload.quantity !== undefined && !('stock' in payload)) {
        payload.stock = payload.quantity;
      }
      delete payload.quantity;

      const response = await api.put(`/inventory/${id}`, payload);
      const updated = extractApiData<InventoryItem | null>(response, null);
      if (updated) {
        items.value = items.value.map((item) =>
          String(item.id) === String(id) ? ({ ...item, ...updated } as InventoryItem) : item
        );
      }
      return updated;
    } catch (err: any) {
      error.value = err;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Delete inventory item
   */
  async function deleteItem(itemId: string): Promise<boolean> {
    isLoading.value = true;
    error.value = null;
    try {
      await api.delete(`/inventory/${itemId}`);
      items.value = items.value.filter((item) => String(item.id) !== String(itemId));
      return true;
    } catch (err: any) {
      error.value = err;
      console.error('Error deleting item', err);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchCatalogStatus(): Promise<Record<string, any> | null> {
    error.value = null;
    try {
      const response = await api.get('/inventory/store-catalog/status');
      catalogStatus.value = extractApiData<Record<string, any> | null>(response, null);
      return catalogStatus.value;
    } catch (err: any) {
      error.value = err;
      throw err;
    }
  }

  async function fetchItemById(itemId: string): Promise<Record<string, any> | null> {
    error.value = null;
    try {
      const response = await api.get(`/inventory/${itemId}`);
      const item = extractApiData<Record<string, any> | null>(response, null);
      if (!item) {
        return null;
      }
      const currentIndex = items.value.findIndex((existing) => String(existing.id) === String(itemId));
      if (currentIndex >= 0) {
        items.value.splice(currentIndex, 1, { ...items.value[currentIndex], ...item });
      } else {
        items.value.unshift(item);
      }
      return item;
    } catch (err: any) {
      error.value = err;
      throw err;
    }
  }

  async function syncCatalog(): Promise<Record<string, any> | null> {
    if (syncingCatalog.value) {
      return null;
    }
    error.value = null;
    syncingCatalog.value = true;
    try {
      const response = await api.post('/inventory/store-catalog/sync');
      const data = extractApiData<Record<string, any> | null>(response, null);
      catalogStatus.value = data?.status || null;
      await fetchItems(page.value, limit.value);
      return data;
    } catch (err: any) {
      error.value = err;
      throw err;
    } finally {
      syncingCatalog.value = false;
    }
  }

  async function triggerImport(): Promise<Record<string, any>> {
    if (importing.value) {
      return {
        run_id: lastRunId.value,
        status: runStatus.value,
      };
    }
    error.value = null;
    importing.value = true;
    try {
      const response = await api.post('/imports/run');
      const data = extractApiData<Record<string, any>>(response, {});
      lastRunId.value = data.run_id || null;
      runStatus.value = data.status || null;
      return data;
    } catch (err: any) {
      error.value = err;
      throw err;
    } finally {
      importing.value = false;
    }
  }

  /**
   * Set error message
   */
  function setError(message: any): void {
    error.value = message;
  }

  return {
    // State
    items,
    loading: isLoading,
    isLoading,
    error,
    searchQuery,
    page,
    limit,
    catalogStatus,
    syncingCatalog,
    importing,
    lastRunId,
    runStatus,
    // Actions
    fetchItems,
    searchItems,
    updateStock,
    getLowStockItems,
    createItem: addItem,
    addItem,
    updateItem,
    deleteItem,
    fetchCatalogStatus,
    fetchItemById,
    syncCatalog,
    triggerImport,
    setError,
  };
});
