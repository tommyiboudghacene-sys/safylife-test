from pathlib import Path

def change(path, old, new):
    p=Path(path); s=p.read_text()
    assert s.count(old)==1, (path, old)
    p.write_text(s.replace(old,new,1))

change('public/sw.js','.then(cache => cache.addAll(ASSETS))',
       '.then(cache => cache.addAll(ASSETS.map(asset => new Request(new URL(asset, self.registration.scope).href, { cache: "reload" }))))')
change('public/sw.js','ready: count === ASSETS.length, count, total: ASSETS.length',
       'build: BUILD, ready: count === ASSETS.length, count, total: ASSETS.length')
change('scripts/test-service-worker.mjs','for (const url of urls) values.set(new URL(url, scope).href, new Response(\'cached:\' + url));',
       '''for (const request of urls) {
          assert.equal(request.cache, 'reload', 'updated offline resources must bypass stale HTTP cache');
          values.set(request.url, new Response('cached:' + request.url));
        }''')
change('scripts/test-service-worker.mjs','  URL, Response,','  URL, Response, Request,')
change('scripts/test-service-worker.mjs','assert.equal(message.ready, true);','assert.equal(message.ready, true);\nassert.ok(message.build, "Worker identifies the installed build");')
change('src/app/fr-main.ts','navigator.serviceWorker.register("sw.js")','navigator.serviceWorker.register("sw.js", { updateViaCache: "none" })')
change('src/app/fr-main.ts','window.addEventListener("online", () => { void registration.update().catch(() => {}); verifyOfflineCache(registration); });',
       '''window.addEventListener("online", () => { void registration.update().catch(() => {}); verifyOfflineCache(registration); });
        document.addEventListener("visibilitychange", () => {
          if (document.visibilityState === "visible" && navigator.onLine) void registration.update().catch(() => {});
        });''')
Path('public/mise-a-jour.html').write_text('''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; worker-src 'self'; object-src 'none'; base-uri 'none'"><title>SAFYLIFE — Mise à jour</title><style>body{font:18px/1.5 system-ui,sans-serif;background:#f5f7f4;color:#173e3d;max-width:38rem;margin:3rem auto;padding:1.25rem}button,a{display:inline-block;padding:.8rem 1.2rem;border:0;border-radius:.8rem;background:#236d69;color:white;font:inherit;text-decoration:none}button:disabled{opacity:.5}small{display:block;color:#526b68}</style></head><body><h1>SAFYLIFE</h1><h2>Mise à jour de l’application</h2><p id="status" role="status" aria-live="polite">Recherche de la dernière version…</p><p>Vos réserves, préférences et informations familiales ne sont pas effacées.</p><button id="retry" type="button" disabled>Réessayer</button><p><a href="./#/monde">Retour à SAFYLIFE</a></p><small>Une connexion Internet est nécessaire pour cette opération.</small><script src="mise-a-jour.js" defer></script></body></html>''')
Path('public/mise-a-jour.js').write_text('''"use strict";
const statusNode = document.getElementById("status");
const retry = document.getElementById("retry");
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
function ask(worker) {
  if (!worker) return Promise.resolve(null);
  return new Promise(resolve => {
    const channel = new MessageChannel();
    const finish = value => { clearTimeout(timer); channel.port1.close(); resolve(value); };
    const timer = setTimeout(() => finish(null), 1200);
    channel.port1.onmessage = event => finish(event.data);
    try { worker.postMessage({type:"SAFYLIFE_OFFLINE_STATUS"}, [channel.port2]); } catch { finish(null); }
  });
}
async function update() {
  retry.disabled = true;
  statusNode.textContent = "Recherche de la dernière version…";
  try {
    if (!navigator.onLine || !("serviceWorker" in navigator)) throw Error("Connexion Internet ou navigateur compatible nécessaire.");
    const response = await fetch("build-info.json?check=" + Date.now(), {cache:"no-store"});
    if (!response.ok) throw Error("La nouvelle version n’est pas accessible.");
    const info = await response.json();
    if (!/^[a-f0-9]{7}$/.test(info.build)) throw Error("Version non identifiable.");
    const reg = await navigator.serviceWorker.register("sw.js?build=" + encodeURIComponent(info.build), {scope:"./", updateViaCache:"none"});
    statusNode.textContent = "Installation de la version " + info.build + " et vérification du cache…";
    const deadline = Date.now() + 45000;
    while (Date.now() < deadline) {
      const worker = navigator.serviceWorker.controller;
      const data = await ask(worker);
      if (data && data.type === "SAFYLIFE_OFFLINE_STATUS" && data.build === info.build && data.ready === true && data.count === data.total) {
        statusNode.textContent = "Mise à jour terminée : " + info.build;
        location.replace("./#/monde");
        return;
      }
      await pause(500);
    }
    throw Error("La nouvelle version n’a pas encore été activée.");
  } catch (error) {
    statusNode.textContent = error.message + " Réessayez avec Internet. Vos données sont conservées.";
    retry.disabled = false;
  }
}
retry.addEventListener("click", update);
void update();
''')
