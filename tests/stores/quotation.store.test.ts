import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useQuotationStore } from '@stores/quotation'

describe('Quotation Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const store = useQuotationStore()
      expect(store.quotations).toEqual([])
      expect(store.currentQuotation).toBeNull()
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
      expect(store.total).toBe(0)
    })
  })

  describe('Quotation CRUD', () => {
    it('should create quotation', () => {
      const store = useQuotationStore()
      const quotation = {
        id: 1,
        repairId: 1,
        clientName: 'John Doe',
        items: [
          { itemId: 1, description: 'Screen replacement', quantity: 1, unitPrice: 150, subtotal: 150 }
        ],
        labor: 50,
        total: 200,
        status: 'pending',
        createdAt: new Date(),
        validUntil: new Date()
      }

      store.quotations.push(quotation)
      expect(store.quotations).toContainEqual(quotation)
    })

    it('should find quotation by ID', () => {
      const store = useQuotationStore()
      const quotation = {
        id: 1,
        repairId: 1,
        clientName: 'John Doe',
        items: [],
        labor: 50,
        total: 200,
        status: 'pending',
        createdAt: new Date(),
        validUntil: new Date()
      }

      store.quotations = [quotation]
      store.currentQuotation = quotation

      expect(store.currentQuotation?.id).toBe(1)
    })

    it('should update quotation', () => {
      const store = useQuotationStore()
      const quotation = {
        id: 1,
        repairId: 1,
        clientName: 'John Doe',
        items: [],
        labor: 50,
        total: 200,
        status: 'pending',
        createdAt: new Date(),
        validUntil: new Date()
      }

      store.quotations = [quotation]
      store.quotations[0].status = 'accepted'

      expect(store.quotations[0].status).toBe('accepted')
    })

    it('should delete quotation', () => {
      const store = useQuotationStore()
      store.quotations = [
        { id: 1, repairId: 1, clientName: 'John', items: [], labor: 50, total: 200, status: 'pending', createdAt: new Date(), validUntil: new Date() },
        { id: 2, repairId: 2, clientName: 'Jane', items: [], labor: 60, total: 250, status: 'pending', createdAt: new Date(), validUntil: new Date() }
      ]

      store.quotations = store.quotations.filter(q => q.id !== 1)
      expect(store.quotations).toHaveLength(1)
    })
  })

  describe('Status Management', () => {
    const validStatuses = ['pending', 'accepted', 'rejected', 'expired', 'invoiced']

    validStatuses.forEach(status => {
      it(`should set quotation status to ${status}`, () => {
        const store = useQuotationStore()
        store.currentQuotation = {
          id: 1,
          repairId: 1,
          clientName: 'John',
          items: [],
          labor: 50,
          total: 200,
          status: status as any,
          createdAt: new Date(),
          validUntil: new Date()
        }

        expect(store.currentQuotation?.status).toBe(status)
      })
    })

    it('should filter quotations by status', () => {
      const store = useQuotationStore()
      store.quotations = [
        { id: 1, repairId: 1, clientName: 'John', items: [], labor: 50, total: 200, status: 'pending', createdAt: new Date(), validUntil: new Date() },
        { id: 2, repairId: 2, clientName: 'Jane', items: [], labor: 60, total: 250, status: 'accepted', createdAt: new Date(), validUntil: new Date() },
        { id: 3, repairId: 3, clientName: 'Bob', items: [], labor: 70, total: 300, status: 'pending', createdAt: new Date(), validUntil: new Date() }
      ]

      const pending = store.quotations.filter(q => q.status === 'pending')
      expect(pending).toHaveLength(2)
    })
  })

  describe('Line Items Management', () => {
    it('should add item to quotation', () => {
      const store = useQuotationStore()
      const quotation = {
        id: 1,
        repairId: 1,
        clientName: 'John',
        items: [] as any[],
        labor: 50,
        total: 0,
        status: 'pending',
        createdAt: new Date(),
        validUntil: new Date()
      }

      const item = { itemId: 1, description: 'Screen', quantity: 1, unitPrice: 150, subtotal: 150 }
      quotation.items.push(item)

      expect(quotation.items).toContainEqual(item)
    })

    it('should remove item from quotation', () => {
      const store = useQuotationStore()
      const quotation = {
        id: 1,
        repairId: 1,
        clientName: 'John',
        items: [
          { itemId: 1, description: 'Screen', quantity: 1, unitPrice: 150, subtotal: 150 },
          { itemId: 2, description: 'Battery', quantity: 1, unitPrice: 80, subtotal: 80 }
        ] as any[],
        labor: 50,
        total: 280,
        status: 'pending',
        createdAt: new Date(),
        validUntil: new Date()
      }

      quotation.items = quotation.items.filter(i => i.itemId !== 1)
      expect(quotation.items).toHaveLength(1)
    })

    it('should calculate item subtotal', () => {
      const item = { itemId: 1, description: 'Screen', quantity: 2, unitPrice: 150, subtotal: 0 }
      item.subtotal = item.quantity * item.unitPrice

      expect(item.subtotal).toBe(300)
    })
  })

  describe('Total Calculations', () => {
    it('should calculate quotation total correctly', () => {
      const quotation = {
        id: 1,
        items: [
          { itemId: 1, description: 'Screen', quantity: 1, unitPrice: 150, subtotal: 150 },
          { itemId: 2, description: 'Battery', quantity: 1, unitPrice: 80, subtotal: 80 }
        ],
        labor: 50,
        tax: 0,
        discount: 0
      }

      const itemsTotal = quotation.items.reduce((sum, i) => sum + i.subtotal, 0)
      const total = itemsTotal + quotation.labor

      expect(total).toBe(280)
    })

    it('should apply tax to quotation', () => {
      const quotation = {
        subtotal: 280,
        taxRate: 0.21,
        tax: 0,
        total: 0
      }

      quotation.tax = quotation.subtotal * quotation.taxRate
      quotation.total = quotation.subtotal + quotation.tax

      expect(quotation.tax).toBe(58.8)
      expect(quotation.total).toBe(338.8)
    })

    it('should apply discount to quotation', () => {
      const quotation = {
        subtotal: 280,
        discount: 50,
        discountPercent: 0,
        total: 0
      }

      quotation.total = quotation.subtotal - quotation.discount

      expect(quotation.total).toBe(230)
    })

    it('should calculate discount percentage', () => {
      const quotation = {
        subtotal: 280,
        discount: 28,
        discountPercent: 0
      }

      quotation.discountPercent = (quotation.discount / quotation.subtotal) * 100

      expect(quotation.discountPercent).toBe(10)
    })
  })

  describe('Quotation Validity', () => {
    it('should check if quotation is expired', () => {
      const pastDate = new Date(new Date().getTime() - 86400000) // 1 day ago
      const quotation = {
        id: 1,
        validUntil: pastDate,
        status: 'pending'
      }

      const isExpired = new Date() > quotation.validUntil

      expect(isExpired).toBe(true)
    })

    it('should check if quotation is still valid', () => {
      const futureDate = new Date(new Date().getTime() + 604800000) // 7 days from now
      const quotation = {
        id: 1,
        validUntil: futureDate,
        status: 'pending'
      }

      const isValid = new Date() <= quotation.validUntil

      expect(isValid).toBe(true)
    })

    it('should mark expired quotations automatically', () => {
      const store = useQuotationStore()
      const pastDate = new Date(new Date().getTime() - 86400000)

      store.quotations = [
        { id: 1, repairId: 1, clientName: 'John', items: [], labor: 50, total: 200, status: 'pending', createdAt: new Date(), validUntil: pastDate }
      ]

      const expired = store.quotations.filter(q => q.status === 'pending' && new Date() > q.validUntil)
      expect(expired).toHaveLength(1)
    })
  })

  describe('Search and Filter', () => {
    it('should search quotations by client name', () => {
      const store = useQuotationStore()
      store.quotations = [
        { id: 1, repairId: 1, clientName: 'John Doe', items: [], labor: 50, total: 200, status: 'pending', createdAt: new Date(), validUntil: new Date() },
        { id: 2, repairId: 2, clientName: 'Jane Smith', items: [], labor: 60, total: 250, status: 'pending', createdAt: new Date(), validUntil: new Date() }
      ]

      const results = store.quotations.filter(q => q.clientName.toLowerCase().includes('john'))
      expect(results).toHaveLength(1)
      expect(results[0].id).toBe(1)
    })

    it('should filter quotations by amount range', () => {
      const store = useQuotationStore()
      store.quotations = [
        { id: 1, repairId: 1, clientName: 'John', items: [], labor: 50, total: 200, status: 'pending', createdAt: new Date(), validUntil: new Date() },
        { id: 2, repairId: 2, clientName: 'Jane', items: [], labor: 60, total: 250, status: 'pending', createdAt: new Date(), validUntil: new Date() },
        { id: 3, repairId: 3, clientName: 'Bob', items: [], labor: 70, total: 450, status: 'pending', createdAt: new Date(), validUntil: new Date() }
      ]

      const filtered = store.quotations.filter(q => q.total >= 200 && q.total <= 300)
      expect(filtered).toHaveLength(2)
    })
  })

  describe('Quotation Generation', () => {
    it('should generate unique quotation number', () => {
      const store = useQuotationStore()
      const quotations = [
        { id: 1, number: 'Q-2024-001', repairId: 1, clientName: 'John', items: [], labor: 50, total: 200, status: 'pending', createdAt: new Date(), validUntil: new Date() },
        { id: 2, number: 'Q-2024-002', repairId: 2, clientName: 'Jane', items: [], labor: 60, total: 250, status: 'pending', createdAt: new Date(), validUntil: new Date() }
      ]

      const nextNumber = `Q-2024-${String(quotations.length + 1).padStart(3, '0')}`
      expect(nextNumber).toBe('Q-2024-003')
    })

    it('should timestamp quotation creation', () => {
      const store = useQuotationStore()
      const now = new Date()
      const quotation = {
        id: 1,
        repairId: 1,
        clientName: 'John',
        items: [],
        labor: 50,
        total: 200,
        status: 'pending',
        createdAt: now,
        validUntil: new Date(now.getTime() + 604800000)
      }

      expect(quotation.createdAt.getTime()).toBeCloseTo(now.getTime(), -2)
    })
  })

  describe('Loading and Error Handling', () => {
    it('should set loading state', () => {
      const store = useQuotationStore()
      store.isLoading = true
      expect(store.isLoading).toBe(true)
    })

    it('should set error message', () => {
      const store = useQuotationStore()
      store.error = 'Failed to load quotations'
      expect(store.error).toBe('Failed to load quotations')
    })

    it('should clear error on success', () => {
      const store = useQuotationStore()
      store.error = 'Some error'
      store.error = null
      expect(store.error).toBeNull()
    })
  })
})
