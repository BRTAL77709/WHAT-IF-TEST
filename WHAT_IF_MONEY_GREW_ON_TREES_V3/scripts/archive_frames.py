"""Lossless temporal backup of native render pixels; never renders a frame."""
from pathlib import Path
import subprocess,json,hashlib
R=Path(__file__).resolve().parents[1]; out=R/'recovery/V3_NATIVE_FRAMES_LOSSLESS.mkv'
with open(R/'reports/lossless_archive_encode.log','w') as log:
 subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y','-framerate','30','-start_number','1','-i',str(R/'renders/frame_%04d.png'),'-frames:v','2340','-an','-c:v','libx264rgb','-crf','0','-preset','veryfast','-threads','3','-pix_fmt','rgb24',str(out)],stdout=log,stderr=subprocess.STDOUT,check=True)
print('LOSSLESS_ARCHIVE_ENCODED',out.stat().st_size,flush=True)
