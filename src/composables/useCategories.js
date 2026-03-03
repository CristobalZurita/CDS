import { storeToRefs } from 'pinia'
import { useCategoriesStore } from '@/stores/categories'
export function useCategories() {
  const store = useCategoriesStore()
  const refs = storeToRefs(store)
  const categories = refs.categories
  const loading = refs.loading || refs.isLoading
  const error = refs.error
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
