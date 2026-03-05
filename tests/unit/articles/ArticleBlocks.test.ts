import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ArticleInfoBlock from '@/vue/components/articles/ArticleInfoBlock.vue'
import ArticlePortfolio from '@/vue/components/articles/ArticlePortfolio.vue'
import ArticleTeamMembers from '@/vue/components/articles/ArticleTeamMembers.vue'
import ArticleTimeline from '@/vue/components/articles/ArticleTimeline.vue'
import ItemTeamMember from '@/vue/components/articles/items/ItemTeamMember.vue'
import ItemTimelineEntry from '@/vue/components/articles/items/ItemTimelineEntry.vue'

describe('article building blocks', () => {
  it('renders ArticleInfoBlock paragraphs and image slot component', () => {
    const wrapper = mount(ArticleInfoBlock, {
      props: {
        image: '/public/logo.png',
        paragraphs: ['Primer párrafo', '<strong>Segundo</strong> párrafo'],
      },
      global: {
        stubs: {
          ImageView: {
            template: '<img class="mock-image-view" />',
          },
        },
      },
    })

    expect(wrapper.find('.mock-image-view').exists()).toBe(true)
    expect(wrapper.findAll('.foxy-article-paragraph')).toHaveLength(2)
    expect(wrapper.html()).toContain('<strong>Segundo</strong>')
  })

  it('renders ArticleTeamMembers slot content', () => {
    const wrapper = mount(ArticleTeamMembers, {
      slots: {
        default: '<div class="member-card">Team Member</div>',
      },
    })

    expect(wrapper.find('.team-grid .member-card').exists()).toBe(true)
    expect(wrapper.text()).toContain('Team Member')
  })

  it('renders ItemTeamMember fields and social links', () => {
    const wrapper = mount(ItemTeamMember, {
      props: {
        name: 'Cristobal',
        role: 'Luthier',
        image: '/img/team/cristobal.jpg',
        links: [
          { href: 'https://github.com/cz', faIcon: 'fa-brands fa-github' },
          { href: 'https://linkedin.com/in/cz', faIcon: 'fa-brands fa-linkedin' },
        ],
      },
    })

    expect(wrapper.text()).toContain('Cristobal')
    expect(wrapper.text()).toContain('Luthier')
    expect(wrapper.findAll('.team-links a')).toHaveLength(2)
    expect(wrapper.findAll('.team-links i')[0].classes()).toContain('fa-github')
  })

  it('renders ItemTimelineEntry with parsed title/description and date range', () => {
    const wrapper = mount(ItemTimelineEntry, {
      props: {
        title: '*Ingreso* equipo',
        description: 'Se recibe para diagnóstico',
        dateStart: '2026-03-01',
        dateEnd: '2026-03-04',
      },
      global: {
        stubs: {
          ImageView: {
            template: '<img class="mock-image-view" />',
          },
        },
      },
    })

    expect(wrapper.html()).toContain('text-primary')
    expect(wrapper.text()).toContain('Se recibe para diagnóstico')
    expect(wrapper.html()).toContain('timeline-arrow-icon')
  })

  it('renders ArticleTimeline slot and appends trailing timeline entry', () => {
    const wrapper = mount(ArticleTimeline, {
      slots: {
        default: '<li class="custom-entry">Inicio</li>',
      },
    })

    expect(wrapper.find('.custom-entry').exists()).toBe(true)
    expect(wrapper.find('.foxy-timeline-item-trailing').exists()).toBe(true)
  })

  it('normalizes categories in ArticlePortfolio before rendering items', () => {
    const wrapper = mount(ArticlePortfolio, {
      props: {
        categories: [
          { id: 'synth', label: 'Sintetizadores' },
        ],
        projects: [
          { id: 1, title: 'Juno 106', category: 'synth', description: 'Calibración' },
          { id: 2, title: 'Proyecto X', category: '', description: 'General' },
        ],
      },
      global: {
        stubs: {
          ArticleProjectGrid: {
            template: '<section class="project-grid"><slot /></section>',
          },
          ItemProjectGrid: {
            props: ['title', 'category'],
            template: '<article class="project-item">{{ title }}::{{ category }}</article>',
          },
        },
      },
    })

    const rows = wrapper.findAll('.project-item')
    expect(rows).toHaveLength(2)
    expect(rows[0].text()).toContain('Juno 106::Sintetizadores')
    expect(rows[1].text()).toContain('Proyecto X::General')
  })
})
