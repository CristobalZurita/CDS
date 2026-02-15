import { useCategoriesStore } from '@/stores/categories'
import type { Ref } from 'vue'

interface Category {
  id: string
  name: string
  description?: string
  createdAt?: string
  updatedAt?: string
}

export interface UseCategoriesComposable {
  categories: Ref<Category[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchCategories: () => Promise<Category[]>
  createCategory: (data: any) => Promise<Category>
  updateCategory: (id: string, data: any) => Promise<Category>
  deleteCategory: (id: string) => Promise<boolean>
}

export function useCategories(): UseCategoriesComposable {
  const store = useCategoriesStore()

  return {
    categories: store.categories,
    loading: store.loading,
    error: store.error,
    fetchCategories: store.fetchCategories,
    createCategory: store.createCategory,
    updateCategory: store.updateCategory,
    deleteCategory: store.deleteCategory
  }
}
