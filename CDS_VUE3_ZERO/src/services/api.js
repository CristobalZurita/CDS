import axios from 'axios'

const API_URL = String(import.meta.env.VITE_API_URL || '/api/v1').replace(/\/+$/, '')
// CSRF endpoint sits outside /api/v1 (at /api/csrf-token)
const CSRF_URL = API_URL.replace(/\/api\/v\d+.*$/, '') + '/api/csrf-token'
const AUTH_TOKEN_KEY = 'cds_auth_token'
const AUTH_USER_KEY = 'cds_auth_user'
const MUTATING_METHODS = new Set(['post', 'put', 'patch', 'delete'])

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

function getStorage() {
  if (typeof window === 'undefined') return null
  return window.localStorage
}

export function getStoredToken() {
  const storage = getStorage()
  if (!storage) return ''
  return storage.getItem(AUTH_TOKEN_KEY) || ''
}

export function setStoredToken(token) {
  const storage = getStorage()
  if (!storage) return
  if (!token) {
    storage.removeItem(AUTH_TOKEN_KEY)
    return
  }
  storage.setItem(AUTH_TOKEN_KEY, token)
}

export function getStoredUser() {
  const storage = getStorage()
  if (!storage) return null
  const raw = storage.getItem(AUTH_USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function setStoredUser(user) {
  const storage = getStorage()
  if (!storage) return
  if (!user) {
    storage.removeItem(AUTH_USER_KEY)
    return
  }
  storage.setItem(AUTH_USER_KEY, JSON.stringify(user))
}

export function clearStoredSession() {
  setStoredToken('')
  setStoredUser(null)
}

api.interceptors.request.use(async (config) => {
  const token = getStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    // Bearer token requests bypass CSRF on the backend — nothing more needed
    return config
  }

  // For unauthenticated mutation requests, inject a fresh CSRF token.
  // The backend enforces CSRF only in production (ENFORCE_CSRF=true) and only
  // for requests without an Authorization: Bearer header.
  if (MUTATING_METHODS.has((config.method || '').toLowerCase())) {
    try {
      const res = await axios.get(CSRF_URL)
      const csrfToken = res.data?.token
      if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken
      }
    } catch {
      // CSRF fetch failed — proceed without token (will only matter in production)
    }
  }

  return config
})

export function extractErrorMessage(error) {
  const data = error?.response?.data
  if (!data) return error?.message || 'Error de red o servidor'

  if (typeof data === 'string') return data
  if (typeof data.detail === 'string') return data.detail
  if (typeof data.message === 'string') return data.message
  if (typeof data.error === 'string') return data.error

  if (Array.isArray(data.detail)) {
    return data.detail
      .map((entry) => entry?.msg || entry?.message || String(entry))
      .filter(Boolean)
      .join(' | ')
  }

  return 'Error de red o servidor'
}

function unwrapResponse(payload) {
  if (!payload || typeof payload !== 'object') return {}
  if (payload.data && typeof payload.data === 'object') return payload.data
  return payload
}

export function pickAccessToken(payload) {
  const data = unwrapResponse(payload)
  return data.access_token || data.token || data.jwt || ''
}

export function pickUser(payload) {
  const data = unwrapResponse(payload)
  return data.user || data.profile || data.account || null
}

export async function login(payload) {
  const { data } = await api.post('/auth/login', payload)
  return data
}

export async function verifyTwoFactor(payload) {
  const { data } = await api.post('/auth/2fa/verify', payload)
  return data
}

export async function register(payload) {
  const { data } = await api.post('/auth/register', payload)
  return data
}

export async function checkAuth() {
  const { data } = await api.get('/auth/me')
  return data
}

export async function logout() {
  const { data } = await api.post('/auth/logout')
  return data
}

export async function requestPasswordReset(payload) {
  const { data } = await api.post('/auth/password-reset/request', payload)
  return data
}

export async function confirmPasswordReset(payload) {
  const { data } = await api.post('/auth/password-reset/confirm', payload)
  return data
}

export default api
