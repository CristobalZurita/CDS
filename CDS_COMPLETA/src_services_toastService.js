/**
 * Toast Notification Service
 * 
 * Proporciona una interfaz global para mostrar notificaciones toast
 * en toda la aplicación sin necesidad de pasar referencias
 */

let toastComponent = null

export function setToastComponent(component) {
  toastComponent = component
}

export function getToastComponent() {
  return toastComponent
}

export function showToast(message, type = 'info', duration = 4000) {
  if (!toastComponent) {
    console.warn('Toast component not initialized')
    return
  }
  return toastComponent.addToast(message, type, duration)
}

export function showSuccess(message, duration = 3000) {
  return showToast(message, 'success', duration)
}

export function showError(message, duration = 5000) {
  return showToast(message, 'error', duration)
}

export function showWarning(message, duration = 4000) {
  return showToast(message, 'warning', duration)
}

export function showInfo(message, duration = 3000) {
  return showToast(message, 'info', duration)
}
