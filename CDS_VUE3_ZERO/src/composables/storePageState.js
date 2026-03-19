export function resolveStoreCheckoutLabel({ isAdmin = false, isAuthenticated = false, submitting = false } = {}) {
  if (isAdmin) return 'Cuenta admin no compra'
  if (!isAuthenticated) return 'Inicia sesión para solicitar'
  if (submitting) return 'Enviando solicitud...'
  return 'Enviar solicitud'
}

export function resolveStoreAddButtonLabel(product, canAddProduct) {
  if (!canAddProduct) {
    if (Number(product?.available_stock || 0) <= 0) return 'Sin stock'
    return Number(product?.sellable_stock || 0) <= 0 ? 'Reservado taller' : 'No disponible'
  }

  if (Number(product?.sellable_stock || 0) > 0 && Number(product?.price || 0) > 0) {
    return 'Agregar'
  }

  return 'Agregar a lista'
}

export function resolveStoreCheckoutGuard({ cartItemsCount = 0, isAdmin = false, isAuthenticated = false } = {}) {
  if (!cartItemsCount) {
    return { kind: 'error', message: 'El carrito está vacío.' }
  }

  if (isAdmin) {
    return { kind: 'error', message: 'La solicitud de tienda está disponible para cuentas cliente.' }
  }

  if (!isAuthenticated) {
    return { kind: 'login' }
  }

  return { kind: 'submit' }
}
