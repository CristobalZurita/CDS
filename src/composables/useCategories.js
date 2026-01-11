import { useCategoriesStore } from '@/stores/categories'
export function useCategories() {
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
