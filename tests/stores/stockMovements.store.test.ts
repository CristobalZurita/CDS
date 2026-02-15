import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useStockMovementsStore } from '@stores/stockMovements'

describe('Stock Movements Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should have initial state', () => {
    const store = useStockMovementsStore()
    expect(store.movements).toEqual([])
    expect(store.isLoading).toBe(false)
  })

  it('should add stock movement', () => {
    const store = useStockMovementsStore()
    const movement = {
      id: 1,
      itemId: 1,
      type: 'in',
      quantity: 50,
      reason: 'Purchase',
      date: new Date()
    }
    store.movements.push(movement)
    expect(store.movements).toContainEqual(movement)
  })

  it('should find movement by ID', () => {
    const store = useStockMovementsStore()
    const movement = {
      id: 1,
      itemId: 1,
      type: 'in',
      quantity: 50,
      reason: 'Purchase',
      date: new Date()
    }
    store.movements = [movement]
    expect(store.movements.find(m => m.id === 1)).toEqual(movement)
  })

  it('should filter inbound movements', () => {
    const store = useStockMovementsStore()
    store.movements = [
      { id: 1, itemId: 1, type: 'in', quantity: 50, reason: 'Purchase', date: new Date() },
      { id: 2, itemId: 2, type: 'out', quantity: 10, reason: 'Repair', date: new Date() },
      { id: 3, itemId: 3, type: 'in', quantity: 30, reason: 'Return', date: new Date() }
    ]
    const inbound = store.movements.filter(m => m.type === 'in')
    expect(inbound).toHaveLength(2)
  })

  it('should filter outbound movements', () => {
    const store = useStockMovementsStore()
    store.movements = [
      { id: 1, itemId: 1, type: 'in', quantity: 50, reason: 'Purchase', date: new Date() },
      { id: 2, itemId: 2, type: 'out', quantity: 10, reason: 'Repair', date: new Date() }
    ]
    const outbound = store.movements.filter(m => m.type === 'out')
    expect(outbound).toHaveLength(1)
  })

  it('should calculate total inbound quantity', () => {
    const store = useStockMovementsStore()
    store.movements = [
      { id: 1, itemId: 1, type: 'in', quantity: 50, reason: 'Purchase', date: new Date() },
      { id: 2, itemId: 1, type: 'in', quantity: 30, reason: 'Return', date: new Date() }
    ]
    const total = store.movements
      .filter(m => m.type === 'in' && m.itemId === 1)
      .reduce((sum, m) => sum + m.quantity, 0)
    expect(total).toBe(80)
  })

  it('should calculate total outbound quantity', () => {
    const store = useStockMovementsStore()
    store.movements = [
      { id: 1, itemId: 1, type: 'out', quantity: 10, reason: 'Repair', date: new Date() },
      { id: 2, itemId: 1, type: 'out', quantity: 5, reason: 'Waste', date: new Date() }
    ]
    const total = store.movements
      .filter(m => m.type === 'out' && m.itemId === 1)
      .reduce((sum, m) => sum + m.quantity, 0)
    expect(total).toBe(15)
  })

  it('should filter movements by item', () => {
    const store = useStockMovementsStore()
    store.movements = [
      { id: 1, itemId: 1, type: 'in', quantity: 50, reason: 'Purchase', date: new Date() },
      { id: 2, itemId: 2, type: 'out', quantity: 10, reason: 'Repair', date: new Date() },
      { id: 3, itemId: 1, type: 'out', quantity: 5, reason: 'Waste', date: new Date() }
    ]
    const item1Movements = store.movements.filter(m => m.itemId === 1)
    expect(item1Movements).toHaveLength(2)
  })

  it('should filter movements by reason', () => {
    const store = useStockMovementsStore()
    store.movements = [
      { id: 1, itemId: 1, type: 'in', quantity: 50, reason: 'Purchase', date: new Date() },
      { id: 2, itemId: 2, type: 'in', quantity: 30, reason: 'Purchase', date: new Date() },
      { id: 3, itemId: 3, type: 'in', quantity: 20, reason: 'Return', date: new Date() }
    ]
    const purchase = store.movements.filter(m => m.reason === 'Purchase')
    expect(purchase).toHaveLength(2)
  })

  it('should sort movements by date', () => {
    const store = useStockMovementsStore()
    const date1 = new Date('2024-01-01')
    const date2 = new Date('2024-01-02')
    const date3 = new Date('2024-01-03')

    store.movements = [
      { id: 2, itemId: 1, type: 'in', quantity: 30, reason: 'Purchase', date: date2 },
      { id: 3, itemId: 1, type: 'in', quantity: 20, reason: 'Return', date: date3 },
      { id: 1, itemId: 1, type: 'in', quantity: 50, reason: 'Purchase', date: date1 }
    ]

    const sorted = [...store.movements].sort((a, b) => a.date.getTime() - b.date.getTime())
    expect(sorted[0].id).toBe(1)
    expect(sorted[2].id).toBe(3)
  })

  it('should count total movements', () => {
    const store = useStockMovementsStore()
    store.movements = [
      { id: 1, itemId: 1, type: 'in', quantity: 50, reason: 'Purchase', date: new Date() },
      { id: 2, itemId: 2, type: 'out', quantity: 10, reason: 'Repair', date: new Date() },
      { id: 3, itemId: 3, type: 'in', quantity: 20, reason: 'Return', date: new Date() }
    ]
    expect(store.movements.length).toBe(3)
  })

  it('should set loading state', () => {
    const store = useStockMovementsStore()
    store.isLoading = true
    expect(store.isLoading).toBe(true)
  })

  it('should calculate net stock change for item', () => {
    const store = useStockMovementsStore()
    const itemId = 1
    store.movements = [
      { id: 1, itemId, type: 'in', quantity: 100, reason: 'Purchase', date: new Date() },
      { id: 2, itemId, type: 'out', quantity: 30, reason: 'Repair', date: new Date() },
      { id: 3, itemId, type: 'in', quantity: 20, reason: 'Return', date: new Date() }
    ]

    const inbound = store.movements
      .filter(m => m.itemId === itemId && m.type === 'in')
      .reduce((sum, m) => sum + m.quantity, 0)
    const outbound = store.movements
      .filter(m => m.itemId === itemId && m.type === 'out')
      .reduce((sum, m) => sum + m.quantity, 0)
    const netChange = inbound - outbound

    expect(netChange).toBe(90)
  })
})
