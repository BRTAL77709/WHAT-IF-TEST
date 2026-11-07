from pathlib import Path
import os,json,base64,hashlib,tempfile,subprocess,urllib.request,urllib.parse
ROOT=Path(__file__).resolve().parents[1]; CACHE=ROOT/'recovery/api-cache'; CACHE.mkdir(parents=True,exist_ok=True)
API='https://api.github.com/repos/BRTAL77709/WHAT-IF-TEST'; BRANCH='what-if-v3-motion-repair'; TOKEN=os.environ.get('GITHUB_RELEASE_TOKEN'); assert TOKEN,'Configured GitHub credential unavailable'
def blobsha(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def request(path,method='GET',data=None):
 with tempfile.TemporaryDirectory(dir=CACHE) as tmp:
  td=Path(tmp); response=td/'response.json';cmd=['curl','--config','-','--silent','--show-error','--request',method,'--header','Accept: application/vnd.github+json','--header','X-GitHub-Api-Version: 2022-11-28','--max-time','240','--output',str(response),'--write-out','%{http_code}']
  if data is not None:
   payload=td/'payload.json';payload.write_text(json.dumps(data));cmd+=['--header','Content-Type: application/json','--data-binary','@'+str(payload)]
  cmd.append(API+path);result=subprocess.run(cmd,input='header = '+json.dumps('Authorization: Bearer '+TOKEN)+'\n',text=True,capture_output=True);assert result.returncode==0,'GitHub transport failed'
  status=int(result.stdout.strip())
  try:j=json.loads(response.read_text())
  except Exception:j={}
  if status>=400 and status!=404: print('GitHub API error',status,str(j.get('message','Non-JSON gateway response')).replace(TOKEN,'[REDACTED]'),flush=True)
  return status,j
def ensure_branch():
 c,j=request('/git/ref/heads/'+BRANCH)
 if c==404:
  c,source=request('/git/ref/heads/what-if-v2-production');assert c==200
  c,j=request('/git/refs','POST',{'ref':'refs/heads/'+BRANCH,'sha':source['object']['sha']});assert c==201
 else:assert c==200
 print('GitHub V3 branch available',BRANCH,flush=True)
def upload(source,target,allow_update=False):
 data=Path(source).read_bytes();expected=blobsha(data);digest=hashlib.sha256(data).hexdigest();url='/contents/'+urllib.parse.quote(target,safe='/');c,old=request(url+'?ref='+BRANCH)
 if c==200 and old['sha']==expected: pass
 else:
  assert c==404 or (c==200 and allow_update),'Existing different file protected: '+target
  payload={'message':'Preserve verified V3 checkpoint: '+Path(target).name,'branch':BRANCH,'content':base64.b64encode(data).decode()}
  if c==200:payload['sha']=old['sha']
  c,j=request(url,'PUT',payload);assert c in [200,201],(c,target)
 c,j=request(url+'?ref='+BRANCH);assert c==200 and j['sha']==expected and j['size']==len(data)
 h=hashlib.sha256();count=0
 with urllib.request.urlopen(urllib.request.Request(j['download_url'],headers={'User-Agent':'WHAT-IF-TEST-V3-integrity'}),timeout=120) as r:
  status=r.status
  while True:
   block=r.read(1024*1024)
   if not block:break
   count+=len(block);h.update(block)
 assert status==200 and count==len(data) and h.hexdigest()==digest
 result={'path':target,'bytes':count,'sha256':digest,'file_url':j['html_url'],'download_url':j['download_url'],'http':status,'byte_match':True};print('VERIFIED',target,count,flush=True);return result
