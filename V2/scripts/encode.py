from pathlib import Path
import subprocess,sys,json
R=Path(__file__).resolve().parents[1]; TEST='--test' in sys.argv
D=R/'test'/'frames' if TEST else R/'renders'; duration=8 if TEST else 78
ASS=R/'final'/'subtitles.ass'
head='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Dialogue,DejaVu Sans,43,&H00F8F8F0,&H000000FF,&H00201810,&H88201810,-1,0,0,0,100,100,0,0,1,2.4,1,2,75,75,160,1
Style: Title,DejaVu Sans,61,&H00ECF4ED,&H000000FF,&H00302412,&H88302412,-1,0,0,0,100,100,0,0,1,2,1,8,65,65,110,1
Style: Small,DejaVu Sans,25,&H00D4E2D0,&H000000FF,&H00302412,&H88302412,0,0,0,0,100,100,0,0,1,1.5,0,8,65,65,90,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def stamp(t):
 c=round(t*100); return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'
events=[]
def event(a,b,style,text): events.append(f'Dialogue: 0,{stamp(a)},{stamp(b)},{style},,0,0,0,,{text}')
for c in json.loads((R/'audio'/'speech_timeline.json').read_text())['cues']: event(c['start'],c['end'],'Dialogue',c['text'])
slash=chr(92)
event(0,2,'Small','WHAT IF / MONEY TREES')
event(40,48,'Small','ILLUSTRATIVE SCENARIO — NOT A FORECAST')
event(72.2,77.6,'Title','WHAT IF MONEY'+slash+'NGREW ON TREES?'+slash+'N'+slash+'NWOULD YOU WANT THIS WORLD?'+slash+'N'+slash+'NYES / NO')
ASS.write_text(head+'\n'.join(events)+'\n')
# Short fades at motivated cuts; no long full-screen title cards.
filters=[f'ass={ASS}']
for t in [8,16,19.5,24,32,40,47,48,52.5,56,58.6,61.2,64,68,72]:
 if t<duration: filters += [f"fade=t=out:st={t-.10}:d=0.10:enable='between(t,{t-.10},{t})'",f"fade=t=in:st={t}:d=0.10:enable='between(t,{t},{t+.10})'"]
filters+=['fade=t=in:d=0.12',f'fade=t=out:st={duration-.35}:d=0.35','format=yuv420p']
out=R/'test'/'V2_MOTION_AUDIO_TEST_8s.mp4' if TEST else R/'final'/'WHAT_IF_MONEY_GREW_ON_TREES_V2.mp4'
cmd=['ffmpeg','-hide_banner','-nostdin','-y','-framerate','30','-start_number','1','-i',str(D/'frame_%04d.png'),'-i',str(R/'audio'/'mix.wav'),'-i',str(R/'final'/'subtitles.srt'),'-map','0:v','-map','1:a','-map','2:0','-vf',','.join(filters),'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-t',str(duration),'-c:v','libx264','-preset','fast','-crf','18','-threads','3','-c:a','aac','-ar','48000','-b:a','192k','-c:s','mov_text','-metadata:s:s:0','language=eng','-movflags','+faststart',str(out)]
with open(R/'reports'/('test_encode.log' if TEST else 'full_encode.log'),'w') as log: subprocess.run(cmd,check=True,stdout=log,stderr=subprocess.STDOUT)
print('ENCODED',out,flush=True)
