from pathlib import Path
import hashlib,json,concurrent.futures,zipfile,time
from PIL import Image
R=Path(__file__).resolve().parents[1]; B=R/'recovery'; B.mkdir(exist_ok=True); files=sorted((R/'renders').glob('frame_*.png')); assert len(files)==2340
provenance=json.loads((R/'reports/render_provenance.json').read_text()); blend=R/'blender/WHAT_IF_MONEY_GREW_ON_TREES_V3.blend'; assert hashlib.sha256(blend.read_bytes()).hexdigest()==provenance['final_scene_sha256']==(R/'renders/source_sha256.txt').read_text()
def check(p):
 pngsha=hashlib.sha256(p.read_bytes()).hexdigest()
 with Image.open(p) as im:
  im.load(); assert im.size==(1080,1920); assert im.mode in ['RGB','RGBA']
  if im.mode=='RGBA': assert im.getchannel('A').getextrema()==(255,255)
  raw=im.convert('RGB').tobytes(); return {'file':p.name,'bytes':p.stat().st_size,'png_sha256':pngsha,'rgb_sha256':hashlib.sha256(raw).hexdigest(),'width':1080,'height':1920,'alpha':'opaque'}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 rows=list(pool.map(check,files))
manifest={'verified_frames':len(rows),'invalid_frames':[],'missing_frames':[],'final_scene_sha256':provenance['final_scene_sha256'],'camera_frames_replaced':provenance['selectively_replaced_frames'],'frames':rows,'frame_archive_format':'Lossless H.264 RGB (libx264rgb CRF 0); opaque alpha is restored as 255. Restored RGB pixels must match every rgb_sha256. PNG compression byte layout may differ.'}
(R/'reports/recovery_checkpoint.json').write_text(json.dumps(manifest,indent=2))
# Snapshot every existing production source/script/report/checkpoint, plus approved source audio/subtitles.
for label,paths in [('SOURCE',[*R.glob('*.md'),*R.glob('*.json'),*R.glob('*.txt'),*R.glob('*.gitignore'),*R.glob('scripts/*.py'),*R.glob('subtitles/*'),*R.glob('audio/*'),*R.glob('reports/*'),*R.glob('renders/*sha256.txt')]),('BLENDER',[blend])]:
 target=B/f'V3_RECOVERY_{label}.zip'
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in paths:
   if p.is_file(): z.write(p,arcname=str(Path(R.name)/p.relative_to(R)))
 with zipfile.ZipFile(target) as z: assert z.testzip() is None
 print('SNAPSHOT',target.name,target.stat().st_size,flush=True)
print('ALL_FRAMES_VERIFIED',len(rows),sum(x['bytes'] for x in rows),flush=True)
