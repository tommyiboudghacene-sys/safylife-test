from pathlib import Path
p=Path('public/styles.css')
s=p.read_text()
old='.skip { position: absolute; left: -999px; top: 0; background: var(--surface); padding: .5rem 1rem; }'
new='''/* Keep the skip link accessible without extending the RTL scroll area. */
.skip { position: absolute; left: 0; top: 0; background: var(--surface); padding: .5rem 1rem; }
.skip:not(:focus) { inline-size: 1px; block-size: 1px; padding: 0; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }'''
assert s.count(old)==1, 'Unexpected skip-link stylesheet'
p.write_text(s.replace(old,new,1))
