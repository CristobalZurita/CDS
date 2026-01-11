import { useRepairsStore } from '@/stores/repairs'
export function useRepairs() {
  const store = useRepairsStore()
  return {
    repairs: store.repairs,
    loading: store.loading,
    error: store.error,
    fetchRepairs: store.fetchRepairs,
    createRepair: store.createRepair,
    updateRepair: store.updateRepair,
    deleteRepair: store.deleteRepair
  }
}
