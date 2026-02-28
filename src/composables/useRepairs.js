import { storeToRefs } from 'pinia'
import { useRepairsStore } from '@/stores/repairs'
export function useRepairs() {
  const store = useRepairsStore()
  const { repairs, loading, error } = storeToRefs(store)
  return {
    repairs,
    loading,
    error,
    fetchRepairs: store.fetchRepairs,
    createRepair: store.createRepair,
    updateRepair: store.updateRepair,
    deleteRepair: store.deleteRepair
  }
}
