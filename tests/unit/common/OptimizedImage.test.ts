import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import OptimizedImage from '@/vue/components/common/OptimizedImage.vue'

describe('OptimizedImage', () => {
  it('renders image attributes with defaults', () => {
    const wrapper = mount(OptimizedImage, {
      props: {
        src: '/images/synth.webp',
      },
    })

    const image = wrapper.get('img')
    expect(image.attributes('src')).toBe('/images/synth.webp')
    expect(image.attributes('alt')).toBe('Image')
    expect(image.attributes('loading')).toBe('lazy')
    expect(image.attributes('srcset')).toBe('')
    expect(image.attributes('sizes')).toBe('')
    expect(image.classes()).toContain('optimized-image')
  })

  it('applies responsive props and custom class composition', () => {
    const wrapper = mount(OptimizedImage, {
      props: {
        src: '/images/synth-large.webp',
        alt: 'Korg MS-20',
        srcset: '/images/small.webp 600w, /images/large.webp 1200w',
        sizes: '(max-width: 768px) 100vw, 50vw',
        loading: 'eager',
        width: 640,
        height: 480,
        class: 'rounded shadow',
      },
    })

    const image = wrapper.get('img')
    expect(image.attributes('alt')).toBe('Korg MS-20')
    expect(image.attributes('loading')).toBe('eager')
    expect(image.attributes('width')).toBe('640')
    expect(image.attributes('height')).toBe('480')
    expect(image.attributes('srcset')).toContain('600w')
    expect(image.attributes('sizes')).toContain('100vw')
    expect(image.classes()).toContain('optimized-image')
    expect(image.classes()).toContain('rounded')
    expect(image.classes()).toContain('shadow')
  })
})
