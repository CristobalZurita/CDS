import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useRepairs } from '@composables/useRepairs'
import { useInventory } from '@composables/useInventory'
import { useQuotation } from '@composables/useQuotation'
import { useCategories } from '@composables/useCategories'
import { useUsers } from '@composables/useUsers'
import { useDiagnostic } from '@composables/useDiagnostic'
import { useDiagnostics } from '@composables/useDiagnostics'
import { useInstruments } from '@composables/useInstruments'
import { useInstrumentsCatalog } from '@composables/useInstrumentsCatalog'
import { useRepairsStore } from '@stores/repairs'
import { useInventoryStore } from '@stores/inventory'
import { useCategoriesStore } from '@stores/categories'
import { useUsersStore } from '@stores/users'
import { useDiagnosticsStore } from '@stores/diagnostics'
import { useInstrumentsStore } from '@stores/instruments'

describe('store-backed composables', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('exposes repairs refs and actions from the store', () => {
    const store = useRepairsStore()
    store.repairs = [{ id: 1, status: 'pending' }]

    const composable = useRepairs()

    expect(composable.repairs.value).toEqual([{ id: 1, status: 'pending' }])
    expect(typeof composable.fetchRepairs).toBe('function')
    expect(typeof composable.createRepair).toBe('function')
    expect(typeof composable.updateRepair).toBe('function')
    expect(typeof composable.deleteRepair).toBe('function')
  })

  it('exposes inventory refs and refresh helpers', () => {
    const store = useInventoryStore()
    store.items = [{ id: 10, name: 'Capacitor' }]
    store.page = 2
    store.limit = 50

    const composable = useInventory()

    expect(composable.items.value).toEqual([{ id: 10, name: 'Capacitor' }])
    expect(composable.page.value).toBe(2)
    expect(composable.limit.value).toBe(50)
    expect(typeof composable.refresh).toBe('function')
    expect(typeof composable.createItem).toBe('function')
    expect(typeof composable.updateItem).toBe('function')
    expect(typeof composable.deleteItem).toBe('function')
  })

  it('exposes categories, users, diagnostics and instruments wrappers', () => {
    useCategoriesStore().categories = [{ id: 1, name: 'Sintes' }]
    useUsersStore().users = [{ id: 1, email: 'admin@test.com' }]
    useDiagnosticsStore().diagnostics = [{ id: 1, result: 'ok' }]
    useInstrumentsStore().instruments = [{ id: 1, name: 'Juno-106' }]

    const categories = useCategories()
    const users = useUsers()
    const diagnostics = useDiagnostics()
    const instruments = useInstruments()

    expect(categories.categories.value).toHaveLength(1)
    expect(users.users.value).toHaveLength(1)
    expect(diagnostics.diagnostics).toHaveLength(1)
    expect(instruments.instruments).toHaveLength(1)
    expect(typeof categories.fetchCategories).toBe('function')
    expect(typeof users.fetchUsers).toBe('function')
    expect(typeof diagnostics.fetchDiagnostics).toBe('function')
    expect(typeof instruments.fetchInstruments).toBe('function')
  })
})

describe('standalone composables', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('provides diagnostic helpers over the catalog datasets', () => {
    const diagnostic = useDiagnostic()
    const firstBrand = diagnostic.brands.value[0]

    expect(diagnostic.brands.value.length).toBeGreaterThan(0)
    expect(diagnostic.instruments.value.length).toBeGreaterThan(0)
    expect(diagnostic.faults.value).toBeDefined()
    expect(diagnostic.getBrands()).toContainEqual(firstBrand)
    expect(typeof diagnostic.getModelsByBrand).toBe('function')
    expect(typeof diagnostic.calculateQuote).toBe('function')

    diagnostic.selectedBrand.value = firstBrand.id
    const models = diagnostic.getModelsByBrand(firstBrand.id)
    if (models.length > 0) {
      diagnostic.selectedModel.value = models[0].id
      const availableFaults = diagnostic.getAvailableFaults()
      expect(Array.isArray(availableFaults)).toBe(true)
    }
  })

  it('exposes quotation state and derived prices', () => {
    const quotation = useQuotation()

    quotation.quotation.value = {
      min_price: 100000,
      max_price: 200000,
      exceeds_recommendation: true,
    }

    expect(quotation.hasQuotation.value).toBe(true)
    expect(quotation.exceedsRecommendation.value).toBe(true)
    expect(quotation.priceRange.value.min).toBe(100000)
    expect(quotation.priceRange.value.max).toBe(200000)
    expect(quotation.priceRange.value.mid).toBe(150000)

    quotation.reset()
    expect(quotation.quotation.value).toBeNull()
    expect(quotation.hasQuotation.value).toBe(false)
  })

  it('exposes the synchronized instrument catalog', () => {
    const catalog = useInstrumentsCatalog()
    const brands = catalog.getAllBrands()

    expect(catalog.brands.value.length).toBeGreaterThan(0)
    expect(catalog.instruments.value.length).toBeGreaterThan(0)
    expect(brands.length).toBeGreaterThan(0)
    expect(catalog.getCatalogStats.value.totalBrands).toBe(brands.length)

    const firstInstrument = catalog.instruments.value[0]
    expect(catalog.getInstrumentById(firstInstrument.id)?.id).toBe(firstInstrument.id)
    expect(Array.isArray(catalog.searchInstruments(firstInstrument.model))).toBe(true)
  })
})
