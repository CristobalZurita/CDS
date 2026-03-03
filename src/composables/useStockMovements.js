import { storeToRefs } from 'pinia'
import { useStockMovementsStore } from '@/stores/stockMovements'
export function useStockMovements() {
  const store = useStockMovementsStore()
  const refs = storeToRefs(store)
  const movements = refs.movements
  const loading = refs.loading || refs.isLoading
  const error = refs.error
  return {
    movements,
    loading,
    error,
    fetchMovements: store.fetchMovements,
    createMovement: store.createMovement
  }
}
