import bpy,math,random,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]; S=bpy.context.scene
S.frame_set(1)
# Add the visible prosperity phase without moving any existing building.
for i in [0,1,4,7,8]:
 b=S.objects['Building_%02d'%i]; x,y,z=b.location; h=z*2
 for part,loc,sc,ma in [('Penthouse',(x,y,h+.8),(2.1,2.1,1.2),'Blue windows'),('Penthouse roof',(x,y,h+1.45),(2.5,2.5,.16),'Ivory')]:
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=part; o.data.materials.append(bpy.data.materials[ma])
  for f,a in [(1,.001),(700,.001),(850,1),(2340,1)]: o.scale=tuple(v*a for v in sc); o.keyframe_insert(data_path='scale',frame=f)
# Wheelbarrow actually travels with an articulated pusher during the price spiral.
barrow=S.objects['Wheelbarrow rig']; person=S.objects['Citizen 16']
barrow.animation_data_clear()
for f in range(1,2342,5):
 t=(f-1)/30; u=max(0,min(1,(t-39)/8)); u=u*u*(3-2*u)
 barrow.location=(-4+u*8,-7,0); barrow.rotation_euler.z=-math.pi/2
 barrow.scale=(1,1,1) if t>=39 else (.001,)*3
 for path in ['location','rotation_euler','scale']: barrow.keyframe_insert(data_path=path,frame=f)
# Blend the pusher into this path from his existing movement.
for fc in person.animation_data.action.fcurves:
 if fc.data_path=='location' and fc.array_index<2:
  for k in fc.keyframe_points:
   t=(k.co.x-1)/30
   v=max(0,min(1,(t-35)/4)); v=v*v*(3-2*v)
   if t>=35:
    u=max(0,min(1,(t-39)/8)); u=u*u*(3-2*u)
    target=(-5.4+u*8) if fc.array_index==0 else -7
    k.co.y=k.co.y*(1-v)+target*v; k.handle_left.y=k.co.y; k.handle_right.y=k.co.y
 if fc.data_path=='rotation_euler' and fc.array_index==2:
  for k in fc.keyframe_points:
   if k.co.x>39*30: k.co.y=-math.pi/2
for p in person.children:
 if p.name.startswith(('Arm pivot','Leg pivot')) and p.animation_data:
  for fc in p.animation_data.action.fcurves:
   if fc.data_path=='rotation_euler' and fc.array_index==0:
    for k in fc.keyframe_points:
     t=(k.co.x-1)/30
     if 39<=t<=47:
      k.co.y=-1.1 if p.name.startswith('Arm') else .45*math.sin(t*8+(0 if p.location.x<0 else math.pi))
      k.handle_left.y=k.co.y; k.handle_right.y=k.co.y
# Densify paper on streets with linked meshes, not new unique geometry.
random.seed(82)
source=next(o for o in S.objects if o.name.startswith('Discarded paper'))
for i in range(140):
 o=source.copy(); o.data=source.data; o.animation_data_clear(); S.collection.objects.link(o); o.name='Street paper instance'
 if i%2: o.location=(random.uniform(-17,17),random.choice([-7,7])+random.uniform(-1.2,1.2),.17)
 else: o.location=(random.choice([-10,10])+random.uniform(-1.4,1.4),random.uniform(-15,15),.17)
 o.rotation_euler.z=random.random()*math.tau
 start=38+random.random()*12
 for f,a in [(1,.001),(int(start*30),.001),(int((start+3)*30),1),(2340,1)]: o.scale=(.62*a,.28*a,.025*a); o.keyframe_insert(data_path='scale',frame=f)
# Join static environment by material: reduces draw overhead without removing detail.
S.frame_set(1); before=len(S.objects)
groups={}
for o in list(S.objects):
 if o.type=='MESH' and not o.animation_data and o.parent is None:
  
  if o.modifiers:
   mesh=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
   o.modifiers.clear(); o.data=mesh
  name=o.active_material.name if o.active_material else 'none'; groups.setdefault(name,[]).append(o)
for name,obs in groups.items():
 if len(obs)<2: continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs: o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]; bpy.ops.object.join(); obs[0].name='Static environment / '+name
# Note decorations move with the note. Join them into each animated note mesh.
for note_name in [o.name for o in S.objects if o.name.startswith('Branch note')]:
 note=S.objects[note_name]
 if note.name.startswith('Branch note'):
  children=[o for o in note.children if o.type=='MESH']
  if not children: continue
  bpy.ops.object.select_all(action='DESELECT'); note.select_set(True)
  for o in children: o.select_set(True)
  bpy.context.view_layer.objects.active=note; bpy.ops.object.join()
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender'/'MONEY_CITY.blend'))
(R/'reports'/'optimization.json').write_text(json.dumps({'before':before,'after':len(S.objects),'native_resolution':[1080,1920],'geometry_detail_removed':False},indent=2))
for f in [800,1300]:
 S.frame_set(f); S.render.filepath=str(R/'renders'/f'optimized_{f}.png'); bpy.ops.render.render(write_still=True)
