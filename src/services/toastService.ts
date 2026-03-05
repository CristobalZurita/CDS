type ToastType = 'info' | 'success' | 'error' | 'warning'

type ToastComponent = {
  addToast: (message: string, type?: ToastType, duration?: number) => unknown
}

let toastComponent: ToastComponent | null = null

export function setToastComponent(component: ToastComponent | null): void {
  toastComponent = component
}

export function getToastComponent(): ToastComponent | null {
  return toastComponent
}

export function showToast(message: string, type: ToastType = 'info', duration = 4000): unknown {
  if (!toastComponent) {
    console.warn('Toast component not initialized')
    return
  }
  return toastComponent.addToast(message, type, duration)
}

export function showSuccess(message: string, duration = 3000): unknown {
  return showToast(message, 'success', duration)
}

export function showError(message: string, duration = 5000): unknown {
  return showToast(message, 'error', duration)
}

export function showWarning(message: string, duration = 4000): unknown {
  return showToast(message, 'warning', duration)
}

export function showInfo(message: string, duration = 3000): unknown {
  return showToast(message, 'info', duration)
}
