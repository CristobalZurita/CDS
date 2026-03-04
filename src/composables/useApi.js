/**
 * Wrapper de compatibilidad para el composable legacy.
 * Reutiliza la capa HTTP central para evitar dos clientes Axios con
 * interceptores y reglas distintas.
 */

import {
  get as apiGet,
  post as apiPost,
  put as apiPut,
  patch as apiPatch,
  deleteRequest,
  handleApiError
} from '@/services/api'

function toLegacyError(error) {
  const normalized = handleApiError(error)
  const responseData = error?.response?.data
  const message =
    typeof responseData?.detail === 'string'
      ? responseData.detail
      : normalized.message

  return {
    message,
    status: error?.response?.status,
    data: responseData
  }
}

async function unwrap(request) {
  try {
    const response = await request
    return response.data
  } catch (error) {
    throw toLegacyError(error)
  }
}

export function useApi() {
  return {
    get(url, config = {}) {
      return unwrap(apiGet(url, config))
    },
    post(url, data = {}, config = {}) {
      return unwrap(apiPost(url, data, config))
    },
    put(url, data = {}, config = {}) {
      return unwrap(apiPut(url, data, config))
    },
    patch(url, data = {}, config = {}) {
      return unwrap(apiPatch(url, data, config))
    },
    delete(url, config = {}) {
      return unwrap(deleteRequest(url, config))
    }
  }
}
