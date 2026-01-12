import { useInstrumentsStore } from '@/stores/instruments'
export function useInstruments() {
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
