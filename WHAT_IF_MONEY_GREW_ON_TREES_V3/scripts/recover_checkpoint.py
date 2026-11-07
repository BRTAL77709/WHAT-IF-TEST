"""Download and restore the public, checksum-verified V3 recovery archives."""
from pathlib import Path
import json,urllib.request,hashlib,sys,concurrent.futures,zipfile
BASE='https://raw.githubusercontent.com/BRTAL77709/WHAT-IF-TEST/what-if-v3-motion-repair/recovery/v3-restored-checkpoint/'
D=Path(sys.argv[1] if len(sys.argv)>1 else 'V3_RECOVERY_DOWNLOAD').resolve();D.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
def get(part):
 p=D/Path(part['path']).name
 if p.exists() and sha(p)==part['sha256']:return p
 tmp=p.with_suffix(p.suffix+'.download')
 with urllib.request.urlopen(part['download_url'],timeout=180) as r,tmp.open('wb') as f:
  while b:=r.read(1024*1024):f.write(b)
 assert sha(tmp)==part['sha256'],p.name;tmp.replace(p);print('Verified',p.name,flush=True);return p
for name in ['SOURCE_BACKUP_INDEX.json','FRAME_BACKUP_INDEX.json']:
 with urllib.request.urlopen(BASE+name,timeout=60) as r:index=json.load(r)
 (D/name).write_text(json.dumps(index,indent=2))
 for item in index['files']:
  assert Path(item['file']).name==item['file'];out=D/item['file']
  if out.exists() and sha(out)==item['sha256']:continue
  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:parts=list(pool.map(get,item['parts']))
  with out.open('wb') as f:
   for p in parts:
    with p.open('rb') as source:
     while b:=source.read(1024*1024):f.write(b)
  assert sha(out)==item['sha256'];print('RESTORED',out,flush=True)
  if out.suffix=='.zip':
   with zipfile.ZipFile(out) as z:
    for p in z.namelist():assert (D/p).resolve().is_relative_to(D),'Unsafe archive member'
    z.extractall(D)
print('Recovered source, editable blend, master and lossless frame archive. Use restore_frames.py for PNG pixels. No rendering is required.')
