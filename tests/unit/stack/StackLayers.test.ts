import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, h, inject, ref } from 'vue'

const settingsState = vi.hoisted(() => ({
  loaderEnabled: true,
}))

const routerState = vi.hoisted(() => ({
  beforeEachHandler: null as any,
  afterEachHandler: null as any,
  beforeEach: vi.fn((handler: any) => {
    routerState.beforeEachHandler = handler
  }),
  afterEach: vi.fn((handler: any) => {
    routerState.afterEachHandler = handler
  }),
}))

const utilsMock = vi.hoisted(() => ({
  getRootLocation: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => routerState,
}))

vi.mock('/src/composables/settings.js', () => ({
  useSettings: () => ({
    getLoaderEnabled: () => settingsState.loaderEnabled,
  }),
}))

vi.mock('/src/composables/utils.js', () => ({
  useUtils: () => utilsMock,
}))

vi.mock('/src/vue/components/loaders/ActivitySpinner.vue', () => ({
  default: {
    props: ['visible', 'message'],
    template: '<div data-testid="activity-stub">{{ visible }}-{{ message }}</div>',
  },
}))

vi.mock('/src/vue/components/loaders/Loader.vue', () => ({
  default: {
    emits: ['rendered', 'ready', 'leaving', 'completed'],
    template: `
      <div data-testid="loader-stub">
        <button data-testid="loader-rendered" @click="$emit('rendered')">rendered</button>
        <button data-testid="loader-ready" @click="$emit('ready')">ready</button>
        <button data-testid="loader-leaving" @click="$emit('leaving')">leaving</button>
        <button data-testid="loader-completed" @click="$emit('completed')">completed</button>
      </div>
    `,
  },
}))

import ContentLayer from '@/vue/stack/ContentLayer.vue'
import FeedbacksLayer from '@/vue/stack/FeedbacksLayer.vue'
import StateProviderLayer from '@/vue/stack/StateProviderLayer.vue'

describe('stack layers', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    settingsState.loaderEnabled = true
    utilsMock.getRootLocation.mockReturnValue('http://localhost:5173/')
    routerState.beforeEachHandler = null
    routerState.afterEachHandler = null
    window.location.hash = ''
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('provides global state from StateProviderLayer and updates spinner state', async () => {
    let injected: any = null
    const Probe = defineComponent({
      setup() {
        const loaderEnabled = inject('loaderEnabled')
        const loaderActive = inject<any>('loaderActive')
        const spinnerActive = inject<any>('spinnerActive')
        const spinnerMessage = inject<any>('spinnerMessage')
        const setSpinnerEnabled = inject<any>('setSpinnerEnabled')
        injected = {
          loaderEnabled,
          loaderActive,
          spinnerActive,
          spinnerMessage,
          setSpinnerEnabled,
        }
        return () => null
      },
    })

    mount(StateProviderLayer, {
      global: {
        components: { Probe },
      },
      slots: {
        default: '<Probe />',
      },
    })

    expect(injected.loaderEnabled).toBe(true)
    expect(injected.loaderActive.value).toBe(true)
    expect(injected.spinnerActive.value).toBe(false)
    injected.setSpinnerEnabled(true, 'Procesando')
    expect(injected.spinnerActive.value).toBe(true)
    expect(injected.spinnerMessage.value).toBe('Procesando')
  })

  it('controls FeedbacksLayer readiness, loader callbacks and first user interaction', async () => {
    const provided = {
      loaderEnabled: true,
      LoaderAnimationStatus: {
        INITIALIZED: 'initialized',
        RENDERED: 'rendered',
        TRACKING_PROGRESS: 'tracking_progress',
        LEAVING: 'leaving',
      },
      loaderActive: ref(true),
      loaderPageRefreshCount: ref(0),
      loaderSmoothTransitionEnabled: ref(false),
      loaderAnimationStatus: ref('initialized'),
      spinnerActive: ref(true),
      spinnerMessage: ref('Cargando'),
      floatingButtonVisible: ref(false),
      hasUserInteracted: ref(false),
    }

    const addEventSpy = vi.spyOn(document, 'addEventListener')
    const removeEventSpy = vi.spyOn(document, 'removeEventListener')

    const wrapper = mount(FeedbacksLayer, {
      global: {
        provide: provided,
      },
      slots: {
        default: ({ floatingButtonVisible }: { floatingButtonVisible: boolean }) =>
          h(
            'div',
            { 'data-testid': 'feedback-slot' },
            floatingButtonVisible ? 'visible' : 'hidden'
          ),
      },
    })

    expect(wrapper.find('[data-testid="feedback-slot"]').exists()).toBe(false)
    expect(wrapper.get('[data-testid="activity-stub"]').text()).toContain('true-Cargando')

    await wrapper.get('[data-testid="loader-rendered"]').trigger('click')
    expect(provided.loaderAnimationStatus.value).toBe('rendered')

    await wrapper.get('[data-testid="loader-ready"]').trigger('click')
    await flushPromises()
    expect(provided.loaderAnimationStatus.value).toBe('tracking_progress')
    expect(wrapper.find('[data-testid="feedback-slot"]').exists()).toBe(true)
    expect(addEventSpy).toHaveBeenCalledWith('scroll', expect.any(Function))
    expect(addEventSpy).toHaveBeenCalledWith('click', expect.any(Function))

    document.dispatchEvent(new Event('scroll'))
    expect(provided.hasUserInteracted.value).toBe(true)
    expect(provided.floatingButtonVisible.value).toBe(true)
    expect(removeEventSpy).toHaveBeenCalledWith('scroll', expect.any(Function))

    await wrapper.get('[data-testid="loader-leaving"]').trigger('click')
    expect(provided.loaderAnimationStatus.value).toBe('leaving')

    await wrapper.get('[data-testid="loader-completed"]').trigger('click')
    expect(provided.loaderActive.value).toBe(false)
  })

  it('handles ContentLayer slot visibility, analytics ping, scroll behavior and router guards', async () => {
    vi.useFakeTimers()
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue({ ok: true } as Response)
    const scrollToSpy = vi.spyOn(window, 'scrollTo').mockImplementation(() => {})
    vi.stubEnv('VITE_ANALYTICS_URL', 'http://analytics.local/visit')

    const provided = {
      loaderEnabled: true,
      loaderActive: ref(false),
      loaderPageRefreshCount: ref(0),
      loaderSmoothTransitionEnabled: ref(false),
      projectModalTarget: ref({ id: 1, title: 'Modal open' }),
      LoaderAnimationStatus: {
        TRACKING_PROGRESS: 'tracking_progress',
        LEAVING: 'leaving',
      },
      loaderAnimationStatus: ref('initialized'),
    }

    const wrapper = mount(ContentLayer, {
      global: {
        provide: provided,
        stubs: {
          ProjectModal: {
            props: ['project'],
            template: '<button data-testid="project-modal-close" @click="$emit(\'close\')">{{ project?.title }}</button>',
          },
        },
      },
      slots: {
        default: '<div data-testid="content-slot">contenido</div>',
      },
    })

    await flushPromises()
    expect(fetchSpy).toHaveBeenCalledWith('http://analytics.local/visit', expect.any(Object))
    expect(wrapper.find('[data-testid="content-slot"]').exists()).toBe(false)

    provided.loaderAnimationStatus.value = 'tracking_progress'
    await flushPromises()
    expect(wrapper.find('[data-testid="content-slot"]').exists()).toBe(true)

    await wrapper.get('[data-testid="project-modal-close"]').trigger('click')
    expect(provided.projectModalTarget.value).toBe(null)

    provided.loaderAnimationStatus.value = 'leaving'
    await flushPromises()
    expect(scrollToSpy).toHaveBeenCalledWith({ top: 0, behavior: 'instant' })

    const anchor = document.createElement('div')
    anchor.id = 'target-section'
    const scrollIntoViewSpy = vi.fn()
    Object.defineProperty(anchor, 'scrollIntoView', {
      value: scrollIntoViewSpy,
      configurable: true,
    })
    document.body.appendChild(anchor)
    window.location.hash = '#target-section'
    provided.loaderAnimationStatus.value = 'tracking_progress'
    await flushPromises()
    provided.loaderAnimationStatus.value = 'leaving'
    await flushPromises()
    expect(scrollIntoViewSpy).toHaveBeenCalledWith({ behavior: 'smooth' })

    const nextSame = vi.fn()
    routerState.beforeEachHandler(
      { name: 'dashboard', matched: [], path: '/admin' },
      { name: 'dashboard', matched: [], path: '/admin' },
      nextSame
    )
    expect(nextSame).toHaveBeenCalled()

    const nextIgnore = vi.fn()
    routerState.beforeEachHandler(
      {
        name: 'public',
        path: '/public',
        matched: [{ props: { default: { shouldAlwaysPreload: false } } }],
      },
      { name: 'other', path: '/old', matched: [] },
      nextIgnore
    )
    expect(nextIgnore).toHaveBeenCalled()

    const nextPreload = vi.fn()
    routerState.beforeEachHandler(
      {
        name: 'stats',
        path: '/admin/stats',
        matched: [{ props: { default: { shouldAlwaysPreload: true } } }],
      },
      { name: 'dashboard', path: '/admin', matched: [] },
      nextPreload
    )
    expect(provided.loaderActive.value).toBe(true)
    expect(provided.loaderPageRefreshCount.value).toBe(1)
    expect(provided.loaderSmoothTransitionEnabled.value).toBe(true)
    vi.advanceTimersByTime(850)
    expect(nextPreload).toHaveBeenCalled()

    routerState.afterEachHandler(
      { path: '/admin/clients' },
      { path: '/admin/stats' }
    )
    expect(scrollToSpy).toHaveBeenCalledWith({ top: 0, behavior: 'smooth' })

    wrapper.unmount()
    anchor.remove()
    vi.unstubAllEnvs()
  })
})
