/* Jumapp Service Worker - PWA Offline Support */

const CACHE_VERSION = 'jumapp-v1';
const APP_SHELL_CACHE = `${CACHE_VERSION}-app-shell`;
const STATIC_ASSETS_CACHE = `${CACHE_VERSION}-static-assets`;
const API_CACHE = `${CACHE_VERSION}-api`;
const OFFLINE_URL = '/offline.html';

const APP_SHELL_URLS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/offline.html',
  '/favicon.ico',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
];

/* ---------- Install: Pre-cache app shell ---------- */
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(APP_SHELL_CACHE)
      .then((cache) => cache.addAll(APP_SHELL_URLS))
      .then(() => self.skipWaiting())
  );
});

/* ---------- Activate: Clean up old caches ---------- */
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) =>
        Promise.all(
          cacheNames
            .filter((cacheName) => !cacheName.startsWith(CACHE_VERSION))
            .map((cacheName) => caches.delete(cacheName))
        )
      )
      .then(() => self.clients.claim())
  );
});

/* ---------- Helper: Is this an API/data request? ---------- */
function isApiRequest(request) {
  const url = new URL(request.url);
  // Treat requests to /api/ or any request with Accept: application/json as data
  return (
    url.pathname.startsWith('/api/') ||
    request.headers.get('accept')?.includes('application/json') ||
    url.pathname.endsWith('.json')
  );
}

/* ---------- Helper: Is this a navigation request? ---------- */
function isNavigationRequest(request) {
  return request.mode === 'navigate';
}

/* ---------- Helper: Is this a static asset? ---------- */
function isStaticAsset(request) {
  const url = new URL(request.url);
  const extension = url.pathname.split('.').pop()?.toLowerCase();
  const staticExtensions = [
    'js', 'css', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp',
    'ico', 'woff', 'woff2', 'ttf', 'otf', 'eot', 'mp4', 'webm',
  ];
  return staticExtensions.includes(extension);
}

/* ---------- Strategy: Cache-First for static assets ---------- */
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_ASSETS_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // Network failed and no cache - return offline fallback for navigations
    if (isNavigationRequest(request)) {
      const offlineResponse = await caches.match(OFFLINE_URL);
      if (offlineResponse) {
        return offlineResponse;
      }
    }
    throw error;
  }
}

/* ---------- Strategy: Network-First for API/data ---------- */
async function networkFirst(request) {
  const cache = await caches.open(API_CACHE);

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

/* ---------- Strategy: Network-First for navigations (app shell) ---------- */
async function networkFirstNavigation(request) {
  const cache = await caches.open(APP_SHELL_CACHE);

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    // Fall back to the root cached page
    const rootResponse = await cache.match('/');
    if (rootResponse) {
      return rootResponse;
    }
    const offlineResponse = await caches.match(OFFLINE_URL);
    if (offlineResponse) {
      return offlineResponse;
    }
    throw error;
  }
}

/* ---------- Fetch handler ---------- */
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Only handle GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip non-http(s) requests (e.g. chrome-extension://)
  const url = new URL(request.url);
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // Skip cross-origin requests (only cache same-origin)
  if (url.origin !== self.location.origin) {
    return;
  }

  // Route to the appropriate strategy
  if (isApiRequest(request)) {
    event.respondWith(networkFirst(request));
  } else if (isNavigationRequest(request)) {
    event.respondWith(networkFirstNavigation(request));
  } else if (isStaticAsset(request)) {
    event.respondWith(cacheFirst(request));
  } else {
    // Default: Network-First with cache fallback
    event.respondWith(networkFirst(request));
  }
});