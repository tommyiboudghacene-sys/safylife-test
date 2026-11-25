"""Exercise an existing installation upgrading to a new build without deleting localStorage."""
import functools,http.server,threading,zipfile,tempfile,os,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright
new=Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory() as tmp:
    old=Path(tmp)
    with zipfile.ZipFile(sys.argv[2]) as archive: archive.extractall(old)
    state={'root':old}
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self,*args,**kw): super().__init__(*args,directory=str(state['root']),**kw)
        def log_message(self,*args): pass
        def send_head(self):
            # Simulate a new deployment, never send 304 for an older fixture's timestamp.
            for header in ('If-Modified-Since','If-None-Match'):
                if header in self.headers: del self.headers[header]
            return super().send_head()
        def end_headers(self):
            self.send_header('Cache-Control','no-store')
            super().end_headers()
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url='http://127.0.0.1:'+str(server.server_port)+'/'
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
            context=browser.new_context(service_workers='allow')
            page=context.new_page()
            page.goto(url+'#/monde',wait_until='load')
            deadline=time.monotonic()+30
            while time.monotonic()<deadline:
                if page.evaluate("() => Boolean(navigator.serviceWorker.controller)"): break
                page.wait_for_timeout(150)
            assert page.evaluate("() => Boolean(navigator.serviceWorker.controller)"), "Original PWA not controlled"
            page.locator('#rp-world-language').wait_for()
            assert page.locator('#rp-world-language option').count()==3
            page.evaluate("localStorage.setItem('safylife-upgrade-regression','preserved')")
            state['root']=new
            page.on('pageerror',lambda err: print('PAGE ERROR',err,flush=True))
            page.on('console',lambda msg: print('CONSOLE',msg.type,msg.text,flush=True) if msg.type=='error' else None)
            response=page.goto(url+'mise-a-jour.html',wait_until='load')
            assert response and response.ok, 'update page not served'
            try:
                page.wait_for_url(url+'#/monde',timeout=60000)
            except Exception:
                print('UPDATE DIAGNOSTICS',page.url,page.locator('body').inner_text(),flush=True)
                print(page.evaluate("""async () => ({controller:navigator.serviceWorker.controller?.scriptURL, registrations:(await navigator.serviceWorker.getRegistrations()).map(r=>({scope:r.scope,active:r.active?.scriptURL,installing:r.installing?.scriptURL,waiting:r.waiting?.scriptURL})),cacheKeys:await caches.keys()})"""),flush=True)
                raise
            page.locator('#rp-world-language').wait_for()
            assert page.locator('#rp-world-language option').count()==9
            assert page.locator('.brand .prototype').count()==0
            assert page.evaluate("localStorage.getItem('safylife-upgrade-regression')")=='preserved'
            context.set_offline(True)
            page.reload(wait_until='load')
            page.locator('#rp-world-language').wait_for()
            assert page.locator('#rp-world-language option').count()==9
            print('PASS: old 3-language installation upgraded to 9, no prototype, storage preserved, offline reload')
            browser.close()
    finally: server.shutdown()
