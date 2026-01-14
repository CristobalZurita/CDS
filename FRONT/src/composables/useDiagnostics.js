import { useDiagnosticsStore } from '@/stores/diagnostics'
export function useDiagnostics() {
  const store = useDiagnosticsStore()
  return {
    diagnostics: store.diagnostics,
    loading: store.loading,
    error: store.error,
    fetchDiagnostics: store.fetchDiagnostics,
    createDiagnostic: store.createDiagnostic,
    updateDiagnostic: store.updateDiagnostic,
    deleteDiagnostic: store.deleteDiagnostic
  }
}
