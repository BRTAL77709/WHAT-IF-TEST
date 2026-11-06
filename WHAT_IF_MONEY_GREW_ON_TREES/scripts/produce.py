"""Resume native 30 fps rendering, then assemble and validate all deliverables."""
from pathlib import Path
import os,subprocess,concurrent.futures,time,json,hashlib,sys
R=Path(__file__).resolve().parents[1]; env=os.environ.copy()
env.update({'LP_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MESA_SHADER_CACHE_DIR':str(R/'renders'/'shader_cache')})
source=R/'blender'/'MONEY_CITY.blend'; fingerprint=hashlib.sha256(source.read_bytes()).hexdigest()
marker=R/'renders'/'source_hash.txt'
if marker.exists() and marker.read_text().strip()!=fingerprint:
 raise SystemExit('Blend file changed. Archive or remove old frame_*.png before a fresh render; do not mix versions.')
marker.write_text(fingerprint+'\n')
chunks=[(1,585),(586,1170),(1171,1755),(1756,2340)]
def render(pair):
 a,b=pair
 with open(R/'reports'/f'render_{a}_{b}.log','w') as log:
  p=subprocess.run(['blender','-b',str(source),'-t','1','--python',str(R/'scripts'/'render.py'),'--',str(a),str(b)],env=env,stdout=log,stderr=subprocess.STDOUT)
 if p.returncode: raise RuntimeError(f'Render chunk {pair} failed: {p.returncode}')
 return pair
start=time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 futures=[pool.submit(render,pair) for pair in chunks]
 while any(not f.done() for f in futures):
  count=len(list((R/'renders').glob('frame_*.png')))
  print(f'RENDER {count}/2340 | elapsed {time.time()-start:.0f}s',flush=True)
  for f in futures:
   if f.done() and f.exception(): raise f.exception()
  time.sleep(10)
 for f in futures: print('Completed',f.result(),flush=True)
frames=list((R/'renders').glob('frame_*.png')); assert len(frames)==2340
subprocess.run([sys.executable,str(R/'scripts'/'assemble.py')],check=True)
subprocess.run([sys.executable,str(R/'scripts'/'validate.py')],check=True)
print('PRODUCTION COMPLETE',flush=True)
