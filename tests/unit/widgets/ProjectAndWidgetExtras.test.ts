import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routeState = vi.hoisted(() => ({
  path: '/admin',
}))

const modalShowMock = vi.hoisted(() => vi.fn())
const modalHideMock = vi.hoisted(() => vi.fn())
const bootstrapModalCtorMock = vi.hoisted(() =>
  vi.fn().mockImplementation(() => ({
    show: modalShowMock,
    hide: modalHideMock,
  }))
)

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
}))

vi.mock('/node_modules/bootstrap/js/src/modal', () => ({
  default: bootstrapModalCtorMock,
}))

vi.mock('/src/composables/layout.js', () => ({
  useLayout: () => ({
    setBodyScrollEnabled: vi.fn(),
  }),
}))

vi.mock('/src/composables/strings.js', () => ({
  useStrings: () => ({
    get: (key: string, replacements?: Array<{ key: string; replacement: string }>) => {
      if (key === 'tags') return 'Etiquetas'
      if (key === 'about') return 'Acerca'
      if (key === 'where_to_find') return 'Dónde encontrar'
      if (key === 'project_available_here') {
        return `Disponible en ${replacements?.[0]?.replacement || ''}`
      }
      return key
    },
  }),
}))

vi.mock('/src/composables/utils.js', () => ({
  useUtils: () => ({
    parseCustomText: (value: string) =>
      (value || '').replace(/\*(.*?)\*/g, '<span class="text-primary">$1</span>'),
    clamp: (value: number, min: number, max: number) => Math.min(Math.max(Number(value), min), max),
  }),
}))

import ProjectInfoContent from '@/vue/components/projects/ProjectInfoContent.vue'
import ProjectModal from '@/vue/components/projects/ProjectModal.vue'
import InlineLinkList from '@/vue/components/widgets/InlineLinkList.vue'
import ProgressBar from '@/vue/components/widgets/ProgressBar.vue'

describe('project and widget extra components', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    routeState.path = '/admin'
  })

  it('renders project info with parsed title, tags, description and social links', () => {
    const wrapper = mount(ProjectInfoContent, {
      props: {
        title: 'Proyecto *MS-20*',
        tags: ['repair', 'analog'],
        description: 'Texto de *detalle*',
        links: [{ label: 'Instagram', href: 'https://instagram.com' }],
      },
      global: {
        stubs: {
          SocialLinks: {
            props: ['items', 'size', 'variant'],
            template: '<div data-testid="social-links-stub">{{ items.length }}-{{ size }}-{{ variant }}</div>',
          },
        },
      },
    })

    expect(wrapper.html()).toContain('Proyecto <span class="text-primary">MS-20</span>')
    expect(wrapper.text()).toContain('Etiquetas')
    expect(wrapper.text()).toContain('repair')
    expect(wrapper.text()).toContain('analog')
    expect(wrapper.text()).toContain('Acerca')
    expect(wrapper.html()).toContain('Texto de <span class="text-primary">detalle</span>')
    expect(wrapper.text()).toContain('Disponible en Proyecto MS-20')
    expect(wrapper.get('[data-testid="social-links-stub"]').text()).toBe('1-3-black')
  })

  it('shows and hides ProjectModal with bootstrap modal lifecycle and emits close', async () => {
    const blurSpy = vi.spyOn(HTMLElement.prototype, 'blur').mockImplementation(() => {})
    const wrapper = mount(ProjectModal, {
      props: {
        project: {
          title: 'Proyecto inicial',
          image: '/images/proyecto.webp',
          tags: ['restauración'],
          description: 'Detalle',
          links: [],
        },
      },
      global: {
        stubs: {
          ProjectInfo: {
            props: ['image', 'shrinkImage'],
            template: '<div data-testid="project-info-stub"><slot /></div>',
          },
          ProjectInfoContent: {
            props: ['title'],
            template: '<div data-testid="project-info-content-stub">{{ title }}</div>',
          },
        },
      },
      attachTo: document.body,
    })

    await flushPromises()
    expect(bootstrapModalCtorMock).toHaveBeenCalled()

    await wrapper.setProps({ project: null })
    await flushPromises()
    expect(modalHideMock).toHaveBeenCalled()

    await wrapper.setProps({
      project: {
        title: 'Proyecto nuevo',
        image: '/images/new.webp',
      },
    })
    await flushPromises()
    expect(modalShowMock).toHaveBeenCalled()

    const focusable = document.createElement('button')
    document.body.appendChild(focusable)
    focusable.focus()
    const modalElement = document.getElementById('foxy-project-modal')
    expect(modalElement).toBeTruthy()
    modalElement!.dispatchEvent(new Event('hide.bs.modal'))
    expect(blurSpy).toHaveBeenCalled()

    modalElement!.dispatchEvent(new Event('hidden.bs.modal'))
    expect(wrapper.emitted('close')).toBeTruthy()

    wrapper.unmount()
    focusable.remove()
  })

  it('renders inline link list with external and active internal links', () => {
    const wrapper = mount(InlineLinkList, {
      props: {
        items: [
          { href: 'https://example.com', label: 'Externo', faIcon: 'fa-solid fa-link' },
          { href: '/admin', label: 'Interno', faIcon: 'fa-solid fa-house' },
        ],
      },
      global: {
        stubs: {
          RouterLink: {
            props: ['to'],
            template: '<a data-testid="router-link" :href="to"><slot /></a>',
          },
        },
      },
    })

    const external = wrapper.get('a[href="https://example.com"]')
    expect(external.attributes('target')).toBe('_blank')
    expect(external.text()).toContain('Externo')

    const internal = wrapper.get('router-link-stub')
    expect(internal.attributes('to')).toBe('/admin')
    expect(internal.classes()).toContain('inline-link-list-link-active')
  })

  it('clamps and exposes progress classes in ProgressBar', async () => {
    const wrapper = mount(ProgressBar, {
      props: {
        percentage: 135,
        class: 'custom-progress',
      },
    })

    const progressBar = wrapper.get('.progress-bar')
    expect(progressBar.classes()).toContain('progress-100')
    expect(progressBar.attributes('aria-valuenow')).toBe('100')
    expect(wrapper.get('.progress-bar-wrapper').classes()).toContain('custom-progress')

    await wrapper.setProps({ percentage: -20 })
    expect(wrapper.get('.progress-bar').classes()).toContain('progress-0')
    expect(wrapper.get('.progress-bar').attributes('aria-valuenow')).toBe('0')
  })
})
