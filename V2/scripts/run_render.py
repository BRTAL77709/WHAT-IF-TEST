from pathlib import Path
import subprocess,concurrent.futures,os,time,sys,json,hashlib
R=Path(__file__).resolve().parents[1]; test='--test' in sys.argv; end=240 if test else 2340
blend=R/'blender'/('V2_TEST.blend' if test else 'V2_CITY.blend'); folder='test/frames' if test else 'renders'
(R/folder).mkdir(parents=True,exist_ok=True); env=os.environ.copy(); env.update({'LP_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MESA_SHADER_CACHE_DIR':str(R/'renders'/'cache'),'XDG_CACHE_HOME':str(R/'.cache')})
missing=[i for i in range(1,end+1) if not (R/folder/f'frame_{i:04}.png').exists()]
first=missing[0] if missing else end+1; count=end-first+1
chunks=[(first+i*count//4,first+(i+1)*count//4-1) for i in range(4) if count>0]
def render(ab):
 a,b=ab
 with open(R/'reports'/f'{"test" if test else "full"}_render_{a}_{b}.log','w') as log:
  p=subprocess.run(['blender','-b',str(blend),'-t','1','--python',str(R/'scripts'/'render.py'),'--',str(a),str(b),folder],env=env,stdout=log,stderr=subprocess.STDOUT)
 assert p.returncode==0,ab
 return ab
marker=R/folder/'source_sha256.txt'; fingerprint=hashlib.sha256(blend.read_bytes()).hexdigest()
if marker.exists(): assert marker.read_text().strip()==fingerprint, 'Do not mix different V2 scene versions'
else: marker.write_text(fingerprint)
start=time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 futures=[pool.submit(render,c) for c in chunks]
 while not all(f.done() for f in futures):
  for f in futures:
   if f.done() and f.exception(): raise f.exception()
  count=len(list((R/folder).glob('frame_*.png'))); print('V2', 'TEST' if test else 'FULL',count,'/',end,'elapsed',round(time.time()-start),flush=True); time.sleep(10)
 for f in futures: print('Chunk complete',f.result(),flush=True)
assert len(list((R/folder).glob('frame_*.png')))==end
subprocess.run([sys.executable,str(R/'scripts'/'encode.py')]+(['--test'] if test else []),check=True,env=env)
subprocess.run([sys.executable,str(R/'scripts'/'qa.py')]+(['--test'] if test else []),check=True,env=env)
if not test: subprocess.run([sys.executable,str(R/'scripts'/'compress.py')],check=True,env=env)
print('V2_RENDER_AND_ENCODE_COMPLETE',flush=True)
