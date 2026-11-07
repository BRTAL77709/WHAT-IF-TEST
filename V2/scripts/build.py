import bpy,math,random,json,sys
from pathlib import Path
from mathutils import Vector, Euler
R=Path(__file__).resolve().parents[1]; TEST='--test' in sys.argv
S=bpy.context.scene; random.seed(2026)
# Load V1 only as a source; never save back to its path.
for o in list(S.objects):
 if not (o.name.startswith('Static environment /') or o.type=='FONT'): bpy.data.objects.remove(o,do_unlink=True)
for o in list(S.objects):
 if o.type=='FONT' and o.name!='Grocery signage' and 'Shop sign' not in o.name: bpy.data.objects.remove(o,do_unlink=True)
for material in bpy.data.materials: material.use_fake_user=True
bpy.data.orphans_purge(do_recursive=True)
M={m.name:m for m in bpy.data.materials}
S.render.engine='BLENDER_WORKBENCH'; S.render.resolution_x=1080; S.render.resolution_y=1920; S.render.resolution_percentage=100; S.render.fps=30
S.frame_start=1; S.frame_end=240 if TEST else 2340
S.display.render_aa='FXAA'; S.display.shading.show_cavity=True; S.display.shading.cavity_type='BOTH'; S.display.shading.show_shadows=True; S.display.shading.show_specular_highlight=False
S.display.shading.curvature_ridge_factor=1.1; S.display.shading.curvature_valley_factor=.8
S.display.shading.studiolight_rotate_z=.4
S.render.image_settings.file_format='PNG'; S.render.image_settings.compression=12
S.world.color=(.055,.12,.17); S.display.shading.background_type='WORLD'
previous_rotations={}
tracks={}; metrics={'grip_errors':[],'stance_foot_z_errors':[],'root_translation':{},'seed':2026}
def mat(n,c):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); M[n]=m; return m
mint=M['Money mint']; navy=M['Deep navy']; gold=M['Golden accent']; ivory=M['Ivory']; skin=M['Warm skin']
meshcache={}
def objmesh(n,kind,ma):
 key=(kind,ma.name)
 if key not in meshcache:
  if kind=='box': bpy.ops.mesh.primitive_cube_add(size=1)
  elif kind=='ball': bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1)
  else: bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=1,depth=1)
  o=bpy.context.object; o.name=n; o.data.materials.append(ma); meshcache[key]=o.data
 else:
  o=bpy.data.objects.new(n,meshcache[key]); S.collection.objects.link(o)
 return o
def box(n,pos,scale,ma):
 o=objmesh(n,'box',ma); o.location=pos; o.scale=scale; return o
def ball(n,pos,scale,ma):
 o=objmesh(n,'ball',ma); o.location=pos; o.scale=scale; return o
def empty(n):
 o=bpy.data.objects.new(n,None); S.collection.objects.link(o); return o
def text(n,body,pos,size,ma):
 d=bpy.data.curves.new(n,'FONT'); d.body=body; d.align_x='CENTER'; d.align_y='CENTER'; d.size=size; d.extrude=.002
 o=bpy.data.objects.new(n,d); S.collection.objects.link(o); o.location=pos; o.rotation_euler=(math.pi/2,0,0); d.materials.append(ma); return o
def record(o,f,loc=None,rot=None,scale=None):
 if loc is not None: o.location=loc
 if rot is not None:
  e=Euler(tuple(rot),'XYZ')
  if o.name in previous_rotations: e.make_compatible(previous_rotations[o.name])
  previous_rotations[o.name]=e.copy(); o.rotation_euler=e
 if scale is not None: o.scale=scale
 d=tracks.setdefault(o.name,{'location':[],'rotation_euler':[],'scale':[]})
 for p in d: d[p].append((f,tuple(getattr(o,p))))
def segment(o,a,b,r,f):
 a,b=Vector(a),Vector(b); v=b-a
 record(o,f,(a+b)/2,v.to_track_quat('Z','Y').to_euler(),(r,r,max(.001,v.length)))
def smooth(u): u=max(0,min(1,u)); return u*u*(3-2*u)
def lerp(a,b,u): return Vector(a).lerp(Vector(b),u)
def ground(x,y):
 if 1.5<y<4.5 and any(abs(x-c)<.325 for c in [-5,-4.1,-3.2,-2.3]): return .343
 if abs(x)<7 and abs(y)<4.5: return .203
 if min(abs(y-7),abs(y+7))<1.7: return .098
 if min(abs(x-10),abs(x+10))<2: return .088
 return .013
def path(knots,t):
 if t<=knots[0][0]: return Vector((knots[0][1],knots[0][2],0))
 for a,b in zip(knots,knots[1:]):
  if t<=b[0]: return lerp((a[1],a[2],0),(b[1],b[2],0),smooth((t-a[0])/(b[0]-a[0])))
 return Vector((knots[-1][1],knots[-1][2],0))
paths=[[(0,-2.7,-2.35),(2,-2.7,-2.35),(3.6,-.3,-2.35),(5.8,-.3,-2.35),(8,-1.9,-3.3),(11,-3.5,-3.3),(19,-3.5,-3.3),(23,3.3,-5),(28,3.3,-14.05),(30,-.6,-14.05),(78,-.6,-14.05)],
[(0,4,-3),(8,4,-3),(11,1.2,-2.4),(13,1.2,-2.4),(17,4.5,-4.5),(24,4.5,-4.5),(31,3.3,-14.4),(34,2,-14.4),(36,2,-14.4),(38,5,-15),(78,5,-15)],
[(0,.5,-11.6),(25,.5,-11.6),(28,-.4,-12.43),(31,-.4,-12.43),(33,.5,-12),(42,.5,-12),(44,.65,-12),(46,.5,-12),(78,.5,-12)],
[(0,-4,2),(54,-4,2),(56,-4,2.8),(59,-4,2.8),(62,-1.8,2.2),(78,-1.8,2.2)],
[(0,4,3),(55,4,3),(58,3.5,2.8),(64,3.5,2.8),(68,5.5,3),(78,5.5,3)],
[(0,-6,-3.9),(9,-6,-3.9),(13,-2.8,-2.3),(18,-2.8,-2.3),(20,-5.5,-4.7),(23,-7.5,-5),(28,-7.5,-15),(31,-3,-17),(36,2,-15.5),(42,2,-15.5),(48,5,-15),(78,-4,-15)],
[(0,5,-4),(10,5,-4),(15,3.5,-1.8),(20,3.5,-1.8),(24,5,-4.7),(27,3.4,-8),(32,3.4,-15.3),(36,3.2,-16.5),(42,3.2,-16.5),(48,5,-15),(78,5,-15)]]
# Distance lookup provides fixed world-space stance anchors instead of feet sliding with a root.
rigs=[]
for i,knots in enumerate(paths):
 root=empty('V2 Actor %d ROOT'%i); torso=box('V2 Jacket', (0,0,0),(.46,.34,.58),M['Building '+str(i%5)])
 head=ball('V2 Head',(0,0,0),(.235,.215,.25),skin); hair=ball('V2 Hair',(0,0,0),(.238,.22,.14),navy)
 eyes=[ball('V2 Eye',(0,0,0),(.028,.018,.032),navy) for _ in range(2)]
 legs=[[objmesh('V2 Thigh','tube',navy),objmesh('V2 Shin','tube',navy),box('V2 Planted shoe',(0,0,0),(.20,.34,.14),navy)] for _ in range(2)]
 arms=[[objmesh('V2 Upper arm','tube',M['Building '+str(i%5)]),objmesh('V2 Forearm','tube',M['Building '+str(i%5)]),ball('V2 Contact hand',(0,0,0),(.10,.095,.105),skin)] for _ in range(2)]
 points=[path(knots,k/30) for k in range(2341)]; distances=[0.]
 for a,b in zip(points,points[1:]): distances.append(distances[-1]+(b-a).length)
 initial=next(((b-a).normalized() for a,b in zip(points,points[1:]) if (b-a).length>.00001),Vector((0,1,0)))
 rigs.append(dict(root=root,torso=torso,head=head,hair=hair,eyes=eyes,legs=legs,arms=arms,path=knots,points=points,dist=distances,lastF=initial,yaw=math.atan2(-initial.x,initial.y),feet_state={}))
def at_distance(r,s):
 import bisect
 ds=r['dist']; j=min(2340,max(1,bisect.bisect_left(ds,max(0,min(ds[-1],s))))); u=(s-ds[j-1])/max(1e-8,ds[j]-ds[j-1]); return r['points'][j-1].lerp(r['points'][j],max(0,min(1,u)))
def planted_foot(r,side,P,F,right,distance,speed,yaw):
 phase=(distance+(0 if side<0 else .5))%1
 states=r['feet_state']; st=states.get(side); landed=False
 if st is None:
  a=P+right*side*.14+F*(.25 if side<0 else -.10); a.z=ground(a.x,a.y)+.14
  st={'anchor':a.copy(),'position':a.copy(),'phase':phase,'yaw':yaw,'stopped':True}; states[side]=st
 if speed<.02:
  a=st['position'].copy(); floor=ground(a.x,a.y)+.14; a.z=max(floor,a.z-.03); lift=max(0,a.z-floor); st['stopped']=True
 else:
  if phase>=.6:
   if st['phase']<.6 or st['stopped']:
    st['start']=st['position'].copy(); end=at_distance(r,distance+(1-phase)+.20)+right*side*.14; end.z=ground(end.x,end.y)+.14; st['end']=end; st['start_phase']=phase; st['start_yaw']=st['yaw']; delta=end-st['start']; st['end_yaw']=math.atan2(-delta.x,delta.y) if delta.length>.001 else yaw
   u=max(0,min(1,(phase-st['start_phase'])/max(.01,1-st['start_phase']))); a=lerp(st['start'],st['end'],smooth(u)); lift=.19*math.sin(math.pi*u); a.z+=lift
   turn=(st['end_yaw']-st['start_yaw']+math.pi)%math.tau-math.pi; st['yaw']=st['start_yaw']+turn*smooth(u)
  else:
   if st['phase']>=.6 and 'end' in st: st['anchor']=st['end'].copy(); landed=True
   a=st['anchor'].copy(); a.z=ground(a.x,a.y)+.14; lift=0
  st['stopped']=False
 st['position']=a.copy(); st['phase']=phase
 return a,st['yaw'],lift,landed
def ik(a,b,L,pole):
 a,b=Vector(a),Vector(b); v=b-a; d=v.length; direction=v.normalized() if d>.00001 else Vector((0,0,-1)); dd=min(d,2*L-.001)
 bend=Vector(pole)-direction*Vector(pole).dot(direction)
 if bend.length<.001: bend=direction.cross(Vector((1,0,0)))
 bend.normalize(); return a+direction*(dd/2)+bend*math.sqrt(max(.00001,L*L-dd*dd/4)), a+direction*dd, max(0,d-2*L+.001)
def make_note(n):
 root=empty(n+' GRIP CORNER'); parts=[]
 for half in [0,1]:
  hinge=empty(n+' fold hinge'); hinge.parent=root; hinge.location=(-.275*half,0,0)
  panel=box(n+' paper',(-.1375,0,-.14),(.275,.016,.28),mint); panel.parent=hinge; panel.location=(-.1375,0,-.14)
  stripe=box(n+' ink',(-.1375,-.010,-.14),(.22,.005,.018),navy); stripe.parent=hinge; stripe.location=(-.1375,-.010,-.14)
  parts.append(hinge)
 mark=ball(n+' fictional gold seal',(-.12,-.018,-.14),(.035,.012,.05),gold); mark.parent=root; mark.location=(-.12,-.018,-.14)
 return root,parts
def flat_note(n):
 key=('banknote',mint.name)
 if key not in meshcache:
  vertices=[]; faces=[]; materials=[]
  for center,dims,mi in [((-.275,0,-.14),(.55,.016,.28),0),((-.275,-.012,-.14),(.44,.006,.022),1),((-.12,-.016,-.14),(.055,.006,.075),2)]:
   x,y,z=center; w,d,h=dims; off=len(vertices)
   vertices.extend([(x+sx*w/2,y+sy*d/2,z+sz*h/2) for sx,sy,sz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]])
   faces.extend([tuple(off+i for i in face) for face in [(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5),(1,5,7,3),(0,2,6,4)]]); materials.extend([mi]*6)
  mesh=bpy.data.meshes.new('Shared detailed V2 currency'); mesh.from_pydata(vertices,[],faces)
  for m in [mint,navy,gold]: mesh.materials.append(m)
  for poly,mi in zip(mesh.polygons,materials): poly.material_index=mi
  meshcache[key]=mesh
 o=bpy.data.objects.new(n,meshcache[key]); S.collection.objects.link(o); return o
notes=[make_note('V2 Hero banknote'),make_note('V2 Harvester banknote')]
# Real low branch puts the growing bill within the character's reach.
for a,b in [((0,0,1.7),(.25,-2.0,1.98)),((0,0,1.7),(1.15,-2.0,1.98))]:
 o=objmesh('V2 Low money branch','tube',M['Tree bark']); segment(o,a,b,.065,1)
# Matched inventory geometry, removed only through animated pick-up or availability changes.
bread=[]
for i in range(12): bread.append(ball('V2 Bread inventory',(-1.8+(i%4)*1.15,-11.65,.65+(i//4)*.8),(.32,.21,.18),gold))
# A real shop price board, not a screen-wide infographic.
board=box('V2 Price board',(1.1,-12.64,2.12),(1.65,.08,.68),navy)
price_texts=[text('V2 Bread price '+s,s,(1.1,-12.70,2.12),.35,gold) for s in ['$2','$20','$200','$2,000']]
price_caption=text('V2 Price caption','BREAD',(1.1,-12.70,2.57),.22,navy)
price_rig=empty('V2 Physical price flip rig'); price_rig.location=(1.1,-12.64,2.12); bpy.context.view_layer.update()
for child in [board,price_caption]+price_texts:
 child.parent=price_rig; child.matrix_parent_inverse=price_rig.matrix_world.inverted()
post=objmesh('V2 Price sign support','tube',gold); segment(post,(1.1,-12.61,1.25),(1.1,-12.61,1.85),.035,1)
# Cash carried at a hand's grip point.
cashroot=empty('V2 Offered cash grip'); cashstack=[]
for i in range(8):
 o=box('V2 Offered banknote',(0,0,0),(.65,.40,.045),mint); o.parent=cashroot; o.location=(-.20,.12,-.04-i*.05); cashstack.append(o)
# Ground papers grow after the widespread cash bloom.
fall=[]
for i in range(80):
 o=box('V2 Windfall',(0,0,0),(.55,.27,.015),mint); x=random.uniform(-16,16); y=random.uniform(7,14) if abs(x)<8 else random.uniform(-5,14); fall.append((o,x,y,random.random(),random.random()*6))
final_fall=[]
for i in range(22):
 o=box('V2 Final tree fall',(0,0,0),(.5,.24,.015),mint); final_fall.append((o,random.uniform(-1.4,1.4),random.uniform(-1.1,1.1),random.random()*2))
attached=[]
for i,(x,y) in enumerate([(0,0),(-6,0),(6,0),(-5,5),(5,5),(-15,5),(15,5),(-15,-5),(15,-5),(-6,-4),(6,-4),(-5,15),(5,15)]):
 for j in range(6):
  ang=j*math.tau/6; n=flat_note('V2 Money foliage'); n.location=(x+math.cos(ang),y+math.sin(ang),3.3 if i==0 else 2.65); attached.append((n,i,j,n.location.copy()))
for i in range(100):
 x=random.uniform(-17,17); y=random.choice([-7,7])+random.uniform(-1.4,1.4)
 o=box('V2 Discarded paper',(x,y,.108),(.6,.3,.02),mint); o.rotation_euler.z=random.random()*6; attached.append((o,99,i,o.location.copy()))
# Delivery van with moving wheels and visible produce crates.
van=empty('V2 Delivery van ROOT'); wheels=[]
for loc,sc,ma in [((0,0,.65),(2.5,1.25,.7),M['Building 1']),((.7,0,1.25),(.9,1.15,.6),M['Blue windows']),((-.65,0,1.35),(1.35,1.2,.8),ivory)]:
 o=box('V2 Delivery van',loc,sc,ma); o.parent=van; o.location=loc
for x in [-.8,.8]:
 for y in [-.65,.65]:
  o=objmesh('V2 Rolling delivery wheel','tube',navy); o.parent=van; o.location=(x,y,.35); o.rotation_euler=(math.pi/2,0,0); o.scale=(.3,.3,.15); wheels.append(o)
crate=box('V2 Harvest crate',(-2,2.1,.45),(.8,.65,.7),M['Tree bark'])
produce=ball('V2 Hand-picked crop',(0,0,0),(.18,.18,.20),M['Foliage 2'])
beam=objmesh('V2 Placed housing beam','tube',gold)
# Perspective camera with one establishing aerial and varied close/action views.
bpy.ops.object.camera_add(); cam=bpy.context.object; cam.name='V2 Perspective story camera'; cam.data.type='PERSP'; cam.data.sensor_fit='HORIZONTAL'; cam.data.sensor_width=36; cam.data.clip_start=.03; cam.data.clip_end=220; S.camera=cam
camera_keys=[]
# Footstep event timestamps are shared with sound generation.
footsteps=[]; lastcycles={}
cuts=[2,8,16,19.5,24,32,40,47,48,52.5,56,58.6,61.2,64,68,72]
frames=sorted(set(range(1,S.frame_end+1))|{S.frame_end}|{n for t in cuts for n in [round(t*30),round(t*30)+1] if 1<=n<=S.frame_end})
for f in frames:
 t=(f-1)/30; hero=path(paths[0],t); hands={}
 price_angle=sum(.20*math.sin(math.pi*(t-change+.18)/.36) for change in [42,44,46] if change-.18<t<change+.18)
 price_grip=Vector((1.1,-12.64,2.12))+Euler((price_angle,0,0)).to_matrix()@Vector((0,-.01,-.37))
 record(price_rig,f,(1.1,-12.64,2.12),(price_angle,0,0),(1,1,1))
 for i,r in enumerate(rigs):
  P=path(r['path'],t); P.z=ground(P.x,P.y)
  travel=path(r['path'],t+.04)-path(r['path'],max(0,t-.04)); speed=travel.length/.08
  if travel.length>.00001: F=travel.normalized(); r['lastF']=F
  else: F=r['lastF'].copy()
  # Seller faces the customer; hero turns naturally to the branch or shop.
  if i==2: F=Vector((0,-1,0))
  if i==0 and 3.6<t<5.9: F=Vector((.1,1,0)).normalized()
  if i==0 and t>=30: F=Vector((0,1,0))
  if i==1 and 11<t<13.3: F=Vector((0,1,0))
  right=Vector((F.y,-F.x,0)); yaw=math.atan2(-F.x,F.y); delta=(yaw-r['yaw']+math.pi)%math.tau-math.pi; r['yaw']+=delta*.20; yaw=r['yaw']; F=Vector((-math.sin(yaw),math.cos(yaw),0)); right=Vector((F.y,-F.x,0))
  bend=.5*math.sin(math.pi*(t-56)/3) if i==3 and 56<t<59 else 0
  distance=r['dist'][min(2340,round(t*30))]; bob=.025*abs(math.sin(distance*math.tau)) if speed>.03 else .004*math.sin(t*2+i)
  feet_targets={side:planted_foot(r,side,P,F,right,distance,speed,yaw) for side in [-1,1]}
  crouch=0
  for side in [-1,1]:
   a=feet_targets[side][0]; hipxy=Vector((P.x,P.y,0))+right*side*.14; delta=Vector((a.x,a.y,0))-hipxy
   ceiling=a.z+math.sqrt(max(.0001,.916*.916-delta.length_squared)); crouch=max(crouch,P.z+.88+bob-ceiling)
  P.z-=max(0,crouch); metrics['max_balance_crouch_m']=max(metrics.get('max_balance_crouch_m',0),crouch)
  record(r['root'],f,P,(0,0,yaw),(1,1,1)); record(r['torso'],f,P+F*(bend*.5)+Vector((0,0,1.16+bob-bend*.4)),(-bend+.04*math.sin(distance*6) if speed>.1 else -bend,0,yaw),(.46,.34,.58))
  headyaw=yaw; nod=0
  if i==0:
   if 3.6<t<5.6: nod=.18; headyaw=-.18
   if 40<t<48: nod=.16*math.sin((t-40)*2)
   if 64<t<67: nod=-.35*smooth((t-64)/2)
   if 67<=t<72: nod=-.35*(1-smooth((t-67)/2))
  if i==2 and 48<t<55: headyaw+=.25*math.sin(t*5)
  if i==3: nod=-bend
  hp=P+F*(bend*.6)+Vector((0,0,1.72+bob-bend*.9)); record(r['head'],f,hp,(nod,0,headyaw),(.235,.215,.25)); record(r['hair'],f,hp+Vector((0,0,.17)),(nod,0,headyaw),(.238,.22,.14))
  hF=Vector((-math.sin(headyaw),math.cos(headyaw),0)); hR=Vector((hF.y,-hF.x,0))
  for eye,side in zip(r['eyes'],[-1,1]): record(eye,f,hp+Euler((nod,0,headyaw)).to_matrix()@Vector((side*.08,.205,.035)),(0,0,headyaw),(.028,.018,.032))
  for side,limb in zip([-1,1],r['legs']):
   a,foot_yaw,lift,landed=feet_targets[side]
   hip=P+right*side*.14+Vector((0,0,.88+bob)); knee,ankle,err=ik(hip,a,.46,F)
   segment(limb[0],hip,knee,.085,f); segment(limb[1],knee,ankle,.075,f); record(limb[2],f,a+Vector((0,0,-.07)),(0,0,foot_yaw),(.20,.34,.14))
   if lift==0 and (r['feet_state'][side]['phase']<.6 or speed<.02): metrics['stance_foot_z_errors'].append(abs((a.z-.14)-ground(a.x,a.y)))
   if landed:
    footsteps.append({'time':t,'actor':i,'side':side,'position':[P.x,P.y]})
  for side,limb in zip([-1,1],r['arms']):
   shoulder=P+right*side*.31+F*(bend*.4)+Vector((0,0,1.43+bob-bend*.8)); hand=P+right*side*.43+F*(.18*math.sin(distance*6+side*math.pi))+Vector((0,0,.97+bob)); contact=False
   if i==0 and side==1:
    grip=Vector((.25,-2.0,1.98)); hold=P+right*.33+F*.48+Vector((0,0,1.43))
    if 4.1<=t<=5.5: hand=lerp(hand,grip,smooth((t-4.1)/1.0)); contact=t>=5.1
    elif 5.5<t<6.1: hand=lerp(grip,hold,smooth((t-5.5)/.6)); contact=True
    elif t>=6.1: hand=hold; contact=True
    if 30<t<38 or 48<t<56: hand=lerp(hand,Vector((-.05,-13.35,1.65)),smooth((t-30)/1.5) if t<38 else smooth((t-48)/1.2))
    if 40<t<48: hand=P+right*.6+Vector((0,0,1.55+.1*math.sin(t*2)))
   if i==0 and side==-1 and 29.5<t<32.5:
    shared=Vector((-.85,-13.23,1.52)); carry=P-right*.35+F*.45+Vector((0,0,1.18))
    hand=lerp(hand,shared,smooth((t-29.5)/.6)) if t<31.2 else lerp(shared,carry,smooth((t-31.2)/.8)); contact=t>=30.4
   if i==1 and side==1:
    grip=Vector((1.15,-2.0,1.98)); hold=P+right*.35+F*.45+Vector((0,0,1.4))
    if 11<t<=12.2: hand=lerp(hand,grip,smooth((t-11)/.8)); contact=t>=11.8
    elif 12.2<t<13: hand=lerp(grip,hold,smooth((t-12.2)/.8)); contact=True
    elif t>=13: hand=hold; contact=True
   if i==2:
    if side==1 and 28<t<31:
     hand=lerp(hand,Vector((-.85,-13.23,1.52)),smooth((t-28)/1)); contact=t>=29
    elif side==-1 and 39.5<t<48: hand=lerp(hand,price_grip,smooth((t-39.5)/.5)); contact=True
    elif side==-1 and 32<t<40: hand=P+Vector((-.5,0,1.5))
    elif side==-1 and 48<t<56: hand=P+Vector((-.45,-.35,1.55+.1*math.sin(t*5)))
   if i==3 and side==1 and 56<t<62:
    plant=Vector((-3.85,3,.55)); carry=P+right*.32+F*.3+Vector((0,0,1.35))
    if t<57.2: hand=lerp(hand,plant,smooth((t-56)/1.2))
    elif t<57.5: hand=plant; contact=True
    else: hand=lerp(plant,carry,smooth((t-57.5)/1.5)); contact=True
   if i==4 and side==1 and 58<t<64: hand=P+right*.3+F*.4+Vector((0,0,1.55+.35*smooth((t-58)/4)))
   elbow,wrist,err=ik(shoulder,hand,.43,right*side+F*.15)
   segment(limb[0],shoulder,elbow,.075,f); segment(limb[1],elbow,wrist,.065,f); record(limb[2],f,wrist,(0,0,yaw),(.10,.095,.105)); hands[(i,side)]=wrist.copy()
   if contact: metrics['grip_errors'].append({'frame':f,'actor':i,'side':side,'error':err})
 # Actual note grasp point is the hand, with copy-location enforcing contact after release.
 for ni,(root,hinges) in enumerate(notes):
  attach=Vector((.25,-2.0,1.98)) if ni==0 else Vector((1.15,-2.0,1.98)); grab=5.5 if ni==0 else 12.2; growth=smooth((t-(-.3 if ni==0 else 8.2))/1.65)
  if ni==0 and t>=24: growth=.001
  location=hands[(ni,1)] if t>=grab else attach
  record(root,f,location,(0,0,.06*math.sin(t*2) if t>grab else 0),(max(.001,growth),)*3)
  record(hinges[1],f,hinges[1].location,(0,0,(1-smooth((t-.15)/1.2))*1.2 if ni==0 else 0),(1,1,1))
 # Hand-held cash stack substitutes increasing nominal wealth for the single note.
 record(cashroot,f,hands[(0,1)],(0,0,0),(.001,)*3 if t<24 else (1,1,1))
 for o in cashstack: pass
 for i,o in enumerate(bread):
  # Shrink only outside relevant shots; visible collection is animated on the bottom loaf.
  available=12 if t<28 else (5 if t<36 else (2 if t<46 else (1 if t<50 else 0)))
  loc=Vector((-1.8+(i%4)*1.15,-11.65,.65+(i//4)*.8))
  if i==0 and 28<t<29: loc=lerp(loc,hands[(2,1)],smooth(t-28))
  elif i==0 and 29<=t<30.4: loc=hands[(2,1)]
  elif i==0 and 30.4<=t<32: loc=hands[(0,-1)]
  record(o,f,loc,(0,0,0),(.32,.21,.18) if i<available and not (i==0 and t>=32) else (.001,)*3)
 index=0 if t<42 else (1 if t<44 else (2 if t<46 else 3))
 for i,o in enumerate(price_texts): record(o,f,o.location,o.rotation_euler,(1,1,1) if i==index else (.001,)*3)
 for o,x,y,phase,ang in fall:
  age=max(0,t-16-phase*4.5); active=smooth((t-16-phase*4.5)/.35); falltime=min(age,5); floor=ground(x+.5*math.sin(falltime+ang),y+.3*math.cos(falltime*.8+ang))+.01; z=max(floor,7.18-7*(falltime/5)**2)
  record(o,f,(x+.5*math.sin(falltime+ang),y+.3*math.cos(falltime*.8+ang),z),(.4*math.sin(falltime*3+ang)*(1-falltime/5),.4*math.sin(falltime*2+ang)*(1-falltime/5),ang+falltime*.8),(.55*max(.001,active),.27*max(.001,active),.015*max(.001,active)))
 for o,x,y,delay in final_fall:
  age=max(0,t-72-delay); active=smooth((t-72-delay)/.3); u=min(age/4,1); z=.605+3*(1-u*u)
  record(o,f,(x+.12*math.sin(age*2),y,z),(.3*math.sin(min(age,4)*4)*(1-u),.3*math.sin(min(age,4)*3)*(1-u),min(age,4)*.5),(.5*max(.001,active),.24*max(.001,active),.015*max(.001,active)))
 for o,ti,j,loc in attached:
  growth=smooth((t-(16+ti*.06 if ti<99 else 28+j*.12))/2); scale=(max(.001,growth),)*3 if ti<99 else (.6*max(.001,growth),.3*max(.001,growth),.02*max(.001,growth))
  record(o,f,loc,(0,0,.06*math.sin(t*1.7+j)) if ti<99 else o.rotation_euler,scale)
 record(van,f,(-8+16*smooth((t-59)/7),-7,.048),(0,0,0),(1,1,1))
 for wheel in wheels: record(wheel,f,wheel.location,(math.pi/2,(van.location.x+8)/.3,0),(.3,.3,.15))
 crop=Vector((-3.85,3,.55)) if t<57.2 else (hands[(3,1)] if t<62 else Vector((-2,2.1,.95))); record(produce,f,crop,(0,0,0),(.18,)*3)
 ha=hands[(4,1)]; b=ha+Vector((0,0,1.1))
 if t>62: ha=lerp(ha,(3,2,3.2),smooth((t-62)/1.7)); b=lerp(b,(6,2,3.2),smooth((t-62)/1.7))
 segment(beam,ha,b,.09,f)
 # Story-specific framing. Smooth moves inside each motivated shot; editorial cuts between shots.
 if t<2:
  cp=lerp((-.15,-3.8,2.12),(-.10,-3.5,2.07),smooth(t/2)); target=Vector((-.02,-2.0,1.84)); lens=80
 elif t<8:
  u=smooth((t-2)/1.1); cp=lerp((-.10,-3.5,2.07),hero+Vector((2.4-4.8*smooth((t-5.8)/2),-3.7+.2*max(0,t-3.1),2.65)),u); target=lerp((-.02,-2.0,1.84),hero+Vector((0,.3,1.3)),u); lens=80-35*u
 elif t<16: cp=lerp((3.8,-5.3,2.5),(3,-4.7,2.35),smooth((t-8)/8)); target=Vector((1.15,-2,1.6)); lens=48
 elif t<19.5: cp=lerp((18,-24,21),(14,-20,17),smooth((t-16)/3.5)); target=Vector((0,0,1.5)); lens=38
 elif t<24: cp=Vector((7-(t-19.5)*.35,-8,2.5)); target=Vector((3.3,-3.5,1.3)); lens=42
 elif t<32: cp=hero+Vector((.6,-3.5,2.5)); target=hero+Vector((0,.1,1.25)); lens=48
 elif t<40: cp=lerp((-3,-16,2.8),(-2.5,-15.2,2.6),smooth((t-32)/8)); target=Vector((.15,-12.4,1.55)); lens=50
 elif t<47: cp=lerp((2.5,-17.1,2.55),(2.1,-16.6,2.4),smooth((t-40)/7)); target=Vector((.45,-13.2,1.7)); lens=43
 elif t<48: cp=Vector((-1.5,-12.1,2.3)); target=hero+Vector((0,0,1.5)); lens=56
 elif t<52.5: cp=lerp((-1.4,-12.1,2.2),(-1.6,-12.15,2.15),smooth((t-48)/4.5)); target=hero+Vector((0,0,1.45)); lens=48
 elif t<56: cp=lerp((-3.1,-17.3,2.5),(-2.4,-16.4,2.3),smooth((t-52.5)/3.5)); target=Vector((-.25,-13.6,1.45)); lens=50
 elif t<58.6: cp=Vector((-1.5,-.8,2.3)); target=Vector((-3.8,2.8,1)); lens=48
 elif t<61.2: cp=Vector((4,-.5,2.6)); target=Vector((3.7,2.8,1.7)); lens=45
 elif t<64: cp=van.location+Vector((3.4,-4.3,2.0)); target=van.location+Vector((0,0,1.0)); lens=45
 elif t<68: cp=lerp((-2.3,-12.2,2.4),(-2,-12.3,2.2),smooth((t-64)/4)); target=hero+Vector((0,0,1.5)); lens=52
 elif t<72: cp=lerp((1,-17.4,2.3),(.65,-16.5,2.2),smooth((t-68)/4)); target=hero+Vector((0,.25,1.45)); lens=57
 else: cp=lerp((3.8,-7,3.6),(10,-14,9),smooth((t-72)/6)); target=Vector((0,-.4,2)); lens=43
 record(cam,f,cp,(Vector(target)-cp).to_track_quat('-Z','Y').to_euler(),(1,1,1)); camera_keys.append((f,lens))
# Bulk key insertion keeps the rebuild practical and the saved file fully editable.
for name,data in tracks.items():
 o=S.objects.get(name)
 if not o: continue
 action=bpy.data.actions.new(name+' baked V2'); o.animation_data_create(); o.animation_data.action=action
 for prop,values in data.items():
  for axis in range(3):
   axis_values=[(frame,vals[axis]) for frame,vals in values]
   if max(v for _,v in axis_values)-min(v for _,v in axis_values)<1e-7:
    getattr(o,prop)[axis]=axis_values[0][1]; continue
   kept=[axis_values[0]]
   for j in range(1,len(axis_values)-1):
    fa,va=axis_values[j-1]; fb,vb=axis_values[j]; fc0,vc=axis_values[j+1]
    if abs((vb-va)/(fb-fa)-(vc-vb)/(fc0-fb))>1e-7: kept.append(axis_values[j])
   kept.append(axis_values[-1])
   fc=action.fcurves.new(data_path=prop,index=axis); fc.keyframe_points.add(len(kept)); co=[x for frame,value in kept for x in (frame,value)]; fc.keyframe_points.foreach_set('co',co)
   for kp in fc.keyframe_points: kp.interpolation='LINEAR'
   fc.update()
a=bpy.data.actions.new('V2 focal length'); cam.data.animation_data_create(); cam.data.animation_data.action=a; fc=a.fcurves.new(data_path='lens'); fc.keyframe_points.add(len(camera_keys)); fc.keyframe_points.foreach_set('co',[v for k in camera_keys for v in k]);
for kp in fc.keyframe_points: kp.interpolation='LINEAR'
fc.update()
# Constraint makes held currency follow the visible hand exactly between baked frames.
for ni,(o,_) in enumerate(notes):
 c=o.constraints.new('COPY_LOCATION'); c.name='Maintain physical hand contact'; c.target=rigs[ni]['arms'][1][2]
 for frame,value in [(1,0),(165 if ni==0 else 366,0),(166 if ni==0 else 367,1),(S.frame_end,1)]: c.influence=value; c.keyframe_insert(data_path='influence',frame=frame)
metrics['max_reach_error_m']=max([m['error'] for m in metrics['grip_errors']] or [0]); metrics['max_stance_floor_error_m']=max(metrics['stance_foot_z_errors'] or [0]); metrics['root_translation']={str(i):r['dist'][min(S.frame_end,2340)] for i,r in enumerate(rigs)}
metrics['footstep_events']=footsteps; metrics['object_count']=len(S.objects); metrics['test']=TEST
(R/'reports'/('test_motion_metrics.json' if TEST else 'full_motion_metrics.json')).write_text(json.dumps(metrics,indent=2))
bpy.context.preferences.filepaths.save_version=0; S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender'/('V2_TEST.blend' if TEST else 'V2_CITY.blend')))
preview_frames=([20,100,150,210] if TEST else [550,820,930,1060,1310,1415,1510,1580,1730,1800,1880,1960,2040,2260])
if '--critical' in sys.argv: preview_frames=[1415,1800]
if '--no-preview' in sys.argv: preview_frames=[]
for f in preview_frames:
 S.frame_set(f); S.render.filepath=str(R/'test'/f'preview_{f:04}.png'); bpy.ops.render.render(write_still=True)
print('V2_BUILD_COMPLETE',metrics['max_reach_error_m'],metrics['max_stance_floor_error_m'],flush=True)
