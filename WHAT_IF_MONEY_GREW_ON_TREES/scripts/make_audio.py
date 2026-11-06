from pathlib import Path
import subprocess,json, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
R=Path(__file__).resolve().parents[1]; A=R/'audio'; rate=48000; N=rate*78
# Each phrase is synthesized separately so subtitle boundaries follow the actual speech.
scenes=[(0,7,['What if money actually grew on trees?']),
(7,15,['At first, everyone would think',"they had just become rich."]),
(15,23,['Then every tree on Earth','starts producing cash.']),
(23,31,['Suddenly, almost everyone has more money', 'than they can spend.']),
(31,39,["But there is one problem.","More money does not mean more food,",'houses, or resources.']),
(39,47,['As cash becomes unlimited,', 'prices could rise faster and faster.']),
(47,55,['Eventually, those piles of money', 'might barely buy anything.']),
(55,64,["Because real wealth is not just money.", 'It is the things people can actually produce.']),
(64,72,['The richest person in this world', 'might still be unable to buy dinner.']),
(72,78,['Would you still want money to grow on trees?', 'Tell us: yes or no?'])]
voice=np.zeros(N,np.float32); cues=[]; timeline=[]
for si,(start,end,phrases) in enumerate(scenes):
 data=[]
 for pi,phrase in enumerate(phrases):
  txt=A/f's{si+1:02}_{pi+1}.txt'; txt.write_text(phrase)
  wav=A/f's{si+1:02}_{pi+1}.wav'
  subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i',f'flite=textfile={txt}:voice=slt','-ar',str(rate),'-y',str(wav)],check=True)
  sr,x=wavfile.read(wav); x=x.astype(np.float32)/32768
  # Remove only surplus synthesis silence; retain natural speech edges.
  nz=np.flatnonzero(abs(x)>.006)
  if len(nz): x=x[max(0,nz[0]-int(.06*rate)):min(len(x),nz[-1]+int(.14*rate))]
  data.append(x)
 total=sum(len(x) for x in data)/rate+.22*(len(data)-1)
 available=end-start-1.05
 if total>available:
  factor=(available-.22*(len(data)-1))/(total-.22*(len(data)-1))
  # Supported local time stretch preserves speech pitch.
  for pi,x in enumerate(data):
   tmp=A/'stretch_in.wav'; out=A/'stretch_out.wav'; wavfile.write(tmp,rate,(x*32767).astype(np.int16))
   subprocess.run(['ffmpeg','-v','error','-i',str(tmp),'-af',f'atempo={1/factor}','-y',str(out)],check=True)
   _,y=wavfile.read(out); data[pi]=y.astype(np.float32)/32768
 cursor=start+.65
 for phrase,x in zip(phrases,data):
  k=int(cursor*rate); voice[k:k+len(x)]+=x
  cues.append((cursor,cursor+len(x)/rate,phrase)); cursor+=len(x)/rate+.22
 timeline.append({'scene':si+1,'start':start,'end':end,'speech_end':cursor-.22,'phrases':phrases})
voice*=.82/max(.01,np.max(abs(voice)))
wavfile.write(A/'narration.wav',rate,(voice*32767).astype(np.int16))
# Entirely original synthesized score: warm arpeggios, deep pulse, evolving harmony.
rng=np.random.default_rng(777); music=np.zeros(N,np.float32); effects=np.zeros(N,np.float32)
def add(dest,x,start,gain=1):
 a=int(start*rate); b=min(N,a+len(x))
 if a<N: dest[a:b]+=x[:b-a]*gain
chords=[[146.832,174.614,220,293.665],[130.813,164.814,195.998,261.626],[110,146.832,174.614,220],[116.541,146.832,174.614,233.082]]
for beat in np.arange(0,78,.5):
 idx=int(beat/.5); chord=chords[int(beat//8)%4]; f=chord[idx%4]*(2 if idx%3==0 else 1)
 tt=np.arange(int(rate*1.3))/rate
 wave=(np.sin(2*np.pi*f*tt)+.22*np.sin(2*np.pi*f*2*tt))*np.exp(-tt*4)*(1-np.exp(-tt*90))
 gain=.035 if beat<64 or beat>=72 else .012
 add(music,wave,beat,gain)
for start in range(0,78,4):
 tt=np.arange(rate*4)/rate; f=chords[(start//8)%4][0]/2
 pad=(np.sin(2*np.pi*f*tt)+.3*np.sin(2*np.pi*f*1.002*tt))*np.sin(np.pi*tt/4)**2
 add(music,pad,start,.032 if start<64 else .014)
# Soft city wind; spectral rustles; birds; wheel / car swishes; price impacts.
noise=rng.standard_normal(N).astype(np.float32)
from scipy.signal import butter,sosfilt
wind=sosfilt(butter(2,450,fs=rate,output='sos'),noise)*.009
effects+=wind
for t in [1.3,2.1,4.4,56.4,58.2,74.3]:
 tt=np.arange(int(rate*.22))/rate; chirp=np.sin(2*np.pi*(1700*tt+2300*tt*tt))*np.sin(np.pi*tt/.22)**2
 add(effects,chirp,t,.025)
for t in np.arange(9,64,1.1):
 tt=np.arange(int(rate*.35))/rate; rustle=rng.standard_normal(len(tt)); rustle=sosfilt(butter(2,[1700,6500],btype='bandpass',fs=rate,output='sos'),rustle)
 add(effects,rustle*np.sin(np.pi*tt/.35)**2,t,.017)
for t in [8,16,24,32,40,44,48,55,64,72]:
 tt=np.arange(int(rate*.8))/rate
 if t in [32,40,44,48]:
  impact=np.sin(2*np.pi*(100*tt-35*tt**2))*np.exp(-tt*7)+.4*np.sin(2*np.pi*1100*tt)*np.exp(-tt*20)
 else: impact=sosfilt(butter(2,1600,fs=rate,output='sos'),rng.standard_normal(len(tt)))*np.sin(np.pi*tt/.8)**2
 add(effects,impact,t,.07)
for t in [12,19,25,29]:
 tt=np.arange(int(rate*.5))/rate
 cheer=sum(np.sin(2*np.pi*(f*tt+30*tt**2)) for f in [310,420,510])/3*np.sin(np.pi*tt/.5)**2
 add(effects,cheer,t,.018)
for t in [18,27,42]:
 tt=np.arange(rate*2)/rate; whoosh=sosfilt(butter(2,600,fs=rate,output='sos'),rng.standard_normal(len(tt)))*np.sin(np.pi*tt/2)**2
 add(effects,whoosh,t,.04)
# Duck underneath narration, and leave a quiet dramatic beat in scene nine.
env=sosfilt(butter(1,5,fs=rate,output='sos'),abs(voice))
duck=1-np.minimum(.72,env*7)
music*=duck
fade=np.minimum(np.arange(N)/rate/1.5,(N-1-np.arange(N))/rate/1.7).clip(0,1)
music*=fade; effects*=fade
for name,x in [('music_original.wav',music),('effects_original.wav',effects)]: wavfile.write(A/name,rate,(x.clip(-1,1)*32767).astype(np.int16))
mono=voice+music+effects
# Subtle stereo bed; narration remains centered.
stereo=np.column_stack([voice+music+effects,voice+np.roll(music,240)+np.roll(effects,100)])
stereo*=min(1,.94/np.max(abs(stereo))); wavfile.write(A/'final_mix.wav',rate,(stereo*32767).astype(np.int16))
def stamp(t):
 ms=round(t*1000); return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(R/'final'/'subtitles.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{s}' for i,(a,b,s) in enumerate(cues))+'\n')
(R/'final'/'narration.txt').write_text('\n\n'.join(' '.join(p) for _,_,p in scenes))
(R/'reports'/'audio_timeline.json').write_text(json.dumps({'scenes':timeline,'cues':cues,'voice':'local Flite slt','duration':78,'peak':float(np.max(abs(stereo))),'license':'Original procedural score and effects; no external audio assets'},indent=2))
print('Audio complete:',len(cues),'speech cues; peak',np.max(abs(stereo)))
