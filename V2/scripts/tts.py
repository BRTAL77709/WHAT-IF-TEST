from pathlib import Path
import json,os,time,numpy as np,soundfile as sf
from kokoro_onnx import Kokoro
R=Path(__file__).resolve().parents[1]
scenes=[(0,8,['What if money actually grew on trees?','One leaf could change everything.']),
(8,16,['At first, people would race','to harvest a fortune.']),
(16,24,['Then more trees bloom.','Soon, cash is everywhere.']),
(24,32,['Everyone can spend more.','But the shelves have not grown.']),
(32,40,['More money cannot instantly create','more bread, homes, or workers.']),
(40,48,['With the same goods and far more cash,','prices could soar.']),
(48,56,['A mountain of banknotes might barely buy','a single loaf.']),
(56,64,['Real wealth comes from growing food,','building homes, and delivering what people need.']),
(64,72,['Even a millionaire could face an empty shop,','and go home hungry.']),
(72,78,['Would you want this world?','Tell us: yes or no.'])]
engine=Kokoro(str(R/'models'/'kokoro-v1.0.onnx'),str(R/'models'/'voices-v1.0.bin'))
records=[]; allcues=[]
for i,(start,end,phrases) in enumerate(scenes):
 samples=[]
 for j,phrase in enumerate(phrases):
  path=R/'audio'/f'voice_{i+1:02}_{j+1}.wav'
  if path.exists(): x,rate=sf.read(path,dtype='float32')
  else:
   x,rate=engine.create(phrase,voice='af_heart',speed=1.0,lang='en-us',sentence_pause=.22,clause_pause=.16)
   sf.write(path,x,rate)
  samples.append((phrase,x,rate))
 duration=sum(len(x)/rate for _,x,rate in samples)+.24*(len(samples)-1)
 assert duration<=end-start-.45, f'Scene {i+1} natural speech {duration:.2f}s exceeds slot; rewrite, never speed up'
 cursor=start+.25
 for phrase,x,rate in samples:
  allcues.append({'start':cursor,'end':cursor+len(x)/rate,'text':phrase,'file':f'voice_{i+1:02}_{samples.index((phrase,x,rate))+1}.wav' if False else None}); cursor+=len(x)/rate+.24
 for j,cue in enumerate(allcues[-len(samples):]): cue['file']=f'voice_{i+1:02}_{j+1}.wav'
 records.append({'scene':i+1,'start':start,'end':end,'speech_duration':duration,'speech_end':cursor-.24})
 print('Natural narration',i+1,round(duration,2),'seconds',flush=True)
 (R/'audio'/'speech_timeline.json').write_text(json.dumps({'engine':'Kokoro ONNX 0.6.1','model':'Kokoro 82M v1.0','voice':'af_heart','speed':1.0,'speedup_applied':False,'cues':allcues,'scenes':records},indent=2))
(R/'final'/'narration.txt').write_text('\n\n'.join(' '.join(p) for _,_,p in scenes))
