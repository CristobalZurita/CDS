import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import ManualsPage from '@/vue/content/pages/admin/ManualsPage.vue'

const adminLayoutStub = {
  template: '<div><slot /></div>',
}

const wizardStub = {
  template: '<div />',
}

describe('ManualsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.get.mockResolvedValue({
      data: [
        {
          id: 5,
          title: 'Manual Original',
          source: 'external',
          url: 'https://example.com/original.pdf',
        },
      ],
    })
    apiMock.patch.mockResolvedValue({})
    apiMock.delete.mockResolvedValue({})
    vi.spyOn(window, 'confirm').mockReturnValue(true)
  })

  it('edits and deletes manuals from the table', async () => {
    const wrapper = mount(ManualsPage, {
      global: {
        stubs: {
          AdminLayout: adminLayoutStub,
          WizardManualUpload: wizardStub,
        },
      },
    })

    await flushPromises()
    expect(wrapper.text()).toContain('Manual Original')

    await wrapper.get('[data-testid="manual-edit"]').trigger('click')
    await wrapper.get('[data-testid="manual-title-input"]').setValue('Manual Editado')
    await wrapper.get('[data-testid="manual-url-input"]').setValue('https://example.com/updated.pdf')
    await wrapper.get('[data-testid="manual-save"]').trigger('click')
    await flushPromises()

    expect(apiMock.patch).toHaveBeenCalledWith('/manuals/5', {
      title: 'Manual Editado',
      source: 'external',
      url: 'https://example.com/updated.pdf',
    })

    await wrapper.get('[data-testid="manual-delete"]').trigger('click')
    await flushPromises()
    expect(apiMock.delete).toHaveBeenCalledWith('/manuals/5')
  })
})
