import bpy,math,random
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]; S=bpy.context.scene
if S.objects.get('Bread price'): bpy.data.objects.remove(S.objects['Bread price'],do_unlink=True)
# Streets gradually acquire stacks of unspent fictional currency.
random.seed(1701)
for i,(x,y) in enumerate([(-4,-6),(-2,-6),(3,-6),(5,-7),(-7,-9),(7,-9),(-3,-14),(4,-14),(-2,1),(3,0),(7,4),(-7,4)]):
 for j in range(4):
  bpy.ops.mesh.primitive_cube_add(size=1,location=(x+j*.13,y+j*.1,.22+j*.23))
  o=bpy.context.object; o.name='Growing cash stack'; o.data.materials.append(bpy.data.materials['Money mint'])
  o.rotation_euler.z=i*.7+j*.3
  for f,a in [(1,.001),(int((26+i*.8)*30),.001),(int((32+i*.8)*30),1),(2340,1)]:
   o.scale=(1.25*a,.65*a,.17*a); o.keyframe_insert(data_path='scale',frame=f)
# Worker body language: harvesting and building replace celebration.
for index in [4,6,8,10,12,14,16]:
 root=S.objects['Citizen %02d'%index]
 arms=[o for o in root.children if o.name.startswith('Arm pivot')]
 for arm in arms:
  if arm.animation_data:
   for fc in arm.animation_data.action.fcurves:
    if fc.data_path=='rotation_euler' and fc.array_index==0:
     for k in fc.keyframe_points:
      t=(k.co.x-1)/30
      if 55<t<64: k.co.y=-.9+.55*math.sin(t*3+index); k.handle_left.y=k.co.y; k.handle_right.y=k.co.y
# Scene eight travels from crops toward the building frame, closer than the aerial shots.
cam=S.camera
for f,loc,target,scale in [(1651,(-8,-5,17),(-3.8,2.7,.8),15),(1920,(10,-4,17),(3.8,3,1),15)]:
 cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=scale
 cam.keyframe_insert(data_path='location',frame=f); cam.keyframe_insert(data_path='rotation_euler',frame=f); cam.data.keyframe_insert(data_path='ortho_scale',frame=f)
for obj in [cam,cam.data]:
 for fc in obj.animation_data.action.fcurves:
  for k in fc.keyframe_points: k.interpolation='LINEAR'
# Gold luxury car appears through an entrance along the existing road.
S.frame_set(1)
# Pack font data and all geometry; avoid backup files during repeated refinements.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender'/'MONEY_CITY.blend'))
for f in [1710,1870]:
 S.frame_set(f); S.render.filepath=str(R/'renders'/f'check_{f}.png'); bpy.ops.render.render(write_still=True)
