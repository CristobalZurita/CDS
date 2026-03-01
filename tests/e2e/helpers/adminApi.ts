import fs from 'node:fs'
import { resolveAuthState } from './auth'

const apiBaseURL = process.env.PLAYWRIGHT_API_URL || 'http://127.0.0.1:8001/api/v1'
const frontendOrigin = new URL(process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5174').origin

function originCandidates(origin: string) {
  if (origin.includes('127.0.0.1')) {
    return [origin, origin.replace('127.0.0.1', 'localhost')]
  }
  if (origin.includes('localhost')) {
    return [origin, origin.replace('localhost', '127.0.0.1')]
  }
  return [origin]
}

function getAccessToken(profile: 'admin' | 'client' = 'admin') {
  const raw = fs.readFileSync(resolveAuthState(profile), 'utf8')
  const state = JSON.parse(raw)
  const origin = state.origins?.find((entry: any) => originCandidates(frontendOrigin).includes(entry.origin))
  const token = origin?.localStorage?.find((entry: any) => entry.name === 'access_token')?.value
  if (!token) {
    throw new Error(`No se encontró access_token en storageState para ${profile}`)
  }
  return token
}

async function parseResponse(response: Response) {
  const text = await response.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}

export async function apiAs(
  profile: 'admin' | 'client',
  path: string,
  options: {
    method?: string
    body?: unknown
    headers?: Record<string, string>
  } = {}
) {
  const token = getAccessToken(profile)
  const response = await fetch(`${apiBaseURL}${path.startsWith('/') ? path : `/${path}`}`, {
    method: options.method || 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.headers || {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  })

  const data = await parseResponse(response)
  if (!response.ok) {
    throw new Error(`API ${response.status} ${path}: ${JSON.stringify(data)}`)
  }
  return data
}

export async function publicApi(
  path: string,
  options: {
    method?: string
    body?: unknown
    headers?: Record<string, string>
  } = {}
) {
  const response = await fetch(`${apiBaseURL}${path.startsWith('/') ? path : `/${path}`}`, {
    method: options.method || 'GET',
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.headers || {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  })

  const data = await parseResponse(response)
  if (!response.ok) {
    throw new Error(`Public API ${response.status} ${path}: ${JSON.stringify(data)}`)
  }
  return data
}
