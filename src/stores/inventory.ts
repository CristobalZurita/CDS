/**
 * Store Pinia - inventory.ts (TypeScript)
 * Gestiona el estado de inventario con tipos completos
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { InventoryStoreState, InventoryItem, CreateInventoryItemData, UpdateInventoryItemData } from '@/types/stores';
import api, { get, put, post, deleteRequest, handleApiError } from '@/services/api';

export const useInventoryStore = defineStore('inventory', () => {
  // State
  const items = ref<InventoryItem[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
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

      const response = await get<InventoryItem[]>(`/inventory?${params.toString()}`);
      items.value = response.data.data || [];
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
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
      await put<InventoryItem>(`/inventory/${id}`, payload);
      await fetchItems(page.value, limit.value);
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
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
      const response = await get<InventoryItem[]>('/inventory/low-stock');
      return response.data.data || [];
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      return [];
    }
  }

  /**
   * Create inventory item
   */
  async function addItem(data: CreateInventoryItemData): Promise<InventoryItem> {
    isLoading.value = true;
    error.value = null;
    try {
      const payload: Record<string, any> = { ...data };
      // Normalize: handle both quantity and stock
      if (payload.quantity !== undefined && !('stock' in payload)) {
        payload.stock = payload.quantity;
      }
      delete payload.quantity;

      const response = await post<InventoryItem>('/inventory', payload);
      const created = response.data.data;
      if (created) {
        items.value.push(created);
      }
      await fetchItems(page.value, limit.value);
      return created;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update inventory item
   */
  async function updateItem(id: string, data: UpdateInventoryItemData): Promise<InventoryItem> {
    isLoading.value = true;
    error.value = null;
    try {
      const payload: Record<string, any> = { ...data };
      // Normalize: handle both quantity and stock
      if (payload.quantity !== undefined && !('stock' in payload)) {
        payload.stock = payload.quantity;
      }
      delete payload.quantity;

      const response = await put<InventoryItem>(`/inventory/${id}`, payload);
      await fetchItems(page.value, limit.value);
      return response.data.data;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
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
      await deleteRequest(`/inventory/${itemId}`);
      items.value = items.value.filter((item) => item.id !== itemId);
      await fetchItems(page.value, limit.value);
      return true;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchCatalogStatus(): Promise<Record<string, any> | null> {
    error.value = null;
    try {
      const response = await api.get('/inventory/store-catalog/status');
      catalogStatus.value = response.data || null;
      return catalogStatus.value;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      throw err;
    }
  }

  async function fetchItemById(itemId: string): Promise<Record<string, any> | null> {
    error.value = null;
    try {
      const response = await api.get(`/inventory/${itemId}`);
      const item = response.data || null;
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
      const apiError = handleApiError(err);
      error.value = apiError.message;
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
      const data = response.data || null;
      catalogStatus.value = data?.status || null;
      await fetchItems(page.value, limit.value);
      return data;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
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
      const data = response.data || {};
      lastRunId.value = data.run_id || null;
      runStatus.value = data.status || null;
      return data;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      throw err;
    } finally {
      importing.value = false;
    }
  }

  /**
   * Set error message
   */
  function setError(message: string): void {
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
