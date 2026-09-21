// AI Driver Monitor — Service Worker
// Caches all assets for full offline functionality

const CACHE_NAME = 'ai-driver-v1';

// Resources to pre-cache on install
const PRECACHE = [
  '/',
  '/index.html',
  '/manifest.json',
  '/static/alarm.wav',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
];

// External resources to cache on first use (MediaPipe CDN files)
const CDN_DOMAINS = [
  'cdn.jsdelivr.net',
  'storage.googleapis.com',
  'fonts.googleapis.com',
  'fonts.gstatic.com',
];

// ─── INSTALL: pre-cache shell ────────────────────────────────
self.addEventListener('install', (event) => {
  console.log('[SW] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE).catch((err) => {
        console.warn('[SW] Pre-cache failed (some files may not exist yet):', err);
      });
    })
  );
  self.skipWaiting();
});

// ─── ACTIVATE: clear old caches ──────────────────────────────
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating...');
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// ─── FETCH: serve from cache, update in background ───────────
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  // For CDN resources (MediaPipe models, fonts): cache-first
  const isCDN = CDN_DOMAINS.some((d) => url.hostname.includes(d));

  if (isCDN) {
    event.respondWith(
      caches.open(CACHE_NAME).then(async (cache) => {
        const cached = await cache.match(event.request);
        if (cached) return cached;
        try {
          const response = await fetch(event.request);
          if (response.ok) cache.put(event.request, response.clone());
          return response;
        } catch {
          return cached || new Response('Offline', { status: 503 });
        }
      })
    );
    return;
  }

  // For local app files: network-first with cache fallback
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response.ok) {
          caches.open(CACHE_NAME).then((cache) =>
            cache.put(event.request, response.clone())
          );
        }
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
