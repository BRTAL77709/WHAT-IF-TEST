"""Publish V2 sources and verified download files only to the V2 branch."""
from pathlib import Path
import os,json,base64,hashlib,tempfile,subprocess,urllib.parse,urllib.request
R=Path(__file__).resolve().parents[1]; REPO='BRTAL77709/WHAT-IF-TEST'; BRANCH='what-if-v2-production'; API='https://api.github.com/repos/'+REPO
TOKEN=os.environ.get('GITHUB_RELEASE_TOKEN'); assert TOKEN,'Configured GitHub credential is unavailable'
assert (R/'reports'/'full_QC.json').exists() and (R/'reports'/'compressed_QC.json').exists()
CACHE=R/'.cache'; CACHE.mkdir(exist_ok=True)
def blobsha(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def request(path,method='GET',data=None):
 with tempfile.TemporaryDirectory(dir=CACHE) as tmp:
  td=Path(tmp); response=td/'response.json'; cmd=['curl','--config','-','--silent','--show-error','--request',method,'--header','Accept: application/vnd.github+json','--header','X-GitHub-Api-Version: 2022-11-28','--max-time','240','--output',str(response),'--write-out','%{http_code}']
  if data is not None:
   payload=td/'payload.json'; payload.write_text(json.dumps(data)); cmd+=['--header','Content-Type: application/json','--data-binary','@'+str(payload)]
  cmd.append(API+path); cfg='header = '+json.dumps('Authorization: Bearer '+TOKEN)+'\n'; result=subprocess.run(cmd,input=cfg,text=True,capture_output=True)
  assert result.returncode==0,'GitHub API transport failed'
  code=int(result.stdout.strip()); raw=response.read_text()
  try: j=json.loads(raw)
  except Exception: j={}
  if code>=400 and code!=404: print('API failure',code,str(j.get('message','Non-JSON proxy error')).replace(TOKEN,'[REDACTED]'),flush=True)
  return code,j
source_commit=None
results=[]
for source,target in [(R/'final'/'WHAT_IF_MONEY_GREW_ON_TREES_V2_DOWNLOAD.mp4','downloads/WHAT_IF_MONEY_GREW_ON_TREES_V2.mp4'),(R/'test'/'V2_MOTION_AUDIO_TEST_8s.mp4','downloads/WHAT_IF_MONEY_GREW_ON_TREES_V2_TEST_8s.mp4'),(R/'final'/'WHAT_IF_MONEY_GREW_ON_TREES_V2_EDITABLE.zip','downloads/WHAT_IF_MONEY_GREW_ON_TREES_V2_EDITABLE.zip'),(R/'final'/'WHAT_IF_MONEY_GREW_ON_TREES_V2_AUDIO.zip','downloads/WHAT_IF_MONEY_GREW_ON_TREES_V2_AUDIO.zip')]:
 data=source.read_bytes(); assert len(data)<100*1024*1024,'Artifact exceeds normal GitHub file limit'; expected=blobsha(data); digest=hashlib.sha256(data).hexdigest()
 url='/contents/'+target; code,existing=request(url+'?ref='+urllib.parse.quote(BRANCH))
 if code==200: assert existing['sha']==expected and existing['size']==len(data),'Do not overwrite a different existing artifact'
 else:
  assert code==404
  code,result=request(url,'PUT',{'message':'Add verified V2 delivery: '+source.name,'branch':BRANCH,'content':base64.b64encode(data).decode()}); assert code==201
 code,verified=request(url+'?ref='+urllib.parse.quote(BRANCH)); assert code==200 and verified['sha']==expected and verified['size']==len(data)
 # Test the actual public download, streaming without credentials.
 h=hashlib.sha256(); count=0
 with urllib.request.urlopen(urllib.request.Request(verified['download_url'],headers={'User-Agent':'WHAT-IF-TEST-V2-download-check'}),timeout=90) as response:
  status=response.status
  while True:
   block=response.read(1024*1024)
   if not block: break
   count+=len(block); h.update(block)
 assert status==200 and count==len(data) and h.hexdigest()==digest
 record={'source':str(source),'path':target,'bytes':count,'sha256':digest,'file_url':verified['html_url'],'download_url':verified['download_url'],'public_http':status,'byte_match':True}; results.append(record); print('Verified GitHub download',json.dumps(record),flush=True)
 (R/'reports'/'github_delivery.json').write_text(json.dumps({'repository':REPO,'branch':BRANCH,'source_commit':source_commit,'artifacts':results},indent=2))
# Only project sources, captions and compact review evidence enter the source commit.
files=[R/'README.md',R/'.gitignore',R/'tts-requirements.lock.txt',R.parent/'V2_PRODUCTION_BRIEF.md']+sorted((R/'scripts').glob('*.py'))
files += [R/'final'/n for n in ['narration.txt','subtitles.srt','subtitles.ass']]
files += [R/'reports'/n for n in ['QUALITY_CONTROL.md','builder_motion_audit.json','foot_state_audit.json','V1_preservation.json','full_QC.json','compressed_QC.json','test_QC.json','tts_model_provenance.json','test_evaluated_contact.json','test_joint_continuity.json','full_joint_continuity.json','BEFORE_AFTER_CONTACT_SHEET.jpg','FULL_ENCODED_CONTACT_SHEET.jpg','TEST_ENCODED_CONTACT_SHEET.jpg','foley_events.json']]
for p in files: assert p.is_file() and p.stat().st_size<4*1024*1024,p
code,ref=request('/git/ref/heads/'+BRANCH); assert code==200; head=ref['object']['sha']
code,commit=request('/git/commits/'+head); assert code==200
code,tree=request('/git/trees/'+commit['tree']['sha']+'?recursive=1'); assert code==200 and not tree.get('truncated')
remote={e['path']:e['sha'] for e in tree['tree'] if e['type']=='blob'}
base_lines=subprocess.check_output(['git','ls-tree','-r','HEAD'],cwd=R.parent,text=True).splitlines(); base={line.split('\t',1)[1]:line.split()[2] for line in base_lines}
entries=[]
for p in files:
 relative=str(p.relative_to(R.parent)); content=p.read_bytes(); sha=blobsha(content); previous=remote.get(relative)
 if previous==sha: continue
 assert previous is None or previous==base.get(relative), 'Concurrent source change: '+relative
 if p.suffix=='.jpg':
  code,result=request('/git/blobs','POST',{'encoding':'base64','content':base64.b64encode(content).decode()}); assert code==201
  entries.append({'path':relative,'mode':'100644','type':'blob','sha':result['sha']})
 else: entries.append({'path':relative,'mode':'100644','type':'blob','content':content.decode()})
source_commit=head
if entries:
 code,newtree=request('/git/trees','POST',{'base_tree':commit['tree']['sha'],'tree':entries}); assert code==201
 code,newcommit=request('/git/commits','POST',{'message':'Produce V2 cinematic animation, neural narration and verified production sources','tree':newtree['sha'],'parents':[head]}); assert code==201
 code,updated=request('/git/refs/heads/'+BRANCH,'PATCH',{'sha':newcommit['sha'],'force':False}); assert code==200
 source_commit=newcommit['sha']; print('V2 sources published',source_commit,flush=True)
(R/'reports'/'github_delivery.json').write_text(json.dumps({'repository':REPO,'branch':BRANCH,'source_commit':source_commit,'artifacts':results},indent=2))
# Confirm the original V1 download blob is unchanged on this branch and main.
V1='downloads/WHAT_IF_MONEY_GREW_ON_TREES.mp4'; v1bytes=(R.parent/V1).read_bytes()
for branch in [BRANCH,'main']:
 code,v1=request('/contents/'+V1+'?ref='+branch); assert code==200 and v1['sha']==blobsha(v1bytes)
print('V2_DELIVERY_COMPLETE; V1 main and branch download unchanged',flush=True)

code,published_ref=request('/git/ref/heads/'+BRANCH)
assert code==200 and published_ref['object']['sha']==source_commit
for relative in ['V2/reports/QUALITY_CONTROL.md','V2/reports/BEFORE_AFTER_CONTACT_SHEET.jpg','V2/README.md']:
 code,item=request('/contents/'+relative+'?ref='+BRANCH)
 assert code==200 and item['sha']==blobsha((R.parent/relative).read_bytes())
 print('Verified review source',item['html_url'],flush=True)
