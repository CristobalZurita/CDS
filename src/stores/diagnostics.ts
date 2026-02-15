/**
 * Store Pinia - diagnostics.ts (TypeScript)
 * Gestiona el estado de diagnósticos con tipos completos
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, put, deleteRequest, handleApiError } from '@/services/api';

interface Diagnostic {
  id: string;
  name: string;
  description?: string;
  [key: string]: any;
}

export const useDiagnosticsStore = defineStore('diagnostics', () => {
  // State
  const diagnostics = ref<Diagnostic[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch all diagnostics
   */
  async function fetchDiagnostics(): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get<Diagnostic[]>('/diagnostic');
      diagnostics.value = response.data.data || [];
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      diagnostics.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Create diagnostic
   */
  async function createDiagnostic(data: any): Promise<any> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post<Diagnostic>('/diagnostic/calculate', data);
      if (response.data.data) {
        diagnostics.value.push(response.data.data);
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
   * Update diagnostic
   */
  async function updateDiagnostic(id: string, data: any): Promise<any> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put<Diagnostic>(`/diagnostic/${id}`, data);
      if (response.data.data) {
        const index = diagnostics.value.findIndex((d) => d.id === id);
        if (index !== -1) {
          diagnostics.value[index] = response.data.data;
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
   * Delete diagnostic
   */
  async function deleteDiagnostic(id: string): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      await deleteRequest(`/diagnostic/${id}`);
      diagnostics.value = diagnostics.value.filter((d) => d.id !== id);
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
    diagnostics,
    isLoading,
    error,
    // Actions
    fetchDiagnostics,
    createDiagnostic,
    updateDiagnostic,
    deleteDiagnostic,
    setError,
  };
});
