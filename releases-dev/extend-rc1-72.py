import json
from pathlib import Path
rows=json.loads("[[\"GH\",\"ghana\",\"112\",\"all\",[]],[\"HK\",\"hong-kong\",\"999\",\"all\",[]],[\"CR\",\"costa-rica\",\"911\",\"all\",[]],[\"JO\",\"jordan\",\"911\",\"all\",[]],[\"TW\",\"taiwan\",\"119\",\"fire-medical\",[[\"110\",\"police\"]]],[\"LK\",\"sri-lanka\",\"1990\",\"ambulance\",[[\"119\",\"police\"],[\"111\",\"fire\"]]],[\"RS\",\"serbia\",\"112\",\"all\",[[\"192\",\"police\"],[\"193\",\"fire\"]]]]")
p=Path('src/app/fr-world.ts')
s=p.read_text()
def source(slug):
    return f'source: "GOV.UK — {slug} (checked 2026-11-24)", url: "https://www.gov.uk/foreign-travel-advice/{slug}/getting-help"'
for code,slug,num,kind,extras in rows:
    assert f'  {code}: {{ number:' not in s, code
primary=''.join(f'  {code}: {{ number: "{num}", kind: "{kind}", {source(slug)} }},\n' for code,slug,num,kind,extras in rows)
extra=''.join('  '+code+': ['+', '.join(f'{{ number: "{n}", type: "{t}", {source(slug)} }}' for n,t in extras)+'],\n' for code,slug,num,kind,extras in rows if extras)
a='const VERIFIED: Record<string, VerifiedNumber> = {\n'
b='const ADDITIONAL: Record<string, AdditionalEmergencyNumber[]> = {\n'
assert s.count(a)==s.count(b)==1
p.write_text(s.replace(a,a+primary,1).replace(b,b+extra,1))
p=Path('tests/world.test.ts')
s=p.read_text()
s+='\n// Official FCDO emergency numbers checked 2026-11-24.\ntest("seven additional country entries preserve agency boundaries", () => {\n  const expected = {\n'+''.join(f'    {code}: ["{num}", "{kind}", '+json.dumps(extras)+'],\n' for code,slug,num,kind,extras in rows)+'  } as const;\n  for (const [code, [number, kind, extras]] of Object.entries(expected)) {\n    assert.equal(emergencyFor(code)?.number, number, code);\n    assert.equal(emergencyFor(code)?.kind, kind, code);\n    assert.match(emergencyFor(code)?.url ?? "", /^https:\\/\\/www\\.gov\\.uk\\/foreign-travel-advice\\/[a-z-]+\\/getting-help$/);\n    assert.deepEqual(additionalEmergencyNumbersFor(code).map(x => [x.number, x.type]), extras);\n  }\n});\n'
p.write_text(s)
