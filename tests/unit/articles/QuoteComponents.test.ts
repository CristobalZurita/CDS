import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('swiper/vue', () => ({
  Swiper: {
    name: 'Swiper',
    template: '<div class="swiper-mock"><slot /></div>',
  },
  SwiperSlide: {
    name: 'SwiperSlide',
    template: '<div class="swiper-slide-mock"><slot /></div>',
  },
}))

vi.mock('swiper/modules', () => ({
  Pagination: {},
}))

import ArticleQuotes from '@/vue/components/articles/ArticleQuotes.vue'
import ItemQuote from '@/vue/components/articles/items/ItemQuote.vue'

describe('quote-related article components', () => {
  it('renders quote slides from slot content in ArticleQuotes', () => {
    const wrapper = mount(ArticleQuotes, {
      slots: {
        default: `
          <div class="quote-a">A</div>
          <div class="quote-b">B</div>
        `,
      },
    })

    expect(wrapper.findAll('.swiper-slide-mock')).toHaveLength(2)
    expect(wrapper.text()).toContain('A')
    expect(wrapper.text()).toContain('B')
  })

  it('renders ItemQuote with parsed highlighted title/quote and social links', () => {
    const wrapper = mount(ItemQuote, {
      props: {
        title: '*Ana* Cliente',
        role: 'Músico',
        image: '/img/team/ana.png',
        quote: '*Excelente* servicio',
        links: [{ href: 'https://example.com', icon: 'fa-link' }],
      },
      global: {
        stubs: {
          ImageView: {
            props: ['src', 'alt'],
            template: '<img class="image-view-stub" :src="src" :alt="alt" />',
          },
          SocialLinks: {
            props: ['items'],
            template: '<div class="social-links-stub">{{ items?.length || 0 }}</div>',
          },
          QuotedText: {
            props: ['text'],
            template: '<blockquote class="quoted-text-stub" v-html="text" />',
          },
        },
      },
    })

    expect(wrapper.find('.foxy-quote-balloon').exists()).toBe(true)
    expect(wrapper.find('.image-view-stub').attributes('alt')).toBe('*Ana* Cliente')
    expect(wrapper.find('.social-links-stub').text()).toBe('1')
    expect(wrapper.html()).toContain('text-primary')
    expect(wrapper.find('.quoted-text-stub').html()).toContain('Excelente')
  })

  it('hides quote balloon and social links when no optional data is provided', () => {
    const wrapper = mount(ItemQuote, {
      props: {
        title: 'Cliente',
        role: 'Tester',
        image: '/img/team/test.png',
        quote: '',
        links: undefined,
      },
      global: {
        stubs: {
          ImageView: { template: '<img class="image-view-stub" />' },
          SocialLinks: { template: '<div class="social-links-stub" />' },
          QuotedText: { template: '<div class="quoted-text-stub" />' },
        },
      },
    })

    expect(wrapper.find('.foxy-quote-balloon').exists()).toBe(false)
    expect(wrapper.find('.social-links-stub').exists()).toBe(false)
    expect(wrapper.text()).toContain('Tester')
  })
})
