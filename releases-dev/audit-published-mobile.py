"""Audit the exact published build, not a physical handset; no real calls, SMS or personal data."""
import sys, time, json
from playwright.sync_api import sync_playwright
BASE='https://tommyiboudghacene-sys.github.io/safylife-test/'
BUILD='d4eadb5'
LANGS=['fr','en','es','pt','de','it','ar','zh','hi']
ROUTES=['#/','#/terrain','#/setup','#/guide','#/missions','#/simulations','#/checklist','#/print','#/data','#/drill','#/aventures','#/world-map','#/sos-tools','#/essai']
with sync_playwright() as p:
    engine, profile=sys.argv[1:3]
    browser=getattr(p,engine).launch(headless=True)
    context=browser.new_context(**p.devices[profile],service_workers='allow')
    page=context.new_page()
    page.set_default_timeout(10000)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(BASE+'#/monde',wait_until='load')
    assert BUILD in page.locator('.topbar').inner_text(), 'Unexpected published build'
    deadline=time.monotonic()+35
    while time.monotonic()<deadline:
        if page.evaluate('() => Boolean(navigator.serviceWorker.controller)'):break
        page.wait_for_timeout(200)
    assert page.evaluate('() => Boolean(navigator.serviceWorker.controller)'), 'No service-worker control'
    status=page.evaluate("""async () => await new Promise(resolve => {
      const c=new MessageChannel();
      const t=setTimeout(()=>{c.port1.close();resolve(null)},5000);
      c.port1.onmessage=e=>{clearTimeout(t);c.port1.close();resolve(e.data)};
      navigator.serviceWorker.controller.postMessage({type:'SAFYLIFE_OFFLINE_STATUS'},[c.port2]);
    })""")
    assert status and status.get('build')==BUILD and status.get('ready') is True and status.get('count')==status.get('total'), status
    context.set_offline(True)
    page.reload(wait_until='load')
    def route(r,lang):
        page.evaluate('(r)=>{location.hash=r;window.dispatchEvent(new Event("hashchange"))}',r)
        page.locator('#main h1').wait_for()
        assert page.locator('html').get_attribute('lang')==lang,(r,lang)
        assert page.locator('#main').inner_text().strip(),(r,lang)
    for lang in LANGS:
        page.evaluate('()=>{location.hash="#/monde";window.dispatchEvent(new Event("hashchange"))}')
        selector=page.locator('#rp-world-language,#rp-extra-language')
        selector.wait_for()
        assert selector.locator('option').count()==9
        selector.select_option(lang)
        page.locator('html[lang="'+lang+'"]').wait_for(state='attached')
        route('#/secours',lang)
        links=page.locator('.rp-aid-tile').evaluate_all('(els)=>els.map(e=>e.getAttribute("href"))')
        assert len(links)==7
        for link in links:
            route(link,lang)
            assert page.locator('.rp-aid-steps li').count()>=3
            assert page.locator('.rp-aid-source a').get_attribute('href').startswith('https://')
            assert page.locator('.rp-aid-callout a[href="#/terrain"]').count()==1
            assert page.locator('.rp-aid-disclaimer').count()==1
            assert page.locator('details [lang="fr"]').count()==(0 if lang=='fr' else 1)
        for r in ROUTES: route(r,lang)
        route('#/setup',lang)
        page.locator('input[name="adults"]').fill('2')
        page.locator('input[name="water"]').fill('17')
        page.locator('button[type="submit"]').click()
        page.reload(wait_until='load')
        route('#/setup',lang)
        assert page.locator('input[name="water"]').input_value()=='17'
        route('#/terrain',lang)
        page.evaluate("""()=>Object.defineProperty(navigator,'geolocation',{configurable:true,value:{getCurrentPosition(cb){cb({coords:{latitude:1.23,longitude:4.56,accuracy:15},timestamp:Date.now()})}}})""")
        btn={'fr':'#rp-terrain-locate','en':'#rp-int-locate','es':'#rp-int-locate'}.get(lang,'#rp-extra-gps')
        page.locator(btn).click()
        page.locator('#main').get_by_text('1.23000',exact=False).first.wait_for()
        print(engine,profile,lang,'PASS: 14 routes, 7 first-aid cards, offline data, mock GPS',flush=True)
    assert not errors,errors
    print('MOBILE_AUDIT_PASS',json.dumps({'build':BUILD,'engine':engine,'profile':profile,'languages':9,'routes':126,'first_aid_cards':63,'cache':status,'physical_device':False}),flush=True)
    context.close()
    browser.close()
