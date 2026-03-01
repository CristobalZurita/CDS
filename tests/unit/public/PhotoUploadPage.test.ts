import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  post: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: { token: 'photo-token-123' },
  }),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import PhotoUploadPage from '@/vue/content/pages/PhotoUploadPage.vue'

describe('PhotoUploadPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.post.mockReset()
  })

  it('submits a photo upload form with token and caption', async () => {
    apiMock.post.mockResolvedValue({ data: { ok: true } })

    const wrapper = mount(PhotoUploadPage)
    const fileInput = wrapper.get('[data-testid="photo-upload-file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [new File(['photo'], 'photo.png', { type: 'image/png' })],
      configurable: true,
    })

    await fileInput.trigger('change')
    await wrapper.get('[data-testid="photo-upload-caption"]').setValue('Detalle del daño')
    await wrapper.get('[data-testid="photo-upload-submit"]').trigger('click')
    await flushPromises()

    expect(apiMock.post).toHaveBeenCalledTimes(1)
    expect(apiMock.post.mock.calls[0][0]).toBe('/photo-requests/submit')
    expect(apiMock.post.mock.calls[0][1]).toBeInstanceOf(FormData)
    expect(wrapper.get('[data-testid="photo-upload-status"]').text()).toContain('Foto enviada correctamente.')
  })

  it('shows an error message when the upload fails', async () => {
    apiMock.post.mockRejectedValue(new Error('boom'))

    const wrapper = mount(PhotoUploadPage)
    const fileInput = wrapper.get('[data-testid="photo-upload-file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [new File(['photo'], 'photo.png', { type: 'image/png' })],
      configurable: true,
    })
    await fileInput.trigger('change')
    await wrapper.get('[data-testid="photo-upload-submit"]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-testid="photo-upload-status"]').text()).toContain('No se pudo enviar la foto.')
  })
})
