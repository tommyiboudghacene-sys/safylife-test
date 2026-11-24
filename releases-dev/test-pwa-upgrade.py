"""Exercise an existing installation upgrading to a new build without deleting localStorage."""
import functools,http.server,threading,zipfile,tempfile,os,sys
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
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url='http://127.0.0.1:'+str(server.server_port)+'/'
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
            context=browser.new_context(service_workers='allow')
            page=context.new_page()
            page.goto(url+'#/monde',wait_until='load')
            page.wait_for_function('navigator.serviceWorker.controller !== null',timeout=30000)
            page.locator('#rp-world-language').wait_for()
            assert page.locator('#rp-world-language option').count()==3
            page.evaluate("localStorage.setItem('safylife-upgrade-regression','preserved')")
            state['root']=new
            page.goto(url+'mise-a-jour.html',wait_until='load')
            page.wait_for_url(url+'#/monde',timeout=60000)
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
