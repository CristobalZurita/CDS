import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import InventoryAlerts from '@/vue/components/admin/InventoryAlerts.vue'

describe('InventoryAlerts', () => {
  it('groups stock alerts by severity bands', () => {
    const wrapper = mount(InventoryAlerts, {
      props: {
        items: [
          { id: 1, sku: 'A-1', name: 'Critico', available_stock: 0, min_stock: 10 },
          { id: 2, sku: 'B-2', name: 'Bajo 20', available_stock: 2, min_stock: 10 },
          { id: 3, sku: 'C-3', name: 'Bajo 50', available_stock: 5, min_stock: 10 },
          { id: 4, sku: 'D-4', name: 'Minimo', available_stock: 10, min_stock: 10 },
        ],
      },
    })

    expect(wrapper.text()).toContain('4 activas')
    expect(wrapper.text()).toContain('Crítico 5%')
    expect(wrapper.text()).toContain('Bajo 20%')
    expect(wrapper.text()).toContain('Bajo 50%')
    expect(wrapper.text()).toContain('Bajo mínimo')
  })

  it('shows a clean state when no alerts are active', () => {
    const wrapper = mount(InventoryAlerts, {
      props: {
        items: [
          { id: 10, sku: 'OK-1', name: 'Disponible', available_stock: 25, min_stock: 10 },
        ],
      },
    })

    expect(wrapper.text()).toContain('0 activas')
    expect(wrapper.text()).toContain('Sin alertas activas')
  })
})
