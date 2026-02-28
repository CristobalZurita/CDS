/**
 * Store Pinia - categories.ts (TypeScript)
 * Gestiona el estado de categorías con tipos completos
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { CategoriesStoreState, CreateCategoryData, UpdateCategoryData, Category } from '@/types/stores';
import { get, post, put, deleteRequest, handleApiError } from '@/services/api';

export const useCategoriesStore = defineStore('categories', () => {
  // State
  const categories = ref<Category[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch all categories
   */
  async function fetchCategories(): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get<Category[]>('/categories/');
      categories.value = response.data.data || [];
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      categories.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Get single category by ID
   */
  async function getCategory(id: string): Promise<Category | null> {
    try {
      const response = await get<Category>(`/categories/${id}`);
      return response.data.data || null;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      return null;
    }
  }

  /**
   * Create new category
   */
  async function createCategory(data: CreateCategoryData): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post<Category>('/categories/', data);
      if (response.data.data) {
        categories.value.push(response.data.data);
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
   * Update category
   */
  async function updateCategory(id: string, data: UpdateCategoryData): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put<Category>(`/categories/${id}`, data);
      if (response.data.data) {
        const index = categories.value.findIndex((c) => c.id === id);
        if (index !== -1) {
          categories.value[index] = response.data.data;
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
   * Delete category
   */
  async function deleteCategory(id: string): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      await deleteRequest(`/categories/${id}`);
      categories.value = categories.value.filter((c) => c.id !== id);
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
    categories,
    isLoading,
    error,
    // Actions
    fetchCategories,
    getCategory,
    createCategory,
    updateCategory,
    deleteCategory,
    setError,
  };
});
