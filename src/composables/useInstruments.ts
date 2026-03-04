/**
 * 🎯 useInstruments - Auto-sync de instrumentos
 * 
 * Sincroniza automáticamente al iniciar la app
 * Detecta cambios en la carpeta de fotos sin intervención manual
 * 
 * CARACTERÍSTICAS:
 * - Auto-ejecuta sync al montar el composable
 * - Detecta cambios (nuevos archivos = nuevos instrumentos)
 * - Modo inteligente: solo sincranza si hay cambios
 * - Fallback a JSON local si el API no está disponible
 * 
 * USO BÁSICO:
 * const { instruments, loading, lastSync } = useInstruments()
 * 
 * USO AVANZADO:
 * - getInstruments(): Instrumento[] → obtener todos
 * - getInstrumentsByMarca(marca): Instrumento[]
 * - getInstrumentById(id): Instrumento | undefined
 */

import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import localInstrumentsData from '@/data/instruments.json'
import { useInstrumentsStore } from '@/stores/instruments'

// ============================================================================
// TIPOS
// ============================================================================

export interface Instrument {
  id: string
  marca: string
  modelo: string
  foto_principal: string
  fotos_adicionales: string[]
  tipos: string[]
  agregado_en?: string
}

export interface InstrumentsData {
  version: string
  total_bases: number
  total_variantes: number
  total_fotos: number
  instruments: Instrument[]
}

// ============================================================================
// ESTADO GLOBAL (compartido entre composables)
// ============================================================================

const instruments = ref<Instrument[]>([])
const loading = ref(false)
const synced = ref(false)
const lastSyncTime = ref<string | null>(null)
const error = ref<string | null>(null)

// ============================================================================
// FUNCIONES DE SINCRONIZACIÓN
// ============================================================================

/**
 * MÉTODO 1: Sincroniza a través del API (ejecuta script Python en backend)
 * Este es el método preferido para producción
 */
async function syncViaAPI(force: boolean = false): Promise<boolean> {
  try {
    loading.value = true
    error.value = null
    
    const response = await fetch(`/api/v1/instruments-sync/sync?force=${force ? 'true' : 'false'}`, {
      method: 'POST'
    })
    
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`)
    }
    
    const payload = await response.json()
    const data: InstrumentsData = payload?.result?.data || payload?.data || payload

    instruments.value = data.instruments
    synced.value = true
    lastSyncTime.value = new Date().toISOString()
    
    console.log(
      `✅ API Sync: ${data.total_fotos} fotos, ${data.total_bases} bases`
    )
    return true
    
  } catch (err) {
    console.warn('API sync falló, intentando fallback a JSON local', err)
    return false
  } finally {
    loading.value = false
  }
}

/**
 * MÉTODO 2: Fallback - carga JSON estático generado
 * Si no hay API disponible, usar JSON que se generó en build time
 */
async function loadFromJSON(): Promise<boolean> {
  try {
    loading.value = true
    error.value = null
    
    const data = localInstrumentsData as InstrumentsData

    instruments.value = data.instruments
    synced.value = true
    lastSyncTime.value = new Date().toISOString()
    
    console.log(
      `✅ JSON Fallback: ${data.total_fotos} fotos, ${data.total_bases} bases`
    )
    return true
    
  } catch (err) {
    console.error('Error cargando JSON local:', err)
    error.value = 'No se pudieron cargar los instrumentos'
    return false
  } finally {
    loading.value = false
  }
}

/**
 * SINCRONIZACIÓN AUTOMÁTICA INTELIGENTE
 * - Intenta API primero (método preferido)
 * - Si falla, usa JSON local (fallback)
 */
async function autoSync(force: boolean = false): Promise<boolean> {
  // Intentar API
  const apiSuccess = await syncViaAPI(force)
  
  if (apiSuccess) {
    return true
  }
  
  // Fallback a JSON local
  return await loadFromJSON()
}

// ============================================================================
// COMPOSABLE PRINCIPAL
// ============================================================================

export function useInstruments() {
  const store = useInstrumentsStore()
  const refs = storeToRefs(store)

  return {
    // Compatibilidad con contrato legacy del composable JS.
    instruments: refs.instruments,
    loading: refs.loading || refs.isLoading,
    error: refs.error,
    fetchInstruments: store.fetchInstruments,
    createInstrument: store.createInstrument,
    updateInstrument: store.updateInstrument,
    deleteInstrument: store.deleteInstrument,

    // API de sincronización existente en la versión TS.
    synced: computed(() => synced.value),
    lastSync: computed(() => lastSyncTime.value),
    sync: (force?: boolean) => autoSync(force),
    syncViaAPI: (force?: boolean) => syncViaAPI(force),
    loadFromJSON
  }
}

// ============================================================================
// UTILIDADES DIRECTAS (sin composable)
// ============================================================================

export function getInstruments(): Instrument[] {
  return instruments.value
}

export function getInstrumentsByMarca(marca: string): Instrument[] {
  return instruments.value.filter(i => i.marca === marca)
}

export function getInstrumentById(id: string): Instrument | undefined {
  return instruments.value.find(i => i.id === id)
}

export function getInstrumentsByType(type: string): Instrument[] {
  return instruments.value.filter(i => i.tipos?.includes(type))
}

export function getTotalInstruments(): number {
  return instruments.value.length
}
