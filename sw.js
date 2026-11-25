// Service worker: makes Yeas and Nays installable and lets pages you've
// visited open offline.
//
// - Pages: network first, so you always get the latest figures when online;
//   falls back to the last copy you viewed when offline.
// - Same-origin files (scripts, maps, portraits, icons): served from cache,
//   refreshed in the background.
const CACHE = 'yeas-nays-v1';

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.add('/')).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

function store(req, res) {
  if (res.ok) {
    const copy = res.clone();
    caches.open(CACHE).then((c) => c.put(req, copy));
  }
  return res;
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then((res) => store(req, res))
        .catch(() => caches.match(req).then((r) => r || caches.match('/')).then((r) => r || Response.error())),
    );
    return;
  }

  e.respondWith(
    caches.match(req).then((hit) => {
      const fresh = fetch(req).then((res) => store(req, res)).catch(() => hit);
      return hit || fresh;
    }),
  );
});
