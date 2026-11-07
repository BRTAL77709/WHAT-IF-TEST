"""Targeted V4 repairs on the completed V3 file. No asset construction or audio changes."""
import bpy,json,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion,Euler
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];V3=R.parent/'WHAT_IF_MONEY_GREW_ON_TREES_V3';S=bpy.context.scene;assert Path(bpy.data.filepath).name=='WHAT_IF_MONEY_GREW_ON_TREES_V3.blend';N=2340
z=np.load(V3/'reports/V3_transforms.npz');names=list(z['names']);A=z['transforms'];rigs=json.loads((V3/'reports/rig_map.json').read_text());stance=np.load(V3/'reports/repaired_plan.npz')['stance'];O={o.name:o for o in S.objects};patches={};reaches=[];fixes=[]
def v(name,k):return Vector(A[k,names.index(name),:3])
def q(name,k):return Quaternion(tuple(A[k,names.index(name),3:7]))
def sm(u):u=max(0,min(1,float(u)));return u*u*(3-2*u)
def mix(a,b,u):return Vector(a).lerp(Vector(b),sm(u))
def patch(name,k,loc=None,rot=None,scale=None):
 props=patches.setdefault(name,{})
 for key,value in [('location',loc),('rotation_euler',rot),('scale',scale)]:
  if value is not None:props.setdefault(key,{})[k+1]=tuple(value)
def segment(name,k,a,b,r):
 d=b-a;patch(name,k,(a+b)/2,d.to_track_quat('Z','Y').to_euler(),(r,r,d.length))
def ik(a,b,L,pole):
 d=b-a;length=d.length;D=min(length,2*L-.0001);direction=d.normalized();bend=Vector(pole)-direction*Vector(pole).dot(direction)
 if bend.length<1e-5:bend=direction.cross(Vector((1,0,0)))
 bend.normalize();return a+direction*D/2+bend*math.sqrt(max(0,L*L-D*D/4)),a+direction*D,max(0,length-D)
S.frame_set(1);verts=[];faces=[]
for o in S.objects:
 if o.type=='MESH' and o.name.startswith('Static environment /') and 'Foliage' not in o.name:
  off=len(verts);verts.extend([o.matrix_world@x.co for x in o.data.vertices]);faces.extend([tuple(off+i for i in p.vertices) for p in o.data.polygons])
bvh=BVHTree.FromPolygons(verts,faces)
def floor(x,y):
 p,n,idx,d=bvh.ray_cast(Vector((float(x),float(y),.75)),Vector((0,0,-1)),1)
 return p.z if p is not None and n.z>.7 else .01
def heights(x,y,yaw):
 c,s=math.cos(yaw),math.sin(yaw);return [floor(x+c*dx-s*dy,y+s*dx+c*dy) for dx,dy in [(-.1,-.17),(-.1,.17),(.1,-.17),(.1,.17)]]
# Preserve footstep/audio timing and stance anchors; solve the whole sole footprint, not just its center.
feet=np.zeros((N,7,2,3))
for i,r in enumerate(rigs):
 for side in [0,1]:
  shoe=r['legs'][side][2];upper=r['legs'][side][0];old=A[:,names.index(shoe),:3].copy();new=old.copy();hip=np.array([v(upper,k)+q(upper,k)@Vector((0,0,-A[k,names.index(upper),9]/2)) for k in range(N)]);mask=stance[:,i,side];yaw_overrides={};k=0
  while k<N:
   if not mask[k]:k+=1;continue
   start=k
   while k+1<N and mask[k+1]:k+=1
   end=k+1;mid=(start+end-1)//2;p=Vector(old[mid]);yaw=q(shoe,mid).to_euler().z;hs=heights(p.x,p.y,yaw)
   if max(hs)-(p.z-.07)>.012:
    candidates=[]
    for dx in np.arange(-.52,.521,.04):
     for dy in np.arange(-.52,.521,.04):
      h=heights(p.x+dx,p.y+dy,yaw)
      if max(h)-min(h)>.025:continue
      target=np.array([p.x+dx,p.y+dy,max(h)+.073]);distance=float(np.linalg.norm(hip[start:end]-(target+np.array([0,0,.07])),axis=1).max())
      if distance<.9195:candidates.append((dx*dx+dy*dy+.03*(target[2]-p.z)**2,target))
    
    if not candidates:
     print('FOOT_DEBUG',i,side,start,end,list(p),hs,'hip_bounds',hip[start:end].min(0).tolist(),hip[start:end].max(0).tolist(),flush=True)
    assert candidates,('No supported reachable foot placement',i,side,start)
    target=min(candidates,key=lambda x:x[0])[1];new[start:end]=target;fixes.append({'actor':i,'side':side,'start_frame':start+1,'end_frame':end,'offset_m':(target-np.array(p)).tolist()})
   k+=1
  # Blend anchor corrections through the existing swing interval, keeping landing times unchanged.
  k=0
  while k<N:
   if mask[k]:k+=1;continue
   start=k
   while k+1<N and not mask[k+1]:k+=1
   end=k+1;a=max(0,start-1);b=min(N-1,end);da=new[a]-old[a];db=new[b]-old[b]
   for f in range(start,end):new[f]=old[f]+da+(db-da)*sm((f-a)/max(1,b-a))
   required=[];shape=[]
   for f in range(start,end):
    yaw=q(shoe,f).to_euler().z;needed=max(0,max(heights(new[f,0],new[f,1],yaw))+.003-(new[f,2]-.07));u=(f-a)/max(1,b-a);w=max(.001,math.sin(math.pi*u));required.append(needed);shape.append(w)
   amplitude=max([need/w for need,w in zip(required,shape)] or [0])
   if amplitude>.25:
    # Anticipate the curb: lift in place, translate while clear, then lower onto the supported target.
    early=max(0,start-5)
    while early<start and not mask[early]:early+=1
    a=early;b=min(N-1,end);origin=new[a].copy();finish=new[b].copy();ya=q(shoe,a).to_euler().z;yb=q(shoe,b).to_euler().z;delta=(yb-ya+math.pi)%math.tau-math.pi;terrain=[]
    for f in range(a,b):
     u=(f-a)/max(1,b-a);phase=sm((u-.25)/.5);xy=origin[:2]+(finish[:2]-origin[:2])*phase;yaw=ya+delta*phase;terrain.extend(heights(*xy,yaw))
    apex=max(max(terrain),origin[2]-.07,finish[2]-.07)+.10
    for f in range(a,b):
     u=(f-a)/max(1,b-a);phase=sm((u-.25)/.5);new[f,:2]=origin[:2]+(finish[:2]-origin[:2])*phase
     sole=(origin[2]-.07)+(apex-(origin[2]-.07))*sm(u/.25) if u<.25 else apex if u<.75 else apex+((finish[2]-.07)-apex)*sm((u-.75)/.25)
     new[f,2]=sole+.07;yaw_overrides[f]=(0,0,ya+delta*phase)
    mask[a:start]=False
   else:
    for f,w in zip(range(start,end),shape):new[f,2]+=amplitude*w
   k+=1
  feet[:,i,side]=new
  for k in range(N):
   if np.linalg.norm(new[k]-old[k])<1e-6:continue
   thigh,shin,_=r['legs'][side];a=Vector(hip[k]);ankle=Vector(new[k])+Vector((0,0,.07));oldknee=v(thigh,k)+q(thigh,k)@Vector((0,0,A[k,names.index(thigh),9]/2));knee,tip,error=ik(a,ankle,.46,oldknee-a)
   if error>.001:reaches.append({'frame':k+1,'actor':i,'limb':'leg','error':error})
   segment(thigh,k,a,knee,.085);segment(shin,k,knee,tip,.075);patch(shoe,k,tip-Vector((0,0,.07)),yaw_overrides.get(k))
 print('V4_SOLE_ACTOR',i,flush=True)
# Floating stock and center-of-loaf hand penetrations: place stock on real shelf planes and grip the side.
for k in range(N):
 t=k/30
 for name in [n for n in names if n.startswith('V2 Bread inventory')]:
  p=v(name,k)
  if name!='V2 Bread inventory':p.z-=.053
  elif t<28:p.z-=.053
  elif t<30.4:p.z-=.053*(1-sm((t-28)/2))
  elif 33.2<t<34.4:p.z-=.008*sm((t-33.2)/1.2)
  elif t>=34.4:p.z-=.008
  patch(name,k,p)
 # Only these actual contact arms require repair; retain all existing models, roots and acting elsewhere.
 for actor,side in [(2,1),(0,0),(2,0)]:
  r=rigs[actor];upper,lower,hand=r['arms'][side];target=v(hand,k);shoulder=v(upper,k)+q(upper,k)@Vector((0,0,-A[k,names.index(upper),9]/2));active=False
  if actor==2 and side==1 and 26.5<t<31.4:
   w=sm((t-26.5)/1.2) if t<30.4 else 1-sm((t-30.4)/1)
   target.x+=.42*w;target.z-=.053*w*(1-sm((t-28)/2));active=True
  if actor==0 and side==0 and 29.8<t<35.3:
   w=sm((t-29.8)/.6) if t<34.4 else 1-sm((t-34.4)/.9)
   target.x-=.42*w
   if t>33.2:target.z-=.008*sm((t-33.2)/1.2)*(1-sm((t-34.4)/.9))
   active=True
  # Recover the reserved loaf rather than leaving it directly in front of the hungry customer's close-up.
  lean_weight=sm((t-53)/.6)*(1-sm((t-54.6)/.9));handoff_weight=sm((t-28.4)/.7)*(1-sm((t-30.4)/.8));lean=Vector((-.18,-.20,0))*lean_weight+Vector((.065,-.035,0))*handoff_weight;cosine=.58/math.sqrt(.58**2+lean.length_squared);drop=.58*(cosine-1)
  if actor==2 and (t>=53 or handoff_weight>0):
   shoulder+=lean+Vector((0,0,drop));active=True
   if side==1 and t>=53:
    grip=Vector((-.43,-13.17,1.482));lift=grip+Vector((0,0,.12));carry=v(r['root'],k)+Vector((-.35,-.05,1.05))
    if t<54.2:target=mix(target,grip,(t-53)/1)
    elif t<54.5:target=mix(grip,lift,(t-54.2)/.3)
    elif t<55:target=mix(lift,Vector((carry.x,carry.y,lift.z)),(t-54.5)/.5)
    else:target=mix(Vector((carry.x,carry.y,lift.z)),carry,(t-55)/.5)
    if t>=54:patch('V2 Bread inventory',k,target-Vector((.42,0,0)))
   elif side==0:target+=lean*.35+Vector((0,0,drop*.5))
  if active:
   oldelbow=v(upper,k)+q(upper,k)@Vector((0,0,A[k,names.index(upper),9]/2));elbow,wrist,error=ik(shoulder,target,.43,oldelbow-shoulder)
   if error>.001:reaches.append({'frame':k+1,'actor':actor,'limb':'arm','error':error})
   segment(upper,k,shoulder,elbow,.075);segment(lower,k,elbow,wrist,.065);patch(hand,k,wrist)
 if lean.length>0:
  r=rigs[2];tilt=Vector((0,0,1)).rotation_difference(Vector((lean.x,lean.y,.58)).normalized());torso=v(r['torso'],k)+lean*.5+Vector((0,0,drop*.5));patch(r['torso'],k,torso,(tilt@q(r['torso'],k)).to_euler())
  hp=v(r['head'],k);newhp=hp+lean+Vector((0,0,drop))
  for name in [r['head'],r['hair'],*r['eyes']]:patch(name,k,newhp+tilt@(v(name,k)-hp),(tilt@q(name,k)).to_euler())
 # Keep the harvester and bill visible during approach; preserve working framing after arrival.
 if 8<=t<16:
  u=sm((t-8)/3);cp=mix((2.6,-6.5,2.6),v(S.camera.name,k),u);target=mix((2.6,-2.7,1.3),(1.15,-2,1.6),u);patch(S.camera.name,k,cp,(target-cp).to_track_quat('-Z','Y').to_euler())
 if 68<=t<69.2:
  # The original sold-out display bay, in a physically clear camera position behind the counter.
  cp=Vector((-1.8,-12.25,.65));target=Vector((-1.8,-11.65,.55));patch(S.camera.name,k,cp,(target-cp).to_track_quat('-Z','Y').to_euler())
 if k%300==0:print('V4_INTERACTION_FRAME',k+1,flush=True)
# Preserve original curves outside changed ranges. Boundary keys prevent correction leaking into valid frames.
modified={}
for name,props in patches.items():
 o=O[name];oldaction=o.animation_data.action if o.animation_data and o.animation_data.action else None;action=oldaction.copy() if oldaction else bpy.data.actions.new(name+' V4 corrections');action.name=name+' V4 corrections';o.animation_data_create();o.animation_data.action=action
 for prop,values in props.items():
  keys=sorted(values);ranges=[];start=last=keys[0]
  for f in keys[1:]:
   if f>last+1:ranges.append((start,last));start=f
   last=f
  ranges.append((start,last))
  for axis in range(3):
   fc=action.fcurves.find(prop,index=axis);original=oldaction.fcurves.find(prop,index=axis) if oldaction else None
   base=float(getattr(o,prop)[axis]);samples=np.array([original.evaluate(f) if original else base for f in range(1,N+1)],dtype=np.float64)
   for f,val in values.items():samples[f-1]=val[axis]
   if fc is None:fc=action.fcurves.new(data_path=prop,index=axis)
   fc.keyframe_points.clear();fc.keyframe_points.add(N);fc.keyframe_points.foreach_set('co',np.stack([np.arange(1,N+1),samples],axis=1).ravel())
   for point in fc.keyframe_points:point.interpolation='LINEAR'
   fc.update()
  modified.setdefault(name,[]).extend(ranges)
# Approach camera uses a wider lens until the character reaches the bill; later approved lens is restored.
cam=S.camera;oldlens=cam.data.animation_data.action;action=oldlens.copy();cam.data.animation_data.action=action;fc=action.fcurves.find('lens');original=oldlens.fcurves.find('lens');samples=np.array([original.evaluate(f) for f in range(1,N+1)])
for f in range(241,481):samples[f-1]=35+13*sm(((f-1)/30-8)/3)
for f in range(2041,2077):samples[f-1]=35
fc.keyframe_points.clear();fc.keyframe_points.add(N);fc.keyframe_points.foreach_set('co',np.stack([np.arange(1,N+1),samples],axis=1).ravel())
for point in fc.keyframe_points:point.interpolation='LINEAR'
fc.update()
(R/'reports/IK_target_errors.json').write_text(json.dumps(reaches,indent=2))
assert not reaches,sorted(reaches,key=lambda x:x['error'],reverse=True)[:10]
np.savez_compressed(R/'reports/corrected_feet.npz',feet=feet,stance=stance)
(R/'reports/source_repairs.json').write_text(json.dumps({'source':str(V3/'blender/WHAT_IF_MONEY_GREW_ON_TREES_V3.blend'),'modified_objects':modified,'foot_placements':fixes,'unreachable_IK_targets':reaches,'camera_changes':[[241,480],[2041,2076]],'new_cut_time':69.2,'assets_created':0,'story_audio_text_changed':False,'inventory_scope':'Existing stock stays physically present. The sold-out lower-left bay is shown briefly; no whole-shop inventory depletion is fabricated.'},indent=2))
for action in list(bpy.data.actions):
 if action.users==0:bpy.data.actions.remove(action)
S.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/WHAT_IF_MONEY_GREW_ON_TREES_V4.blend'));print('V4_SOURCE_SAVED',len(modified),len(fixes),flush=True)
