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
  currentRepair: Ref<Record<string, any> | null>
  currentRepairTimeline: Ref<Record<string, any>[]>
  currentRepairPhotos: Ref<Record<string, any>[]>
  currentRepairNotes: Ref<Record<string, any>[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchRepairs: () => Promise<Repair[]>
  fetchClientRepairs: () => Promise<Repair[]>
  fetchClientRepairDetail: (id: string) => Promise<Record<string, any> | null>
  downloadClientClosurePdf: (id: string) => Promise<BlobPart>
  clearCurrentRepairDetail: () => void
  createRepair: (data: any) => Promise<Repair>
  updateRepair: (id: string, data: any) => Promise<Repair>
  deleteRepair: (id: string) => Promise<boolean>
}

export function useRepairs(): UseRepairsComposable {
  const store = useRepairsStore()
  const refs = storeToRefs(store)
  const repairs = refs.repairs
  const currentRepair = refs.currentRepair
  const currentRepairTimeline = refs.currentRepairTimeline
  const currentRepairPhotos = refs.currentRepairPhotos
  const currentRepairNotes = refs.currentRepairNotes
  const error = refs.error
  const loading = 'loading' in store ? refs.loading : refs.isLoading

  return {
    repairs,
    currentRepair,
    currentRepairTimeline,
    currentRepairPhotos,
    currentRepairNotes,
    loading,
    error,
    fetchRepairs: store.fetchRepairs,
    fetchClientRepairs: store.fetchClientRepairs,
    fetchClientRepairDetail: store.fetchClientRepairDetail,
    downloadClientClosurePdf: store.downloadClientClosurePdf,
    clearCurrentRepairDetail: store.clearCurrentRepairDetail,
    createRepair: store.createRepair,
    updateRepair: store.updateRepair,
    deleteRepair: store.deleteRepair
  }
}
