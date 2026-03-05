import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AnalyticsEvents } from '@/analytics/events'

const apiComposableMock = vi.hoisted(() => ({
  post: vi.fn(),
}))
const utilsMock = vi.hoisted(() => ({
  getAbsoluteLocation: vi.fn(),
}))
const trackMock = vi.hoisted(() => vi.fn())

vi.mock('/src/composables/useApi.js', () => ({
  useApi: () => apiComposableMock,
}))

vi.mock('/src/composables/utils.js', () => ({
  useUtils: () => utilsMock,
}))

vi.mock('/src/composables/strings.js', () => ({
  useStrings: () => ({
    get: (key: string) => {
      if (key === 'where_to_find') return 'Dónde encontrarnos'
      return key
    },
  }),
}))

vi.mock('@/analytics', () => ({
  track: trackMock,
}))

import HistorySection from '@/vue/content/sections/HistorySection.vue'
import NewsletterSection from '@/vue/content/sections/NewsletterSection.vue'
import PortfolioSection from '@/vue/content/sections/PortfolioSection.vue'
import TeamSection from '@/vue/content/sections/TeamSection.vue'

const stubs = {
  PageSection: {
    props: ['id', 'variant'],
    template: '<section :data-testid="`section-${id}`" :data-variant="variant"><slot /></section>',
  },
  PageSectionHeader: {
    props: ['title', 'subtitle'],
    template: '<header data-testid="section-header">{{ title }}|{{ subtitle }}</header>',
  },
  PageSectionContent: {
    template: '<div data-testid="section-content"><slot /></div>',
  },
  ArticleTimeline: {
    template: '<div data-testid="article-timeline"><slot /></div>',
  },
  ItemTimelineEntry: {
    props: ['title', 'dateStart', 'dateEnd', 'image', 'description', 'inverted'],
    template: `
      <article data-testid="timeline-entry">
        <h3>{{ title }}</h3>
        <span data-testid="timeline-inverted">{{ inverted ? 'yes' : 'no' }}</span>
      </article>
    `,
  },
  ArticlePortfolio: {
    props: ['projects', 'categories', 'linkLabel'],
    template: `
      <div data-testid="portfolio-stub">
        <span data-testid="portfolio-projects">{{ projects.length }}</span>
        <span data-testid="portfolio-categories">{{ categories.length }}</span>
        <span data-testid="portfolio-link">{{ linkLabel }}</span>
      </div>
    `,
  },
  ArticleTeamMembers: {
    template: '<div data-testid="team-members"><slot /></div>',
  },
  ItemTeamMember: {
    props: ['name', 'role', 'links'],
    template: `
      <article data-testid="team-member">
        <span data-testid="team-name">{{ name }}</span>
        <span data-testid="team-role">{{ role }}</span>
        <span data-testid="team-links">{{ links.length }}</span>
      </article>
    `,
  },
  XLButton: {
    props: ['type', 'label'],
    template: '<button :type="type" data-testid="newsletter-submit">{{ label }}</button>',
  },
  TurnstileWidget: {
    template: '<button data-testid="newsletter-turnstile" @click="$emit(\'verify\', \'token-newsletter\')">captcha</button>',
  },
}

describe('additional public sections', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    utilsMock.getAbsoluteLocation.mockReturnValue('http://localhost:5173/')
    apiComposableMock.post.mockResolvedValue({ ok: true })
  })

  it('renders static history, portfolio and team datasets', () => {
    const history = mount(HistorySection, {
      props: { id: 'history' },
      global: { stubs },
    })
    expect(history.findAll('[data-testid="timeline-entry"]')).toHaveLength(5)
    expect(history.text()).toContain('El origen del taller')

    const portfolio = mount(PortfolioSection, {
      props: { id: 'portfolio' },
      global: { stubs },
    })
    expect(portfolio.get('[data-testid="portfolio-projects"]').text()).toBe('4')
    expect(portfolio.get('[data-testid="portfolio-categories"]').text()).toBe('3')
    expect(portfolio.get('[data-testid="portfolio-link"]').text()).toBe('Dónde encontrarnos')

    const team = mount(TeamSection, {
      props: { id: 'team' },
      global: { stubs },
    })
    expect(team.get('[data-testid="team-name"]').text()).toContain('Cristóbal Zurita')
    expect(team.get('[data-testid="team-role"]').text()).toContain('Fundador y Técnico')
    expect(team.get('[data-testid="team-links"]').text()).toBe('2')
  })

  it('validates captcha and submits newsletter with tracking', async () => {
    const wrapper = mount(NewsletterSection, {
      props: { id: 'newsletter' },
      global: { stubs },
    })

    await wrapper.get('[data-testid="newsletter-email"]').setValue('user@test.cl')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.get('[data-testid="newsletter-status"]').text()).toContain('Completa el captcha')
    expect(apiComposableMock.post).not.toHaveBeenCalled()

    await wrapper.get('[data-testid="newsletter-turnstile"]').trigger('click')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(apiComposableMock.post).toHaveBeenCalledWith('/newsletter/subscribe', {
      email: 'user@test.cl',
      source_url: 'http://localhost:5173/',
      turnstile_token: 'token-newsletter',
    })
    expect(wrapper.get('[data-testid="newsletter-status"]').text()).toContain('Gracias por suscribirte')
    expect(trackMock).toHaveBeenCalledWith(
      AnalyticsEvents.NEWSLETTER_SUBMIT_SUCCESS,
      { source: 'newsletter_section' },
      { page: 'http://localhost:5173/' }
    )
    expect((wrapper.get('[data-testid="newsletter-email"]').element as HTMLInputElement).value).toBe('')
  })

  it('tracks newsletter submit errors when API request fails', async () => {
    apiComposableMock.post.mockRejectedValueOnce(new Error('newsletter error'))
    const wrapper = mount(NewsletterSection, {
      props: { id: 'newsletter' },
      global: { stubs },
    })

    await wrapper.get('[data-testid="newsletter-email"]').setValue('error@test.cl')
    await wrapper.get('[data-testid="newsletter-turnstile"]').trigger('click')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.get('[data-testid="newsletter-status"]').text()).toContain('No pudimos registrar tu suscripción')
    expect(trackMock).toHaveBeenCalledWith(
      AnalyticsEvents.NEWSLETTER_SUBMIT_ERROR,
      { source: 'newsletter_section' },
      { page: 'http://localhost:5173/' }
    )
  })
})
