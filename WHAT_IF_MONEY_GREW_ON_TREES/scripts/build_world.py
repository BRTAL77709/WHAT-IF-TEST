import bpy, math, random, os, sys, json
from mathutils import Vector
from bpy.app.handlers import persistent
random.seed(777)
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials: bpy.data.materials.remove(d)
S=bpy.context.scene
S.render.engine='BLENDER_WORKBENCH'
S.render.resolution_x=1080; S.render.resolution_y=1920; S.render.resolution_percentage=100
S.render.fps=30; S.frame_start=1; S.frame_end=2340
S.render.image_settings.file_format='PNG'; S.render.film_transparent=False
S.display.shading.light='STUDIO'; S.display.shading.studiolight_rotate_z=0.5
S.display.shading.color_type='MATERIAL'; S.display.shading.show_shadows=True
S.display.shading.show_cavity=True; S.display.shading.cavity_type='BOTH'
S.display.shading.curvature_ridge_factor=1.4; S.display.shading.curvature_valley_factor=1.1
S.display.shading.show_specular_highlight=True
S.display.shading.background_type='WORLD'; S.world.color=(.055,.12,.17)
S.display.render_aa='8'
S.view_settings.view_transform='Standard'
def mat(n,c):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); return m
cream=mat('Warm limestone',(.81,.75,.57)); asphalt=mat('Midnight teal asphalt',(.075,.16,.19)); white=mat('Ivory',(.94,.91,.78)); gold=mat('Golden accent',(.98,.61,.16)); dark=mat('Deep navy',(.025,.075,.11)); glass=mat('Blue windows',(.17,.52,.63)); green=mat('Money mint',(.23,.83,.48)); ink=mat('Fictional currency ink',(.025,.25,.13)); bark=mat('Tree bark',(.29,.13,.07)); leafs=[mat('Foliage '+str(i),c) for i,c in enumerate([(.16,.44,.26),(.26,.60,.32),(.42,.69,.35)])]
palette=[mat('Building '+str(i),c) for i,c in enumerate([(.9,.39,.24),(.2,.51,.58),(.88,.65,.34),(.54,.68,.66),(.77,.48,.42)])]
red=mat('Coral red',(.95,.22,.16)); soil=mat('Garden soil',(.25,.17,.10)); skin=mat('Warm skin',(.76,.48,.29))
def cube(n,loc,scale,m,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=n; o.scale=scale
 o.data.materials.append(m)
 if bevel:
  mod=o.modifiers.new('Soft miniature edges','BEVEL'); mod.width=bevel; mod.segments=2
  o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o
def ico(n,loc,r,m,sub=1):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=r,location=loc); o=bpy.context.object; o.name=n; o.data.materials.append(m); return o
def cyl(n,a,b,r,m,vertices=8):
 a,b=Vector(a),Vector(b); v=b-a
 bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r,radius2=r*.83,depth=v.length,location=(a+b)/2)
 o=bpy.context.object; o.name=n; o.rotation_euler=v.to_track_quat('Z','Y').to_euler(); o.data.materials.append(m); return o
def text(n,body,loc,size,m,rot=(math.pi/2,0,0)):
 cr=bpy.data.curves.new(n,'FONT'); cr.body=body; cr.align_x='CENTER'; cr.size=size; cr.extrude=.008
 o=bpy.data.objects.new(n,cr); S.collection.objects.link(o); o.location=loc; o.rotation_euler=rot; cr.materials.append(m); return o
cube('Floating city foundation',(0,0,-.65),(37,34,1.3),cream,.3)
cube('Ground',(0,0,-.06),(36.7,33.7,.14),leafs[0])
for x in [-10,10]: cube('North south road',(x,0,.04),(4,34,.09),asphalt)
for y in [-7,7]: cube('East west road',(0,y,.045),(37,3.4,.1),asphalt)
for x in [-10,10]:
 for y in range(-15,17,3): cube('Lane marking',(x,y,.105),(.10,1.15,.015),white)
for y in [-7,7]:
 for x in range(-17,18,3): cube('Lane marking',(x,y,.11),(1.1,.1,.015),white)
for x in [-10,10]:
 for y in [-7,7]:
  for k in range(6): cube('Pedestrian crossing',(x-1.5+k*.6,y+2,.12),(.3,1,.025),white)
cube('Central park plaza',(0,0,.10),(14,9,.2),cream,.08)
cube('Tree planter',(0,0,.3),(3.4,3.4,.5),white,.12)
cube('Tree planter soil',(0,0,.56),(3.1,3.1,.07),soil)
# Permanent recognizable buildings; positions never change.
for i,(x,y,w,d,h) in enumerate([(-15,-12,4,4,4),(-5,-12,4,4,3),(1,-12,4.6,4,3.6),(6,-12,3,4,5.5),(15,-12,4,4,4.5),(-15,0,4,7,5),(15,0,4.5,7,4),(-15,12,4,5,6),(-5,12,4,4,5),(1,12,4,4,7),(6,12,3,4,4.5),(15,12,4,5,7)]):
 m=palette[i%len(palette)]
 cube('Building_%02d'%i,(x,y,h/2+.2),(w,d,h),m,.06)
 cube('Roof cornice',(x,y,h+.22),(w+.3,d+.3,.25),white)
 cube('Roof inset',(x,y,h+.4),(w-.3,d-.3,.18),dark)
 for z in [1.5+q*1.35 for q in range(max(1,int(h/1.4)))]:
  for xx in [-.28,.28]: cube('Window',(x+xx*w,y-d/2-.025,z),(.7,.08,.8),glass)
  for yy in [-.25,.25]: cube('Side window',(x+w/2+.025,y+yy*d,z),(.06,.7,.8),glass)
 if i in [1,2,5,6]:
  cube('Shop awning',(x,y-d/2-.5,2.3),(w,.95,.2),gold)
  text('Shop sign',['MARKET','BAKERY','BANK','GROCER'][[1,2,5,6].index(i)],(x,y-d/2-.08,2.65),.45,white)
# Market facing camera in foreground, cutaway empty shelves later.
cube('Market counter',(0,-10,.65),(4.5,.8,1.3),palette[0],.05)
for z in [.35,1.15,1.95]: cube('Grocery shelf',(0,-11.7,z),(4.5,.6,.13),white)
food=[]
for i in range(15):
 x=-1.8+(i%5)*.9; z=.65+(i//5)*.8
 o=ico('Loaf of bread',(x,-11.65,z),.32,gold,2); o.scale=(1,.65,.55); food.append(o)
# Productive corner: farm, construction and delivery in same city.
for row in range(4):
 cube('Crop bed',(-5+row*.9,3,.22),(.65,3,.24),soil)
 for j in range(5):
  ico('Crop produce',(-5+row*.9,1.8+j*.6,.5),.22,leafs[2])
for x in [3,6]:
 for y in [2,4.7]: cube('Construction post',(x,y,1.65),(.2,.2,3.3),gold)
for z in [1.7,3.2]:
 cube('Construction cross beam',(4.5,2,z),(3.3,.2,.2),gold); cube('Construction side beam',(3,3.4,z),(.2,3,.2),gold)
# Benches, lamps, mountains.
for x in [-6,6]:
 cube('Park bench',(x,-2,.7),(2,.6,.18),bark)
 for dx in [-.7,.7]: cube('Bench foot',(x+dx,-2,.35),(.12,.4,.7),dark)
for x in [-7.6,7.6]:
 for y in [-5,5]:
  cyl('Street light',(x,y,0),(x,y,3.5),.06,dark)
  ico('Lamp globe',(x,y,3.6),.24,gold,2)
for i in range(9):
 bpy.ops.mesh.primitive_cone_add(vertices=5,radius1=random.uniform(4,8),radius2=0,depth=random.uniform(4,9),location=(-30+i*8,27,-.5)); bpy.context.object.data.materials.append(palette[3])
# Tree geometry and branch-attached fictional notes.
trees=[]; bills=[]
positions=[(0,0),(-6,0),(6,0),(-5,5),(5,5),(-15,5),(15,5),(-15,-5),(15,-5),(-6,-4),(6,-4),(-5,15),(5,15)]
for ti,(x,y) in enumerate(positions):
 height=4.3 if ti==0 else 3.2
 cyl('Money tree trunk',(x,y,.2),(x,y,height),.24,bark)
 for j in range(5):
  ang=j*math.tau/5; ex=x+math.cos(ang)*1.3; ey=y+math.sin(ang)*1.3; ez=height+.3+(j%2)*.5
  cyl('Tree branch',(x,y,height*.62),(ex,ey,ez),.11,bark)
  ico('Faceted crown',(ex,ey,ez+.55),1.05,leafs[(ti+j)%3],1)
  for k in range(3):
   px=ex+math.cos(ang+k)*.45; py=ey+math.sin(ang+k)*.45; pz=ez-.10-k*.18
   # Horizontal paper mesh with inset stripe and fictional diamond mark.
   note=cube('Branch note %d %d %d'%(ti,j,k),(px,py,pz),(.65,.3,.018),green)
   stripe=cube('Currency stripe',(0,0,.012),(.48,.025,.004),ink); stripe.parent=note; stripe.location=(0,0,.7); stripe.scale=(.72,.08,.22)
   mark=ico('Fictional diamond',(0,0,0),.09,gold); mark.parent=note; mark.location=(0,0,1.1); mark.scale=(.13,.27,.4)
   note.rotation_euler=(.35,random.random()*.5,ang)
   bills.append((note,(px,py,pz),ti,random.random()*math.tau))
# Falling sheets and ground cover share meshes.
fall=[]
for i in range(120):
 o=cube('Fluttering cash %03d'%i,(0,0,0),(.55,.27,.018),green if i%3 else gold)
 fall.append((o,random.uniform(-17,17),random.uniform(-15,15),random.random(),random.random()*math.tau))
ground=[]
for i in range(180):
 x=random.uniform(-17,17); y=random.uniform(-15,15)
 o=cube('Discarded paper %03d'%i,(x,y,.18),(.62,.28,.025),green)
 o.rotation_euler.z=random.random()*math.tau; ground.append((o,random.uniform(20,54)))
# Cars.
cars=[]
for i in range(5):
 root=bpy.data.objects.new('Car rig %d'%i,None); S.collection.objects.link(root)
 for n,loc,sc,ma in [('Car body',(0,0,.55),(1.05,2,.5),palette[i]),('Car cabin',(0,-.1,.95),(.9,.95,.55),glass)]:
  o=cube(n,loc,sc,ma,.06); o.parent=root
 for xx in [-.55,.55]:
  for yy in [-.65,.65]:
   o=ico('Wheel',(xx,yy,.35),.28,dark,2); o.scale=(.4,1,1); o.parent=root
 cars.append(root)
# Simplified articulated humans; roots move with gait.
people=[]
for i in range(18):
 root=bpy.data.objects.new('Citizen %02d'%i,None); S.collection.objects.link(root)
 def part(n,loc,sc,ma):
  o=cube(n,loc,sc,ma,.06); o.parent=root; return o
 torso=part('Jacket',(0,0,1.04),(.43,.31,.55),palette[i%5])
 head=ico('Head',(0,0,1.55),.23,skin,2); head.parent=root
 hair=ico('Hair',(0,.025,1.69),.22,dark,1); hair.scale=(1,1,.6); hair.parent=root
 limbs=[]
 for side in [-1,1]:
  # pivot origins at hips/shoulders, children offset down.
  for kind,z,length in [('Leg',.80,.67),('Arm',1.24,.57)]:
   p=bpy.data.objects.new(kind+' pivot',None); S.collection.objects.link(p); p.parent=root; p.location=(side*(.13 if kind=='Leg' else .31),0,z)
   o=cube(kind,(0,0,0),(.14,.17,length),dark if kind=='Leg' else palette[i%5],.04); o.parent=p; o.location=(0,0,-length/2)
   if kind=='Leg':
    shoe=cube('Shoe',(0,0,0),(.18,.3,.13),dark,.025); shoe.parent=p; shoe.location=(0,-.06,-length)
   else:
    hand=ico('Hand',(0,0,0),.10,skin,1); hand.parent=p; hand.location=(0,0,-length)
   limbs.append((p,kind,side))
 people.append((root,limbs,i))
# A wheelbarrow and visible cash load near the market.
barrow=bpy.data.objects.new('Wheelbarrow rig',None); S.collection.objects.link(barrow)
for n,loc,sc,ma in [('Wheelbarrow tray',(0,0,.65),(1,1.2,.35),gold),('Barrow cash',(0,0,.92),(.85,1,.24),green),('Handle L',(-.5,.8,.8),(.07,1.1,.07),dark),('Handle R',(.5,.8,.8),(.07,1.1,.07),dark)]:
 o=cube(n,loc,sc,ma); o.parent=barrow
wheel=ico('Barrow wheel',(0,-.7,.3),.3,dark,2); wheel.parent=barrow
# Price marker in-world.
price=text('Bread price','$2',(0,-10.5,2.7),.9,gold)
# Camera and shot positions: constant city, intentional cuts, smooth dollies.
bpy.ops.object.camera_add(); cam=bpy.context.object; cam.name='Cinematic camera'; S.camera=cam; cam.data.type='ORTHO'; cam.data.lens=45; cam.data.clip_end=250
shots=[(0,7,(24,-34,30),(13,-20,17),(0,0,1.8),27,19),(7,15,(9,-14,11),(6,-10,8),(0,0,2.1),16,13),(15,23,(-25,-18,25),(20,-17,25),(0,1,1),31,29),(23,31,(20,-28,22),(12,-20,18),(0,-1,1.5),27,24),(31,39,(8,-23,12),(4,-19,9),(0,-10,1.2),14,11),(39,47,(-18,-25,21),(15,-25,22),(0,-4,1.5),27,28),(47,55,(12,-21,15),(6,-18,12),(0,-8,1),21,17),(55,64,(-13,-13,18),(-9,-9,13),(0,2,1.2),20,17),(64,72,(7,-20,10),(3,-17,7),(0,-10,1.2),13,9.5),(72,78,(20,-29,26),(26,-36,32),(0,0,1.5),29,36)]
for st,en,a,b,target,sa,sb in shots:
 for f,pos,scale in [(int(st*30)+1,a,sa),(int(en*30),b,sb)]:
  cam.location=pos; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=scale
  cam.keyframe_insert(data_path='location',frame=f); cam.keyframe_insert(data_path='rotation_euler',frame=f); cam.data.keyframe_insert(data_path='ortho_scale',frame=f)
for obj in [cam,cam.data]:
 for fc in obj.animation_data.action.fcurves:
  for p in fc.keyframe_points: p.interpolation='LINEAR'
# Bake procedural movements: portable editable animation, no external handler needed.
def smooth(x): return max(0,min(1,x))**2*(3-2*max(0,min(1,x)))
def key(o,path,f): o.keyframe_insert(data_path=path,frame=f)
for f in range(1,2342,5):
 t=(min(f,2340)-1)/30
 for o,base,ti,phase in bills:
  growth=smooth((t-(2 if ti==0 else 15+ti*.15))/2)
  o.scale=(.65*max(.001,growth),.3*max(.001,growth),.018*max(.001,growth)); o.rotation_euler.x=.35+.16*math.sin(t*2+phase)
  key(o,'scale',f); key(o,'rotation_euler',f)
 for o,x,y,phase,ang in fall:
  active=smooth((t-10-phase*10)/3); cycle=(t*.17+phase)%1
  o.location=(x+math.sin(t+ang)*.8,y+math.cos(t*.7+ang)*.4,.2+(1-cycle)*7)
  o.scale=(.55*max(.001,active),.27*max(.001,active),.018*max(.001,active))
  o.rotation_euler=(math.sin(t*3+ang)*.6,math.cos(t*2+ang)*.5,ang+t*.7)
  key(o,'location',f); key(o,'rotation_euler',f); key(o,'scale',f)
 for o,start in ground:
  a=max(.001,smooth((t-start)/4)); o.scale=(.62*a,.28*a,.025*a); key(o,'scale',f)
 for o in food:
  a=max(.001,1-smooth((t-36)/16)); o.scale=(a,.65*a,.55*a); key(o,'scale',f)
 for i,car in enumerate(cars):
  car.location=((-10 if i%2 else 10)+(-.7 if i%2 else .7),-16+((t*.65+i*6)%32),0)
  # Motion wraps outside the city, not in foreground.
  key(car,'location',f)
 for root,limbs,i in people:
  phase=i*.83
  if i==0: # recurring protagonist at central tree, then grocery
   u=smooth((t-25)/9); x=-2.3+u*2.7; y=-2.5-u*6.1
   speed=25<t<34
  else:
   a=i*2.399; radius=3.8+(i%3)*.8
   u=smooth((t-7-i*.1)/5); startx=math.cos(a)*7; starty=math.sin(a)*5
   x=startx*(1-u)+math.cos(a)*radius*u; y=starty*(1-u)+math.sin(a)*radius*u
   # After celebration, move toward shops, then productive work.
   v=smooth((t-28-i*.1)/7); endx=(-6+(i%7)*1.8); endy=-8.8 if i%2 else 3.2
   x=x*(1-v)+endx*v; y=y*(1-v)+endy*v
   speed=(7+i*.1<t<12+i*.1) or (28+i*.1<t<35+i*.1)
  root.location=(x,y,.02); root.rotation_euler.z=(math.pi if i%2 else 0)
  key(root,'location',f); key(root,'rotation_euler',f)
  for p,kind,side in limbs:
   if speed: p.rotation_euler.x=side*math.sin(t*9+phase)*(.6 if kind=='Leg' else -.6)
   elif kind=='Arm' and 10<t<29: p.rotation_euler.x=-1.6+.7*math.sin(t*3+phase+side)
   elif kind=='Arm' and t>47: p.rotation_euler.x=-.2+.12*math.sin(t+phase)
   else: p.rotation_euler.x=0
   key(p,'rotation_euler',f)
 barrow.location=(2,-8.5,0); barrow.scale=(1,1,1) if t>39 else (.001,)*3; key(barrow,'scale',f)
# Constant interpolation for discontinuous car wrapping and growth ordinary linear.
for o in bpy.data.objects:
 if o.animation_data and o.animation_data.action:
  for fc in o.animation_data.action.fcurves:
   for kp in fc.keyframe_points: kp.interpolation='LINEAR'
# Save all visual data, no external assets.
S.frame_set(110)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'blender','MONEY_CITY.blend'))
json.dump({'seed':777,'frames':2340,'fps':30,'resolution':[1080,1920],'objects':len(S.objects),'engine':S.render.engine,'shots':shots},open(os.path.join(ROOT,'reports','world_manifest.json'),'w'),indent=2)
if '--preview' in sys.argv:
 S.render.filepath=os.path.join(ROOT,'renders','preview.png'); bpy.ops.render.render(write_still=True)
