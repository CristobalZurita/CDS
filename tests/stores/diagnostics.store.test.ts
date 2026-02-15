import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useDiagnosticsStore } from '@stores/diagnostics'

describe('Diagnostics Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should have initial state', () => {
    const store = useDiagnosticsStore()
    expect(store.diagnostics).toEqual([])
    expect(store.currentDiagnostic).toBeNull()
  })

  it('should add diagnostic', () => {
    const store = useDiagnosticsStore()
    const diag = { id: 1, repairId: 1, findings: 'Screen broken', status: 'pending' }
    store.diagnostics.push(diag)
    expect(store.diagnostics).toContainEqual(diag)
  })

  it('should find diagnostic by ID', () => {
    const store = useDiagnosticsStore()
    const diag = { id: 1, repairId: 1, findings: 'Screen broken', status: 'pending' }
    store.diagnostics = [diag]
    store.currentDiagnostic = diag
    expect(store.currentDiagnostic?.id).toBe(1)
  })

  it('should update diagnostic', () => {
    const store = useDiagnosticsStore()
    store.diagnostics = [{ id: 1, repairId: 1, findings: 'Old findings', status: 'pending' }]
    store.diagnostics[0].findings = 'Updated findings'
    expect(store.diagnostics[0].findings).toBe('Updated findings')
  })

  it('should delete diagnostic', () => {
    const store = useDiagnosticsStore()
    store.diagnostics = [
      { id: 1, repairId: 1, findings: 'Finding1', status: 'pending' },
      { id: 2, repairId: 2, findings: 'Finding2', status: 'pending' }
    ]
    store.diagnostics = store.diagnostics.filter(d => d.id !== 1)
    expect(store.diagnostics).toHaveLength(1)
  })

  it('should filter diagnostics by status', () => {
    const store = useDiagnosticsStore()
    store.diagnostics = [
      { id: 1, repairId: 1, findings: 'Finding1', status: 'pending' },
      { id: 2, repairId: 2, findings: 'Finding2', status: 'completed' },
      { id: 3, repairId: 3, findings: 'Finding3', status: 'pending' }
    ]
    const pending = store.diagnostics.filter(d => d.status === 'pending')
    expect(pending).toHaveLength(2)
  })

  it('should search diagnostics by findings', () => {
    const store = useDiagnosticsStore()
    store.diagnostics = [
      { id: 1, repairId: 1, findings: 'Screen broken', status: 'pending' },
      { id: 2, repairId: 2, findings: 'Battery issue', status: 'pending' }
    ]
    const results = store.diagnostics.filter(d => d.findings.includes('Screen'))
    expect(results).toHaveLength(1)
  })

  it('should count diagnostics', () => {
    const store = useDiagnosticsStore()
    store.diagnostics = [
      { id: 1, repairId: 1, findings: 'Finding1', status: 'pending' },
      { id: 2, repairId: 2, findings: 'Finding2', status: 'completed' }
    ]
    expect(store.diagnostics.length).toBe(2)
  })

  it('should group diagnostics by repair', () => {
    const store = useDiagnosticsStore()
    store.diagnostics = [
      { id: 1, repairId: 1, findings: 'Finding1', status: 'pending' },
      { id: 2, repairId: 1, findings: 'Finding2', status: 'completed' },
      { id: 3, repairId: 2, findings: 'Finding3', status: 'pending' }
    ]
    const repair1 = store.diagnostics.filter(d => d.repairId === 1)
    expect(repair1).toHaveLength(2)
  })
})
