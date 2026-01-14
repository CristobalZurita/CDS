/**
 * Composable useAuth.js - Gestión de autenticación
 * 
 * Proporciona funciones para:
 * - Login/Register
 * - Logout
 * - Verificación de sesión
 * - Almacenamiento de tokens
 */

import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// Estado global de autenticación
const user = ref(null)
const token = ref(localStorage.getItem('access_token'))
const refreshToken = ref(localStorage.getItem('refresh_token'))
const isLoading = ref(false)
const error = ref(null)

// Computed properties
const isAuthenticated = computed(() => !!token.value && !!user.value)
const isAdmin = computed(() => user.value?.role === 'admin')

export function useAuth() {
  const router = useRouter()

  /**
   * Registrar nuevo usuario
   * @param {Object} data - { email, username, full_name, password, phone }
   */
  async function register(data) {
    isLoading.value = true
    error.value = null

    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        email: data.email,
        username: data.username,
        full_name: data.full_name,
        password: data.password,
        phone: data.phone || null
      })

      user.value = response.data
      return user.value
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error en el registro'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Login
   * @param {string} email - Email del usuario
   * @param {string} password - Contraseña
   */
  async function login(email, password) {
    isLoading.value = true
    error.value = null

    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        password
      })

      const { access_token, refresh_token } = response.data

      // Guardar tokens
      token.value = access_token
      refreshToken.value = refresh_token
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      // Obtener información del usuario
      await fetchUserInfo()

      return user.value
    } catch (err) {
      error.value = err.response?.data?.detail || 'Email o contraseña incorrectos'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtener información del usuario actual
   */
  async function fetchUserInfo() {
    if (!token.value) return null

    try {
      const response = await axios.get(`${API_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })

      user.value = response.data
      return user.value
    } catch (err) {
      // Token expirado o inválido
      logout()
      throw err
    }
  }

  /**
   * Refrescar access token
   */
  async function refreshAccessToken() {
    if (!refreshToken.value) {
      logout()
      return null
    }

    try {
      const response = await axios.post(`${API_URL}/auth/refresh`, {
        refresh_token: refreshToken.value
      })

      const { access_token, refresh_token: new_refresh_token } = response.data

      token.value = access_token
      refreshToken.value = new_refresh_token
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', new_refresh_token)

      return access_token
    } catch (err) {
      logout()
      throw err
    }
  }

  /**
   * Logout
   */
  function logout() {
    user.value = null
    token.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/login')
  }

  /**
   * Verificar autenticación en app init
   */
  async function checkAuth() {
    if (token.value) {
      try {
        await fetchUserInfo()
      } catch (err) {
        logout()
      }
    }
  }

  return {
    // Estado
    user,
    token,
    refreshToken,
    isLoading,
    error,

    // Computed
    isAuthenticated,
    isAdmin,

    // Métodos
    register,
    login,
    logout,
    checkAuth,
    fetchUserInfo,
    refreshAccessToken
  }
}
