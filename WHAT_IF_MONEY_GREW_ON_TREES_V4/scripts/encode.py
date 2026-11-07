from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[1]; ASS=R/'subtitles/subtitles.ass'; filters=[f'ass={ASS}']
for t in [8,16,19.5,24,32,40,47,48,52.5,56,58.6,61.2,64,68,69.2,72]:
 filters += [f"fade=t=out:st={t-.1}:d=0.1:enable='between(t,{t-.1},{t})'",f"fade=t=in:st={t}:d=0.1:enable='between(t,{t},{t+.1})'"]
filters += ['fade=t=in:d=0.12','fade=t=out:st=77.65:d=0.35','format=yuv420p']
out=R/'final/WHAT_IF_MONEY_GREW_ON_TREES_V4.mp4'
cmd=['ffmpeg','-hide_banner','-nostdin','-y','-framerate','30','-start_number','1','-i',str(R/'renders/frame_%04d.png'),'-i',str(R/'audio/V3_ORIGINAL_SOUNDTRACK.m4a'),'-i',str(R/'subtitles/subtitles.srt'),'-map','0:v:0','-map','1:a:0','-map','2:0','-vf',','.join(filters),'-c:v','libx264','-preset','fast','-crf','18','-g','30','-keyint_min','30','-sc_threshold','0','-threads','3','-c:a','copy','-c:s','mov_text','-metadata:s:s:0','language=eng','-movflags','+faststart','-t','78',str(out)]
with open(R/'reports/encode.log','w') as log: subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)

print('V4_NATIVE_MASTER_ENCODED',flush=True)
