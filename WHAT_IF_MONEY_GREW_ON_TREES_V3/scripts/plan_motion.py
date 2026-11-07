"""Prepare repaired paths and continuous swing/stance tracks; no geometry creation."""
from pathlib import Path
import ast,json,numpy as np
from scipy.ndimage import gaussian_filter1d
R=Path(__file__).resolve().parents[1]; src=(R.parent/'V2/scripts/build.py').read_text(); tree=ast.parse(src)
paths=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='paths' for t in n.targets))
paths[2]=[(0,.5,-12.27),(25,.5,-12.27),(27,-1.15,-12.27),(29,-1.15,-12.27),(30.35,-.4,-12.32),(32,-.4,-12.32),(34,.5,-12.27),(42,.5,-12.27),(44,.65,-12.27),(46,.5,-12.27),(78,.5,-12.27)]
paths[3]=[(0,-4.8,1.15),(54,-4.8,1.15),(56,-4.1,1.15),(59,-4.1,1.15),(62,-2.15,1.3),(78,-2.15,1.3)]
paths[4]=[(0,4,3),(55,4,3),(58,4.5,2.85),(64,4.5,2.85),(68,5.5,3),(78,5.5,3)]
paths[5]=[(t,(-7.0 if t==23 else x),(-5.6 if t==23 else y)) for t,x,y in paths[5]]
paths[5].insert(4,(18.5,-2.7,-4.2))
paths[6]=[(t,(4.2 if t in [27,32,36,42] else x),(-15.6 if t==32 else -16.8 if t in [36,42] else y)) for t,x,y in paths[6]]
paths[5][0]=(0,-6.7,-3.8); paths[5][1]=(9,-6.7,-3.8)
paths[5]=[(t,(1.1 if t in [36,42] else 4.0 if t==48 else x),(-16.2 if t in [36,42] else -16.1 if t==48 else y)) for t,x,y in paths[5]]
paths[6]=[(t,(5.8 if t>=48 else x),(-15.6 if t>=48 else y)) for t,x,y in paths[6]]
paths[6]=[(0,5,-4),(10,5,-4),(15,3.5,-1.8),(20,3.5,-1.8),(23,5.5,-3.7),(24,5.5,-4.7),(26,5.5,-4.7),(27.5,3.4,-8),(29.5,3.4,-8),(34,3.4,-16.6),(36,4.2,-16.8),(42,4.2,-16.8),(48,5.8,-15.6),(78,5.8,-15.6)]
original_steps=json.loads((R.parent/'V2/reports/full_motion_metrics.json').read_text())['footstep_events']
N=2340; times=np.arange(N)/30; roots=np.zeros((N,7,3)); yaw=np.zeros((N,7)); feet=np.zeros((N,7,2,3)); fyaw=np.zeros((N,7,2)); stance=np.ones((N,7,2),bool); events=[]
def ease(u): u=np.clip(u,0,1); return u*u*(3-2*u)
for i,path in enumerate(paths):
 for a,b in zip(path,path[1:]):
  mask=(times>=a[0])&(times<=b[0]); u=ease((times[mask]-a[0])/(b[0]-a[0])); roots[mask,i,:2]=np.array(a[1:])+(np.array(b[1:])-a[1:])*u[:,None]
 roots[:,i,:2]=gaussian_filter1d(roots[:,i,:2],1.5,axis=0,mode='nearest')
 v=np.gradient(roots[:,i,:2],axis=0); speeds=np.linalg.norm(v,axis=1)*30; angle=np.zeros(N); old=0
 for k in range(N):
  if speeds[k]>.025: old=np.arctan2(-v[k,0],v[k,1])
  angle[k]=old
 # Established facing overrides are approached gradually through the body.
 if i==2: angle[:]=np.pi
 if i==0:
  angle[(times>=3.5)&(times<=5.9)]=-.1; angle[times>=30]=0
 if i==1: angle[(times>=11)&(times<=13.2)]=0
 if i==3: angle[:]=0
 if i==4: angle[(times>=58)&(times<=64)]=np.pi
 angle=gaussian_filter1d(np.unwrap(angle),4,mode='nearest'); yaw[:,i]=angle
 F=np.stack([-np.sin(angle),np.cos(angle)],axis=1); right=np.stack([np.cos(angle),np.sin(angle)],axis=1)
 # Plan alternating landing events in advance, completing each swing even if the root stops.
 ds=np.r_[0,np.cumsum(np.linalg.norm(np.diff(roots[:,i,:2],axis=0),axis=1))]
 boundaries=np.where(np.diff((speeds>.025).astype(int))!=0)[0]+1
 segments=[]; start=0 if speeds[0]>.025 else None
 for k in boundaries:
  if speeds[k]>.025: start=k
  elif start is not None: segments.append((start,k)); start=None
 if start is not None: segments.append((start,N-1))
 for side in range(2):
  sign=-1 if side==0 else 1
  feet[:,i,side,:2]=roots[0,i,:2]+right[0]*sign*.14+F[0]*(-.045 if side==0 else .045); fyaw[:,i,side]=angle[0]
 last_end=[-1,-1]; turn=0
 for sa,sb in segments:
  total=ds[sb]-ds[sa]; targets=list(np.arange(.20,total,.37))
  lands=[int(np.searchsorted(ds,ds[sa]+d)) for d in targets]
  if not lands or lands[-1]<sb-4: lands.append(min(N-1,sb+3))
  lands.append(min(N-1,sb+10))
  audio_lands=[(round(e['time']*30),0 if e['side']<0 else 1) for e in original_steps if i in [0,1,3,4] and e['actor']==i and sa-4<=round(e['time']*30)<=sb+4]
  scheduled=audio_lands if audio_lands else [(land,(turn+j)%2) for j,land in enumerate(lands)]
  for side in range(2):
   last=max([f for f,s in scheduled if s==side] or [-100])
   if last<sb-5: scheduled.append((min(N-1,sb+4+side*7),side))
  for land,side in sorted(scheduled):
   turn+=1; sign=-1 if side==0 else 1
   begin=max(last_end[side]+1,land-10,sa-7)
   if land<=begin: continue
   future=min(sb,land+2); target=roots[future,i,:2]+right[future]*sign*.14+F[future]*.055
   if np.linalg.norm(target-feet[max(0,begin-1),i,side,:2])<.025: continue
   old=feet[max(0,begin-1),i,side,:2].copy(); oldyaw=fyaw[max(0,begin-1),i,side]; newyaw=angle[future]
   u=np.linspace(0,1,land-begin+1); w=ease(u)
   feet[begin:land+1,i,side,:2]=old+(target-old)*w[:,None]; feet[land+1:,i,side,:2]=target
   feet[begin:land+1,i,side,2]=.14*np.sin(np.pi*u)**1.4
   fyaw[begin:land+1,i,side]=oldyaw+(newyaw-oldyaw)*w; fyaw[land+1:,i,side]=newyaw
   stance[begin:land,i,side]=False; last_end[side]=land
   events.append({'actor':i,'side':side,'begin_frame':begin+1,'land_frame':land+1,'time':land/30})
np.savez_compressed(R/'reports/motion_plan.npz',roots=roots,yaw=yaw,feet=feet,foot_yaw=fyaw,stance=stance)
(R/'reports/locomotion_plan.json').write_text(json.dumps({'paths':paths,'events':events,'note':'Continuous scheduled swings finish at stops; world-space stance anchors. V2 soundtrack is unchanged; no new Foley is synthesized.'},indent=2,default=lambda x:x.item()))
print('PLANNED',len(events),'foot placements')
