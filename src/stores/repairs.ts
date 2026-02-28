/**
 * Store Pinia - repairs.ts (TypeScript)
 * Gestiona el estado de reparaciones con tipos completos
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { RepairsStoreState, Repair, CreateRepairData, UpdateRepairData, RepairFilters } from '@/types/stores';
import { get, post, put, deleteRequest, handleApiError } from '@/services/api';

export const useRepairsStore = defineStore('repairs', () => {
  // State
  const repairs = ref<Repair[]>([]);
  const currentRepair = ref<Repair | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const filters = ref<RepairFilters>({});

  /**
   * Fetch repairs with optional filters
   */
  async function fetchRepairs(filterParams?: RepairFilters): Promise<void> {
    isLoading.value = true;
    error.value = null;

    if (filterParams) {
      filters.value = filterParams;
    }

    try {
      const response = await get<Repair[]>('/repairs/');
      repairs.value = response.data.data || [];
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      repairs.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Get single repair by ID
   */
  async function getRepair(id: string): Promise<void> {
    try {
      const response = await get<Repair>(`/repairs/${id}`);
      currentRepair.value = response.data.data || null;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      currentRepair.value = null;
    }
  }

  /**
   * Create repair
   */
  async function createRepair(data: CreateRepairData): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post<Repair>('/repairs/', data);
      if (response.data.data) {
        repairs.value.push(response.data.data);
      }
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update repair
   */
  async function updateRepair(id: string, data: UpdateRepairData): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put<Repair>(`/repairs/${id}`, data);
      if (response.data.data) {
        const index = repairs.value.findIndex((r) => r.id === id);
        if (index !== -1) {
          repairs.value[index] = response.data.data;
        }
        if (currentRepair.value?.id === id) {
          currentRepair.value = response.data.data;
        }
      }
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Delete repair
   */
  async function deleteRepair(id: string): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      await deleteRequest(`/repairs/${id}`);
      repairs.value = repairs.value.filter((r) => r.id !== id);
      if (currentRepair.value?.id === id) {
        currentRepair.value = null;
      }
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Change repair status
   */
  async function changeStatus(id: string, status: Repair['status']): Promise<void> {
    try {
      const response = await put<Repair>(`/repairs/${id}`, { status });
      if (response.data.data) {
        const index = repairs.value.findIndex((r) => r.id === id);
        if (index !== -1) {
          repairs.value[index] = response.data.data;
        }
        if (currentRepair.value?.id === id) {
          currentRepair.value = response.data.data;
        }
      }
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      throw err;
    }
  }

  /**
   * Set error message
   */
  function setError(message: string): void {
    error.value = message;
  }

  /**
   * Clear repairs
   */
  function clearRepairs(): void {
    repairs.value = [];
    currentRepair.value = null;
  }

  return {
    // State
    repairs,
    currentRepair,
    isLoading,
    error,
    filters,
    // Actions
    fetchRepairs,
    getRepair,
    createRepair,
    updateRepair,
    deleteRepair,
    changeStatus,
    setError,
    clearRepairs,
  };
});
