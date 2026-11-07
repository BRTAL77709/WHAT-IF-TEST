from pathlib import Path
import subprocess,json,hashlib
R=Path(__file__).resolve().parents[1]; src=R/'final'/'WHAT_IF_MONEY_GREW_ON_TREES_V2.mp4'; out=R/'final'/'WHAT_IF_MONEY_GREW_ON_TREES_V2_DOWNLOAD.mp4'
with open(R/'reports'/'compress.log','w') as log:
 subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y','-i',str(src),'-map','0:v:0','-map','0:a:0','-map','0:s?','-c:v','libx264','-preset','fast','-b:v','1800k','-maxrate','2200k','-bufsize','4400k','-threads','3','-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-b:a','96k','-c:s','mov_text','-t','78','-movflags','+faststart',str(out)],check=True,stdout=log,stderr=subprocess.STDOUT)
j=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)])); v=next(s for s in j['streams'] if s['codec_type']=='video'); a=next(s for s in j['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1080,1920,'30/1',2340) and a['channels']==2
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(out),'-f','null','-'],check=True)
report={'path':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'frames':2340,'duration':float(j['format']['duration']),'full_decode':'passed','dimensions':[1080,1920],'fps':30,'stereo_audio':True}
(R/'reports'/'compressed_QC.json').write_text(json.dumps(report,indent=2)); print('COMPRESSED',json.dumps(report),flush=True)
