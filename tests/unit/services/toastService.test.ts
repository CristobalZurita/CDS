import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  setToastComponent,
  getToastComponent,
  showToast,
  showSuccess,
  showError,
  showWarning,
  showInfo,
} from '@/services/toastService'

describe('toastService compatibility contract', () => {
  beforeEach(() => {
    setToastComponent(null)
    vi.restoreAllMocks()
  })

  it('warns and returns undefined when toast component is missing', () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => undefined)

    const result = showToast('Mensaje sin init')

    expect(result).toBeUndefined()
    expect(warnSpy).toHaveBeenCalledWith('Toast component not initialized')
  })

  it('delegates addToast and keeps convenience defaults', () => {
    const addToast = vi.fn()
      .mockReturnValueOnce('toast-main')
      .mockReturnValueOnce('toast-success')
      .mockReturnValueOnce('toast-error')
      .mockReturnValueOnce('toast-warning')
      .mockReturnValueOnce('toast-info')

    setToastComponent({ addToast })

    expect(getToastComponent()).toEqual({ addToast })
    expect(showToast('Principal', 'warning', 2222)).toBe('toast-main')
    expect(showSuccess('Listo')).toBe('toast-success')
    expect(showError('Fallo')).toBe('toast-error')
    expect(showWarning('Atención')).toBe('toast-warning')
    expect(showInfo('Dato')).toBe('toast-info')

    expect(addToast).toHaveBeenNthCalledWith(1, 'Principal', 'warning', 2222)
    expect(addToast).toHaveBeenNthCalledWith(2, 'Listo', 'success', 3000)
    expect(addToast).toHaveBeenNthCalledWith(3, 'Fallo', 'error', 5000)
    expect(addToast).toHaveBeenNthCalledWith(4, 'Atención', 'warning', 4000)
    expect(addToast).toHaveBeenNthCalledWith(5, 'Dato', 'info', 3000)
  })
})
