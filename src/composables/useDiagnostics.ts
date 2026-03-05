import { storeToRefs } from 'pinia'
import { useDiagnosticsStore } from '@/stores/diagnostics'
import type { Ref } from 'vue'

interface Diagnostic {
  id: string
  instrumentId: string
  faults: string[]
  status?: string
  createdAt?: string
  updatedAt?: string
}

export interface UseDiagnosticsComposable {
  diagnostics: Ref<Diagnostic[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchDiagnostics: () => Promise<Diagnostic[]>
  createDiagnostic: (data: any) => Promise<Diagnostic>
  updateDiagnostic: (id: string, data: any) => Promise<Diagnostic>
  deleteDiagnostic: (id: string) => Promise<boolean>
}

export function useDiagnostics(): UseDiagnosticsComposable {
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
