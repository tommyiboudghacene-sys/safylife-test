from pathlib import Path
p=Path('scripts/smoke-sos-i18n.py')
s=p.read_text()
a=s.index('            # French-only notice')
b=s.index('            pg.evaluate(\'location.hash="#/"',a)
s=s[:a]+'''            # First-aid cards are now translated; check SOS, locale, source and French original.
            pg.evaluate('location.hash="#/secours";window.dispatchEvent(new Event("hashchange"))')
            pg.wait_for_selector('.rp-aid-tile')
            check(pg.locator('.rp-fr-only').count() == 0, f'{lang}: obsolete French-only notice')
            check(pg.locator('.rp-aid-tile').count() == 7, f'{lang}: missing aid cards')
            check(pg.locator('.rp-aid-callout a[href="#/terrain"]').count() == 1, f'{lang}: missing SOS link')
            check(pg.locator('html').get_attribute('lang') == lang, f'{lang}: document language incorrect')
            pg.locator('.rp-aid-tile').first.click()
            pg.wait_for_selector('.rp-aid-steps')
            expected = {'fr':'Ne respire pas normalement','en':'Not breathing normally','es':'No respira normalmente'}[lang]
            check(pg.locator('#main h1').inner_text() == expected, f'{lang}: wrong cardiac arrest translation')
            check(pg.locator('.rp-aid-steps li').count() == 5, f'{lang}: missing instructions')
            check(pg.locator('.rp-aid-source a').get_attribute('href').startswith('https://www.croix-rouge.fr/'), f'{lang}: missing source')
            check(pg.locator('.rp-aid-disclaimer').inner_text().strip() != '', f'{lang}: missing disclaimer')
            if lang != 'fr':
                check(pg.locator('details [lang="fr"]').count() == 1, f'{lang}: missing French original')
            pg.screenshot(path=f'{SHOTS}/secours_{lang}.png')
'''+s[b:]
p.write_text(s.replace('French-only notice with SOS link + lang=fr','translated first-aid cards, original, SOS link and sources'))
p=Path('scripts/test-family-i18n-dom.py');s=p.read_text()
old="   if lang!='fr': assert pg.locator('#main').get_attribute('lang')=='fr'"
assert s.count(old)==1
p.write_text(s.replace(old,"   assert pg.locator('html').get_attribute('lang')==lang\n   assert pg.locator('.rp-aid-tile').count()==7\n   assert pg.locator('.rp-fr-only').count()==0"))
