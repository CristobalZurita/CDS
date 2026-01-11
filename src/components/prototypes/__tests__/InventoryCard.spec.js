import { shallowMount } from '@vue/test-utils'
import InventoryCard from '../InventoryCard.vue'

describe('InventoryCard', () => {
  it('renders item props', () => {
    const item = { id: 1, name: 'Resistor 10k', category: 'Resistencias', stock: 42 }
    const wrapper = shallowMount(InventoryCard, { props: { item } })
    expect(wrapper.text()).toContain('Resistor 10k')
    expect(wrapper.text()).toContain('Resistencias')
    expect(wrapper.text()).toContain('42')
  })
})
