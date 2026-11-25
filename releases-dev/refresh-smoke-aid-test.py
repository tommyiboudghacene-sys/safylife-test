from pathlib import Path
p=Path('scripts/smoke-sos-i18n.py')
s=p.read_text()
a=s.index('            # French-only notice')
b=s.index('            pg.evaluate(\'location.hash="#/"',a)
s=s[:a]+'''            # Translated first aid: keep the original safety assertions, check all 7 cards.
            pg.evaluate('location.hash="#/secours";window.dispatchEvent(new Event("hashchange"))')
            pg.wait_for_selector('.rp-aid-tile')
            check(pg.locator('.rp-fr-only').count() == 0, f'{lang}: obsolete French-only notice')
            check(pg.locator('.rp-aid-tile').count() == 7, f'{lang}: missing first aid cards')
            check(pg.locator('html').get_attribute('lang') == lang, f'{lang}: incorrect document language')
            check(pg.locator('.rp-aid-callout a[href="#/terrain"]').count() == 1, f'{lang}: missing SOS link')
            check(bool(pg.locator('.rp-aid-disclaimer').inner_text().strip()), f'{lang}: missing safety disclaimer')
            expected = {'fr':'Ne respire pas normalement','en':'Not breathing normally','es':'No respira normalmente'}
            pg.locator('.rp-aid-tile[href="#/secours/arret-cardiaque"]').click()
            pg.wait_for_selector('.rp-aid-steps')
            check(pg.locator('#main h1').inner_text()==expected[lang], f'{lang}: CPR translation absent')
            check(pg.locator('.rp-aid-steps li').count()==5, f'{lang}: missing CPR steps')
            check(pg.locator('.rp-aid-source a').get_attribute('href')=='https://www.croix-rouge.fr/les-gestes-de-premiers-secours/arret-cardiaque', f'{lang}: missing source')
            check(pg.locator('details [lang="fr"]').count()==(0 if lang=='fr' else 1), f'{lang}: French reference missing or duplicated')
            pg.screenshot(path=f'{SHOTS}/secours_{lang}.png')
'''+s[b:]
s=s.replace('French-only notice with SOS link + lang=fr','localized first aid with SOS link, source and French reference')
p.write_text(s)

p=Path('scripts/test-family-i18n-dom.py')
s=p.read_text()
old="   if lang!='fr': assert pg.locator('#main').get_attribute('lang')=='fr'"
assert s.count(old)==1
s=s.replace(old,'''   assert pg.locator('html').get_attribute('lang')==lang
   assert pg.locator('.rp-fr-only').count()==0
   assert pg.locator('.rp-aid-tile').count()==7
   assert pg.locator('.rp-aid-disclaimer').count()==1''')
p.write_text(s)
