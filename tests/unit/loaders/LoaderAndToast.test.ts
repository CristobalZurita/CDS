import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const layoutMock = vi.hoisted(() => ({
  setBodyScrollEnabled: vi.fn(),
}))

const schedulerState = vi.hoisted(() => ({
  queue: [] as Array<() => void>,
  clearAllWithTag: vi.fn(),
  schedule: vi.fn((callback: () => void) => {
    schedulerState.queue.push(callback)
  }),
  interval: vi.fn((callback: () => void) => {
    for (let i = 0; i < 60; i += 1) {
      callback()
    }
  }),
}))

vi.mock('/src/composables/layout.js', () => ({
  useLayout: () => layoutMock,
}))

vi.mock('/src/composables/utils.js', () => ({
  useUtils: () => ({
    clamp: (value: number, min: number, max: number) => Math.min(Math.max(Number(value), min), max),
  }),
}))

vi.mock('/src/composables/scheduler.js', () => ({
  useScheduler: () => schedulerState,
}))

import ActivitySpinner from '@/vue/components/loaders/ActivitySpinner.vue'
import Loader from '@/vue/components/loaders/Loader.vue'
import ToastNotification from '@/vue/components/system/ToastNotification.vue'

const flushScheduledQueue = () => {
  let guard = 0
  while (schedulerState.queue.length > 0 && guard < 200) {
    const callback = schedulerState.queue.shift()
    callback?.()
    guard += 1
  }
}

describe('loader and toast components', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    schedulerState.queue = []
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('adds/removes toasts and supports timed dismissal', async () => {
    vi.useFakeTimers()
    const wrapper = mount(ToastNotification)
    const vm = wrapper.vm as unknown as {
      addToast: (message: string, type?: string, duration?: number) => number
      error: (message: string, duration?: number) => number
    }

    const manualId = vm.addToast('Mensaje manual', 'success', 500)
    expect(manualId).toBe(1)
    await flushPromises()
    expect(wrapper.text()).toContain('Mensaje manual')
    expect(wrapper.text()).toContain('✓')

    const timedId = vm.error('Mensaje temporal', 1000)
    expect(timedId).toBe(2)
    await flushPromises()
    expect(wrapper.text()).toContain('Mensaje temporal')
    expect(wrapper.findAll('.toast')).toHaveLength(2)

    vi.advanceTimersByTime(1000)
    await flushPromises()
  })

  it('toggles ActivitySpinner visibility and keeps the data-url image', async () => {
    const wrapper = mount(ActivitySpinner, {
      props: {
        visible: false,
        message: 'Cargando datos',
      },
    })

    expect(wrapper.find('#foxy-activity-spinner').exists()).toBe(false)

    await wrapper.setProps({ visible: true })
    expect(wrapper.find('#foxy-activity-spinner').exists()).toBe(true)
    expect(wrapper.text()).toContain('Cargando datos')
    expect(wrapper.get('.foxy-spinner').attributes('src')).toContain('data:image/svg+xml;base64')
  })

  it('runs Loader lifecycle and emits rendered/ready/leaving/completed', async () => {
    const appRoot = document.createElement('div')
    appRoot.id = 'app'
    appRoot.appendChild(document.createElement('div'))
    document.body.appendChild(appRoot)

    const wrapper = mount(Loader, {
      props: {
        visible: true,
        refreshCount: 0,
        smoothTransitionEnabled: false,
      },
      global: {
        stubs: {
          ImageView: {
            emits: ['completed'],
            template: '<img class="image" load-status="loaded" />',
            mounted() {
              this.$emit('completed')
            },
          },
          ProgressBar: {
            props: ['percentage'],
            template: '<div data-testid="loader-progress">{{ percentage }}</div>',
          },
        },
      },
      attachTo: document.body,
    })

    await flushPromises()
    flushScheduledQueue()
    await flushPromises()

    expect(wrapper.emitted('rendered')).toBeTruthy()
    expect(wrapper.emitted('ready')).toBeTruthy()
    expect(wrapper.emitted('leaving')).toBeTruthy()
    expect(wrapper.emitted('completed')).toBeTruthy()
    expect(layoutMock.setBodyScrollEnabled).toHaveBeenCalledWith(false)
    expect(layoutMock.setBodyScrollEnabled).toHaveBeenCalledWith(true)

    const renderedCountBeforeRefresh = wrapper.emitted('rendered')?.length || 0
    await wrapper.setProps({ refreshCount: 1 })
    await flushPromises()
    flushScheduledQueue()
    expect((wrapper.emitted('rendered')?.length || 0)).toBeGreaterThan(renderedCountBeforeRefresh)

    const clearCallsBeforeHide = schedulerState.clearAllWithTag.mock.calls.length
    await wrapper.setProps({ visible: false })
    expect(schedulerState.clearAllWithTag.mock.calls.length).toBeGreaterThan(clearCallsBeforeHide)

    wrapper.unmount()
    appRoot.remove()
  })
})
