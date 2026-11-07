from pathlib import Path
import subprocess,json,hashlib,concurrent.futures,os,sys
from PIL import Image
R=Path(__file__).resolve().parents[1];M=R/'reports/render_manifest.json';manifest=json.loads(M.read_text());blend=Path(manifest['source_blend']);assert hashlib.sha256(blend.read_bytes()).hexdigest()==manifest['source_blend_sha256'];assert json.loads((R/'reports/github_source_checkpoint.json').read_text())['validated_blend_backup_verified'];assert json.loads((R/'reports/native_proof.json').read_text())[0]['V3_V4_native_pixels_identical']
env=os.environ.copy();env.update(LP_NUM_THREADS='1',OMP_NUM_THREADS='1',XDG_CACHE_HOME=str(R/'test/cache'),MESA_SHADER_CACHE_DIR=str(R/'test/cache/mesa'))
# Accept already decoded PNGs produced under the same fingerprint after an interruption.
for row in manifest['frames']:
 p=Path(row['path'])
 if row['status']=='needs_render' and p.exists():
  try:
   with Image.open(p) as im:im.load();assert im.size==(1080,1920)
   row['png_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();row['status']='rendered_verified'
  except Exception:p.unlink()
M.write_text(json.dumps(manifest,indent=2))
def render(a,b,scene):
 with open(R/'reports'/f'render_scene{scene:02d}_{a}_{b}.log','w') as log:r=subprocess.run(['blender','-b',str(blend),'-t','1','--python',str(R/'scripts/render.py'),'--',str(a),str(b)],env=env,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,(a,b)
scenes=[4] if '--test-only' in sys.argv else [4,1,2,3,5,6,7,8,9,10]
if '--test-only' not in sys.argv:assert (R/'reports/TEST_ACCEPTED.json').exists(),'Inspect and accept the actual interaction clip before completing the film'
for scene in scenes:
 manifest=json.loads(M.read_text());a=(scene-1)*240+1;b=min(2340,scene*240)
 if str(scene) not in manifest['completed_scene_archives']:
  n=b-a+1
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
   futures=[pool.submit(render,a+i*n//4,a+(i+1)*n//4-1,scene) for i in range(4)]
   for f in futures:f.result()
  subprocess.run([sys.executable,str(R/'scripts/backup_batch.py'),str(scene)],check=True,env=env)
 print('V4_SCENE_COMPLETE',scene,flush=True)
 if '--test-only' in sys.argv:
  cmd=['ffmpeg','-hide_banner','-nostdin','-y','-framerate','30','-start_number',str(a),'-i',str(R/'renders/frame_%04d.png'),'-ss','24','-i',str(R/'audio/V3_ORIGINAL_SOUNDTRACK.m4a'),'-vf',f'setpts=PTS+24/TB,ass={R}/subtitles/subtitles.ass,setpts=PTS-24/TB','-frames:v','240','-t','8','-c:v','libx264','-preset','fast','-crf','18','-threads','3','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(R/'test/V4_INTERACTION_TEST_8s.mp4')]
  with open(R/'reports/test_encode.log','w') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,env=env)
  print('V4_CONTINUOUS_INTERACTION_TEST_READY',flush=True)
print('V4_BATCH_RUN_COMPLETE',flush=True)
