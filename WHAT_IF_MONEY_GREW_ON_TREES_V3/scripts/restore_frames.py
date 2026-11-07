"""Restore backed-up PNG pixels after joining the verified lossless archive parts."""
from pathlib import Path
import subprocess,json,hashlib,sys
from PIL import Image
base=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
manifest=json.loads((base/'reports/recovery_checkpoint.json').read_text()); archive=base/'recovery/V3_NATIVE_FRAMES_LOSSLESS.mkv'; out=base/'restored_frames'; out.mkdir(exist_ok=True)
p=subprocess.Popen(['ffmpeg','-v','error','-i',str(archive),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
for row in manifest['frames']:
 raw=p.stdout.read(1080*1920*3); assert hashlib.sha256(raw).hexdigest()==row['rgb_sha256'],row['file']
 Image.frombytes('RGB',(1080,1920),raw).convert('RGBA').save(out/row['file'])
assert not p.stdout.read(1);assert p.wait()==0
print('Restored and verified',len(manifest['frames']),'frames. Original rendered pixels preserved; PNG compression bytes may differ.')
