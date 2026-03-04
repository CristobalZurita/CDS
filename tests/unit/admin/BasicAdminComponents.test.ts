import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'

const authStoreMock = vi.hoisted(() => ({
  logout: vi.fn(),
}))

const categoriesMock = vi.hoisted(() => ({
  categories: [] as Array<any>,
  fetchCategories: vi.fn(),
  deleteCategory: vi.fn(),
  createCategory: vi.fn(),
  updateCategory: vi.fn(),
}))

const instrumentsMock = vi.hoisted(() => ({
  instruments: [] as Array<any>,
  fetchInstruments: vi.fn(),
  deleteInstrument: vi.fn(),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

vi.mock('@/composables/useCategories', () => ({
  useCategories: () => categoriesMock,
}))

vi.mock('@/composables/useInstruments', () => ({
  useInstruments: () => instrumentsMock,
}))

import AdminToolbar from '@/vue/components/admin/AdminToolbar.vue'
import CategoryForm from '@/vue/components/admin/CategoryForm.vue'
import CategoryList from '@/vue/components/admin/CategoryList.vue'
import CategoryManager from '@/vue/components/admin/CategoryManager.vue'
import ClientList from '@/vue/components/admin/ClientList.vue'
import InstrumentList from '@/vue/components/admin/InstrumentList.vue'
import StockMovements from '@/vue/components/admin/StockMovements.vue'

describe('basic admin components', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    categoriesMock.categories = []
    instrumentsMock.instruments = []
  })

  it('renders AdminToolbar and triggers logout', async () => {
    const wrapper = mount(AdminToolbar, {
      props: {
        title: 'Panel Admin',
        subtitle: 'Operación',
      },
    })

    expect(wrapper.text()).toContain('Panel Admin')
    expect(wrapper.text()).toContain('Operación')

    await wrapper.get('button.btn-logout').trigger('click')
    expect(authStoreMock.logout).toHaveBeenCalledTimes(1)
  })

  it('creates and updates categories from CategoryForm', async () => {
    categoriesMock.createCategory.mockResolvedValueOnce({})
    categoriesMock.updateCategory.mockResolvedValueOnce({})

    const createWrapper = mount(CategoryForm)
    await createWrapper.get('[data-testid="category-name"]').setValue('Capacitores')
    await createWrapper.get('[data-testid="category-description"]').setValue('Componentes')
    await createWrapper.get('[data-testid="category-form"]').trigger('submit.prevent')

    expect(categoriesMock.createCategory).toHaveBeenCalledWith({
      name: 'Capacitores',
      description: 'Componentes',
    })
    expect(createWrapper.emitted('saved')).toBeTruthy()

    const editWrapper = mount(CategoryForm, {
      props: {
        category: { id: 99, name: 'Original', description: 'Antes' },
      },
    })
    await editWrapper.get('[data-testid="category-name"]').setValue('Actualizada')
    await editWrapper.get('[data-testid="category-form"]').trigger('submit.prevent')

    expect(categoriesMock.updateCategory).toHaveBeenCalledWith(99, {
      name: 'Actualizada',
      description: 'Antes',
    })
    expect(editWrapper.emitted('saved')).toBeTruthy()
  })

  it('loads, edits and deletes categories from CategoryList', async () => {
    categoriesMock.categories = [
      { id: 1, name: 'Resistencias', description: 'Película metálica' },
      { id: 2, name: 'IC', description: 'Integrados' },
    ]
    categoriesMock.fetchCategories.mockResolvedValueOnce(undefined)
    categoriesMock.deleteCategory.mockResolvedValueOnce(undefined)

    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    const wrapper = mount(CategoryList)
    await flushPromises()

    expect(categoriesMock.fetchCategories).toHaveBeenCalledTimes(1)
    expect(wrapper.findAll('[data-testid="category-row"]')).toHaveLength(2)

    await wrapper.findAll('[data-testid="category-edit"]')[0].trigger('click')
    expect(wrapper.emitted('edit')?.[0]?.[0]).toEqual(categoriesMock.categories[0])

    await wrapper.findAll('[data-testid="category-delete"]')[0].trigger('click')
    expect(confirmSpy).toHaveBeenCalledWith('Eliminar categoría "Resistencias"?')
    expect(categoriesMock.deleteCategory).toHaveBeenCalledWith(1)
  })

  it('renders CategoryManager empty and populated states', () => {
    const emptyWrapper = mount(CategoryManager, {
      props: { categories: [] },
    })
    expect(emptyWrapper.text()).toContain('Sin categorias.')

    const dataWrapper = mount(CategoryManager, {
      props: { categories: [{ id: 1, name: 'Filtros', description: 'VCF' }] },
    })
    expect(dataWrapper.text()).toContain('Filtros')
    expect(dataWrapper.text()).toContain('VCF')
  })

  it('emits selected client from ClientList', async () => {
    const clients = [
      { id: 1, name: 'Ana', email: '' },
      { id: 2, name: 'Pablo', email: 'pablo@test.com', client_code: 'C-002' },
    ]
    const wrapper = mount(ClientList, {
      props: { clients },
    })

    expect(wrapper.text()).toContain('Sin correo')
    await wrapper.findAll('li')[0].trigger('click')
    expect(wrapper.emitted('select')?.[0]?.[0]).toEqual(clients[0])
  })

  it('fetches and deletes instruments from InstrumentList', async () => {
    instrumentsMock.instruments = [
      { id: 10, brand_id: 1, model: 'Juno-106', type: 'Synth' },
    ]
    instrumentsMock.fetchInstruments.mockResolvedValueOnce(undefined)
    instrumentsMock.deleteInstrument.mockResolvedValueOnce(undefined)

    const wrapper = mount(InstrumentList)
    expect(wrapper.text()).toContain('Juno-106')

    const refreshButton = wrapper.findAll('button').find((button) => button.text() === 'Actualizar')
    const deleteButton = wrapper.findAll('button').find((button) => button.text() === 'Borrar')

    expect(refreshButton).toBeTruthy()
    expect(deleteButton).toBeTruthy()

    await refreshButton!.trigger('click')
    await deleteButton!.trigger('click')

    expect(instrumentsMock.fetchInstruments).toHaveBeenCalledTimes(1)
    expect(instrumentsMock.deleteInstrument).toHaveBeenCalledWith(10)
  })

  it('renders movement table and fallback date label', () => {
    const wrapper = mount(StockMovements, {
      props: {
        movements: [
          { id: 1, item_name: 'Resistencia 10K', quantity: 4, created_at: '2026-03-04T10:00:00Z' },
          { id: 2, item_id: 77, quantity: 1, created_at: null },
        ],
      },
    })

    expect(wrapper.text()).toContain('Resistencia 10K')
    expect(wrapper.text()).toContain('77')
    expect(wrapper.text()).toContain('—')
  })
})
