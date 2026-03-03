import { storeToRefs } from 'pinia'
import { useDiagnosticsStore } from '@/stores/diagnostics'
export function useDiagnostics() {
  const store = useDiagnosticsStore()
  const refs = storeToRefs(store)
  const diagnostics = refs.diagnostics
  const loading = refs.loading || refs.isLoading
  const error = refs.error
  return {
    diagnostics,
    loading,
    error,
    fetchDiagnostics: store.fetchDiagnostics,
    createDiagnostic: store.createDiagnostic,
    updateDiagnostic: store.updateDiagnostic,
    deleteDiagnostic: store.deleteDiagnostic
  }
}
