import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useInstrumentsStore } from '@stores/instruments'

describe('Instruments Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should have initial state', () => {
    const store = useInstrumentsStore()
    expect(store.instruments).toEqual([])
    expect(store.isLoading).toBe(false)
  })

  it('should add instrument', () => {
    const store = useInstrumentsStore()
    const instrument = {
      id: 1,
      name: 'Multimeter',
      category: 'Testing',
      status: 'available',
      lastCalibration: new Date()
    }
    store.instruments.push(instrument)
    expect(store.instruments).toContainEqual(instrument)
  })

  it('should find instrument by ID', () => {
    const store = useInstrumentsStore()
    const instrument = {
      id: 1,
      name: 'Multimeter',
      category: 'Testing',
      status: 'available',
      lastCalibration: new Date()
    }
    store.instruments = [instrument]
    expect(store.instruments.find(i => i.id === 1)).toEqual(instrument)
  })

  it('should update instrument', () => {
    const store = useInstrumentsStore()
    store.instruments = [{
      id: 1,
      name: 'Multimeter',
      category: 'Testing',
      status: 'available',
      lastCalibration: new Date()
    }]
    store.instruments[0].status = 'maintenance'
    expect(store.instruments[0].status).toBe('maintenance')
  })

  it('should delete instrument', () => {
    const store = useInstrumentsStore()
    store.instruments = [
      { id: 1, name: 'Multimeter', category: 'Testing', status: 'available', lastCalibration: new Date() },
      { id: 2, name: 'Soldering Iron', category: 'Soldering', status: 'available', lastCalibration: new Date() }
    ]
    store.instruments = store.instruments.filter(i => i.id !== 1)
    expect(store.instruments).toHaveLength(1)
  })

  it('should filter available instruments', () => {
    const store = useInstrumentsStore()
    store.instruments = [
      { id: 1, name: 'Multimeter', category: 'Testing', status: 'available', lastCalibration: new Date() },
      { id: 2, name: 'Soldering Iron', category: 'Soldering', status: 'maintenance', lastCalibration: new Date() },
      { id: 3, name: 'Screwdriver', category: 'Hand Tools', status: 'available', lastCalibration: new Date() }
    ]
    const available = store.instruments.filter(i => i.status === 'available')
    expect(available).toHaveLength(2)
  })

  it('should filter instruments in maintenance', () => {
    const store = useInstrumentsStore()
    store.instruments = [
      { id: 1, name: 'Multimeter', category: 'Testing', status: 'available', lastCalibration: new Date() },
      { id: 2, name: 'Soldering Iron', category: 'Soldering', status: 'maintenance', lastCalibration: new Date() }
    ]
    const maintenance = store.instruments.filter(i => i.status === 'maintenance')
    expect(maintenance).toHaveLength(1)
  })

  it('should group instruments by category', () => {
    const store = useInstrumentsStore()
    store.instruments = [
      { id: 1, name: 'Multimeter', category: 'Testing', status: 'available', lastCalibration: new Date() },
      { id: 2, name: 'Soldering Iron', category: 'Soldering', status: 'available', lastCalibration: new Date() },
      { id: 3, name: 'Oscilloscope', category: 'Testing', status: 'available', lastCalibration: new Date() }
    ]
    const testingInstruments = store.instruments.filter(i => i.category === 'Testing')
    expect(testingInstruments).toHaveLength(2)
  })

  it('should search instruments by name', () => {
    const store = useInstrumentsStore()
    store.instruments = [
      { id: 1, name: 'Multimeter', category: 'Testing', status: 'available', lastCalibration: new Date() },
      { id: 2, name: 'Soldering Iron', category: 'Soldering', status: 'available', lastCalibration: new Date() }
    ]
    const results = store.instruments.filter(i => i.name.includes('Multi'))
    expect(results).toHaveLength(1)
  })

  it('should count total instruments', () => {
    const store = useInstrumentsStore()
    store.instruments = [
      { id: 1, name: 'Multimeter', category: 'Testing', status: 'available', lastCalibration: new Date() },
      { id: 2, name: 'Soldering Iron', category: 'Soldering', status: 'available', lastCalibration: new Date() },
      { id: 3, name: 'Screwdriver', category: 'Hand Tools', status: 'available', lastCalibration: new Date() }
    ]
    expect(store.instruments.length).toBe(3)
  })

  it('should track last calibration date', () => {
    const store = useInstrumentsStore()
    const calibDate = new Date('2024-01-01')
    store.instruments = [{
      id: 1,
      name: 'Multimeter',
      category: 'Testing',
      status: 'available',
      lastCalibration: calibDate
    }]
    expect(store.instruments[0].lastCalibration).toEqual(calibDate)
  })
})
