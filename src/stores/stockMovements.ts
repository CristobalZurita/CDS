/**
 * Store Pinia - stockMovements.ts (TypeScript)
 * Gestiona el estado de movimientos de stock con tipos completos
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, handleApiError } from '@/services/api';

interface StockMovement {
  id: string;
  itemId: string;
  quantity: number;
  type: 'in' | 'out';
  reason: string;
  createdAt: string;
  [key: string]: any;
}

interface CreateStockMovementData {
  itemId: string;
  quantity: number;
  type: 'in' | 'out';
  reason?: string;
}

export const useStockMovementsStore = defineStore('stockMovements', () => {
  // State
  const movements = ref<StockMovement[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch all stock movements
   */
  async function fetchMovements(): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get<StockMovement[]>('/stock-movements');
      movements.value = response.data.data || [];
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      movements.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Create stock movement
   */
  async function createMovement(data: CreateStockMovementData): Promise<any> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post<StockMovement>('/stock-movements', data);
      if (response.data.data) {
        movements.value.push(response.data.data);
      }
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
   * Set error message
   */
  function setError(message: string): void {
    error.value = message;
  }

  return {
    // State
    movements,
    loading: isLoading,
    isLoading,
    error,
    // Actions
    fetchMovements,
    createMovement,
    setError,
  };
});
