"""Collect publicly available official travel-advice emergency sections for manual review.
Never automatically enable an emergency number. No credentials, calls, or location data."""
import concurrent.futures as cf, urllib.request, re, json, html, datetime
from html.parser import HTMLParser
ROWS="AF afghanistan\nDZ algeria\nAO angola\nAI anguilla\nAQ -\nAG antigua-and-barbuda\nSA saudi-arabia\nAM armenia\nAW aruba\nBS bahamas\nBB barbados\nBZ belize\nBJ benin\nBM bermuda\nBT bhutan\nBY belarus\nBW botswana\nBN brunei\nBF burkina-faso\nBI burundi\nKH cambodia\nCM cameroon\nCV cape-verde\nKM comoros\nCG congo\nCD democratic-republic-of-the-congo\nKP north-korea\nCI cote-d-ivoire\nCU cuba\nCW curacao\nDJ djibouti\nDM dominica\nER eritrea\nSZ eswatini\nVA vatican-city\nET ethiopia\nFJ fiji\nGA gabon\nGM the-gambia\nGS south-georgia-and-south-sandwich-islands\nGD grenada\nGL greenland\nGU guam\nGT guatemala\nGG guernsey\nGN guinea\nGQ equatorial-guinea\nGW guinea-bissau\nGY guyana\nHT haiti\nHN honduras\nIM isle-of-man\nNF norfolk-island\nAX aland-islands\nKY cayman-islands\nCK cook-islands\nFO faroe-islands\nHM -\nFK falkland-islands\nMP northern-mariana-islands\nMH marshall-islands\nPN pitcairn-island\nSB solomon-islands\nTC turks-and-caicos-islands\nVG british-virgin-islands\nVI us-virgin-islands\nIQ iraq\nIR iran\nIL israel\nJM jamaica\nJE jersey\nKZ kazakhstan\nKG kyrgyzstan\nKI kiribati\nKW kuwait\nLA laos\nLS lesotho\nLB lebanon\nLR liberia\nLY libya\nLI liechtenstein\nMG madagascar\nMW malawi\nMV maldives\nML mali\nMU mauritius\nMR mauritania\nFM micronesia\nMC monaco\nMN mongolia\nME montenegro\nMS montserrat\nMZ mozambique\nMM myanmar\nNA namibia\nNR nauru\nNP nepal\nNI nicaragua\nNE niger\nNG nigeria\nNU niue\nNC new-caledonia\nUG uganda\nUZ uzbekistan\nPW palau\nPA panama\nPG papua-new-guinea\nPF french-polynesia\nPR puerto-rico\nMO macao\nCF central-african-republic\nDO dominican-republic\nRU russia\nRW rwanda\nEH western-sahara\nBL st-barthelemy\nKN st-kitts-and-nevis\nMF st-martin-and-st-barthelemy\nSX st-maarten\nPM st-pierre-and-miquelon\nVC st-vincent-and-the-grenadines\nSH st-helena-ascension-and-tristan-da-cunha\nLC st-lucia\nSV el-salvador\nWS samoa\nAS american-samoa\nST sao-tome-and-principe\nSN senegal\nSC seychelles\nSL sierra-leone\nSO somalia\nSD sudan\nSS south-sudan\nSR suriname\nSY syria\nTJ tajikistan\nTZ tanzania\nTD chad\nTF -\nIO british-indian-ocean-territory\nPS palestine\nTL timor-leste\nTG togo\nTO tonga\nTT trinidad-and-tobago\nTN tunisia\nTM turkmenistan\nTV tuvalu\nUA ukraine\nVU vanuatu\nVE venezuela\nWF wallis-and-futuna\nYE yemen\nZM zambia\nZW zimbabwe".splitlines()
class Extract(HTMLParser):
    def __init__(self):
        super().__init__(); self.active=False; self.done=False; self.head=False; self.ht=''; self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('h2','h3'):
            self.head=True; self.ht=''
        if self.active and tag in ('p','li','br','div','h3'): self.parts.append(' | ')
    def handle_endtag(self,tag):
        if tag in ('h2','h3') and self.head:
            self.head=False; heading=self.ht.strip().lower()
            if self.active: self.active=False; self.done=True
            if not self.done and ('emergency services' in heading or 'local emergency' in heading or 'emergency medical number' in heading):
                self.active=True
    def handle_data(self,data):
        if self.head: self.ht+=data
        elif self.active: self.parts.append(data)
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'SAFYLIFE-source-review/1.0 (public emergency directory audit)'})
    with urllib.request.urlopen(req,timeout=18) as r:
        if not r.geturl().startswith(('https://www.gov.uk/','https://travel.gc.ca/')): raise ValueError('unexpected redirect')
        parser=Extract(); parser.feed(r.read(4_000_000).decode('utf-8','replace'))
        return re.sub(r'\s+',' ',''.join(parser.parts)).strip(' |')[:1200],r.geturl()
def get(row):
    code,slug=row.split()
    if slug=='-': return {'code':code,'status':'manual-territorial-review'}
    result={'code':code}
    for name,url in [('uk',f'https://www.gov.uk/foreign-travel-advice/{slug}/getting-help'),('ca',f'https://travel.gc.ca/destinations/{slug}')]:
        try:
            snippet,final=fetch(url);result[name]={'url':final,'section':snippet or None}
        except Exception as e: result[name]={'url':url,'error':str(e)[:120]}
    return result
assert len(ROWS)==155 and len({r.split()[0] for r in ROWS})==155
with cf.ThreadPoolExecutor(max_workers=8) as pool:
    results=list(pool.map(get,ROWS))
for r in results: print('SOURCE_REVIEW '+json.dumps(r,ensure_ascii=True),flush=True)
with open('emergency-source-review.json','w') as f: json.dump({'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':results},f,indent=2)
print('Reviewed retrieval attempts:',len(results),'UK sections:',sum(bool(r.get('uk',{}).get('section')) for r in results),'Canada sections:',sum(bool(r.get('ca',{}).get('section')) for r in results))
