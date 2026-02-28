import { storeToRefs } from 'pinia'
import { useRepairsStore } from '@/stores/repairs'
import type { Ref } from 'vue'

interface Repair {
  id: string
  status: string
  description?: string
  createdAt?: string
  updatedAt?: string
}

export interface UseRepairsComposable {
  repairs: Ref<Repair[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchRepairs: () => Promise<Repair[]>
  createRepair: (data: any) => Promise<Repair>
  updateRepair: (id: string, data: any) => Promise<Repair>
  deleteRepair: (id: string) => Promise<boolean>
}

export function useRepairs(): UseRepairsComposable {
  const store = useRepairsStore()
  const { repairs, error } = storeToRefs(store)
  const loading = 'loading' in store ? storeToRefs(store).loading : storeToRefs(store).isLoading

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
