from pathlib import Path
import subprocess,json,hashlib,zipfile
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]; master=R/'final/WHAT_IF_MONEY_GREW_ON_TREES_V3.mp4'; old=R.parent/'V2/final/WHAT_IF_MONEY_GREW_ON_TREES_V2.mp4'; D=R/'comparisons'
segments=[('WALK',2,3.7),('GRASP',4.1,6.5),('SHOP',27,35),('PRICES',39.5,48.5),('WORK',55.8,64)]
parts=[]
for name,start,end in segments:
 target=D/f'{name}_V2_V3.mp4'; duration=round(end-start,3)
 filters="[0:v]scale=540:960,setsar=1[l];[1:v]scale=540:960,setsar=1[r];[l][r]hstack=inputs=2,drawbox=x=0:y=0:w=iw:h=42:color=black@0.75:t=fill,drawtext=text='V2 / BEFORE':x=20:y=10:fontsize=22:fontcolor=white,drawtext=text='V3 / REPAIR':x=560:y=10:fontsize=22:fontcolor=white[v]"
 cmd=['ffmpeg','-hide_banner','-nostdin','-y','-ss',str(start),'-i',str(old),'-ss',str(start),'-i',str(master),'-filter_complex',filters,'-map','[v]','-map','1:a:0','-t',str(duration),'-c:v','libx264','-preset','fast','-crf','20','-threads','3','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(target)]
 with open(R/'reports'/f'compare_{name}.log','w') as log: subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
 parts.append(target)
listing=D/'concat.txt';listing.write_text('\n'.join("file '"+str(p)+"'" for p in parts))
subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(D/'V2_V3_MOTION_COMPARISON.mp4')],check=True)
# Full-film overview extracted from actual encoded movies, not Blender-only previews.
times=[1,6,11.8,18,27.5,30.4,43.5,51,57.2,60,62.8,75]
canvas=Image.new('RGB',(1080,3120),(8,20,28));draw=ImageDraw.Draw(canvas)
for i,t in enumerate(times):
 for version,movie in enumerate([old,master]):
  p=D/f'still_{i:02}_{version}.jpg';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(movie),'-frames:v','1','-q:v','2',str(p)],check=True)
  x=(i%2)*540+version*270;y=(i//2)*520;canvas.paste(Image.open(p).resize((270,480)),(x,y));draw.text((x+8,y+488),f'V{version+2} / {t:.1f}s',fill='white')
canvas.save(D/'V2_V3_CONTACT_SHEET.jpg',quality=94)
# Consecutive-frame strips at critical boundaries (one frame apart, 30fps).
canvas=Image.new('RGB',(1080,2080),(8,20,28));draw=ImageDraw.Draw(canvas)
for row,frame in enumerate([164,911,1438,1715]):
 for version,movie in enumerate([old,master]):
  for j in range(4):
   p=D/f'strip_{row}_{version}_{j}.jpg';t=(frame+j-1)/30;subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(movie),'-frames:v','1',str(p)],check=True)
   x=(version*4+j)*135;y=row*520;canvas.paste(Image.open(p).resize((135,480)),(x,y));draw.text((x+3,y+487),f'V{version+2} f{frame+j}',fill='white')
canvas.save(D/'CONSECUTIVE_CONTACT_FRAMES.jpg',quality=94)
print('REVIEW_ASSETS_READY',flush=True)
