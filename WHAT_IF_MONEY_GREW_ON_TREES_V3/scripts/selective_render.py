from pathlib import Path
import subprocess,json,hashlib,concurrent.futures,os
R=Path(__file__).resolve().parents[1]; D=R/'renders'; blend=R/'blender/WHAT_IF_MONEY_GREW_ON_TREES_V3.blend'; change=json.loads((R/'reports/selective_camera_repair.json').read_text()); marker=D/'source_sha256.txt'; current=hashlib.sha256(blend.read_bytes()).hexdigest()
assert current==change['new_source_sha256']
if marker.read_text()==current: print('SELECTIVE_RENDER_ALREADY_COMPLETE'); raise SystemExit(0)
assert marker.read_text()==change['old_source_sha256']; assert len(list(D.glob('frame_*.png')))==2340
first,last=change['affected_frames']; assert change['changed_objects']==['V2 Perspective story camera']
for frame in range(first,last+1): (D/f'frame_{frame:04}.png').unlink()
env=os.environ.copy();env.update(LP_NUM_THREADS='1',OMP_NUM_THREADS='1',XDG_CACHE_HOME=str(R/'test/cache'))
def render(a,b):
 with open(R/'reports'/f'selective_{a}_{b}.log','w') as log:
  r=subprocess.run(['blender','-b',str(blend),'-t','1','--python',str(R/'scripts/render.py'),'--',str(a),str(b)],env=env,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0
n=last-first+1
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 futures=[pool.submit(render,first+i*n//4,first+(i+1)*n//4-1) for i in range(4)]
 for f in futures: f.result()
assert len(list(D.glob('frame_*.png')))==2340
(D/'base_source_sha256.txt').write_text(marker.read_text()); marker.write_text(current)
(R/'reports/render_provenance.json').write_text(json.dumps({'final_scene_sha256':current,'native_frames':2340,'base_source_sha256':change['old_source_sha256'],'selectively_replaced_frames':[first,last],'all_other_frames':'From the same V3 motion revision; only camera keys within the replaced range changed. No V2 frames reused.'},indent=2));print('SELECTIVE_REPAIR_RENDER_COMPLETE',flush=True)
