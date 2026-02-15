import { useInstrumentsStore } from '@/stores/instruments'
import type { Ref } from 'vue'

interface Instrument {
  id: string
  brand: string
  model: string
  type: string
  components?: any
  createdAt?: string
  updatedAt?: string
}

export interface UseInstrumentsComposable {
  instruments: Ref<Instrument[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchInstruments: () => Promise<Instrument[]>
  createInstrument: (data: any) => Promise<Instrument>
  updateInstrument: (id: string, data: any) => Promise<Instrument>
  deleteInstrument: (id: string) => Promise<boolean>
}

export function useInstruments(): UseInstrumentsComposable {
  const store = useInstrumentsStore()

  return {
    instruments: store.instruments,
    loading: store.loading,
    error: store.error,
    fetchInstruments: store.fetchInstruments,
    createInstrument: store.createInstrument,
    updateInstrument: store.updateInstrument,
    deleteInstrument: store.deleteInstrument
  }
}
