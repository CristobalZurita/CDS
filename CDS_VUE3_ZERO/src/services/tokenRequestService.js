import api from '@/services/api'

function buildApiPath(path) {
  const base = String(api.defaults.baseURL || '/api/v1').replace(/\/+$/, '')
  const normalizedPath = String(path || '').startsWith('/') ? path : `/${path || ''}`
  return `${base}${normalizedPath}`
}

function normalizeSignatureRequest(entry) {
  return {
    id: Number(entry?.id || 0),
    repair_id: Number(entry?.repair_id || 0),
    request_type: String(entry?.request_type || ''),
    token: String(entry?.token || ''),
    status: String(entry?.status || ''),
    created_at: entry?.created_at || null,
    signed_at: entry?.signed_at || null,
    expires_at: entry?.expires_at || null
  }
}

function normalizePhotoRequest(entry) {
  return {
    id: Number(entry?.id || 0),
    repair_id: Number(entry?.repair_id || 0),
    photo_type: String(entry?.photo_type || ''),
    status: String(entry?.status || ''),
    expires_at: entry?.expires_at || null
  }
}

export async function fetchSignatureRequestByToken(token) {
  const response = await api.get(`/signatures/requests/token/${token}`)
  return normalizeSignatureRequest(response?.data)
}

export async function cancelSignatureRequestById(requestId) {
  await api.post(`/signatures/requests/${requestId}/cancel`)
}

export function openSignatureRequestStream(token, { onEvent, onError } = {}) {
  if (typeof window === 'undefined' || typeof window.EventSource === 'undefined') {
    return () => {}
  }

  const stream = new window.EventSource(buildApiPath(`/signatures/stream/${token}`))

  stream.onmessage = (event) => {
    if (typeof onEvent === 'function') {
      onEvent(String(event?.data || '').trim())
    }
  }

  stream.onerror = (event) => {
    if (typeof onError === 'function') {
      onError(event)
    }
    stream.close()
  }

  return () => {
    stream.close()
  }
}

export async function fetchPhotoRequestByToken(token) {
  const response = await api.get(`/photo-requests/token/${token}`)
  return normalizePhotoRequest(response?.data)
}
