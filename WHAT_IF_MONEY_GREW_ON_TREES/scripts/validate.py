from pathlib import Path
import subprocess,json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.io import wavfile
R=Path(__file__).resolve().parents[1]; V=R/'final'/'WHAT_IF_MONEY_GREW_ON_TREES_FINAL_1080x1920.mp4'
def probe(p): return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
info=probe(V); streams=info['streams']; v=next(s for s in streams if s['codec_type']=='video'); a=next(s for s in streams if s['codec_type']=='audio')
assert (v['width'],v['height'],v['avg_frame_rate'])==(1080,1920,'30/1')
assert v['codec_name']=='h264' and a['codec_name']=='aac'
assert a['channels']==2 and a['sample_rate']=='48000'
assert abs(float(a['duration'])-78)<.05
subs=[x for x in streams if x['codec_type']=='subtitle']
assert len(subs)==1 and subs[0]['tags']['language']=='eng'
assert abs(float(info['format']['duration'])-78)<.1
assert int(v['nb_frames'])==2340
# Decode the full file, retaining exit status; container metadata alone is insufficient.
p=subprocess.run(['ffmpeg','-hide_banner','-v','warning','-i',str(V),'-f','null','-'],capture_output=True,text=True)
(R/'reports'/'full_decode.log').write_text(p.stderr); assert p.returncode==0
# Verify the decoded AAC signal itself, in addition to the source mix.
audio_bytes=subprocess.check_output(['ffmpeg','-v','error','-i',str(V),'-vn','-f','f32le','-acodec','pcm_f32le','-'])
decoded=np.frombuffer(audio_bytes,dtype=np.float32)
encoded_peak=float(np.max(np.abs(decoded)))
assert encoded_peak<1, 'Clipping in decoded master audio'
# Raw-frame integrity, completeness, duplicate detection.
frames=[R/'renders'/f'frame_{i:04}.png' for i in range(1,2341)]
assert all(f.exists() for f in frames)
hashes=[hashlib.sha256(f.read_bytes()).hexdigest() for f in frames]
assert len(set(hashes))==2340, 'Duplicate rendered images detected'
for f in frames[::60]:
 with Image.open(f) as im: im.verify()
sr,samples=wavfile.read(R/'audio'/'final_mix.wav'); peak=float(np.max(np.abs(samples.astype(float)))/32768)
assert peak<1 and len(samples)/sr==78
cues=json.loads((R/'reports'/'audio_timeline.json').read_text())['cues']; assert len(cues)==20
assert all(0<=x<y<=78 for x,y,_ in cues)
for one,two in zip(cues,cues[1:]): assert one[1]<=two[0]
# Inspect a contact sheet made from the encoded deliverable, not source stills.
sheet=Image.new('RGB',(1350,1060),(9,23,31)); d=ImageDraw.Draw(sheet)
times=[3.7,11,19,27,35,43,51,59.5,68,75]
for i,t in enumerate(times):
 out=R/'reports'/f'final_scene_{i+1:02}.jpg'
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(V),'-frames:v','1','-q:v','2',str(out)],check=True)
 im=Image.open(out).resize((270,480)); x=(i%5)*270; y=(i//5)*530; sheet.paste(im,(x,y)); d.text((x+15,y+492),f'SCENE {i+1:02} / {t}s',fill='white')
sheet.save(R/'reports'/'FINAL_CONTACT_SHEET.jpg',quality=94)
report={'file':V.name,'duration_seconds':float(info['format']['duration']),'video_codec':v['codec_name'],'dimensions':[1080,1920],'fps':v['avg_frame_rate'],'frames':int(v['nb_frames']),'audio_codec':a['codec_name'],'audio_channels':a['channels'],'sample_rate':a['sample_rate'],'complete_decode':'passed','raw_frames_present':len(frames),'unique_raw_frames':len(set(hashes)),'subtitle_cues':len(cues),'subtitle_timing':'Derived from the actual individually synthesized speech segments','audio_peak_before_mastering':peak,'decoded_master_audio_peak':encoded_peak,'sha256':hashlib.sha256(V.read_bytes()).hexdigest(),'scene_clips':[p.name for p in sorted((R/'scenes').glob('scene_*.mp4'))],'limitations':['Reference video blocked by network policy; never viewed. Written specifications used.','Narration uses the existing local Flite slt synthetic voice.','Workbench studio rendering on CPU with FXAA; no path-traced lighting.','Money motion is deterministic procedural animation, not full cloth simulation.','Human animation is stylized and approximate; foot placement is not a full contact-solver simulation.']}
(R/'reports'/'quality_control.json').write_text(json.dumps(report,indent=2))
clip_counts=[]
for i,n in enumerate([210,240,240,240,240,240,240,270,240,180],1):
 clip=probe(R/'scenes'/f'scene_{i:02}.mp4'); cv=next(x for x in clip['streams'] if x['codec_type']=='video')
 assert int(cv['nb_frames'])==n
 clip_counts.append(n)
report['scene_frame_counts']=clip_counts
(R/'reports'/'quality_control.json').write_text(json.dumps(report,indent=2))
lines=['# Render and quality-control report','',f"Final file: `{V.name}`",'',
 f"- Duration: {report['duration_seconds']} seconds; 2,340 frames at 30 fps.",
 '- Native resolution: 1080 × 1920; H.264 video, YUV 4:2:0, stereo AAC at 48 kHz.',
 '- Full MP4 decoding: passed. All ten scene clips have the expected frame counts.',
 '- All 2,340 source images are present and unique; sampled PNG integrity checks passed.',
 '- All 20 subtitle cues are within the film duration and do not overlap; timings follow the actual synthesized phrases.',
 '- English captions are burned into the image and also supplied as a selectable English subtitle stream and SRT.',
 f"- Decoded final audio peak: {encoded_peak:.6f} (below full scale); no clipping detected.",
 '- Original narration, score, effects, separate audio stems, Blender file and Python sources are retained.',
 '', '## Production', '',
 '- Reused the existing Blender, Python, FFmpeg, Flite voice and scientific Python packages. No dependencies were installed.',
 '- Deterministic seed 777; one persistent city with ten camera sequences. Software studio rendering, shadows and FXAA at native output resolution.',
 '- Static geometry and note decorations were merged to reduce draw overhead without removing visible detail.',
 '- CPU rendering used four single-thread workers within the four-CPU quota. Render logs record every completed frame.',
 '- Short scene fades, original synthesized score, local speech and counters are applied in the supplied assembly script.',
 '', '## Limits and provenance', '']
lines += ['- '+x for x in report['limitations']]
lines += ['', 'All models, currency, graphics, score and effects were created specifically for this project. No assets from unrelated projects or paid services were used.', '', '## Integrity', '', 'SHA-256: `'+report['sha256']+'`', '']
(R/'reports'/'QUALITY_CONTROL.md').write_text('\n'.join(lines))
print(json.dumps(report,indent=2))
