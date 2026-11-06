from pathlib import Path
import zipfile,json,hashlib
R=Path(__file__).resolve().parents[1]
assert (R/'reports'/'quality_control.json').exists(), 'Validate the final file before packaging.'
archive=R/'final'/'WHAT_IF_MONEY_GREW_ON_TREES_PRODUCTION.zip'
files=[]
for folder in ['blender','scripts','assets','audio','scenes','reports','final']:
 for p in (R/folder).rglob('*'):
  if not p.is_file() or p.suffix in ['.zip','.blend1','.pyc'] or '__pycache__' in p.parts: continue
  if p.name in ['assembled_picture.mp4']: continue
  files.append(p)
files.append(R/'README.md')
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for p in sorted(files): z.write(p,arcname=str(Path(R.name)/p.relative_to(R)))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
manifest={'archive':archive.name,'bytes':archive.stat().st_size,'files':len(files),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'omitted':'Raw PNG frame sequence and local caches; all ten scene movie renders are included.'}
(R/'reports'/'delivery_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
