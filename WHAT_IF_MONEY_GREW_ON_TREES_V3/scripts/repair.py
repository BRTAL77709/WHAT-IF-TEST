"""Repair animation on the actual V2 file. Never creates, edits or replaces mesh/material data."""
import bpy,math,json,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector,Euler,Quaternion
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]; S=bpy.context.scene; N=2340
assert Path(bpy.data.filepath).name=='V2_CITY.blend'
S.frame_set(1); rigmap=json.loads((R/'reports/rig_map.json').read_text()); baseline=np.load(R/'reports/V2_transforms.npz'); names=list(baseline['names']); old=baseline['transforms']; plan=np.load(R/'reports/motion_plan.npz'); roots=plan['roots'].copy(); yaws=plan['yaw']; feet=plan['feet'].copy(); fyaw=plan['foot_yaw']; stance=plan['stance']
O={o.name:o for o in S.objects}; tracks={}; prev={}; reaches=[]; foot_events=[]
def sm(u): u=max(0,min(1,float(u))); return u*u*(3-2*u)
def mix(a,b,u): return Vector(a).lerp(Vector(b),sm(u))
def oldpos(name,k): return Vector(old[k,names.index(name),:3])
def scalar_smooth(a,r=4):
 w=np.exp(-np.arange(-r,r+1)**2/(2*(r/2)**2)); w/=w.sum(); return np.convolve(np.pad(a,(r,r),mode='edge'),w,mode='valid')
def record(o,k,p=None,e=None,s=None):
 if isinstance(o,str): o=O[o]
 if p is not None: o.location=p
 if e is not None:
  e=Euler(tuple(e),'XYZ')
  if o.name in prev: e.make_compatible(prev[o.name])
  prev[o.name]=e.copy(); o.rotation_euler=e
 if s is not None: o.scale=s
 data=tracks.setdefault(o.name,{'location':[],'rotation_euler':[],'scale':[]})
 for prop in data: data[prop].append(tuple(getattr(o,prop)))
def seg(o,k,a,b,r):
 v=Vector(b)-Vector(a); record(o,k,(Vector(a)+Vector(b))/2,v.to_track_quat('Z','Y').to_euler(),(r,r,v.length))
def ik(a,b,L,pole):
 v=Vector(b)-a; dist=v.length; d=min(dist,2*L-.0001); direction=v.normalized() if dist>1e-6 else Vector((0,0,-1)); bend=Vector(pole)-direction*Vector(pole).dot(direction)
 if bend.length<.001: bend=direction.cross(Vector((1,0,0)))
 bend.normalize(); return a+direction*d/2+bend*math.sqrt(max(0,L*L-d*d/4)),a+direction*d, max(0,dist-d)
# Exact triangles, not replacement geometry. Ground excludes plant leaves and shelves above .61m.
verts=[]; polys=[]; gv=[]; gp=[]
for o in S.objects:
 if o.type!='MESH' or not o.name.startswith('Static environment /'): continue
 off=len(verts); coords=[o.matrix_world@v.co for v in o.data.vertices]; verts.extend(coords); polys.extend([tuple(off+j for j in p.vertices) for p in o.data.polygons])
 for p in o.data.polygons:
  q=[coords[j] for j in p.vertices]
  if 'Foliage' not in o.name and max(v.z for v in q)<.61 and min(v.z for v in q)>-.1:
   g=len(gv); gv.extend(q); gp.append(tuple(range(g,g+len(q))))
bvh=BVHTree.FromPolygons(verts,polys); ground_bvh=BVHTree.FromPolygons(gv,gp)
def ground(x,y):
 p,n,idx,d=ground_bvh.ray_cast(Vector((float(x),float(y),.72)),Vector((0,0,-1)),1)
 return float(p.z)+.003 if p else .013
# Elevation smoothly interpolates during swing; planted anchors never move.
for i in range(7):
 for side in range(2):
  g=np.array([ground(*p[:2]) for p in feet[:,i,side]])
  run=None
  for k in range(N):
   if not stance[k,i,side] and run is None: run=k
   if stance[k,i,side] and run is not None:
    g[run:k+1]=g[max(0,run-1)]+(g[k]-g[max(0,run-1)])*np.array([sm(u) for u in np.linspace(0,1,k-run+1)]); run=None
  feet[:,i,side,2]+=g+.14
 base=np.array([ground(*p[:2]) for p in roots[:,i]])
 base=scalar_smooth(base,7)
 speed=np.linalg.norm(np.gradient(roots[:,i,:2],axis=0),axis=1)*30
 for k in range(N):
  F=np.array([-math.sin(yaws[k,i]),math.cos(yaws[k,i]),0]); right=np.array([F[1],-F[0],0]); wanted=base[k]+(.012*math.sin(k*.35) if speed[k]>.1 else .002*math.sin(k/19+i))
  ceilings=[]
  for side,sign in enumerate([-1,1]):
   delta=feet[k,i,side,:2]-(roots[k,i,:2]+right[:2]*sign*.14); ceilings.append(feet[k,i,side,2]+math.sqrt(max(.001,.919**2-float(delta@delta)))-.88)
  roots[k,i,2]=min(wanted,*ceilings)
# Reuse body performance, correcting relative transforms rather than changing appearance.
oldroots=np.stack([old[:,names.index(r['root']),:3] for r in rigmap],axis=1)
oldhand={}
for i,r in enumerate(rigmap):
 for side in range(2):
  a=old[:,names.index(r['arms'][side][2]),:3]-oldroots[:,i]
  oldhand[i,side]=np.stack([scalar_smooth(a[:,j],6) for j in range(3)],axis=1)
head_angles={}
for i,r in enumerate(rigmap):
 head=np.array([tuple(Quaternion(tuple(q)).to_euler()) for q in old[:,names.index(r['head']),3:7]])
 root=np.array([tuple(Quaternion(tuple(q)).to_euler()) for q in old[:,names.index(r['root']),3:7]])
 head[:,2]=np.unwrap(head[:,2]-root[:,2])
 head_angles[i]=np.stack([scalar_smooth(np.unwrap(head[:,j]),6) for j in range(3)],axis=1)
# Fixed sources for the existing two held bills; no mesh changes.
hero_note=O['V2 Hero banknote GRIP CORNER']; other_note=O['V2 Harvester banknote GRIP CORNER']
cam=S.camera; bread=sorted([o for o in S.objects if o.name.startswith('V2 Bread inventory')],key=lambda o:o.name)
windfall=sorted([o for o in S.objects if o.name.startswith('V2 Windfall')],key=lambda o:o.name); finalfall=sorted([o for o in S.objects if o.name.startswith('V2 Final tree fall')],key=lambda o:o.name)
# Keep props continuous through all visibility changes; no scale-to-zero inventory disposal.
# A sold loaf is moved on a continuous shelf-to-counter-to-buyer path.
leafdata=[]
trees=[(0,0),(-6,0),(6,0),(-5,5),(5,5),(-15,5),(15,5),(-15,-5),(15,-5),(-6,-4),(6,-4),(-5,15),(5,15)]
for j,o in enumerate(windfall+finalfall):
 k0=next((k for k in range(N) if old[k,names.index(o.name),7]>.05),0)
 if o in finalfall: k0=2160+(j%60); tx,ty=0,0; h=3.6
 else:
  original=old[min(N-1,k0+10),names.index(o.name),:3]; tx,ty=min(trees,key=lambda xy:(xy[0]-original[0])**2+(xy[1]-original[1])**2); h=4.0 if tx==ty==0 else 3.1
 angle=j*2.39996; p=Vector((tx+1.35*math.cos(angle),ty+1.35*math.sin(angle),h)); v=Vector((.18*math.sin(j),.15*math.cos(j),0)); leafdata.append({'object':o,'start':k0,'p':p,'v':v,'settled':False,'angle':angle,'base_scale':(.5,.24,.015) if o in finalfall else (.55,.27,.015)})
# Baseline exact lens curve and scene cuts are retained. Correct only two demonstrably colliding paths.
cuts=[2,8,16,19.5,24,32,40,47,48,52.5,56,58.6,61.2,64,68,72]
for k in range(N):
 t=k/30; S.frame_set(k+1); hands={}; body={}
 for i,r in enumerate(rigmap):
  P=Vector(roots[k,i]); yaw=float(yaws[k,i]); F=Vector((-math.sin(yaw),math.cos(yaw),0)); right=Vector((F.y,-F.x,0)); oldroot=Vector(oldroots[k,i]); torso=O[r['torso']]; oldtorso=oldpos(r['torso'],k)-oldroot
  crouch=.31*sm((t-26)/1)* (1-sm((t-28.5)/.8)) if i==2 else (.41*sm((t-55.8)/.9)*(1-sm((t-57.6)/1))+.18*sm((t-61.5)/.7)*(1-sm((t-63.3)/.9))) if i==3 else 0
  # Contact reach comes from a supported torso lean, not changing limb lengths.
  lean=(.13*sm((t-29)/1)*(1-sm((t-31)/1)) if i==2 else .17*sm((t-29.2)/.5)*(1-sm((t-34.6)/.8)) if i==0 else (.24*sm((t-55.8)/1)*(1-sm((t-58)/1))+.16*sm((t-61.5)/.7)*(1-sm((t-63.3)/.9))) if i==3 else 0)
  P.z-=crouch; hips=P+Vector((0,0,.88)); theta=(-.22 if i==3 else -.1)*sm((t-(55.8 if i==3 else 26))/.8)*(1-sm((t-(58 if i==3 else 29))/.8)) if i in [2,3] else 0
  body[i]=(P,F,right,yaw)
  record(r['root'],k,P,(0,0,yaw),(1,1,1)); record(torso,k,P+Vector((0,0,1.16))+F*lean,(theta,0,yaw),(.46,.34,.58))
  oldhead=oldpos(r['head'],k)-oldroot; hp=P+oldhead+F*lean; head_e=Euler(tuple(head_angles[i][k])); head_e.z+=yaw; head_e.x+=theta
  record(r['head'],k,hp,head_e,(.235,.215,.25)); record(r['hair'],k,hp+head_e.to_matrix()@Vector((0,0,.17)),head_e,(.238,.22,.14))
  for en,sign in zip(r['eyes'],[-1,1]): record(en,k,hp+head_e.to_matrix()@Vector((sign*.08,.205,.035)),head_e,(.028,.018,.032))
  for side,sign in enumerate([-1,1]):
   ankle=Vector(feet[k,i,side]); hip=hips+right*sign*.14
   knee,tip,err=ik(hip,ankle,.46,F); reaches.append({'frame':k+1,'actor':i,'limb':'leg','side':side,'error':err}) if err>.002 else None
   seg(r['legs'][side][0],k,hip,knee,.085); seg(r['legs'][side][1],k,knee,tip,.075)
   record(r['legs'][side][2],k,tip-Vector((0,0,.07)),(0,0,float(fyaw[k,i,side])),(.20,.34,.14))
   shoulder=P+right*sign*.31+Vector((0,0,1.43))+F*lean; idle=P+right*sign*.43+Vector((0,0,.97))+F*(-.5*(ankle-P).dot(F) if np.linalg.norm(roots[min(k+1,N-1),i,:2]-roots[max(0,k-1),i,:2])>.003 else .03*math.sin(t*1.3+i))
   hand=idle.copy()
   if i==0 and side==1:
    grip=Vector((.25,-2,1.98)); carry=P+right*.33+F*.48+Vector((0,0,1.43)); hand=mix(idle,grip,(t-4.1)/1) if t<5.5 else mix(grip,carry,(t-5.5)/.8)
    if t>=30:
     offer=Vector((-.05,-13.35,1.65)); hand=mix(carry,offer,(t-30)/1.5) if t<37.5 else mix(offer,carry,(t-37.5)/.8)
     react=P+right*.55+Vector((0,0,1.5+.07*math.sin(t*2)))
     if 39.5<t<48: hand=mix(hand,react,(t-39.5)/.7) if t<47.2 else mix(react,offer,(t-47.2)/.8)
     if 48<=t<56: hand=offer if t<55 else mix(offer,carry,t-55)
   elif i==0 and side==0:
    shared=Vector((-.85,-13.17,1.52)); carry=P-right*.35+F*.45+Vector((0,0,1.18)); counter=Vector((-.85,-13.17,1.49))
    if t<31.2: hand=mix(idle,shared,(t-29.8)/.6)
    elif t<32: hand=mix(shared,carry,(t-31.2)/.8)
    elif t<33.2: hand=carry
    elif t<34.4: hand=mix(carry,counter,(t-33.2)/1.2)
    else: hand=mix(counter,idle,(t-34.4)/.9)
   elif i==1 and side==1:
    grip=Vector((1.15,-2,1.98)); carry=P+right*.35+F*.45+Vector((0,0,1.4)); hand=mix(idle,grip,(t-11)/.8) if t<12.2 else mix(grip,carry,(t-12.2)/.8)
   elif i==2:
    if side==1:
     shelf=Vector((-1.8,-11.65,.65)); shared=Vector((-.85,-13.17,1.52))
     if t<28: hand=mix(idle,shelf,(t-26.5)/1.2)
     elif t<30: hand=mix(shelf,shared,(t-28)/2)
     elif t<30.4: hand=shared
     else: hand=mix(shared,idle,(t-30.4)/1.0)
    else:
     angle=sum(.20*math.sin(math.pi*(t-c+.18)/.36) for c in [42,44,46] if c-.18<t<c+.18)
     target=Vector((1.1,-12.64,2.12))+Euler((angle,0,0)).to_matrix()@Vector((0,-.01,-.37))
     hand=mix(idle,target,(t-39.1)/.9) if t<47.2 else mix(target,idle,(t-47.2)/1.0)
   elif i==3 and side==1:
    crop=Vector((-4.1,1.8,.55)); carry=P+right*.32+F*.3+Vector((0,0,1.35)); deposit=Vector((-2,2.1,.98))
    if t<57.5: hand=mix(idle,crop,(t-56)/1.2)
    elif t<59: hand=mix(crop,carry,(t-57.5)/1.5)
    elif t<62: hand=carry
    elif t<63.2: hand=mix(carry,deposit,(t-62)/1.2)
    else: hand=mix(deposit,idle,(t-63.2)/1)
   elif i==4:
    # Two-hand contact on a rigid 3m beam, placed on the reachable lower house frame.
    center=mix((4.2,2.5,1.5),(4.5,2.18,1.82),(t-58)/4)
    contact=center+right*sign*.35
    hand=mix(idle,contact,(t-57.2)/.8) if t<63.2 else mix(contact,idle,(t-63.2)/.8)
   elbow,wrist,err=ik(shoulder,hand,.43,right*sign+F*.15)
   if err>.002: reaches.append({'frame':k+1,'actor':i,'limb':'arm','side':side,'error':err})
   seg(r['arms'][side][0],k,shoulder,elbow,.075); seg(r['arms'][side][1],k,elbow,wrist,.065); record(r['arms'][side][2],k,wrist,(0,0,yaw),(.10,.095,.105)); hands[i,side]=wrist
 # Stable hand attachments and continuous collection, preserving source constraints.
 for i,note,grab,attach in [(0,hero_note,5.5,(.25,-2,1.98)),(1,other_note,12.2,(1.15,-2,1.98))]:
  growth=sm((t-(-.3 if i==0 else 8.2))/1.65); record(note,k,hands[i,1] if t>=grab else attach,(0,0,.045*math.sin(t*2) if t>grab else 0),(max(.001,growth),)*3)
 record('V2 Offered cash grip',k,hands[0,1],(0,0,0),(.001,)*3 if t<24 else (1,1,1))
 for j,o in enumerate(bread):
  shelf=Vector((-1.8+(j%4)*1.15,-11.65,.65+(j//4)*.8))
  if j==0:
   p=shelf if t<28 else hands[2,1] if t<30.4 else hands[0,0] if t<34.4 else Vector((-.85,-13.17,1.49))
   if 27.7<t<28: p=mix(shelf,hands[2,1],(t-27.7)/.3)
  else: p=shelf
  record(o,k,p,(0,0,0),(.32,.21,.18))
 crop=Vector((-4.1,1.8,.55)) if t<57.2 else hands[3,1] if t<63.2 else Vector((-2,2.1,.98))
 record('V2 Hand-picked crop',k,crop,(0,0,0),(.18,)*3)
 center=mix((4.2,2.5,1.5),(4.5,2.18,1.82),(t-58)/4)
 seg('V2 Placed housing beam',k,center-Vector((1.5,0,0)),center+Vector((1.5,0,0)),.09)
 for d in leafdata:
  o=d['object']; age=(k-d['start'])/30
  if age>0 and not d['settled']:
   d['v']+=Vector((.23*math.sin(t*3+d['angle']),.17*math.cos(t*2+d['angle']),-9.81))/30; d['v']*=math.exp(-2.7/30)
   new=d['p']+d['v']/30; delta=new-d['p']; hit,normal,idx,dist=bvh.ray_cast(d['p'],delta.normalized(),delta.length+.014)
   if hit is not None:
    new=hit+normal*.018
    if normal.z>.45: d['settled']=True
    else: d['v']-=normal*1.1*d['v'].dot(normal)
   if new.z<.018: new.z=.018; d['settled']=True
   d['p']=new
  rot=(0,0,d['angle']) if d['settled'] else (.2*math.sin(age*3+d['angle']),.17*math.sin(age*4+d['angle']),d['angle']+.3*max(0,age))
  record(o,k,d['p'],rot,tuple(v*max(.001,sm((age+.15)/.25)) for v in d['base_scale']))
 cp=oldpos(cam.name,k)
 if 61.2<=t<64: cp.y=-9.5
 if t>=72:
  u=sm((t-72)/6); cp=Vector((3.8+6.2*u,-7-7*sm((t-74)/4),3.6+5.4*sm((t-72)/2.5)))
 if 56<=t<58.6:
  cp=Vector((-5.8,3.6,2.6)); target=Vector((-4.1,1.45,1.0)); rot=(target-cp).to_track_quat('-Z','Y').to_euler()
 elif 58.6<=t<61.2:
  cp=Vector((6.5,.3,2.7)); rot=(Vector((4.5,2.65,1.5))-cp).to_track_quat('-Z','Y').to_euler()
 elif 61.2<=t<64: rot=(oldpos('V2 Delivery van ROOT',k)+Vector((0,0,1))-cp).to_track_quat('-Z','Y').to_euler()
 elif t>=72: rot=(Vector((0,-.4,2))-cp).to_track_quat('-Z','Y').to_euler()
 else: rot=cam.rotation_euler.copy()
 record(cam,k,cp,rot,(1,1,1))
 if k%300==0: print('REPAIR_FRAME',k+1,flush=True)
# Bake linear curves at every output frame; preserve unchanged actions and all original mesh data.
for name,data in tracks.items():
 o=O[name]; constraint_keys=[]
 if o in [hero_note,other_note]:
  # Exact switch, not Bezier anticipation. Grasp already established before detach.
  for c in o.constraints:
   if c.type=='COPY_LOCATION': c.influence=0
 o.animation_data_clear(); action=bpy.data.actions.new(name+' V3 repaired animation'); o.animation_data_create(); o.animation_data.action=action
 for prop,values in data.items():
  values=np.asarray(values)
  for axis in range(3):
   vals=values[:,axis]
   if np.ptp(vals)<1e-7: getattr(o,prop)[axis]=float(vals[0]); continue
   keep=np.r_[True,np.abs(np.diff(vals,2))>1e-7,True]; frames=np.arange(1,N+1)[keep]; saved=vals[keep]
   fc=action.fcurves.new(data_path=prop,index=axis); fc.keyframe_points.add(len(frames)); co=np.stack([frames,saved],axis=1).ravel(); fc.keyframe_points.foreach_set('co',co)
   for p in fc.keyframe_points: p.interpolation='LINEAR'
   fc.update()
# Original note fold animation, focal length, price changes, van motion and all environment stay intact.
(R/'reports/reach_targets.json').write_text(json.dumps({'unreachable_targets_over_2mm':reaches,'maximum_error':max([x['error'] for x in reaches] or [0]),'note':'Reach targets are clamped by fixed-length IK; target misses must be reviewed rather than hidden.'},indent=2))
np.savez_compressed(R/'reports/repaired_plan.npz',roots=roots,feet=feet,stance=stance,foot_yaw=fyaw)
for action in list(bpy.data.actions):
 if action.users==0: bpy.data.actions.remove(action)
S.frame_set(1); bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/WHAT_IF_MONEY_GREW_ON_TREES_V3.blend'))
print('V3_REPAIRED',len(tracks),'objects; target misses',len(reaches),flush=True)
