from pathlib import Path
import subprocess,json,hashlib,csv,math,sys
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]; V=R/'final/WHAT_IF_MONEY_GREW_ON_TREES_V3.mp4'; V2=R.parent/'V2/final/WHAT_IF_MONEY_GREW_ON_TREES_V2.mp4'
def probe(p): return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
def audiohash(p): return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
j=probe(V); v=next(x for x in j['streams'] if x['codec_type']=='video'); audio=next(x for x in j['streams'] if x['codec_type']=='audio')
assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1080,1920,'30/1',2340)
assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p' and audio['codec_name']=='aac' and audio['channels']==2
assert abs(float(j['format']['duration'])-78)<.05
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(V),'-f','null','-'],check=True)
audio_sha=audiohash(V); assert audio_sha==audiohash(V2)==audiohash(R/'audio/V2_ORIGINAL_SOUNDTRACK.m4a')
if '--resume-master-qc' in sys.argv:
 with open(R/'reports/pixel_frame_diagnostics.csv') as f: pixel=list(csv.DictReader(f))
 assert len(pixel)==2340 and all(int(row['frame'])==k+1 for k,row in enumerate(pixel))
 max_run=0; run=0
 for row in pixel:
  run=run+1 if row['exact_duplicate_previous']=='True' else 0; max_run=max(max_run,run)
 black=[row for row in pixel if float(row['mean_luma'])<2 and row['near_editorial_fade']!='True']
 assert max_run<21 and not black
 cuts=[0,8,16,19.5,24,32,40,47,48,52.5,56,58.6,61.2,64,68,72,78]
 assert (R/'reports/optical_flow_actions.json').exists()
 print('REUSED_BACKED_UP_2340_FRAME_PIXEL_QC',flush=True)
else:
 # Every decoded frame receives temporal pixel screening. No metadata-only motion verdict.
 p=subprocess.Popen(['ffmpeg','-v','error','-i',str(V),'-vf','scale=270:480','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
 size=270*480*3; pixel=[]; previous=None; repeat_run=0; max_run=0; images={}; cuts=[0,8,16,19.5,24,32,40,47,48,52.5,56,58.6,61.2,64,68,72,78]
 try:
  import cv2
 except ImportError: cv2=None
 flow_rows=[]
 for k in range(2340):
  data=p.stdout.read(size); assert len(data)==size,k; img=np.frombuffer(data,np.uint8).reshape(480,270,3); diff=abs(img.astype(np.float32)-previous.astype(np.float32)) if previous is not None else np.zeros_like(img,dtype=float)
  same=previous is not None and np.array_equal(img,previous); repeat_run=repeat_run+1 if same else 0; max_run=max(max_run,repeat_run)
  row={'frame':k+1,'time':k/30,'mean_luma':float(img.mean()),'mean_absolute_difference':float(diff.mean()),'pixels_changed_over_12':int((diff.max(2)>12).sum()),'exact_duplicate_previous':bool(same),'near_editorial_fade':any(abs(k/30-t)<.16 for t in cuts) or k/30>77.6}; pixel.append(row)
  if cv2 is not None and previous is not None and any(a<=k/30<=b for a,b in [(4,6.5),(27,34.5),(39.5,48.5),(56,64)]):
   flow=cv2.calcOpticalFlowFarneback(cv2.cvtColor(previous,cv2.COLOR_RGB2GRAY),cv2.cvtColor(img,cv2.COLOR_RGB2GRAY),None,.5,2,12,2,5,1.1,0)
   flow_rows.append({'frame':k+1,'mean_flow_pixels_per_frame':float(np.linalg.norm(flow,axis=2).mean()),'p95_flow_pixels_per_frame':float(np.percentile(np.linalg.norm(flow,axis=2),95))})
  previous=img.copy()
 assert not p.stdout.read(1); assert p.wait()==0
 assert max_run<21,('sustained exact duplicates',max_run)
 black=[r for r in pixel if r['mean_luma']<2 and not r['near_editorial_fade']]; assert not black,black
 with open(R/'reports/pixel_frame_diagnostics.csv','w') as f:
  w=csv.DictWriter(f,fieldnames=pixel[0]);w.writeheader();w.writerows(pixel)
 (R/'reports/optical_flow_actions.json').write_text(json.dumps({'available':cv2 is not None,'measurements':flow_rows,'scope':'Temporal flow on consecutive decoded frames of critical actions; not a physical collision certification.'},indent=2))
# Match soundtrack cues to actual landing frames and existing exact-timed grasp/flip events.
old_steps=json.loads((R.parent/'V2/reports/full_motion_metrics.json').read_text())['footstep_events']; foley=json.loads((R.parent/'V2/reports/foley_events.json').read_text()); events=json.loads((R/'reports/locomotion_plan.json').read_text())['events']; sync=[]
for cue in foley:
 if cue['type']=='footstep':
  actor=cue['actor']; nearest=min([abs(cue['time']-e['time']) for e in events if e['actor']==actor] or [1e9]); sync.append({'time':cue['time'],'actor':actor,'landing_error_seconds':nearest})
# Inspect all-frame transform discontinuities, excluding documented cuts only for camera.
z=np.load(R/'reports/V3_transforms.npz'); names=list(z['names']); arr=z['transforms']; before=np.load(R/'reports/V2_transforms.npz'); bnames=list(before['names']); old=before['transforms']; movement=[]
for idx,name in enumerate(names):
 if name not in bnames: continue
 d=np.linalg.norm(np.diff(arr[:,idx,:3],axis=0),axis=1); od=np.linalg.norm(np.diff(old[:,bnames.index(name),:3],axis=0),axis=1)
 if name=='V2 Perspective story camera':
  for t in cuts:
   at=round(t*30)-1
   if 0<=at<len(d): d[at]=0;od[at]=0
 movement.append({'object':name,'V2_max_frame_displacement_m':float(od.max()),'V3_max_frame_displacement_m':float(d.max()),'V3_worst_frame':int(d.argmax()+2)})
(R/'reports/motion_before_after.json').write_text(json.dumps(movement,indent=2))
scenes=[]; source=R/'blender/WHAT_IF_MONEY_GREW_ON_TREES_V3.blend'
for i,path in enumerate(sorted((R/'scenes').glob('SCENE_*_V3.mp4'))):
 q=probe(path); stream=next(s for s in q['streams'] if s['codec_type']=='video'); expected=240 if i<9 else 180
 assert int(stream['nb_frames'])==expected,(path,int(stream['nb_frames']))
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','null','-'],check=True)
 scenes.append({'scene_id':i+1,'status':'TECHNICAL PASS','artistic_status':'ARTISTIC REVIEW REQUIRED','user_approved':False,'source_blender':str(source),'animation_script':str(R/'scripts/repair.py'),'render_command':f'blender -b {source} -t 1 --python {R}/scripts/render.py -- {i*240+1} {i*240+expected}','file':str(path),'duration':float(q['format']['duration']),'resolution':[1080,1920],'fps':30,'frames':expected,'bytes':path.stat().st_size,'audio_status':'Original V2 AAC packets stream-copied; scene boundaries may retain one AAC frame of packet alignment. Full-film stream hash is exact.','character_motion':'All-frame fixed-length IK, root, stance and contact checks: scene_validation.json and frame_diagnostics.csv','collision_camera_findings':'All-frame static-surface proximity and root separation screening in scene_validation.json; full swept mesh collision proof is not available.','lighting_findings':'V2 lighting and materials preserved; pixel-level temporal screening performed.','frame_findings':'Consecutive-frame differences and critical-action optical flow are recorded.','remaining_limitations':['ARTISTIC REVIEW REQUIRED: automated motion/pixel screening cannot certify every physical contact, self-collision, silhouette or performance.']})
assert len(scenes)==10
(R/'reports/scene_reports.json').write_text(json.dumps(scenes,indent=2))
# Original versions must remain byte-identical.
protected=json.loads((R/'reports/protected_files.json').read_text())
for relative,x in protected.items(): assert hashlib.sha256((R.parent/relative).read_bytes()).hexdigest()==x['sha256'],relative
report={'status':'TECHNICAL PASS','artistic_status':'ARTISTIC REVIEW REQUIRED','user_approved':False,'path':str(V),'bytes':V.stat().st_size,'sha256':hashlib.sha256(V.read_bytes()).hexdigest(),'duration':float(j['format']['duration']),'resolution':[1080,1920],'fps':30,'frames':2340,'full_decode':'PASS','audio_packet_sha256':audio_sha,'V2_audio_exact_bitstream_match':True,'V1_V2_protected_files_unchanged':True,'pixel_QC_checkpoint_reused':'--resume-master-qc' in sys.argv,'max_identical_consecutive_frames':max_run,'unexpected_black_frames':black,'audible_footstep_alignment':sync,'max_audible_footstep_error_seconds':max(x['landing_error_seconds'] for x in sync),'limitations':['No claim of exhaustive every-pixel artistic acceptance or full swept mesh collision proof.','Human continuous-motion and soundtrack listening acceptance remain unverified. No user approval is claimed.','Existing Workbench FXAA, lighting and materials retained; no path tracing or added motion blur.','Shelf inventory props are kept physically present instead of disappearing by scale changes; the existing narration, price sequence and 78-second story are preserved.']}
(R/'reports/final_validation.json').write_text(json.dumps(report,indent=2)); print('V3_FINAL_QC',json.dumps({k:v for k,v in report.items() if k not in ['audible_footstep_alignment']}),flush=True)
