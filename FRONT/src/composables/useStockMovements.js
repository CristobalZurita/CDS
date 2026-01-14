import { useStockMovementsStore } from '@/stores/stockMovements'
export function useStockMovements() {
  const store = useStockMovementsStore()
  return {
    movements: store.movements,
    loading: store.loading,
    error: store.error,
    fetchMovements: store.fetchMovements,
    createMovement: store.createMovement
  }
}
