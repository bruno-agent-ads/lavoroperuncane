/* L'ufficio del capo: funziona anche senza rete dopo la prima apertura. */
var CACHE='ufficio-v3';
var FILES=['/ufficio/','/ufficio/manifest.webmanifest','/js/zampe.js','/img/bruno-sedia.jpg','/img/icon-192.png','/img/icon-512.png','/js/qrcode.min.js'];
self.addEventListener('install',function(e){e.waitUntil(caches.open(CACHE).then(function(c){return c.addAll(FILES)}).then(function(){return self.skipWaiting()}))});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(k){return Promise.all(k.filter(function(n){return n!==CACHE}).map(function(n){return caches.delete(n)}))}).then(function(){return self.clients.claim()}))});
self.addEventListener('fetch',function(e){
  if(e.request.method!=='GET')return;
  e.respondWith(fetch(e.request).then(function(r){
    if(r.ok&&new URL(e.request.url).origin===location.origin){var cp=r.clone();caches.open(CACHE).then(function(c){c.put(e.request,cp)})}
    return r;
  }).catch(function(){return caches.match(e.request).then(function(m){return m||caches.match('/ufficio/')})}));
});
