from pathlib import Path
import json,hashlib,base64,concurrent.futures,threading,urllib.request,subprocess
from github_io import ROOT as R,BRANCH,request,blobsha
qa=json.loads((R/'reports/final_validation.json').read_text());assert qa['status']=='TECHNICAL PASS' and json.loads((R/'reports/github_checkpoint.json').read_text())['frames_backup_verified']
master=R/'final/WHAT_IF_MONEY_GREW_ON_TREES_V3.mp4';assert hashlib.sha256(master.read_bytes()).hexdigest()==qa['sha256'];lock=threading.Lock();state=R/'recovery/delivery_blob_index.json';saved=json.loads(state.read_text()) if state.exists() else {};failures=[]
files=[(master,'downloads/'+master.name),(R/'recovery/V3_RECOVERY_BLENDER.zip','downloads/V3_EDITABLE_BLENDER.zip'),(R/'final/V3_SCRIPTS_AUDIO_REPORTS.zip','downloads/V3_SCRIPTS_AUDIO_REPORTS.zip'),(R/'comparisons/V2_V3_MOTION_COMPARISON.mp4','downloads/V2_V3_MOTION_COMPARISON.mp4')]
files += [(p,'downloads/V3_SCENES/'+p.name) for p in sorted((R/'scenes').glob('SCENE_*_V3.mp4'))]
files += [(p,str(p.relative_to(R.parent))) for p in (R/'comparisons').glob('*.jpg') if p.name in ['V2_V3_CONTACT_SHEET.jpg','CONSECUTIVE_CONTACT_FRAMES.jpg']]
def stage(item):
 p,target=item;data=p.read_bytes();sha=blobsha(data);digest=hashlib.sha256(data).hexdigest()
 if saved.get(target,{}).get('sha')==sha:return saved[target]
 code,j=request('/git/blobs','POST',{'encoding':'base64','content':base64.b64encode(data).decode()})
 if code!=201:
  error={'path':target,'http':code,'message':j.get('message','Non-JSON gateway response')}
  with lock:failures.append(error)
  return None
 assert j['sha']==sha
 row={'path':target,'source':str(p),'sha':sha,'sha256':digest,'bytes':len(data)}
 with lock:saved[target]=row;state.write_text(json.dumps(saved,indent=2))
 print('DELIVERY_BLOB_READY',target,len(data),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: staged=[x for x in pool.map(stage,files) if x]
# A single lower-bandwidth copy is a fallback only if the native master exceeds a real API limit.
if any(x['path']=='downloads/'+master.name for x in failures):
 small=R/'final/WHAT_IF_MONEY_GREW_ON_TREES_V3_DOWNLOAD.mp4'
 with open(R/'reports/download_copy_encode.log','w') as log:
  subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y','-i',str(master),'-map','0:v:0','-map','0:a:0','-map','0:s?','-c:v','libx264','-preset','fast','-b:v','1800k','-maxrate','2400k','-bufsize','4800k','-threads','3','-c:a','copy','-c:s','copy','-movflags','+faststart',str(small)],stdout=log,stderr=subprocess.STDOUT,check=True)
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(small),'-f','null','-'],check=True)
 row=stage((small,'downloads/'+small.name));assert row;staged.append(row)
assert all(x['path']=='downloads/'+master.name for x in failures),failures
c,ref=request('/git/ref/heads/'+BRANCH);assert c==200;head=ref['object']['sha'];c,commit=request('/git/commits/'+head);assert c==200
entries=[{'path':x['path'],'mode':'100644','type':'blob','sha':x['sha']} for x in staged]
c,t=request('/git/trees','POST',{'base_tree':commit['tree']['sha'],'tree':entries});assert c==201
c,j=request('/git/commits','POST',{'message':'Deliver verified V3 master, exact scene exports, editable source and motion comparisons','tree':t['sha'],'parents':[head]});assert c==201;newhead=j['sha']
c,j=request('/git/refs/heads/'+BRANCH,'PATCH',{'sha':newhead,'force':False});assert c==200
results=[]
def verify(row):
 url='https://raw.githubusercontent.com/BRTAL77709/WHAT-IF-TEST/'+BRANCH+'/'+row['path'];h=hashlib.sha256();size=0
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'WHAT-IF-TEST-V3-delivery-check'}),timeout=180) as response:
  status=response.status
  while True:
   block=response.read(1024*1024)
   if not block:break
   h.update(block);size+=len(block)
 assert status==200 and size==row['bytes'] and h.hexdigest()==row['sha256'],row['path']
 result={**row,'download_url':url,'file_url':'https://github.com/BRTAL77709/WHAT-IF-TEST/blob/'+BRANCH+'/'+row['path'],'http':status,'byte_match':True}
 with lock:
  results.append(result);(R/'reports/github_delivery.json').write_text(json.dumps({'branch':BRANCH,'commit':newhead,'artifacts':results,'upload_limit_failures':failures},indent=2))
 print('VERIFIED_FINAL_DOWNLOAD',row['path'],size,flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(verify,staged))
print('V3_FINAL_DOWNLOADS_VERIFIED',len(results),flush=True)
