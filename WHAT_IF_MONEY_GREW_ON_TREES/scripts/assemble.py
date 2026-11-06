from pathlib import Path
import subprocess,json,time,os
from concurrent.futures import ThreadPoolExecutor
R=Path(__file__).resolve().parents[1]
bounds=[0,7,15,23,31,39,47,55,64,72,78]
os.environ['XDG_CACHE_HOME']=str(R/'renders'/'cache')
(R/'renders'/'cache').mkdir(exist_ok=True)
def run(args,log):
 with open(R/'reports'/log,'w') as f: subprocess.run(args,check=True,stdout=f,stderr=subprocess.STDOUT)
def encode_scene(args):
 i,a,b=args
 out=R/'scenes'/f'scene_{i+1:02}.mp4'
 cmd=['ffmpeg','-hide_banner','-y','-threads','2','-framerate','30','-start_number',str(a*30+1),'-i',str(R/'renders'/'frame_%04d.png'),'-loop','1','-i',str(R/'assets'/f'title_{i+1:02}.png'),'-filter_complex_threads','1','-filter_complex',f'[0:v][1:v]overlay=0:0:shortest=1,fade=t=in:d=0.16,fade=t=out:st={b-a-.16}:d=0.16,format=yuv420p[v]','-map','[v]','-frames:v',str((b-a)*30),'-r','30','-c:v','libx264','-preset','fast','-crf','18','-threads','2',str(out)]
 run(cmd,f'encode_scene_{i+1:02}.log'); print('Encoded scene',i+1,flush=True)
with ThreadPoolExecutor(max_workers=2) as pool:
 list(pool.map(encode_scene,[(i,a,b) for i,(a,b) in enumerate(zip(bounds,bounds[1:]))]))
listing=R/'scenes'/'concat.txt'; listing.write_text('\n'.join("file 'scene_%02d.mp4'"%i for i in range(1,11)))
run(['ffmpeg','-hide_banner','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(R/'renders'/'assembled_picture.mp4')],'concat.log')
final=R/'final'/'WHAT_IF_MONEY_GREW_ON_TREES_FINAL_1080x1920.mp4'
run(['ffmpeg','-hide_banner','-y','-i',str(R/'renders'/'assembled_picture.mp4'),'-i',str(R/'audio'/'final_mix.wav'),'-i',str(R/'final'/'subtitles.srt'),'-map','0:v','-map','1:a','-map','2:0','-vf',f"ass={R/'final'/'subtitles_and_counters.ass'}",'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-c:v','libx264','-preset','fast','-crf','18','-threads','3','-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-b:a','192k','-c:s','mov_text','-metadata','title=What If Money Grew on Trees?','-metadata','comment=Original procedural miniature film. Fictional accelerated economic thought experiment.','-metadata:s:s:0','language=eng','-movflags','+faststart','-t','78',str(final)],'encode_final.log')
print('FINAL',final,flush=True)
