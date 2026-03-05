/**
 * Wrapper de compatibilidad para imports legacy en JavaScript.
 * La implementación autoritativa vive en `api.ts`.
 */

import api, {
  API_URL,
  get,
  post,
  put,
  patch,
  deleteRequest,
  handleApiError,
  healthCheck
} from './api.ts'

export {
  api,
  API_URL,
  get,
  post,
  put,
  patch,
  deleteRequest,
  handleApiError,
  healthCheck
}

export default api
