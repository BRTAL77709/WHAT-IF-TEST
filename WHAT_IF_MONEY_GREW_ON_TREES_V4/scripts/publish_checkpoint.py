from pathlib import Path
import json,hashlib,zipfile,sys,base64
from github_io import ROOT as R,BRANCH,ensure_branch,request,blobsha,upload
ensure_branch();files=[*R.glob('*.md'),*R.glob('scripts/*.py'),*R.glob('reports/*.json'),*R.glob('reports/*.csv'),*R.glob('reports/*.md')];files=[p for p in files if p.is_file()]
c,ref=request('/git/ref/heads/'+BRANCH);assert c==200;head=ref['object']['sha'];c,commit=request('/git/commits/'+head);assert c==200;c,tree=request('/git/trees/'+commit['tree']['sha']+'?recursive=1');assert c==200 and not tree.get('truncated');known={x['path']:x['sha'] for x in tree['tree'] if x['type']=='blob'};entries=[]
for p in files:
 relative=str(p.relative_to(R.parent));data=p.read_bytes()
 if known.get(relative)!=blobsha(data):entries.append({'path':relative,'mode':'100644','type':'blob','content':data.decode()})
if entries:
 c,t=request('/git/trees','POST',{'base_tree':commit['tree']['sha'],'tree':entries});assert c==201;c,j=request('/git/commits','POST',{'message':'Checkpoint V4 timeline audit and source repairs; preserve V1-V3','tree':t['sha'],'parents':[head]});assert c==201;head=j['sha'];c,j=request('/git/refs/heads/'+BRANCH,'PATCH',{'sha':head,'force':False});assert c==200
if '--blend' in sys.argv:
 validation=json.loads((R/'reports/scene_validation.json').read_text());assert validation['status']=='TECHNICAL PASS';assert validation['source_blend_sha256']==hashlib.sha256((R/'blender/WHAT_IF_MONEY_GREW_ON_TREES_V4.blend').read_bytes()).hexdigest()
 archive=R/'recovery/V4_VALIDATED_SOURCE.zip';paths=[*R.glob('*.md'),*R.glob('scripts/*.py'),*R.glob('blender/*.blend'),*R.glob('subtitles/*'),*R.glob('audio/*'),*R.glob('reports/*')]
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in paths:
   if p.is_file() and p.suffix!='.log':z.write(p,arcname=str(Path(R.name)/p.relative_to(R)))
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None
 records=[]
 with archive.open('rb') as f:
  i=0
  while block:=f.read(19*1024*1024):
   i+=1;part=R/'recovery'/(archive.name+f'.part{i:03d}');part.write_bytes(block);records.append(upload(part,'recovery/v4-validated-source/'+part.name))
 index=R/'recovery/SOURCE_BACKUP_INDEX.json';index.write_text(json.dumps({'file':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'parts':records},indent=2));upload(index,'recovery/v4-validated-source/'+index.name)
(R/'reports/github_source_checkpoint.json').write_text(json.dumps({'branch':BRANCH,'commit':head,'source_files':len(files),'validated_blend_backup_verified':'--blend' in sys.argv},indent=2));print('V4_SOURCE_CHECKPOINT_SAVED',head,flush=True)
