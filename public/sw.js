const CACHE_NAME = 'cds-v2';
const CORE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
];

// Define cache strategy: which assets to cache by type
const CACHE_STRATEGIES = {
  static: ['js', 'css', 'woff2', 'png', 'jpg', 'jpeg', 'svg', 'webp'],
  dynamic: ['json'], // API responses
  network: ['api'] // Always fetch, then cache
};

// Check if URL should be cached based on extension
function shouldCache(url) {
  const ext = url.split('.').pop()?.split('?')[0] || '';
  return CACHE_STRATEGIES.static.includes(ext);
}

// Check if it's an API request
function isApiRequest(url) {
  return url.includes('/api/') || url.includes('maps.googleapis.com') || url.includes('fonts.gstatic.com');
}

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((key) => (key !== CACHE_NAME ? caches.delete(key) : null)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  
  const { request } = event;
  const url = new URL(request.url);
  
  // API requests: Network first, fallback to cache
  if (isApiRequest(url.href)) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }
  
  // Static assets: Cache first, fallback to network
  if (shouldCache(url.href)) {
    event.respondWith(
      caches.match(request).then((cached) =>
        cached || fetch(request).then((response) => {
          if (response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return response;
        }).catch(() => {
          // Fallback for offline: return placeholder
          if (url.href.match(/\.(png|jpg|jpeg|svg|webp)$/)) {
            return new Response('', { status: 404 });
          }
          return cached || new Response('Offline', { status: 503 });
        })
      )
    );
    return;
  }
  
  // HTML pages: Network first
  event.respondWith(
    fetch(request)
      .then((response) => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
        }
        return response;
      })
      .catch(() => caches.match(request) || new Response('Offline', { status: 503 }))
  );
});
