import { storeToRefs } from 'pinia'
import { useRepairsStore } from '@/stores/repairs'
export function useRepairs() {
  const store = useRepairsStore()
  const refs = storeToRefs(store)
  const repairs = refs.repairs
  const currentRepair = refs.currentRepair
  const currentRepairTimeline = refs.currentRepairTimeline
  const currentRepairPhotos = refs.currentRepairPhotos
  const currentRepairNotes = refs.currentRepairNotes
  const loading = refs.loading || refs.isLoading
  const error = refs.error
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
