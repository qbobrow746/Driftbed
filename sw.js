const CACHE_NAME = 'driftbed-v2';
const APP_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './icon-180.png',
  './icon-32.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// The app itself (the HTML document) is network-first: cache-first froze it permanently,
// because the whole instrument lives in one index.html and the cache name rarely changes —
// a returning visitor kept getting the copy from their first ever visit and no update could
// ever reach them. Now the network wins when reachable and the cache is the offline fallback.
//
// Static assets (icons, manifest) stay cache-first: they're byte-stable, and serving them
// from cache is what keeps the instrument opening instantly with no signal.
self.addEventListener('fetch', (event) => {
  const req = event.request;
  const isSameOrigin = new URL(req.url).origin === self.location.origin;
  const isDocument = req.mode === 'navigate' ||
    (req.headers.get('accept') || '').includes('text/html');

  if (isSameOrigin && isDocument) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req).then((cached) => cached || caches.match('./index.html')))
    );
  } else if (isSameOrigin) {
    event.respondWith(
      caches.match(req).then((cached) => cached || fetch(req))
    );
  } else {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req))
    );
  }
});
