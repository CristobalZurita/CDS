import { storeToRefs } from 'pinia'
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
  const { categories, error } = storeToRefs(store)
  const loading = 'loading' in store ? storeToRefs(store).loading : storeToRefs(store).isLoading

  return {
    categories,
    loading,
    error,
    fetchCategories: store.fetchCategories,
    createCategory: store.createCategory,
    updateCategory: store.updateCategory,
    deleteCategory: store.deleteCategory
  }
}
