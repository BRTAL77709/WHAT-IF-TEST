from pathlib import Path
import time,subprocess,sys,os
R=Path(__file__).resolve().parents[1]; done=R/'reports/full_render.log'; start=time.time()
while 'V3_ALL_NATIVE_FRAMES_RENDERED' not in done.read_text():
 if 'Traceback' in done.read_text(): raise RuntimeError('Base render failed; inspect full_render.log')
 print('WAITING_FOR_NATIVE_RENDER',len(list((R/'renders').glob('frame_*.png'))),flush=True);time.sleep(10)
env=os.environ.copy(); env.update(LP_NUM_THREADS='1',OMP_NUM_THREADS='1',XDG_CACHE_HOME=str(R/'test/cache'))
commands=[[sys.executable,str(R/'scripts/selective_render.py')],['blender','-b',str(R/'blender/WHAT_IF_MONEY_GREW_ON_TREES_V3.blend'),'-t','2','--python',str(R/'scripts/validate_scene.py')],[sys.executable,str(R/'scripts/encode.py')],[sys.executable,str(R/'scripts/qa.py')]]
for cmd in commands:
 print('PRODUCTION_STAGE',Path(cmd[-1]).name,flush=True)
 subprocess.run(cmd,env=env,check=True)
print('V3_RENDER_ENCODE_QC_COMPLETE',round(time.time()-start),flush=True)
