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
