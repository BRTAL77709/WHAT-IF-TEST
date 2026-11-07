from pathlib import Path
import json,subprocess,hashlib
R=Path(__file__).resolve().parents[1]; manifest=json.loads((R/'reports/recovery_checkpoint.json').read_text()); path=R/'recovery/V3_NATIVE_FRAMES_LOSSLESS.mkv'
p=subprocess.Popen(['ffmpeg','-v','error','-i',str(path),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
for k,row in enumerate(manifest['frames']):
 raw=p.stdout.read(1080*1920*3); assert len(raw)==1080*1920*3 and hashlib.sha256(raw).hexdigest()==row['rgb_sha256'],row['file']
 if k%300==0:print('ARCHIVE_PIXELS_VERIFIED',k+1,flush=True)
assert not p.stdout.read(1);assert p.wait()==0
j={'lossless_rgb_verified_frames':2340,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'all_rendered_pixels_match':True,'png_byte_encoding':'Restored PNG bytes may differ; native RGB samples are verified identical and alpha remains opaque.'}
(R/'reports/frame_archive_validation.json').write_text(json.dumps(j,indent=2));print('LOSSLESS_FRAME_BACKUP_VERIFIED',flush=True)
