"""Retrieve the original full-quality V3 MP4; Python standard library only."""
from pathlib import Path
import urllib.request,json,hashlib,sys
url='https://raw.githubusercontent.com/BRTAL77709/WHAT-IF-TEST/what-if-v3-motion-repair/recovery/v3-restored-checkpoint/FRAME_BACKUP_INDEX.json'
with urllib.request.urlopen(url,timeout=60) as r:index=json.load(r)
item=next(x for x in index['files'] if x['file']=='WHAT_IF_MONEY_GREW_ON_TREES_V3.mp4');D=Path(sys.argv[1] if len(sys.argv)>1 else 'V3_FULL_QUALITY_DOWNLOAD');D.mkdir(parents=True,exist_ok=True);out=D/item['file']
if out.exists():
 assert hashlib.sha256(out.read_bytes()).hexdigest()==item['sha256'],'A different output file already exists'
 print('Already verified:',out);raise SystemExit(0)
tmp=out.with_suffix('.mp4.download');whole=hashlib.sha256()
with tmp.open('wb') as f:
 for part in item['parts']:
  with urllib.request.urlopen(part['download_url'],timeout=180) as r:data=r.read()
  assert len(data)==part['bytes'] and hashlib.sha256(data).hexdigest()==part['sha256'];whole.update(data);f.write(data);print('Verified',Path(part['path']).name,flush=True)
assert tmp.stat().st_size==item['bytes'] and whole.hexdigest()==item['sha256'];tmp.replace(out);print('Full-quality native master verified:',out)
