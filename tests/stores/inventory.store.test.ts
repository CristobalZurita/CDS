import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useInventoryStore } from '@stores/inventory'

describe('Inventory Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const store = useInventoryStore()
      expect(store.items).toEqual([])
      expect(store.categories).toEqual([])
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
      expect(store.selectedCategory).toBeNull()
    })
  })

  describe('Inventory Items Management', () => {
    it('should add item to inventory', () => {
      const store = useInventoryStore()
      const item = {
        id: 1,
        name: 'Capacitor 10µF',
        category: 'capacitors',
        quantity: 100,
        minStock: 20,
        maxStock: 500,
        unitPrice: 0.50,
        lastUpdated: new Date()
      }

      store.items.push(item)
      expect(store.items).toContainEqual(item)
    })

    it('should find item by ID', () => {
      const store = useInventoryStore()
      const item = {
        id: 1,
        name: 'Resistor 1kΩ',
        category: 'resistors',
        quantity: 500,
        minStock: 50,
        maxStock: 1000,
        unitPrice: 0.05,
        lastUpdated: new Date()
      }

      store.items = [item]
      const found = store.items.find(i => i.id === 1)

      expect(found).toEqual(item)
    })

    it('should update item quantity', () => {
      const store = useInventoryStore()
      store.items = [{
        id: 1,
        name: 'Resistor',
        category: 'resistors',
        quantity: 100,
        minStock: 20,
        maxStock: 500,
        unitPrice: 0.05,
        lastUpdated: new Date()
      }]

      store.items[0].quantity = 85
      expect(store.items[0].quantity).toBe(85)
    })

    it('should delete item from inventory', () => {
      const store = useInventoryStore()
      store.items = [
        { id: 1, name: 'Item1', category: 'cat1', quantity: 100, minStock: 20, maxStock: 500, unitPrice: 1, lastUpdated: new Date() },
        { id: 2, name: 'Item2', category: 'cat2', quantity: 50, minStock: 10, maxStock: 200, unitPrice: 2, lastUpdated: new Date() }
      ]

      store.items = store.items.filter(i => i.id !== 1)
      expect(store.items).toHaveLength(1)
      expect(store.items[0].id).toBe(2)
    })
  })

  describe('Stock Level Checks', () => {
    it('should identify low stock items', () => {
      const store = useInventoryStore()
      store.items = [
        { id: 1, name: 'Item1', category: 'cat1', quantity: 15, minStock: 20, maxStock: 500, unitPrice: 1, lastUpdated: new Date() },
        { id: 2, name: 'Item2', category: 'cat2', quantity: 100, minStock: 20, maxStock: 500, unitPrice: 2, lastUpdated: new Date() }
      ]

      const lowStock = store.items.filter(i => i.quantity < i.minStock)
      expect(lowStock).toHaveLength(1)
      expect(lowStock[0].id).toBe(1)
    })

    it('should identify overstocked items', () => {
      const store = useInventoryStore()
      store.items = [
        { id: 1, name: 'Item1', category: 'cat1', quantity: 600, minStock: 20, maxStock: 500, unitPrice: 1, lastUpdated: new Date() },
        { id: 2, name: 'Item2', category: 'cat2', quantity: 100, minStock: 20, maxStock: 500, unitPrice: 2, lastUpdated: new Date() }
      ]

      const overstock = store.items.filter(i => i.quantity > i.maxStock)
      expect(overstock).toHaveLength(1)
      expect(overstock[0].id).toBe(1)
    })

    it('should identify items at optimal stock', () => {
      const store = useInventoryStore()
      store.items = [
        { id: 1, name: 'Item1', category: 'cat1', quantity: 100, minStock: 20, maxStock: 500, unitPrice: 1, lastUpdated: new Date() },
        { id: 2, name: 'Item2', category: 'cat2', quantity: 15, minStock: 20, maxStock: 500, unitPrice: 2, lastUpdated: new Date() }
      ]

      const optimal = store.items.filter(i => i.quantity >= i.minStock && i.quantity <= i.maxStock)
      expect(optimal).toHaveLength(1)
      expect(optimal[0].id).toBe(1)
    })
  })

  describe('Categories Management', () => {
    it('should add category', () => {
      const store = useInventoryStore()
      store.categories.push('capacitors')
      store.categories.push('resistors')

      expect(store.categories).toContain('capacitors')
      expect(store.categories).toContain('resistors')
    })

    it('should filter items by category', () => {
      const store = useInventoryStore()
      store.items = [
        { id: 1, name: 'Item1', category: 'resistors', quantity: 100, minStock: 20, maxStock: 500, unitPrice: 1, lastUpdated: new Date() },
        { id: 2, name: 'Item2', category: 'capacitors', quantity: 50, minStock: 10, maxStock: 200, unitPrice: 2, lastUpdated: new Date() },
        { id: 3, name: 'Item3', category: 'resistors', quantity: 200, minStock: 30, maxStock: 600, unitPrice: 1.5, lastUpdated: new Date() }
      ]

      const resistors = store.items.filter(i => i.category === 'resistors')
      expect(resistors).toHaveLength(2)
    })

    it('should select category', () => {
      const store = useInventoryStore()
      store.selectedCategory = 'resistors'
      expect(store.selectedCategory).toBe('resistors')
    })
  })

  describe('Inventory Value Calculations', () => {
    it('should calculate total inventory value', () => {
      const store = useInventoryStore()
      store.items = [
        { id: 1, name: 'Item1', category: 'cat1', quantity: 100, minStock: 20, maxStock: 500, unitPrice: 10, lastUpdated: new Date() },
        { id: 2, name: 'Item2', category: 'cat2', quantity: 50, minStock: 10, maxStock: 200, unitPrice: 20, lastUpdated: new Date() },
        { id: 3, name: 'Item3', category: 'cat3', quantity: 200, minStock: 30, maxStock: 600, unitPrice: 5, lastUpdated: new Date() }
      ]

      const totalValue = store.items.reduce((sum, item) => sum + (item.quantity * item.unitPrice), 0)
      expect(totalValue).toBe(2500)
    })

    it('should calculate inventory value by category', () => {
      const store = useInventoryStore()
      store.items = [
        { id: 1, name: 'Item1', category: 'resistors', quantity: 100, minStock: 20, maxStock: 500, unitPrice: 0.50, lastUpdated: new Date() },
        { id: 2, name: 'Item2', category: 'capacitors', quantity: 50, minStock: 10, maxStock: 200, unitPrice: 1.00, lastUpdated: new Date() },
        { id: 3, name: 'Item3', category: 'resistors', quantity: 200, minStock: 30, maxStock: 600, unitPrice: 0.50, lastUpdated: new Date() }
      ]

      const resistorValue = store.items
        .filter(i => i.category === 'resistors')
        .reduce((sum, item) => sum + (item.quantity * item.unitPrice), 0)

      expect(resistorValue).toBe(150)
    })

    it('should calculate average item price', () => {
      const store = useInventoryStore()
      store.items = [
        { id: 1, name: 'Item1', category: 'cat1', quantity: 100, minStock: 20, maxStock: 500, unitPrice: 10, lastUpdated: new Date() },
        { id: 2, name: 'Item2', category: 'cat2', quantity: 50, minStock: 10, maxStock: 200, unitPrice: 20, lastUpdated: new Date() }
      ]

      const avgPrice = store.items.reduce((sum, item) => sum + item.unitPrice, 0) / store.items.length
      expect(avgPrice).toBe(15)
    })
  })

  describe('Reorder Management', () => {
    it('should identify items needing reorder', () => {
      const store = useInventoryStore()
      store.items = [
        { id: 1, name: 'Item1', category: 'cat1', quantity: 15, minStock: 20, maxStock: 500, unitPrice: 1, lastUpdated: new Date() },
        { id: 2, name: 'Item2', category: 'cat2', quantity: 100, minStock: 20, maxStock: 500, unitPrice: 2, lastUpdated: new Date() }
      ]

      const needsReorder = store.items.filter(i => i.quantity <= i.minStock)
      expect(needsReorder).toHaveLength(1)
      expect(needsReorder[0].id).toBe(1)
    })

    it('should calculate reorder quantity', () => {
      const store = useInventoryStore()
      const item = {
        id: 1,
        name: 'Item1',
        category: 'cat1',
        quantity: 10,
        minStock: 50,
        maxStock: 500,
        unitPrice: 1,
        lastUpdated: new Date()
      }

      const reorderQty = item.maxStock - item.quantity
      expect(reorderQty).toBe(490)
    })
  })

  describe('Search and Filter', () => {
    it('should search items by name', () => {
      const store = useInventoryStore()
      store.items = [
        { id: 1, name: 'Capacitor 10µF', category: 'capacitors', quantity: 100, minStock: 20, maxStock: 500, unitPrice: 0.50, lastUpdated: new Date() },
        { id: 2, name: 'Resistor 1kΩ', category: 'resistors', quantity: 50, minStock: 10, maxStock: 200, unitPrice: 0.05, lastUpdated: new Date() }
      ]

      const search = store.items.filter(i => i.name.toLowerCase().includes('capacitor'))
      expect(search).toHaveLength(1)
      expect(search[0].id).toBe(1)
    })

    it('should filter items by quantity range', () => {
      const store = useInventoryStore()
      store.items = [
        { id: 1, name: 'Item1', category: 'cat1', quantity: 50, minStock: 10, maxStock: 200, unitPrice: 1, lastUpdated: new Date() },
        { id: 2, name: 'Item2', category: 'cat2', quantity: 100, minStock: 10, maxStock: 200, unitPrice: 2, lastUpdated: new Date() },
        { id: 3, name: 'Item3', category: 'cat3', quantity: 200, minStock: 30, maxStock: 600, unitPrice: 3, lastUpdated: new Date() }
      ]

      const filtered = store.items.filter(i => i.quantity >= 50 && i.quantity <= 150)
      expect(filtered).toHaveLength(2)
    })
  })

  describe('Loading and Errors', () => {
    it('should set loading state', () => {
      const store = useInventoryStore()
      store.isLoading = true
      expect(store.isLoading).toBe(true)
    })

    it('should set error message', () => {
      const store = useInventoryStore()
      store.error = 'Failed to load inventory'
      expect(store.error).toBe('Failed to load inventory')
    })

    it('should clear error', () => {
      const store = useInventoryStore()
      store.error = 'Some error'
      store.error = null
      expect(store.error).toBeNull()
    })
  })

  describe('Inventory Movements', () => {
    it('should increase item quantity', () => {
      const store = useInventoryStore()
      store.items = [{
        id: 1,
        name: 'Item1',
        category: 'cat1',
        quantity: 100,
        minStock: 20,
        maxStock: 500,
        unitPrice: 1,
        lastUpdated: new Date()
      }]

      store.items[0].quantity += 50
      expect(store.items[0].quantity).toBe(150)
    })

    it('should decrease item quantity', () => {
      const store = useInventoryStore()
      store.items = [{
        id: 1,
        name: 'Item1',
        category: 'cat1',
        quantity: 100,
        minStock: 20,
        maxStock: 500,
        unitPrice: 1,
        lastUpdated: new Date()
      }]

      store.items[0].quantity -= 30
      expect(store.items[0].quantity).toBe(70)
    })
  })
})
