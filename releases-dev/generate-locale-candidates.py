"""Generate review candidates for UI/game localization on a free public-repo runner.
Only fixed English application strings; no user data and no medical card content.
"""
import sys, json, pathlib, tempfile, urllib.request, zipfile, hashlib, re, collections
import ctranslate2
import sentencepiece as sp
LANG=sys.argv[1]
VERSIONS={"pt":"1_9","de":"1_3","it":"1_0","ar":"1_0","zh":"1_9","hi":"1_1"}
keys=json.loads(pathlib.Path("releases-dev/remaining-catalog.json").read_text())
assert len(keys)==525 and len(set(keys))==525
url=f"https://argos-net.com/v1/translate-en_{LANG}-{VERSIONS[LANG]}.argosmodel"
with tempfile.TemporaryDirectory() as temp:
 p=pathlib.Path(temp)
 urllib.request.urlretrieve(url,p/"model.zip")
 digest=hashlib.sha256((p/"model.zip").read_bytes()).hexdigest()
 with zipfile.ZipFile(p/"model.zip") as z:
  for name in z.namelist():
   assert not pathlib.PurePosixPath(name).is_absolute() and ".." not in pathlib.PurePosixPath(name).parts
  z.extractall(p/"model")
 folder=next((p/"model").rglob("metadata.json")).parent
 meta=json.loads((folder/"metadata.json").read_text())
 assert meta["from_code"]=="en" and meta["to_code"]==LANG
 spm=sp.SentencePieceProcessor(model_file=str(folder/"sentencepiece.model"))
 translator=ctranslate2.Translator(str(folder/"model"),device="cpu",compute_type="int8",intra_threads=2)
 pref=meta.get("target_prefix","")
 out={}; warnings=[]
 for i in range(0,len(keys),24):
  batch=keys[i:i+24]
  tokens=[spm.encode(x.strip(),out_type=str) for x in batch]
  results=translator.translate_batch(tokens,target_prefix=[[pref]]*len(batch) if pref else None,beam_size=3,replace_unknowns=True,max_decoding_length=256)
  for key,r in zip(batch,results):
   value=spm.decode(r.hypotheses[0]).strip()
   if pref and value.startswith(pref):value=value[len(pref):].strip()
   # Whitespace for UI fragments is semantic, and placeholders/numbers must not change.
   value=key[:len(key)-len(key.lstrip())]+value+key[len(key.rstrip()):]
   if not value.strip() or collections.Counter(re.findall(r'\{\d+\}',key))!=collections.Counter(re.findall(r'\{\d+\}',value)):
    warnings.append(key);value=key
   out[key]=value
  print("progress",LANG,i+len(batch),flush=True)
 report={"language":LANG,"model":url,"sha256":digest,"translations":out,"needs_review":warnings}
 pathlib.Path(f"locale-{LANG}.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
 print("LOCALE_RESULT "+json.dumps(report,ensure_ascii=True,separators=(",",":")),flush=True)
