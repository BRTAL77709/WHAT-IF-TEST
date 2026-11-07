from pathlib import Path
import json,hashlib
from github_io import ROOT as R,request,BRANCH,blobsha
assert json.loads((R/'reports/github_checkpoint.json').read_text())['frames_backup_verified']
files=[*R.glob('*.md'),*R.glob('scripts/*.py'),*R.glob('subtitles/*'),*R.glob('reports/*.json'),*R.glob('reports/*.csv'),*R.glob('reports/*.md')]
# Large arrays/blend/audio are already in verified recovery archives. Never include temporary credentials or raw frames.
files=[p for p in files if p.is_file()]
c,ref=request('/git/ref/heads/'+BRANCH);assert c==200;head=ref['object']['sha'];c,commit=request('/git/commits/'+head);assert c==200;c,tree=request('/git/trees/'+commit['tree']['sha']+'?recursive=1');assert c==200 and not tree.get('truncated');remote={e['path']:e['sha'] for e in tree['tree'] if e['type']=='blob'}
entries=[]
for p in files:
 relative=str(p.relative_to(R.parent));data=p.read_bytes()
 if remote.get(relative)==blobsha(data):continue
 entries.append({'path':relative,'mode':'100644','type':'blob','content':data.decode()})
if entries:
 c,t=request('/git/trees','POST',{'base_tree':commit['tree']['sha'],'tree':entries});assert c==201
 c,j=request('/git/commits','POST',{'message':'Save V3 recovery scripts, source and verification reports','tree':t['sha'],'parents':[head]});assert c==201;head=j['sha']
 c,j=request('/git/refs/heads/'+BRANCH,'PATCH',{'sha':head,'force':False});assert c==200
c,verified=request('/git/ref/heads/'+BRANCH);assert c==200 and verified['object']['sha']==head
(R/'reports/source_publication.json').write_text(json.dumps({'branch':BRANCH,'commit':head,'files':len(files),'verified':True,'url':'https://github.com/BRTAL77709/WHAT-IF-TEST/tree/'+BRANCH+'/'+R.name},indent=2));print('V3_SOURCE_SAVED',head,len(files),flush=True)
