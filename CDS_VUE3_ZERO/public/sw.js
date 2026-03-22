// CDS Service Worker — PWA shell cache
// Estrategia: cache-first para assets estaticos, network-only para /api/*

const CACHE_NAME = 'cds-shell-v1'

// Assets del shell que se cachean en la instalacion
const SHELL_ASSETS = [
  '/',
  '/manifest.json',
]

// ----- Install: pre-cachear el shell -----
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS))
  )
  self.skipWaiting()
})

// ----- Activate: limpiar caches viejos -----
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    )
  )
  self.clients.claim()
})

// ----- Fetch: estrategia por tipo de recurso -----
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url)

  // API y auth → siempre red, nunca cache
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/auth/')) {
    event.respondWith(fetch(event.request))
    return
  }

  // Navegacion HTML (rutas SPA) → red primero, fallback a cache /
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() =>
        caches.match('/').then((cached) => cached || fetch(event.request))
      )
    )
    return
  }

  // Assets estaticos (JS, CSS, fuentes, imagenes) → cache primero
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached
      return fetch(event.request).then((response) => {
        // Solo cachear respuestas validas de origen propio
        if (
          response.ok &&
          url.origin === self.location.origin &&
          event.request.method === 'GET'
        ) {
          const clone = response.clone()
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone))
        }
        return response
      })
    })
  )
})
