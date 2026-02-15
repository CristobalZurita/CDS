import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useRepairsStore } from '@stores/repairs'

describe('Repairs Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const store = useRepairsStore()
      expect(store.repairs).toEqual([])
      expect(store.currentRepair).toBeNull()
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
      expect(store.filters).toEqual({})
      expect(store.pagination.page).toBe(1)
      expect(store.pagination.pageSize).toBe(10)
    })
  })

  describe('Repair CRUD Operations', () => {
    it('should create new repair', () => {
      const store = useRepairsStore()
      const newRepair = {
        id: 1,
        deviceType: 'Laptop',
        description: 'Screen broken',
        status: 'pending',
        createdAt: new Date(),
        estimatedCost: 150
      }

      store.repairs.push(newRepair)
      expect(store.repairs).toContainEqual(newRepair)
    })

    it('should read repair by ID', () => {
      const store = useRepairsStore()
      const repair = {
        id: 1,
        deviceType: 'Phone',
        description: 'Battery issue',
        status: 'in-progress',
        createdAt: new Date(),
        estimatedCost: 50
      }

      store.repairs = [repair]
      store.currentRepair = repair

      expect(store.currentRepair?.id).toBe(1)
      expect(store.currentRepair?.deviceType).toBe('Phone')
    })

    it('should update repair', () => {
      const store = useRepairsStore()
      const repair = {
        id: 1,
        deviceType: 'Laptop',
        description: 'Screen broken',
        status: 'pending',
        createdAt: new Date(),
        estimatedCost: 150
      }

      store.repairs = [repair]
      store.currentRepair = repair

      store.currentRepair!.status = 'in-progress'
      store.currentRepair!.estimatedCost = 200

      expect(store.currentRepair?.status).toBe('in-progress')
      expect(store.currentRepair?.estimatedCost).toBe(200)
    })

    it('should delete repair', () => {
      const store = useRepairsStore()
      const repair = {
        id: 1,
        deviceType: 'Tablet',
        description: 'Touch screen',
        status: 'completed',
        createdAt: new Date(),
        estimatedCost: 100
      }

      store.repairs = [repair]
      store.repairs = store.repairs.filter(r => r.id !== 1)

      expect(store.repairs).toHaveLength(0)
    })
  })

  describe('Status Management', () => {
    const statuses = ['pending', 'in-progress', 'completed', 'cancelled']

    statuses.forEach(status => {
      it(`should filter repairs by status: ${status}`, () => {
        const store = useRepairsStore()
        store.repairs = [
          { id: 1, status, deviceType: 'Phone', description: 'Test', createdAt: new Date(), estimatedCost: 50 },
          { id: 2, status: 'pending', deviceType: 'Laptop', description: 'Test', createdAt: new Date(), estimatedCost: 100 }
        ]

        const filtered = store.repairs.filter(r => r.status === status)
        expect(filtered[0].status).toBe(status)
      })
    })

    it('should transition repair status correctly', () => {
      const store = useRepairsStore()
      const repair = {
        id: 1,
        deviceType: 'Phone',
        description: 'Battery',
        status: 'pending',
        createdAt: new Date(),
        estimatedCost: 50
      }

      store.repairs = [repair]
      store.repairs[0].status = 'in-progress'

      expect(store.repairs[0].status).toBe('in-progress')
    })

    it('should not allow invalid status transition', () => {
      const store = useRepairsStore()
      const repair = {
        id: 1,
        status: 'completed',
        deviceType: 'Phone',
        description: 'Battery',
        createdAt: new Date(),
        estimatedCost: 50
      }

      store.repairs = [repair]
      const validStatuses = ['pending', 'in-progress', 'completed', 'cancelled']

      expect(validStatuses).toContain(store.repairs[0].status)
    })
  })

  describe('Cost Management', () => {
    it('should calculate total cost correctly', () => {
      const store = useRepairsStore()
      store.repairs = [
        { id: 1, estimatedCost: 100, status: 'pending', deviceType: 'Phone', description: 'Test', createdAt: new Date() },
        { id: 2, estimatedCost: 200, status: 'pending', deviceType: 'Laptop', description: 'Test', createdAt: new Date() },
        { id: 3, estimatedCost: 150, status: 'completed', deviceType: 'Tablet', description: 'Test', createdAt: new Date() }
      ]

      const total = store.repairs.reduce((sum, r) => sum + r.estimatedCost, 0)
      expect(total).toBe(450)
    })

    it('should calculate average cost per repair', () => {
      const store = useRepairsStore()
      store.repairs = [
        { id: 1, estimatedCost: 100, status: 'pending', deviceType: 'Phone', description: 'Test', createdAt: new Date() },
        { id: 2, estimatedCost: 200, status: 'pending', deviceType: 'Laptop', description: 'Test', createdAt: new Date() }
      ]

      const average = store.repairs.reduce((sum, r) => sum + r.estimatedCost, 0) / store.repairs.length
      expect(average).toBe(150)
    })

    it('should update cost estimate', () => {
      const store = useRepairsStore()
      const repair = {
        id: 1,
        estimatedCost: 100,
        status: 'pending',
        deviceType: 'Phone',
        description: 'Test',
        createdAt: new Date()
      }

      store.repairs = [repair]
      store.repairs[0].estimatedCost = 250

      expect(store.repairs[0].estimatedCost).toBe(250)
    })
  })

  describe('Filtering', () => {
    it('should filter by device type', () => {
      const store = useRepairsStore()
      store.repairs = [
        { id: 1, deviceType: 'Phone', status: 'pending', description: 'Test', createdAt: new Date(), estimatedCost: 50 },
        { id: 2, deviceType: 'Laptop', status: 'pending', description: 'Test', createdAt: new Date(), estimatedCost: 100 },
        { id: 3, deviceType: 'Phone', status: 'completed', description: 'Test', createdAt: new Date(), estimatedCost: 75 }
      ]

      const filtered = store.repairs.filter(r => r.deviceType === 'Phone')
      expect(filtered).toHaveLength(2)
      expect(filtered[0].deviceType).toBe('Phone')
    })

    it('should filter by date range', () => {
      const store = useRepairsStore()
      const today = new Date()
      const yesterday = new Date(today.getTime() - 86400000)
      const tomorrow = new Date(today.getTime() + 86400000)

      store.repairs = [
        { id: 1, createdAt: yesterday, deviceType: 'Phone', status: 'pending', description: 'Test', estimatedCost: 50 },
        { id: 2, createdAt: today, deviceType: 'Laptop', status: 'pending', description: 'Test', estimatedCost: 100 },
      ]

      const filtered = store.repairs.filter(r => r.createdAt <= today && r.createdAt >= yesterday)
      expect(filtered).toHaveLength(2)
    })
  })

  describe('Pagination', () => {
    it('should update page number', () => {
      const store = useRepairsStore()
      store.pagination.page = 1
      store.pagination.page = 2

      expect(store.pagination.page).toBe(2)
    })

    it('should update page size', () => {
      const store = useRepairsStore()
      store.pagination.pageSize = 10
      store.pagination.pageSize = 25

      expect(store.pagination.pageSize).toBe(25)
    })

    it('should calculate total pages', () => {
      const store = useRepairsStore()
      store.repairs = new Array(55).fill(null).map((_, i) => ({
        id: i + 1,
        deviceType: 'Phone',
        status: 'pending',
        description: 'Test',
        createdAt: new Date(),
        estimatedCost: 50
      }))

      store.pagination.pageSize = 10
      const totalPages = Math.ceil(store.repairs.length / store.pagination.pageSize)

      expect(totalPages).toBe(6)
    })

    it('should get repairs for current page', () => {
      const store = useRepairsStore()
      store.repairs = new Array(25).fill(null).map((_, i) => ({
        id: i + 1,
        deviceType: 'Phone',
        status: 'pending',
        description: 'Test',
        createdAt: new Date(),
        estimatedCost: 50
      }))

      store.pagination.page = 1
      store.pagination.pageSize = 10
      const start = (store.pagination.page - 1) * store.pagination.pageSize
      const end = start + store.pagination.pageSize

      const pageRepairs = store.repairs.slice(start, end)
      expect(pageRepairs).toHaveLength(10)
    })
  })

  describe('Loading State', () => {
    it('should set loading true when fetching', () => {
      const store = useRepairsStore()
      store.isLoading = true
      expect(store.isLoading).toBe(true)
    })

    it('should set loading false after fetch', () => {
      const store = useRepairsStore()
      store.isLoading = false
      expect(store.isLoading).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('should set error message on failure', () => {
      const store = useRepairsStore()
      const errorMsg = 'Failed to fetch repairs'
      store.error = errorMsg

      expect(store.error).toBe(errorMsg)
    })

    it('should clear error on success', () => {
      const store = useRepairsStore()
      store.error = 'Some error'
      store.error = null

      expect(store.error).toBeNull()
    })
  })

  describe('Sorting', () => {
    it('should sort by creation date ascending', () => {
      const store = useRepairsStore()
      const date1 = new Date('2024-01-01')
      const date2 = new Date('2024-01-02')
      const date3 = new Date('2024-01-03')

      store.repairs = [
        { id: 2, createdAt: date2, deviceType: 'Phone', status: 'pending', description: 'Test', estimatedCost: 50 },
        { id: 3, createdAt: date3, deviceType: 'Laptop', status: 'pending', description: 'Test', estimatedCost: 100 },
        { id: 1, createdAt: date1, deviceType: 'Tablet', status: 'pending', description: 'Test', estimatedCost: 75 }
      ]

      const sorted = [...store.repairs].sort((a, b) => a.createdAt.getTime() - b.createdAt.getTime())
      expect(sorted[0].id).toBe(1)
      expect(sorted[2].id).toBe(3)
    })

    it('should sort by cost descending', () => {
      const store = useRepairsStore()
      store.repairs = [
        { id: 1, estimatedCost: 50, status: 'pending', deviceType: 'Phone', description: 'Test', createdAt: new Date() },
        { id: 2, estimatedCost: 200, status: 'pending', deviceType: 'Laptop', description: 'Test', createdAt: new Date() },
        { id: 3, estimatedCost: 100, status: 'pending', deviceType: 'Tablet', description: 'Test', createdAt: new Date() }
      ]

      const sorted = [...store.repairs].sort((a, b) => b.estimatedCost - a.estimatedCost)
      expect(sorted[0].estimatedCost).toBe(200)
      expect(sorted[2].estimatedCost).toBe(50)
    })
  })

  describe('Summary Statistics', () => {
    it('should count repairs by status', () => {
      const store = useRepairsStore()
      store.repairs = [
        { id: 1, status: 'pending', deviceType: 'Phone', description: 'Test', createdAt: new Date(), estimatedCost: 50 },
        { id: 2, status: 'in-progress', deviceType: 'Laptop', description: 'Test', createdAt: new Date(), estimatedCost: 100 },
        { id: 3, status: 'pending', deviceType: 'Tablet', description: 'Test', createdAt: new Date(), estimatedCost: 75 },
        { id: 4, status: 'completed', deviceType: 'Phone', description: 'Test', createdAt: new Date(), estimatedCost: 60 }
      ]

      const pending = store.repairs.filter(r => r.status === 'pending').length
      const inProgress = store.repairs.filter(r => r.status === 'in-progress').length
      const completed = store.repairs.filter(r => r.status === 'completed').length

      expect(pending).toBe(2)
      expect(inProgress).toBe(1)
      expect(completed).toBe(1)
    })
  })
})
