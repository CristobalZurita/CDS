/**
 * Store Pinia - repairs.ts (TypeScript)
 * Gestiona el estado de reparaciones con tipos completos
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { RepairsStoreState, Repair, CreateRepairData, UpdateRepairData, RepairFilters } from '@/types/stores';
import api, { get, post, put, deleteRequest, handleApiError } from '@/services/api';
import { hydrateRepairPhotos, revokeHydratedRepairPhotos } from '@/services/secureMedia';

export const useRepairsStore = defineStore('repairs', () => {
  // State
  const repairs = ref<Repair[]>([]);
  const currentRepair = ref<Repair | null>(null);
  const currentRepairTimeline = ref<Record<string, any>[]>([]);
  const currentRepairPhotos = ref<Record<string, any>[]>([]);
  const currentRepairNotes = ref<Record<string, any>[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const filters = ref<RepairFilters>({});

  /**
   * Fetch repairs with optional filters
   */
  async function fetchRepairs(filterParams?: RepairFilters): Promise<Repair[]> {
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
    return repairs.value;
  }

  async function fetchClientRepairs(): Promise<Repair[]> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.get('/client/repairs');
      repairs.value = response.data || [];
      return repairs.value;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      repairs.value = [];
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Get single repair by ID
   */
  async function getRepair(id: string): Promise<Repair | null> {
    try {
      const response = await get<Repair>(`/repairs/${id}`);
      currentRepair.value = response.data.data || null;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      currentRepair.value = null;
    }
    return currentRepair.value;
  }

  async function fetchClientRepairDetail(id: string): Promise<Record<string, any> | null> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.get(`/client/repairs/${id}/details`);
      const detail = response.data || null;
      const nextPhotos = await hydrateRepairPhotos(detail?.photos || []);
      revokeHydratedRepairPhotos(currentRepairPhotos.value);
      currentRepair.value = detail?.repair || null;
      currentRepairTimeline.value = detail?.timeline || [];
      currentRepairPhotos.value = nextPhotos;
      currentRepairNotes.value = detail?.notes || [];
      return detail;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      currentRepair.value = null;
      currentRepairTimeline.value = [];
      revokeHydratedRepairPhotos(currentRepairPhotos.value);
      currentRepairPhotos.value = [];
      currentRepairNotes.value = [];
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function downloadClientClosurePdf(id: string): Promise<BlobPart> {
    error.value = null;
    try {
      const response = await api.get(`/client/repairs/${id}/closure-pdf`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      throw err;
    }
  }

  function clearCurrentRepairDetail(): void {
    revokeHydratedRepairPhotos(currentRepairPhotos.value);
    currentRepair.value = null;
    currentRepairTimeline.value = [];
    currentRepairPhotos.value = [];
    currentRepairNotes.value = [];
  }

  /**
   * Create repair
   */
  async function createRepair(data: CreateRepairData): Promise<Repair | null> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post<Repair>('/repairs/', data);
      const created = response.data.data || null;
      if (created) {
        repairs.value.push(created);
      }
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
   * Update repair
   */
  async function updateRepair(id: string, data: UpdateRepairData): Promise<Repair | null> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put<Repair>(`/repairs/${id}`, data);
      const updated = response.data.data || null;
      if (updated) {
        const index = repairs.value.findIndex((r) => r.id === id);
        if (index !== -1) {
          repairs.value[index] = updated;
        }
        if (currentRepair.value?.id === id) {
          currentRepair.value = updated;
        }
      }
      return updated;
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
  async function deleteRepair(id: string): Promise<boolean> {
    isLoading.value = true;
    error.value = null;
    try {
      await deleteRequest(`/repairs/${id}`);
      repairs.value = repairs.value.filter((r) => r.id !== id);
      if (currentRepair.value?.id === id) {
        currentRepair.value = null;
      }
      return true;
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
  async function changeStatus(id: string, status: Repair['status']): Promise<Repair | null> {
    try {
      const response = await put<Repair>(`/repairs/${id}`, { status });
      const updated = response.data.data || null;
      if (updated) {
        const index = repairs.value.findIndex((r) => r.id === id);
        if (index !== -1) {
          repairs.value[index] = updated;
        }
        if (currentRepair.value?.id === id) {
          currentRepair.value = updated;
        }
      }
      return updated;
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
    currentRepairTimeline,
    currentRepairPhotos,
    currentRepairNotes,
    loading: isLoading,
    isLoading,
    error,
    filters,
    // Actions
    fetchRepairs,
    fetchClientRepairs,
    getRepair,
    fetchClientRepairDetail,
    downloadClientClosurePdf,
    clearCurrentRepairDetail,
    createRepair,
    updateRepair,
    deleteRepair,
    changeStatus,
    setError,
    clearRepairs,
  };
});
