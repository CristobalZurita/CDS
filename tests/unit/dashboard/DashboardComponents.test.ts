import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import DashboardPanel from '@/vue/components/dashboard/DashboardPanel.vue'
import QuickStats from '@/vue/components/dashboard/QuickStats.vue'
import RepairCard from '@/vue/components/dashboard/RepairCard.vue'
import RepairTimeline from '@/vue/components/dashboard/RepairTimeline.vue'
import RepairsList from '@/vue/components/dashboard/RepairsList.vue'
import StatusBadge from '@/vue/components/dashboard/StatusBadge.vue'
import UserProfile from '@/vue/components/dashboard/UserProfile.vue'

describe('dashboard components', () => {
  it('renders DashboardPanel placeholders', () => {
    const wrapper = mount(DashboardPanel)

    expect(wrapper.text()).toContain('Panel')
    expect(wrapper.text()).toContain('Quick stats')
    expect(wrapper.text()).toContain('Reparaciones recientes')
    expect(wrapper.text()).toContain('Alertas de inventario')
  })

  it('renders QuickStats values and defaults', () => {
    const withValues = mount(QuickStats, {
      props: {
        stats: { pending: 3, active: 5, completed: 8 },
      },
    })
    const withDefaults = mount(QuickStats, {
      props: { stats: {} },
    })

    expect(withValues.text()).toContain('3')
    expect(withValues.text()).toContain('5')
    expect(withValues.text()).toContain('8')
    expect(withDefaults.findAll('.value').every((node) => node.text() === '0')).toBe(true)
  })

  it('normalizes status aliases in StatusBadge classes', () => {
    const wrapper = mount(StatusBadge, {
      props: {
        status: 'in_progress',
        label: '',
      },
    })

    expect(wrapper.classes()).toContain('status-badge')
    expect(wrapper.classes()).toContain('status-en_trabajo')
    expect(wrapper.text()).toContain('in_progress')
  })

  it('renders RepairCard and emits open event', async () => {
    const repair = {
      id: 77,
      status: 'pending',
      status_label: 'Ingreso',
      description: 'No enciende',
      created_at: '2026-03-04T10:00:00Z',
    }
    const wrapper = mount(RepairCard, {
      props: { repair },
    })

    expect(wrapper.text()).toContain('Ticket 77')
    expect(wrapper.text()).toContain('No enciende')
    expect(wrapper.text()).toContain('Ingreso:')

    await wrapper.get('button.link').trigger('click')

    expect(wrapper.emitted('open')?.[0]?.[0]).toEqual(repair)
  })

  it('renders RepairTimeline empty and populated states', () => {
    const empty = mount(RepairTimeline, {
      props: { events: [] },
    })
    const withEvents = mount(RepairTimeline, {
      props: {
        events: [{ id: 1, title: 'Ingreso OT', timestamp: '2026-03-04T10:00:00Z' }],
      },
    })

    expect(empty.text()).toContain('Sin eventos registrados.')
    expect(withEvents.text()).toContain('Ingreso OT')
    expect(withEvents.findAll('li.event')).toHaveLength(1)
  })

  it('renders RepairsList and bubbles open event from RepairCard', async () => {
    const repair = {
      id: 81,
      status: 'quoted',
      status_label: 'Presupuesto',
      description: 'Ruido en VCF',
      created_at: '2026-03-01T12:00:00Z',
    }
    const wrapper = mount(RepairsList, {
      props: { repairs: [repair] },
    })

    await wrapper.get('button.link').trigger('click')

    expect(wrapper.emitted('open')?.[0]?.[0]).toEqual(repair)

    const empty = mount(RepairsList, {
      props: { repairs: [] },
    })
    expect(empty.text()).toContain('No hay reparaciones.')
  })

  it('renders UserProfile custom and fallback fields', () => {
    const custom = mount(UserProfile, {
      props: {
        user: {
          full_name: 'Ana Test',
          email: 'ana@example.com',
          phone: '+56 9 1234 5678',
          role: 'admin',
        },
      },
    })
    const fallback = mount(UserProfile, {
      props: { user: {} },
    })

    expect(custom.text()).toContain('Ana Test')
    expect(custom.text()).toContain('ana@example.com')
    expect(custom.text()).toContain('admin')

    expect(fallback.text()).toContain('Usuario')
    expect(fallback.text()).toContain('sin correo')
    expect(fallback.text()).toContain('sin telefono')
    expect(fallback.text()).toContain('cliente')
  })
})
