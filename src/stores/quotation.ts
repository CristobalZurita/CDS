/**
 * Store Pinia - quotation.ts (TypeScript)
 * Gestiona el estado de cotizaciones con tipos completos
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { QuotationsStoreState, Quotation, QuotationItem } from '@/types/stores';
import { get, post, handleApiError } from '@/services/api';

interface Instrument {
  id: string;
  name: string;
  [key: string]: any;
}

interface Fault {
  id: string;
  name: string;
  [key: string]: any;
}

export const useQuotationStore = defineStore('quotation', () => {
  // State
  const quotations = ref<Quotation[]>([]);
  const selectedInstrument = ref<Instrument | null>(null);
  const selectedFaults = ref<Fault[]>([]);
  const currentQuotation = ref<Quotation | null>(null);
  const quotationHistory = ref<any[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const quotationItems = ref<QuotationItem[]>([]);

  // Computed
  const hasSelected = computed(() => selectedInstrument.value !== null);
  const hasFaults = computed(() => selectedFaults.value.length > 0);
  const hasQuotation = computed(() => currentQuotation.value !== null);
  const total = computed(() => {
    if (currentQuotation.value && Number.isFinite(Number(currentQuotation.value.total))) {
      return Number(currentQuotation.value.total);
    }

    return quotationItems.value.reduce((sum, item) => {
      const quantity = Number(item?.quantity || 0);
      const unitPrice = Number((item as any)?.unitPrice ?? (item as any)?.unit_price ?? 0);
      return sum + quantity * unitPrice;
    }, 0);
  });

  /**
   * Set selected instrument
   */
  function setInstrument(instrument: Instrument): void {
    selectedInstrument.value = instrument;
  }

  /**
   * Set selected faults
   */
  function setFaults(faults: Fault[]): void {
    selectedFaults.value = faults;
  }

  /**
   * Set quotation
   */
  function setQuotation(quotation: Quotation): void {
    currentQuotation.value = quotation;
    quotationHistory.value.push({
      ...quotation,
      savedAt: new Date(),
    });

    if (!quotation || (quotation as any).id == null) {
      return;
    }

    const quoteId = Number((quotation as any).id);
    const existingIndex = quotations.value.findIndex((item: any) => Number(item?.id) === quoteId);
    if (existingIndex >= 0) {
      quotations.value[existingIndex] = quotation;
      return;
    }

    quotations.value.push(quotation);
  }

  /**
   * Fetch quotations
   */
  async function fetchQuotations(): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get<Quotation[]>('/quotations');
      quotations.value = response.data.data || [];
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Get single quotation
   */
  async function getQuotation(id: string): Promise<Quotation | null> {
    try {
      const response = await get<Quotation>(`/quotations/${id}`);
      if (response.data.data) {
        currentQuotation.value = response.data.data;
      }
      return response.data.data || null;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      return null;
    }
  }

  /**
   * Create quotation from diagnostic
   */
  async function createQuotation(diagnosticId: string): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post<Quotation>('/quotations', {
        diagnostic_id: diagnosticId,
      });
      if (response.data.data) {
        currentQuotation.value = response.data.data;
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
   * Add item to quotation
   */
  function addItem(item: QuotationItem): void {
    quotationItems.value.push(item);
  }

  /**
   * Remove item from quotation
   */
  function removeItem(itemId: string): void {
    quotationItems.value = quotationItems.value.filter((item) => item.id !== itemId);
  }

  /**
   * Update item in quotation
   */
  function updateItem(itemId: string, updates: Partial<QuotationItem>): void {
    const index = quotationItems.value.findIndex((item) => item.id === itemId);
    if (index !== -1) {
      quotationItems.value[index] = {
        ...quotationItems.value[index],
        ...updates,
      };
    }
  }

  /**
   * Accept quotation
   */
  async function acceptQuotation(id: string): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      await post(`/quotations/${id}/accept`, {});
      if (currentQuotation.value && currentQuotation.value.id === id) {
        currentQuotation.value.status = 'accepted';
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
   * Reject quotation
   */
  async function rejectQuotation(id: string): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      await post(`/quotations/${id}/reject`, {});
      if (currentQuotation.value && currentQuotation.value.id === id) {
        currentQuotation.value.status = 'rejected';
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
   * Calculate total of items
   */
  function calculateTotal(): number {
    return quotationItems.value.reduce((sum, item) => {
      return sum + (item.quantity * (item.unitPrice || 0));
    }, 0);
  }

  /**
   * Reset quotation state
   */
  function reset(): void {
    selectedInstrument.value = null;
    selectedFaults.value = [];
    currentQuotation.value = null;
    quotationItems.value = [];
    error.value = null;
    isLoading.value = false;
  }

  /**
   * Clear instrument
   */
  function clearInstrument(): void {
    selectedInstrument.value = null;
  }

  /**
   * Clear faults
   */
  function clearFaults(): void {
    selectedFaults.value = [];
  }

  /**
   * Set error message
   */
  function setError(message: string): void {
    error.value = message;
  }

  return {
    // State
    quotations,
    selectedInstrument,
    selectedFaults,
    currentQuotation,
    quotationHistory,
    loading: isLoading,
    isLoading,
    error,
    quotationItems,
    // Computed
    hasSelected,
    hasFaults,
    hasQuotation,
    total,
    // Actions
    setInstrument,
    setFaults,
    setQuotation,
    fetchQuotations,
    getQuotation,
    createQuotation,
    addItem,
    removeItem,
    updateItem,
    acceptQuotation,
    rejectQuotation,
    calculateTotal,
    reset,
    clearInstrument,
    clearFaults,
    setError,
  };
});
