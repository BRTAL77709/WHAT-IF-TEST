from pathlib import Path
import subprocess,json,csv,re,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];V3=R.parent/'WHAT_IF_MONEY_GREW_ON_TREES_V3';source=V3/'final/WHAT_IF_MONEY_GREW_ON_TREES_V3.mp4'
# Inspect the actual encoded master at each second, independently of filenames/metadata.
subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-vf','select=not(mod(n\,30))','-fps_mode','passthrough','-frames:v','78',str(R/'test/timeline_%03d.jpg')],check=True)
rows=[]
for i in range(1,79):
 p=R/'test'/f'timeline_{i:03d}.jpg';im=Image.open(p);crop=R/'test'/f'text_{i:03d}.png';im.crop((0,0,1080,900)).save(crop)
 text=subprocess.check_output(['tesseract',str(crop),'stdout','--psm','11'],stderr=subprocess.DEVNULL,text=True);text=' '.join(text.split());rows.append({'sample_second':i-1,'upper_frame_text':text,'ending_question_detected':bool(re.search(r'YES\s*[/|]?\s*NO|WOULD YOU WANT|WANT THIS WORLD',text,re.I))})
(R/'reports/V3_encoded_text_audit.json').write_text(json.dumps({'master':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'samples':rows,'scope':'OCR of decoded upper frame, once per second; exact source ASS timing is separately mapped.'},indent=2))
canvas=Image.new('RGB',(1080,2080),(8,20,28));draw=ImageDraw.Draw(canvas)
for n,t in enumerate([0,3,8,12,16,18,24,30,40,44,56,60,64,68,72,75]):
 p=R/'test'/f'timeline_{t+1:03d}.jpg';x=n%4*270;y=n//4*520;canvas.paste(Image.open(p).resize((270,480)),(x,y));draw.text((x+10,y+488),f'V3 decoded {t}s',fill='white')
canvas.save(R/'reports/V3_TIMELINE_EVIDENCE.jpg',quality=94)
print('TIMELINE_OCR',[(r['sample_second'],r['upper_frame_text']) for r in rows if r['ending_question_detected']],flush=True)
