/**
 * Store Pinia - inventory.ts (TypeScript)
 * Gestiona el estado de inventario con tipos completos
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { InventoryStoreState, InventoryItem, CreateInventoryItemData, UpdateInventoryItemData } from '@/types/stores';
import { get, put, post, deleteRequest, handleApiError } from '@/services/api';

export const useInventoryStore = defineStore('inventory', () => {
  // State
  const items = ref<InventoryItem[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const searchQuery = ref('');
  const page = ref(1);
  const limit = ref(20);

  /**
   * Fetch inventory items with pagination and filters
   */
  async function fetchItems(
    pageNum: number = 1,
    limitNum: number = 20,
    search: string | null = null,
    categoryId: string | null = null
  ): Promise<void> {
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
  }

  /**
   * Search inventory items
   */
  async function searchItems(query: string): Promise<void> {
    searchQuery.value = query;
    await fetchItems(1, limit.value, query);
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
  async function addItem(data: CreateInventoryItemData): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const payload = { ...data };
      // Normalize: handle both quantity and stock
      if ((payload as any).quantity !== undefined && !('stock' in payload)) {
        (payload as any).stock = (payload as any).quantity;
      }
      delete (payload as any).quantity;

      const response = await post<InventoryItem>('/inventory', payload);
      if (response.data.data) {
        items.value.push(response.data.data);
      }
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
   * Update inventory item
   */
  async function updateItem(id: string, data: UpdateInventoryItemData): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const payload = { ...data };
      // Normalize: handle both quantity and stock
      if ((payload as any).quantity !== undefined && !('stock' in payload)) {
        (payload as any).stock = (payload as any).quantity;
      }
      delete (payload as any).quantity;

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
   * Delete inventory item
   */
  async function deleteItem(itemId: string): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      await deleteRequest(`/inventory/${itemId}`);
      items.value = items.value.filter((item) => item.id !== itemId);
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
   * Set error message
   */
  function setError(message: string): void {
    error.value = message;
  }

  return {
    // State
    items,
    isLoading,
    error,
    searchQuery,
    page,
    limit,
    // Actions
    fetchItems,
    searchItems,
    updateStock,
    getLowStockItems,
    addItem,
    updateItem,
    deleteItem,
    setError,
  };
});
