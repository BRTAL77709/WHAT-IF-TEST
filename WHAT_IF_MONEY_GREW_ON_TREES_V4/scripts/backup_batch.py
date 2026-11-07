from pathlib import Path
import subprocess,json,hashlib,base64,concurrent.futures,urllib.request,sys
from PIL import Image
from github_io import ROOT as R,BRANCH,request,blobsha,upload
scene=int(sys.argv[1]);a=(scene-1)*240+1;b=min(2340,scene*240);M=R/'reports/render_manifest.json';manifest=json.loads(M.read_text());source=manifest['source_blend_sha256'];assert hashlib.sha256(Path(manifest['source_blend']).read_bytes()).hexdigest()==source
key=str(scene);cached=manifest['completed_scene_archives'].get(key)
if cached and cached.get('public_byte_verified'):
 print('PRESERVED_VERIFIED_SCENE_BACKUP',scene,flush=True);raise SystemExit(0)
rows=[]
for f in range(a,b+1):
 p=R/'renders'/f'frame_{f:04}.png'
 with Image.open(p) as image:image.load();assert image.size==(1080,1920);raw=image.convert('RGB').tobytes()
 row=manifest['frames'][f-1];row['png_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();row['rgb_sha256']=hashlib.sha256(raw).hexdigest()
 if not row['status'].startswith('reused'):row['status']='rendered_verified'
 rows.append({'frame':f,'file':p.name,'png_sha256':row['png_sha256'],'rgb_sha256':row['rgb_sha256']})
M.write_text(json.dumps(manifest,indent=2));(R/'reports/production_checkpoint.json').write_text(json.dumps({'stage':'scene_rendered_archive_pending','scene':scene,'valid_frames':sum(r['status']!='needs_render' for r in manifest['frames']),'next_step':f'Complete source-{source[:12]} scene {scene} backup, then continue missing scenes.'},indent=2))
archive=R/'recovery'/f'V4_{source[:12]}_SCENE_{scene:02d}_NATIVE_LOSSLESS.mkv'
if not archive.exists():
 with open(R/'reports'/f'archive_scene_{scene:02d}.log','w') as log:subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y','-framerate','30','-start_number',str(a),'-i',str(R/'renders/frame_%04d.png'),'-frames:v',str(b-a+1),'-an','-c:v','libx264rgb','-crf','0','-preset','veryfast','-threads','3','-pix_fmt','rgb24',str(archive)],stdout=log,stderr=subprocess.STDOUT,check=True)
p=subprocess.Popen(['ffmpeg','-v','error','-i',str(archive),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
for row in rows:assert hashlib.sha256(p.stdout.read(1080*1920*3)).hexdigest()==row['rgb_sha256'],row['frame']
assert not p.stdout.read(1);assert p.wait()==0
prefix=f'recovery/v4-render-batches/{source[:12]}/scene{scene:02d}';parts=[]
with archive.open('rb') as f:
 i=0
 while block:=f.read(19*1024*1024):
  i+=1;local=R/'recovery'/(archive.name+f'.part{i:03d}');local.write_bytes(block);parts.append({'local':str(local),'path':prefix+'/'+local.name,'sha':blobsha(block),'sha256':hashlib.sha256(block).hexdigest(),'bytes':len(block)})
def stage(row):
 c,j=request('/git/blobs','POST',{'encoding':'base64','content':base64.b64encode(Path(row['local']).read_bytes()).decode()});assert c==201 and j['sha']==row['sha'];return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(stage,parts))
c,ref=request('/git/ref/heads/'+BRANCH);assert c==200;head=ref['object']['sha'];c,commit=request('/git/commits/'+head);assert c==200
entries=[{'path':r['path'],'mode':'100644','type':'blob','sha':r['sha']} for r in parts]
c,t=request('/git/trees','POST',{'base_tree':commit['tree']['sha'],'tree':entries});assert c==201;c,j=request('/git/commits','POST',{'message':f'Persist verified native V4 scene {scene:02d} render checkpoint','tree':t['sha'],'parents':[head]});assert c==201;c,j=request('/git/refs/heads/'+BRANCH,'PATCH',{'sha':j['sha'],'force':False});assert c==200
def verify(row):
 url='https://raw.githubusercontent.com/BRTAL77709/WHAT-IF-TEST/'+BRANCH+'/'+row['path'];h=hashlib.sha256();size=0
 with urllib.request.urlopen(url,timeout=180) as response:
  assert response.status==200
  while block:=response.read(1024*1024):h.update(block);size+=len(block)
 assert size==row['bytes'] and h.hexdigest()==row['sha256'];return {k:v for k,v in {**row,'download_url':url,'byte_match':True}.items() if k!='local'}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:verified=list(pool.map(verify,parts))
index=R/'recovery'/f'SCENE_{scene:02d}_BACKUP_INDEX.json';record={'scene':scene,'source_sha256':source,'frames':[a,b],'archive':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'exact_RGB_pixel_hashes_verified':True,'public_byte_verified':True,'parts':verified,'native_frame_hashes':rows};index.write_text(json.dumps(record,indent=2));upload(index,prefix+'/'+index.name)
manifest=json.loads(M.read_text());manifest['completed_scene_archives'][key]=record;M.write_text(json.dumps(manifest,indent=2));(R/'reports/production_checkpoint.json').write_text(json.dumps({'stage':'scene_rendered_and_durably_backed_up','scene':scene,'source_sha256':source,'valid_frames':sum(r['status']!='needs_render' for r in manifest['frames']),'completed_scenes':sorted(map(int,manifest['completed_scene_archives'])),'next_step':'Resume only scenes missing from completed_scene_archives; retain every verified frame.'},indent=2));print('V4_SCENE_BACKUP_VERIFIED',scene,len(parts),archive.stat().st_size,flush=True)
