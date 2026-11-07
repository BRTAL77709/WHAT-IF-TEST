from pathlib import Path
import subprocess,concurrent.futures,hashlib,json,os,time
R=Path(__file__).resolve().parents[1]; blend=R/'blender/WHAT_IF_MONEY_GREW_ON_TREES_V3.blend'; D=R/'renders'; D.mkdir(exist_ok=True)
qc=json.loads((R/'reports/scene_validation.json').read_text()); assert qc['status']=='TECHNICAL PASS',qc['status']
assert json.loads((R/'reports/reach_targets.json').read_text())['maximum_error']==0
sha=hashlib.sha256(blend.read_bytes()).hexdigest(); marker=D/'source_sha256.txt'
if marker.exists(): assert marker.read_text()==sha,'Scene changed: do not mix stale render frames'
else: marker.write_text(sha)
env=os.environ.copy(); env.update(LP_NUM_THREADS='1',OMP_NUM_THREADS='1',XDG_CACHE_HOME=str(R/'test/cache'),MESA_SHADER_CACHE_DIR=str(D/'cache'))
def render(a,b):
 with open(R/'reports'/f'render_{a}_{b}.log','w') as log:
  result=subprocess.run(['blender','-b',str(blend),'-t','1','--python',str(R/'scripts/render.py'),'--',str(a),str(b)],env=env,stdout=log,stderr=subprocess.STDOUT)
 assert result.returncode==0,(a,b)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 futures=[pool.submit(render,1+i*585,(i+1)*585) for i in range(4)]
 while not all(f.done() for f in futures):
  for f in futures:
   if f.done() and f.exception(): raise f.exception()
  print('V3_RENDER_PROGRESS',len(list(D.glob('frame_*.png'))),'/ 2340',flush=True); time.sleep(10)
 for f in futures: f.result()
assert len(list(D.glob('frame_*.png')))==2340
print('V3_ALL_NATIVE_FRAMES_RENDERED',flush=True)
