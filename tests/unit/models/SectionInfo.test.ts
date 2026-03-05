import { describe, expect, it } from 'vitest'

import SectionInfo from '@/models/SectionInfo.js'

const MockSection = {
  template: '<div />',
}

describe('SectionInfo', () => {
  it('stores the section metadata and builds its hash', () => {
    const section = new SectionInfo('diagnostic', MockSection, 'Cotizar', 'pi pi-calculator')

    expect(section.id).toBe('diagnostic')
    expect(section.name).toBe('Cotizar')
    expect(section.faIcon).toBe('pi pi-calculator')
    expect(section.component).toBe(MockSection)
    expect(section.hash).toBe('#diagnostic')
  })

  it('falls back to the default icon and null name when optional values are empty', () => {
    const section = new SectionInfo('hero', MockSection)

    expect(section.name).toBeNull()
    expect(section.faIcon).toBe('fa-solid fa-circle')
  })

  it('throws when id or component are missing', () => {
    expect(() => new SectionInfo('', MockSection)).toThrow(
      'You must specify an ID and a component for every SectionInfo object!'
    )
    expect(() => new SectionInfo('hero', null as any)).toThrow(
      'You must specify an ID and a component for every SectionInfo object!'
    )
  })
})
