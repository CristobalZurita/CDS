/**
 * Store Pinia - instruments.ts (TypeScript)
 * Gestiona el estado de instrumentos con tipos completos
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, put, deleteRequest, handleApiError } from '@/services/api';

interface Instrument {
  id: string;
  name: string;
  description?: string;
  [key: string]: any;
}

export const useInstrumentsStore = defineStore('instruments', () => {
  // State
  const instruments = ref<Instrument[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch all instruments
   */
  async function fetchInstruments(): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get<Instrument[]>('/instruments');
      instruments.value = response.data.data || [];
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      instruments.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Create instrument
   */
  async function createInstrument(data: any): Promise<any> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post<Instrument>('/instruments', data);
      if (response.data.data) {
        instruments.value.push(response.data.data);
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
   * Update instrument
   */
  async function updateInstrument(id: string, data: any): Promise<any> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put<Instrument>(`/instruments/${id}`, data);
      if (response.data.data) {
        const index = instruments.value.findIndex((i) => i.id === id);
        if (index !== -1) {
          instruments.value[index] = response.data.data;
        }
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
   * Delete instrument
   */
  async function deleteInstrument(id: string): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      await deleteRequest(`/instruments/${id}`);
      instruments.value = instruments.value.filter((i) => i.id !== id);
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
    instruments,
    isLoading,
    error,
    // Actions
    fetchInstruments,
    createInstrument,
    updateInstrument,
    deleteInstrument,
    setError,
  };
});
