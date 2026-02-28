import { storeToRefs } from 'pinia'
import { useCategoriesStore } from '@/stores/categories'
export function useCategories() {
  const store = useCategoriesStore()
  const { categories, loading, error } = storeToRefs(store)
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
