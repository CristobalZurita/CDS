import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  post: vi.fn(),
}))

const clearRect = vi.fn()
const beginPath = vi.fn()
const moveTo = vi.fn()
const lineTo = vi.fn()
const stroke = vi.fn()

vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: { token: 'signature-token-123' },
  }),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import SignaturePage from '@/vue/content/pages/SignaturePage.vue'

describe('SignaturePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.post.mockResolvedValue({ data: { ok: true } })

    Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
      configurable: true,
      value: vi.fn(() => ({
        beginPath,
        moveTo,
        lineTo,
        stroke,
        clearRect,
        lineWidth: 0,
        lineCap: '',
        strokeStyle: '',
      })),
    })

    Object.defineProperty(HTMLCanvasElement.prototype, 'toDataURL', {
      configurable: true,
      value: vi.fn(() => 'data:image/png;base64,firma'),
    })
  })

  it('clears the canvas and submits a signature payload with token', async () => {
    const wrapper = mount(SignaturePage)
    await flushPromises()

    await wrapper.get('[data-testid="signature-clear"]').trigger('click')
    expect(clearRect).toHaveBeenCalled()

    await wrapper.get('[data-testid="signature-submit"]').trigger('click')
    await flushPromises()

    expect(apiMock.post).toHaveBeenCalledWith('/signatures/submit', {
      token: 'signature-token-123',
      image_base64: 'data:image/png;base64,firma',
    })
    expect(wrapper.get('[data-testid="signature-status"]').text()).toContain('Firma enviada correctamente.')
  })

  it('shows an error message when signature submission fails', async () => {
    apiMock.post.mockRejectedValueOnce(new Error('boom'))

    const wrapper = mount(SignaturePage)
    await wrapper.get('[data-testid="signature-submit"]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-testid="signature-status"]').text()).toContain('No se pudo enviar la firma.')
  })
})
