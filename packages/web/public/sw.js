/**
 * AI知识图谱 — Service Worker
 * 
 * Strategy:
 * - App shell (HTML, CSS, JS) → Cache First with network update
 * - API calls → Network First with cache fallback
 * - Static assets → Cache First (immutable hashed filenames)
 * 
 * This is a simple, manually written SW (not Workbox) for transparency.
 */

const CACHE_VERSION = 'akg-v1';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const API_CACHE = `${CACHE_VERSION}-api`;

// App shell files to precache
const PRECACHE_URLS = [
  '/',
  '/manifest.json',
];

// Install — precache app shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(PRECACHE_URLS);
    }).then(() => self.skipWaiting())
  );
});

// Activate — clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys
          .filter((key) => key.startsWith('akg-') && key !== STATIC_CACHE && key !== API_CACHE)
          .map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch — routing strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Skip cross-origin requests (fonts, analytics, etc.)
  if (url.origin !== location.origin) return;

  // API calls → Network First
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request, API_CACHE));
    return;
  }

  // Hashed static assets → Cache First (immutable)
  if (url.pathname.startsWith('/assets/') && url.pathname.match(/\.[a-f0-9]{8}\./)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }

  // Everything else (HTML navigation) → Network First
  event.respondWith(networkFirst(request, STATIC_CACHE));
});

// ── Strategies ──────────────────────────────────────────

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('Offline', { status: 503 });
  }
}

async function networkFirst(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    
    // For navigation requests, return cached index.html (SPA)
    if (request.mode === 'navigate') {
      const index = await caches.match('/');
      if (index) return index;
    }
    
    return new Response('Offline', { status: 503 });
  }
}
