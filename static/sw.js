const CACHE_NAME = 'campopawa-v1';
const STATIC_ASSETS = ['/', '/offline/'];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // Only intercept same-origin requests to avoid CORS errors with external CDNs (like Tailwind)
  // This ensures third-party assets are handled directly by the browser's standard network stack.
  if (url.origin !== self.location.origin) {
    return; 
  }

  // Only serve the offline page logic for navigation requests (HTML pages)
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .catch(() => caches.match('/offline/'))
    );
  } else {
    // For local assets (JS, CSS, Images), try network first, then cache, then fail gracefully
    event.respondWith(
      fetch(event.request)
        .catch(() => caches.match(event.request))
    );
  }
});
