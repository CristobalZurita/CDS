/**
 * Composable useApi.js - Cliente HTTP para API
 * 
 * Proporciona un cliente Axios configurado con:
 * - Base URL
 * - Autenticación automática
 * - Manejo de errores
 * - Refresh token automático
 */

import axios from 'axios'
import { useAuth } from './useAuth'

const API_URL = 'http://localhost:8000/api/v1'

// Instancia de axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para agregar token en requests
api.interceptors.request.use(
  (config) => {
    const { token } = useAuth()
    if (token.value) {
      config.headers.Authorization = `Bearer ${token.value}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Interceptor para manejar respuestas y refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { token, refreshAccessToken, logout } = useAuth()
    const originalRequest = error.config

    // Si es error 401 y aún no hemos reintentado
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Intentar refrescar token
        await refreshAccessToken()
        
        // Reintentar request original con nuevo token
        return api(originalRequest)
      } catch (refreshError) {
        // Si refresh falla, logout
        logout()
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export function useApi() {
  /**
   * GET request
   */
  async function get(url, config = {}) {
    try {
      const response = await api.get(url, config)
      return response.data
    } catch (error) {
      throw handleError(error)
    }
  }

  /**
   * POST request
   */
  async function post(url, data = {}, config = {}) {
    try {
      const response = await api.post(url, data, config)
      return response.data
    } catch (error) {
      throw handleError(error)
    }
  }

  /**
   * PUT request
   */
  async function put(url, data = {}, config = {}) {
    try {
      const response = await api.put(url, data, config)
      return response.data
    } catch (error) {
      throw handleError(error)
    }
  }

  /**
   * PATCH request
   */
  async function patch(url, data = {}, config = {}) {
    try {
      const response = await api.patch(url, data, config)
      return response.data
    } catch (error) {
      throw handleError(error)
    }
  }

  /**
   * DELETE request
   */
  async function del(url, config = {}) {
    try {
      const response = await api.delete(url, config)
      return response.data
    } catch (error) {
      throw handleError(error)
    }
  }

  /**
   * Manejo centralizado de errores
   */
  function handleError(error) {
    const message = error.response?.data?.detail || 
                   error.message || 
                   'Error en la solicitud'
    
    return {
      message,
      status: error.response?.status,
      data: error.response?.data
    }
  }

  return {
    get,
    post,
    put,
    patch,
    delete: del
  }
}
