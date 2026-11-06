from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
R=Path(__file__).resolve().parents[1]
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F=lambda n:ImageFont.truetype(font,n)
chapters=[('01 / THE DISCOVERY',['WHAT IF MONEY','GREW ON TREES?'],'ONE CITY. ONE IMPOSSIBLE CHANGE.'),('02 / THE FIRST MILLION',['EVERYONE','FEELS RICH.'],'THE FIRST HARVEST'),('03 / THE CASH BLOOM',['MONEY','EVERYWHERE.'],'ONE TREE BECOMES A FOREST'),('04 / THE GOLDEN MOMENT',['A CITY OF','MILLIONAIRES.'],'SO MUCH CASH. THE SAME CITY.'),('05 / THE CATCH',['SAME BREAD.','MORE MONEY.'],'SUPPLY HAS NOT CAUGHT UP'),('06 / THE PRICE SPIRAL',['PRICES','TAKE OFF.'],'FICTIONAL, ACCELERATED SCENARIO'),('07 / PURCHASING POWER',['A FORTUNE.','ALMOST NOTHING.'],'CASH PILES UP. SHELVES EMPTY.'),('08 / REAL WEALTH',['GROW. BUILD.','DELIVER.'],'REAL GOODS GIVE MONEY ITS POWER'),('09 / THE TWIST',['RICH IN CASH.','SHORT ON DINNER.'],'UNLIMITED MONEY ≠ UNLIMITED FOOD'),('10 / YOUR CALL',['WOULD YOU','STILL WANT IT?'],'MONEY TREES: YES OR NO?')]
for i,(label,lines,tag) in enumerate(chapters):
 im=Image.new('RGBA',(1080,1920)); d=ImageDraw.Draw(im)
 # Dark top scrim protects typography while the city stays visible.
 for y in range(510): d.line((0,y,1080,y),fill=(8,23,32,int(245*max(0,1-y/510)**.4)))
 d.rounded_rectangle((70,80,154,86),3,fill=(108,239,168,255))
 d.text((70,112),label,font=F(23),fill=(133,223,192,255))
 for j,line in enumerate(lines):
  size=70 if len(line)<19 else 60
  d.text((65,168+j*83),line,font=F(size),fill=(250,245,221,255),stroke_width=1)
 d.text((70,365),tag,font=F(19),fill=(221,230,219,255))
 # Bottom subtitle backdrop and permanent series mark.
 for y in range(1510,1920): d.line((0,y,1080,y),fill=(8,23,32,int(210*((y-1510)/410)**.5)))
 d.text((70,1820),'WHAT IF / 001',font=F(20),fill=(170,198,192,255))
 d.text((785,1820),f'{i+1:02} / 10',font=F(20),fill=(170,198,192,255))
 if i==9:
  d.rounded_rectangle((205,1390,875,1488),radius=48,fill=(113,233,164,255))
  d.text((540,1439),'COMMENT: YES OR NO',font=F(35),fill=(10,39,35,255),anchor='mm')
 im.save(R/'assets'/f'title_{i+1:02}.png')
# ASS subtitles and rapidly evolving readable currency counters.
def ts(t):
 cs=round(t*100); return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
head='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Subtitle,DejaVu Sans,43,&H00F5F5EF,&H000000FF,&H00150F09,&H99150F09,-1,0,0,0,100,100,0,0,1,2.5,1,2,80,80,210,1
Style: Counter,DejaVu Sans,75,&H009EEB7A,&H000000FF,&H0020170A,&HAA20170A,-1,0,0,0,100,100,0,0,3,15,0,8,40,40,470,1
Style: Small,DejaVu Sans,25,&H00E2E8DA,&H000000FF,&H0020170A,&HAA20170A,-1,0,0,0,100,100,0,0,1,2,0,8,50,50,575,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
events=[]
def event(a,b,style,txt): events.append(f'Dialogue: 0,{ts(a)},{ts(b)},{style},,0,0,0,,{txt}')
for a,b,s in json.loads((R/'reports'/'audio_timeline.json').read_text())['cues']: event(a,b,'Subtitle',s)
for j in range(48):
 t=7+j/6; value=int(1000000*(j/47)**1.4)
 event(t,min(15,t+1/6),'Counter',f'${value:,}')
event(7,15,'Small','CASH HARVESTED')
for a,b,txt in [(15,18,'$1 MILLION'),(18,20.5,'$100 MILLION'),(20.5,23,'$1 BILLION'),(23,31,'MORE CASH / SAME GOODS'),(31,33,'BREAD  $2'),(33,36,'BREAD  $20'),(36,39,'BREAD  $200'),(39,41,'$2'),(41,43,'$20'),(43,45,'$200'),(45,47,'$2,000'),(47,55,'CASH ≠ VALUE'),(55,64,'FOOD  +  HOMES  +  WORK'),(64,72,'DINNER: SOLD OUT')]:
 event(a,b,'Counter',('{'+chr(92)+'fs44}' if len(txt)>18 else '')+txt)
event(39,47,'Small','ILLUSTRATIVE PRICES — NOT A FORECAST')
(R/'final'/'subtitles_and_counters.ass').write_text(head+'\n'.join(events)+'\n')
print('Created 10 title plates and ASS captions/counters.')
