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
