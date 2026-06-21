const CACHE_NAME = "emkt-v1";
const URLS = ["/","/api/health","/api/simulate/status","/api/market/overview","/static/manifest.json"];
self.addEventListener("install",(e)=>{e.waitUntil(caches.open(CACHE_NAME).then(c=>c.addAll(URLS)));self.skipWaiting()});
self.addEventListener("activate",(e)=>{e.waitUntil(clients.claim())});
self.addEventListener("fetch",(e)=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)))});
