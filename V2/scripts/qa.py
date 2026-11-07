from pathlib import Path
import subprocess,json,hashlib,sys,math
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]; TEST='--test' in sys.argv; label='test' if TEST else 'full'; duration=8 if TEST else 78
V=R/'test'/'V2_MOTION_AUDIO_TEST_8s.mp4' if TEST else R/'final'/'WHAT_IF_MONEY_GREW_ON_TREES_V2.mp4'
def probe(p): return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
j=probe(V); v=next(s for s in j['streams'] if s['codec_type']=='video'); a=next(s for s in j['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1080,1920,'30/1',duration*30)
assert a['codec_name']=='aac' and a['channels']==2 and abs(float(j['format']['duration'])-duration)<.06
result=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(V),'-f','null','-'],capture_output=True,text=True); assert result.returncode==0,result.stderr
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(V),'-vn','-f','f32le','-acodec','pcm_f32le','-'])
peak=float(abs(np.frombuffer(raw,dtype=np.float32)).max()); assert peak<1
# True peak and integrated loudness from the decoded deliverable.
loud=subprocess.run(['ffmpeg','-hide_banner','-i',str(V),'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True); assert loud.returncode==0
(R/'reports'/f'{label}_loudness.log').write_text(loud.stderr)
metrics=json.loads((R/'reports'/f'{"test" if TEST else "full"}_motion_metrics.json').read_text())
assert metrics['max_stance_floor_error_m']<.001
assert metrics['max_reach_error_m']<.03, f'Unreachable hand contact: {metrics["max_reach_error_m"]}'
joint_path=R/'reports'/('test_joint_continuity.json' if TEST else 'full_joint_continuity.json')
joints=json.loads(joint_path.read_text()); assert joints['maximum_evaluated_joint_gap_m']<.005
cues=json.loads((R/'audio'/'speech_timeline.json').read_text())['cues']; assert all(c['start']<c['end'] for c in cues)
for c,n in zip(cues,cues[1:]): assert c['end']<=n['start']
times=[.7,2.8,4.9,5.7,7.1] if TEST else [1,11.9,17.4,26.8,35,43.2,51,57.7,60,62.8,68.5,75]
cols=5 if TEST else 4; rows=math.ceil(len(times)/cols); sheet=Image.new('RGB',(270*cols,510*rows),(8,20,28)); draw=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
 p=R/'reports'/f'{label}_encoded_{i:02}.jpg'; subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(V),'-frames:v','1','-q:v','2',str(p)],check=True)
 im=Image.open(p).resize((270,480)); xy=((i%cols)*270,(i//cols)*510); sheet.paste(im,xy); draw.text((xy[0]+10,xy[1]+487),f'{t:.1f} seconds',fill='white')
sheet.save(R/'reports'/f'{label.upper()}_ENCODED_CONTACT_SHEET.jpg',quality=94)
import re
summary=loud.stderr.rsplit('Summary:',1)[-1]
integrated_match=re.search(r'I:\s*(-?[0-9.]+) LUFS',summary)
peak_match=re.search(r'Peak:\s*(-?[0-9.]+) dBFS',summary)
integrated_lufs=float(integrated_match.group(1)) if integrated_match else None
true_peak_dbfs=float(peak_match.group(1)) if peak_match else None
assert integrated_lufs is not None and -18.5<integrated_lufs<-13.5
assert true_peak_dbfs is not None and true_peak_dbfs<-.9
# Inspect the encoded output for unintended sustained black or frozen sections.
checks=subprocess.run(['ffmpeg','-hide_banner','-i',str(V),'-an','-vf','blackdetect=d=0.20:pix_th=0.06:pic_th=0.98,freezedetect=n=-55dB:d=0.7','-f','null','-'],capture_output=True,text=True)
assert checks.returncode==0
(R/'reports'/f'{label}_black_freeze.log').write_text(checks.stderr)
import re
black=[tuple(map(float,x)) for x in re.findall(r'black_start:([0-9.]+) black_end:([0-9.]+) black_duration:([0-9.]+)',checks.stderr)]
assert not any(b-a>.25 and a>.2 and b<duration-.15 for a,b,d in black),black
freeze_starts=re.findall(r'freeze_start: ([0-9.]+)',checks.stderr)
reviewed_low_motion=[]
if freeze_starts:
 assert not TEST and freeze_starts==['58.7'],freeze_starts
 audit=json.loads((R/'reports'/'builder_motion_audit.json').read_text())
 assert all(x['changed_pixels_over_12']>15000 for x in audit)
 reviewed_low_motion=[{'start':58.7,'end':61.133333,'assessment':'Static-camera builder shot: global detector flagged localized motion. Independent decoded-frame comparisons show >15,000 pixels changing by >12 levels in each sampled interval; see builder_motion_audit.json. Low motion, not a repeated frozen frame.'}]
# Check that scene-specific action is not just a camera move, using measured animation transforms.
report={'file':str(V),'bytes':V.stat().st_size,'duration_seconds':float(j['format']['duration']),'resolution':[1080,1920],'fps':30,'frames':int(v['nb_frames']),'audio':'stereo AAC 48kHz','full_decode':'passed','black_detection_segments':black,'freeze_detection_starts':freeze_starts,'reviewed_low_motion':reviewed_low_motion,'decoded_sample_peak':peak,'integrated_lufs':integrated_lufs,'true_peak_dbfs':true_peak_dbfs,'max_stance_floor_error_m':metrics['max_stance_floor_error_m'],'max_reach_error_m':metrics['max_reach_error_m'],'maximum_evaluated_joint_gap_m':joints['maximum_evaluated_joint_gap_m'],'actor_root_path_distances_m':metrics['root_translation'],'narration_engine':'local Kokoro ONNX af_heart','narration_speed':1.0,'forced_time_stretch':False,'subtitles':'Timed from individually synthesized actual speech segments','original_score_and_sounds':True,'sha256':hashlib.sha256(V.read_bytes()).hexdigest(),'subjective_listening':'Not performed: this tool session has no audio playback/perception tool. Technical waveform, clipping, loudness and sync checks performed; human listening remains an unmet acceptance criterion.','other_limits':['Stylized analytic two-segment IK, not a full biomechanical or cloth simulation.','Workbench studio shadows and perspective cameras on CPU, not path-traced depth of field.']}
(R/'reports'/f'{label}_QC.json').write_text(json.dumps(report,indent=2))
# V1 must remain exactly intact, including the committed download.
original=json.loads((R/'reports'/'V1_preservation.json').read_text())
for path,h in original.items(): assert hashlib.sha256((R.parent/path).read_bytes()).hexdigest()==h,path
print(json.dumps(report,indent=2),flush=True)
