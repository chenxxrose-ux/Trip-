// 旅遊清單離線快取：網頁本身先用快取，有網路時背景更新；外部資料有網路就抓新的，沒網路用上次的。
const CACHE='trip-v9.3';
const CORE=['./','./index.html','./manifest.json','./icon-180.png','./icon-192.png','./icon-512.png'];
// 逐一快取：網頁本身必須成功，圖示等其他檔案失敗不影響安裝
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(async c=>{
  await c.addAll(['./','./index.html']);
  await Promise.allSettled(CORE.filter(u=>u!=='./'&&u!=='./index.html').map(u=>c.add(u)));
}).then(()=>self.skipWaiting()))});
const cleanOld=()=>caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k))));
self.addEventListener('activate',e=>{e.waitUntil(cleanOld().then(()=>self.clients.claim()))});
// 只從這一版的快取讀，避免讀到舊版網頁
const fromOwn=req=>caches.open(CACHE).then(c=>c.match(req));
self.addEventListener('fetch',e=>{
  const req=e.request;if(req.method!=='GET')return;
  const url=new URL(req.url);
  if(url.origin===location.origin){
    // 網頁：有網路拿最新版並更新快取，沒網路用快取
    e.respondWith(fetch(req).then(r=>{const cp=r.clone();caches.open(CACHE).then(c=>c.put(req,cp));return r})
      .catch(()=>fromOwn(req).then(r=>r||fromOwn('./index.html'))));
    if(req.mode==='navigate')e.waitUntil(cleanOld());
    return;
  }
  // 匯率、天氣、旅遊評級：先試網路，失敗用上次的回應
  e.respondWith(fetch(req).then(r=>{if(r.ok){const cp=r.clone();caches.open(CACHE).then(c=>c.put(req,cp))}return r}).catch(()=>fromOwn(req)));
});
