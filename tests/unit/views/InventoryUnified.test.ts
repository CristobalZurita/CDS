import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'

const routerPushMock = vi.hoisted(() => vi.fn())

const inventoryStoreMock = vi.hoisted(() => ({
  items: [] as Array<any>,
  loading: false,
  importing: false,
  lastRunId: null as string | null,
  runStatus: null as string | null,
  fetchItems: vi.fn(),
  deleteItem: vi.fn(),
  triggerImport: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: routerPushMock,
  }),
}))

vi.mock('@/stores/inventory', () => ({
  useInventoryStore: () => inventoryStoreMock,
}))

import InventoryUnified from '@/views/InventoryUnified.vue'

describe('InventoryUnified view', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    inventoryStoreMock.items = [
      { id: 101, name: 'Filtro VCF' },
    ]
    inventoryStoreMock.loading = false
    inventoryStoreMock.importing = false
    inventoryStoreMock.lastRunId = null
    inventoryStoreMock.runStatus = null
    inventoryStoreMock.fetchItems.mockResolvedValue(undefined)
    inventoryStoreMock.deleteItem.mockResolvedValue(true)
    inventoryStoreMock.triggerImport.mockResolvedValue({ run_id: 'run-1', status: 'started' })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    vi.spyOn(window, 'alert').mockImplementation(() => undefined)
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
  })

  it('loads inventory on mount, filters, and routes to edit flow', async () => {
    const wrapper = mount(InventoryUnified, {
      global: {
        stubs: {
          AdminLayout: {
            name: 'AdminLayout',
            template: '<div data-testid="admin-layout"><slot /></div>',
          },
          InventoryCard: {
            name: 'InventoryCard',
            props: ['item'],
            template: `
              <div data-testid="inventory-card">
                <button data-testid="request-edit" @click="$emit('request-edit', item)">edit</button>
                <button data-testid="request-delete" @click="$emit('request-delete', item)">delete</button>
              </div>
            `,
          },
        },
      },
    })

    await flushPromises()
    expect(inventoryStoreMock.fetchItems).toHaveBeenCalledWith(1, 20, null, null)

    await wrapper.get('[data-testid="inventory-unified-filter"]').setValue('vcf')
    await wrapper.get('[data-testid="inventory-unified-search"]').trigger('click')
    expect(inventoryStoreMock.fetchItems).toHaveBeenLastCalledWith(1, 20, 'vcf', null)

    await wrapper.get('[data-testid="request-edit"]').trigger('click')
    expect(routerPushMock).toHaveBeenCalledWith({
      name: 'admin-inventory',
      query: { edit: 101 },
    })
  })

  it('handles delete confirmation and import not-found errors', async () => {
    inventoryStoreMock.deleteItem.mockResolvedValueOnce(false)
    inventoryStoreMock.triggerImport.mockRejectedValueOnce({
      response: { data: { detail: 'Not Found' } },
    })

    const wrapper = mount(InventoryUnified, {
      global: {
        stubs: {
          AdminLayout: {
            name: 'AdminLayout',
            template: '<div><slot /></div>',
          },
          InventoryCard: {
            name: 'InventoryCard',
            props: ['item'],
            template: `
              <div>
                <button data-testid="request-delete" @click="$emit('request-delete', item)">delete</button>
              </div>
            `,
          },
        },
      },
    })

    await flushPromises()
    await wrapper.get('[data-testid="request-delete"]').trigger('click')
    expect(window.confirm).toHaveBeenCalledWith('Eliminar item "Filtro VCF"?')
    expect(inventoryStoreMock.deleteItem).toHaveBeenCalledWith(101)
    expect(window.alert).toHaveBeenCalledWith('No se pudo eliminar el item')

    const importButton = wrapper.findAll('button').find((button) =>
      button.text().includes('Iniciar importación')
    )
    expect(importButton).toBeTruthy()

    await importButton!.trigger('click')
    await flushPromises()
    expect(window.alert).toHaveBeenCalledWith('Importación no disponible en este entorno.')
  })
})
