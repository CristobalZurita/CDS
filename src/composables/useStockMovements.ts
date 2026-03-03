import { storeToRefs } from 'pinia'
import { useStockMovementsStore } from '@/stores/stockMovements'
import type { Ref } from 'vue'

interface StockMovement {
  id: string
  itemId: string
  quantity: number
  type: 'in' | 'out'
  reason?: string
  createdAt?: string
  updatedAt?: string
}

export interface UseStockMovementsComposable {
  movements: Ref<StockMovement[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchMovements: () => Promise<StockMovement[]>
  createMovement: (data: any) => Promise<StockMovement>
}

export function useStockMovements(): UseStockMovementsComposable {
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
