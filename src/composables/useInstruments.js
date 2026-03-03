import { storeToRefs } from 'pinia'
import { useInstrumentsStore } from '@/stores/instruments'
export function useInstruments() {
  const store = useInstrumentsStore()
  const refs = storeToRefs(store)
  const instruments = refs.instruments
  const loading = refs.loading || refs.isLoading
  const error = refs.error
  return {
    instruments,
    loading,
    error,
    fetchInstruments: store.fetchInstruments,
    createInstrument: store.createInstrument,
    updateInstrument: store.updateInstrument,
    deleteInstrument: store.deleteInstrument
  }
}
