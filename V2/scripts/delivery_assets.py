from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,json,zipfile,hashlib
R=Path(__file__).resolve().parents[1]; repo=R.parent
assert (R/'reports'/'full_QC.json').exists()
qa=json.loads((R/'reports'/'full_QC.json').read_text()); small=json.loads((R/'reports'/'compressed_QC.json').read_text())
brief=repo/'V2_PRODUCTION_BRIEF.md'
if brief.exists():
 text=brief.read_text().replace('Status: V2 planning started; no V2 render or audio mix has been generated yet.','Status: V2 rendered and technically validated; human listening review remains unverified. See V2/reports/QUALITY_CONTROL.md.').replace('- This production brief is the initial committed work; video generation has not yet run.','- The eight-second test and full V2 render are complete; neural narration, scene-specific sound and technical QC are generated in V2/.')
 brief.write_text(text)
# Side-by-side frames from the actual encoded V1 and V2 movies.
times=[.7,27.3,43.6,57.6,60,68.5]; canvas=Image.new('RGB',(1080,1560),(8,20,28)); draw=ImageDraw.Draw(canvas)
for i,t in enumerate(times):
 for vi,movie in enumerate([repo/'downloads'/'WHAT_IF_MONEY_GREW_ON_TREES.mp4',R/'final'/'WHAT_IF_MONEY_GREW_ON_TREES_V2.mp4']):
  target=R/'reports'/f'compare_{i}_{vi}.jpg'; subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(movie),'-frames:v','1','-q:v','2',str(target)],check=True)
  x=(i%2)*540+vi*270; y=(i//2)*520; canvas.paste(Image.open(target).resize((270,480)),(x,y)); draw.text((x+10,y+487),f'V{vi+1} / {t:.1f}s',fill='white')
canvas.save(R/'reports'/'BEFORE_AFTER_CONTACT_SHEET.jpg',quality=94)
lines=['# V2 render and quality-control report','',f"Final native master: {qa['bytes']:,} bytes.",f"Download version: {small['bytes']:,} bytes.",'',
'- 78-second timeline; 2,340 individually rendered frames, 1080 × 1920, 30 FPS; stereo AAC.',
'- Full master and compressed-file decoding passed.',
'- Seven characters have measured world-space root paths; stance-floor and reach measurements are in `full_QC.json`.',
'- The eight-second motion/audio test was rendered, decoded, visually inspected and technically checked before the full batch.',
'- The hero banknote grasp was checked on the evaluated Blender scene: zero distance between its grip point and the constrained hand on the sampled held frames.',
'- Normal-speed local neural Kokoro narration; no forced speech speedup. Captions are based on actual generated speech segments.',
'- Scene-matched original score and Foley; footsteps, collection, handoff and price changes have recorded animation/event times.',
 f"- Integrated loudness: {qa.get('integrated_lufs')} LUFS; true peak: {qa.get('true_peak_dbfs')} dBFS; decoded sample peak: {qa['decoded_sample_peak']:.6f}.",
 f"- Sustained frozen detections: {qa.get('freeze_detection_starts',[])}; black detections: {qa.get('black_detection_segments',[])}. Short intended scene fades are included. The 58.7–61.13s builder shot triggers the global low-motion threshold; decoded-frame comparisons confirm localized movement (builder_motion_audit.json).",
'- V1 download, source Blender file and audio mix retain their original SHA-256 hashes.',
'', '## Unmet / limited criteria', '', qa['subjective_listening']]
lines += ['- '+s for s in qa['other_limits']]
lines += ['', '## Visual inspection evidence', '', 'Contact sheets are extracted from the encoded MP4s. `BEFORE_AFTER_CONTACT_SHEET.jpg` pairs V1 and V2 views; `FULL_ENCODED_CONTACT_SHEET.jpg` covers the V2 scenes. Review them along with the actual test and final clip. No purely technical test is claimed to certify every subjective animation or sound-quality judgment.', '', '## Integrity', '', 'Master SHA-256: `'+qa['sha256']+'`', '', 'Download SHA-256: `'+small['sha256']+'`', '']
(R/'reports'/'QUALITY_CONTROL.md').write_text('\n'.join(lines))
# Editable source + narration/score/Foley. Omit large model weights, toolchain and raw frames.
archive=R/'final'/'WHAT_IF_MONEY_GREW_ON_TREES_V2_PROJECT.zip'; files=[R/'README.md',R/'.gitignore',R/'tts-requirements.lock.txt',R/'blender'/'V2_CITY.blend',R/'blender'/'V2_TEST.blend']
for directory in ['scripts','audio']:
 for p in (R/directory).rglob('*'):
  if p.is_file() and p.suffix not in ['.pyc','.log'] and '__pycache__' not in p.parts: files.append(p)
for name in ['QUALITY_CONTROL.md','full_QC.json','compressed_QC.json','test_QC.json','full_motion_metrics.json','test_motion_metrics.json','full_joint_continuity.json','test_joint_continuity.json','test_evaluated_contact.json','tts_model_provenance.json','V1_preservation.json','foot_state_audit.json','builder_motion_audit.json','foley_events.json','BEFORE_AFTER_CONTACT_SHEET.jpg','FULL_ENCODED_CONTACT_SHEET.jpg','TEST_ENCODED_CONTACT_SHEET.jpg']:
 files.append(R/'reports'/name)
for name in ['narration.txt','subtitles.srt','subtitles.ass']: files.append(R/'final'/name)
for name in ['KOKORO_ONNX_LICENSE.txt','KOKORO_ONNX_README.md']: files.append(R/'models'/name)
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for p in files: z.write(p,arcname=str(Path('V2')/p.relative_to(R)))
with zipfile.ZipFile(archive) as z: assert z.testzip() is None
print('PROJECT ARCHIVE',archive.stat().st_size,'bytes; files',len(files),flush=True)
(R/'reports'/'package_manifest.json').write_text(json.dumps({'file':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(files),'omitted':'Native PNG sequence, model weights and local toolchain; full native master retained separately.'},indent=2))

# Smaller archives stay within the Contents API request-size ceiling.
for kind in ['EDITABLE','AUDIO']:
 target=R/'final'/f'WHAT_IF_MONEY_GREW_ON_TREES_V2_{kind}.zip'
 subset=[p for p in files if ((p.relative_to(R).parts[0]=='audio') == (kind=='AUDIO'))]
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for p in subset: z.write(p,arcname=str(Path('V2')/p.relative_to(R)))
 with zipfile.ZipFile(target) as z: assert z.testzip() is None
 print(kind,target.stat().st_size,'bytes',flush=True)
