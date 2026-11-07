"""Upload independent immutable recovery blobs concurrently; publish one non-force commit."""
from pathlib import Path
import concurrent.futures,json,hashlib,base64,threading,urllib.request
from github_io import ROOT as R,BRANCH,request,blobsha,upload
B=R/'recovery';prefix='recovery/v3-restored-checkpoint';journal=R/'reports/github_checkpoint.json';known=json.loads(journal.read_text());results={r['path']:r for r in known['artifacts']};lock=threading.Lock();pending=B/'uploaded_blob_index.json';blobs=json.loads(pending.read_text()) if pending.exists() else {}
c,ref=request('/git/ref/heads/'+BRANCH);assert c==200;c,commit=request('/git/commits/'+ref['object']['sha']);assert c==200;c,tree=request('/git/trees/'+commit['tree']['sha']+'?recursive=1');assert c==200 and not tree.get('truncated');remote={r['path']:r for r in tree['tree'] if r['type']=='blob'}
parts=[]; index=[]
for p in [B/'V3_NATIVE_FRAMES_LOSSLESS.mkv',R/'final/WHAT_IF_MONEY_GREW_ON_TREES_V3.mp4']:
 entries=[];whole=hashlib.sha256()
 with p.open('rb') as f:
  i=0
  while True:
   block=f.read(19*1024*1024)
   if not block:break
   whole.update(block);i+=1;part=B/(p.name+f'.part{i:03d}');part.write_bytes(block);target=prefix+'/'+part.name;sha=blobsha(block);digest=hashlib.sha256(block).hexdigest();entry={'source':str(part),'path':target,'sha':sha,'bytes':len(block),'sha256':digest};parts.append(entry);entries.append(entry)
 index.append({'file':p.name,'bytes':p.stat().st_size,'sha256':whole.hexdigest(),'parts':entries})
def create_blob(row):
 target=row['path']
 if target in remote:
  assert remote[target]['sha']==row['sha'],'Different existing recovery file';return
 if blobs.get(target)==row['sha']:return
 content=Path(row['source']).read_bytes();c,j=request('/git/blobs','POST',{'encoding':'base64','content':base64.b64encode(content).decode()});assert c==201 and j['sha']==row['sha'],(c,target)
 with lock:
  blobs[target]=j['sha'];pending.write_text(json.dumps(blobs,indent=2))
 print('RECOVERY_BLOB_STORED',Path(target).name,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for _ in pool.map(create_blob,parts):pass
# Refresh branch after staging blobs; preserve every prior commit and unrelated path.
c,ref=request('/git/ref/heads/'+BRANCH);assert c==200;head=ref['object']['sha'];c,commit=request('/git/commits/'+head);assert c==200
entries=[{'path':r['path'],'mode':'100644','type':'blob','sha':r['sha']} for r in parts if r['path'] not in remote]
if entries:
 c,t=request('/git/trees','POST',{'base_tree':commit['tree']['sha'],'tree':entries});assert c==201
 c,j=request('/git/commits','POST',{'message':'Back up verified V3 native frame pixels and existing master before resuming production','tree':t['sha'],'parents':[head]});assert c==201
 c,j=request('/git/refs/heads/'+BRANCH,'PATCH',{'sha':j['sha'],'force':False});assert c==200
print('RECOVERY_BLOBS_COMMITTED',len(parts),flush=True)
def verify(row):
 target=row['path']; prior=results.get(target)
 if prior and prior['sha256']==row['sha256'] and prior.get('byte_match'):return prior
 url='https://raw.githubusercontent.com/BRTAL77709/WHAT-IF-TEST/'+BRANCH+'/'+target;h=hashlib.sha256();count=0
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'WHAT-IF-TEST-V3-backup-check'}),timeout=120) as response:
  status=response.status
  while True:
   block=response.read(1024*1024)
   if not block:break
   h.update(block);count+=len(block)
 assert status==200 and count==row['bytes'] and h.hexdigest()==row['sha256'],target
 result={'path':target,'bytes':count,'sha256':row['sha256'],'download_url':url,'file_url':'https://github.com/BRTAL77709/WHAT-IF-TEST/blob/'+BRANCH+'/'+target,'http':status,'byte_match':True}
 with lock:
  results[target]=result;journal.write_text(json.dumps({'branch':BRANCH,'source_backup_verified':True,'frames_backup_verified':False,'artifacts':list(results.values())},indent=2))
 print('RECOVERY_DOWNLOAD_VERIFIED',Path(target).name,flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 list(pool.map(verify,parts))
for file in index:
 file['parts']=[results[p['path']] for p in file['parts']]
manifest=B/'FRAME_BACKUP_INDEX.json';manifest.write_text(json.dumps({'files':index,'restore':'Concatenate numbered parts, verify whole SHA-256. Restore PNG pixels from the lossless archive using scripts/restore_frames.py and reports/recovery_checkpoint.json.'},indent=2));r=upload(manifest,prefix+'/'+manifest.name);results[r['path']]=r
journal.write_text(json.dumps({'branch':BRANCH,'source_backup_verified':True,'frames_backup_verified':True,'artifacts':list(results.values())},indent=2));print('DURABLE_FRAME_AND_MASTER_BACKUP_COMPLETE',flush=True)
