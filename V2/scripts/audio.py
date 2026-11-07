from pathlib import Path
import json,sys,numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly,butter,sosfilt
R=Path(__file__).resolve().parents[1]; sr=48000; N=78*sr; rng=np.random.default_rng(2026)
timeline=json.loads((R/'audio'/'speech_timeline.json').read_text()); voice=np.zeros(N,np.float32)
for cue in timeline['cues']:
 rate,x=wavfile.read(R/'audio'/cue['file']); x=x.astype(np.float32)/32768; x=resample_poly(x,sr,rate); i=round(cue['start']*sr); voice[i:i+len(x)]+=x
voice*=.76/max(.001,np.max(abs(voice)))
music=np.zeros(N,np.float32); fx=np.zeros(N,np.float32); events=[]
def add(dest,x,time,gain=1):
 i=round(time*sr); end=min(N,i+len(x))
 if 0<=i<N: dest[i:end]+=x[:end-i]*gain
def tone(freq,duration,kind='bell'):
 t=np.arange(round(duration*sr))/sr
 if kind=='pad': env=np.sin(np.pi*t/duration)**1.3; x=np.sin(2*np.pi*freq*t)+.25*np.sin(2*np.pi*freq*2.003*t)
 else: env=(1-np.exp(-t*90))*np.exp(-t*(3.2 if kind=='bell' else 5)); x=np.sin(2*np.pi*freq*t)+.23*np.sin(2*np.pi*freq*2*t)+.08*np.sin(2*np.pi*freq*3*t)
 return x*env
# Distinct harmonic and rhythmic sections, no reused generic whole-film cue loop.
sections=[(0,8,[146.83,174.61,220],1.0,.014),(8,16,[174.61,220,261.63],.5,.022),(16,24,[196,246.94,293.66],.375,.022),(24,32,[164.81,196,246.94],.5,.022),(32,40,[146.83,174.61,207.65],.75,.017),(40,48,[138.59,164.81,196],.25,.022),(48,56,[130.81,155.56,196],1.5,.013),(56,64,[130.81,164.81,196],.8,.020),(64,72,[110,130.81,164.81],2.0,.009),(72,78,[130.81,164.81,196,261.63],.75,.023)]
for si,(a,b,chord,pulse,gain) in enumerate(sections):
 for j,t in enumerate(np.arange(a,b,pulse)):
  f=chord[(j*(1 if si%2 else 2)+si)%len(chord)]*(2 if j%5==1 else 1)
  add(music,tone(f,1.4),t,gain)
 for f in chord:
  add(music,tone(f/2,min(8,b-a),'pad'),a,gain*.45)
 if si in [3,5]:
  for t in np.arange(a,b,.5):
   tt=np.arange(int(sr*.16))/sr; add(music,np.sin(2*np.pi*(90*tt-120*tt**2))*np.exp(-tt*30),t,.022)
# Ambient wind is quiet; Foley events derive from visible actions.
noise=rng.standard_normal(N).astype(np.float32); fx+=sosfilt(butter(2,380,fs=sr,output='sos'),noise)*.005

def rustle(time,duration=.3,gain=.04,why='cash'):
 t=np.arange(round(sr*duration))/sr; x=sosfilt(butter(2,[1400,6500],btype='bandpass',fs=sr,output='sos'),rng.standard_normal(len(t)))
 add(fx,x*np.sin(np.pi*t/duration)**2,time,gain); events.append({'time':time,'type':'paper/leaf rustle','motivation':why})
for t,why in [(.4,'bill growth'),(1.1,'bill unfolding'),(5.5,'hero grasps and plucks bill'),(6.1,'hero carries bill'),(12.2,'second bill pluck'),(28.5,'cash at market'),(30.4,'bread handoff at counter'),(49,'offering cash stack'),(73,'falling cash at original tree')]: rustle(t,why=why)
# First reveal is soft and curious, not a repeating impact on each chapter.
add(fx,tone(880,.8),1.2,.045); add(fx,tone(1320,.7),1.35,.025)
for t in [42,44,46]:
 tt=np.arange(round(sr*.4))/sr; click=sosfilt(butter(2,4000,fs=sr,output='sos'),rng.standard_normal(len(tt)))*np.exp(-tt*35)
 add(fx,click,t,.10); add(fx,tone(1100+(t-42)*80,.32),t,.05); events.append({'time':t,'type':'wood/card flip + price tick','motivation':'visible bread price changes'})
metrics_path=R/'reports'/('test_motion_metrics.json' if '--test' in sys.argv else 'full_motion_metrics.json')
if not metrics_path.exists(): metrics_path=R/'reports'/'test_motion_metrics.json'
metrics=json.loads(metrics_path.read_text())
visible={0:[(2,4),(6,8),(24,30)],1:[(8,11),(13,16)],3:[(55,56),(59,62)],4:[(55,58)]}
for e in metrics['footstep_events']:
 if not any(a<=e['time']<=b for a,b in visible.get(e['actor'],[])): continue
 t=np.arange(round(sr*.12))/sr; step=sosfilt(butter(2,1400,fs=sr,output='sos'),rng.standard_normal(len(t)))*np.exp(-t*35)+.3*np.sin(2*np.pi*130*t)*np.exp(-t*40)
 add(fx,step,e['time'],.07); events.append({'time':e['time'],'type':'footstep','actor':e['actor'],'motivation':'stance onset in animation'})
for time in [16.2,19.5,24,32,48,56,64,72]:
 dur=.25; tt=np.arange(round(sr*dur))/sr; sweep=sosfilt(butter(2,1600,fs=sr,output='sos'),rng.standard_normal(len(tt)))*np.sin(np.pi*tt/dur)**2
 add(fx,sweep,time,.018); events.append({'time':time,'type':'subtle transition','motivation':'editorial cut'})
for time in [56.4,57.1,60.3]:
 tt=np.arange(round(sr*.18))/sr; add(fx,np.sin(2*np.pi*(1900*tt+1400*tt**2))*np.sin(np.pi*tt/.18)**2,time,.015)
# Delivery engine appears only when the delivery van is the subject.
t=np.arange(sr*3)/sr; engine=(np.sin(2*np.pi*70*t)+.3*np.sin(2*np.pi*140*t))*np.sin(np.pi*t/3)**2; add(fx,engine,61,.025)
# Farm pick and beam placement happen on screen.
rustle(57.2,.25,.035,'farmer picks produce'); add(fx,tone(170,.25),63.4,.045)
# Sustained paper texture only under the wide money bloom, not random repeated cash hits.
t=np.arange(sr*8)/sr; add(fx,sosfilt(butter(2,[1800,4500],btype='bandpass',fs=sr,output='sos'),rng.standard_normal(len(t)))*np.sin(np.pi*t/8)**2,16,.012)
env=sosfilt(butter(1,5,fs=sr,output='sos'),abs(voice)); duck=1-np.minimum(.8,env*8); music*=duck
fade=np.minimum(np.arange(N)/sr/.35,(N-1-np.arange(N))/sr/1.2).clip(0,1); music*=fade; fx*=fade
stereo=np.column_stack([voice+music+fx,voice+np.roll(music,140)+np.roll(fx,70)]); stereo*=min(1,.93/max(.001,abs(stereo).max()))
for name,x in [('narration.wav',voice),('music.wav',music),('foley.wav',fx),('mix.wav',stereo)]: wavfile.write(R/'audio'/name,sr,(x.clip(-1,1)*32767).astype(np.int16))
(R/'reports'/'foley_events.json').write_text(json.dumps(events,indent=2))
def stamp(t):
 m=round(t*1000); return f'{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02},{m%1000:03}'
(R/'final'/'subtitles.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(timeline['cues']))+'\n')
print('V2 audio mix ready; neural narration speed 1.0; matched Foley events',len(events),'peak',abs(stereo).max())
