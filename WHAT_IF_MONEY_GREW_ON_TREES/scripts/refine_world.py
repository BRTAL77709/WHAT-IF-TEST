import bpy,os,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]; S=bpy.context.scene
# Replace the obstructed market block with an open-front miniature shop.
remove=[]
for o in S.objects:
 x,y,z=o.location
 if -1.6<x<3.6 and -14.6<y<-9.8 and not (o.name.startswith(('Citizen','Car rig','Fluttering','Discarded','Leg','Arm'))):
  if o.name.startswith(('Building_02','Roof','Window','Side window','Shop awning','Shop sign')): remove.append(o)
for o in remove: bpy.data.objects.remove(o,do_unlink=True)
def box(n,loc,sc,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=n; o.scale=sc; o.data.materials.append(bpy.data.materials[ma]); return o
box('Market back wall',(0,-10.9,1.6),(5,.18,3.2),'Building 1')
for x in [-2.6,2.6]: box('Market side wall',(x,-11.8,1.5),(.16,1.8,3),'Warm limestone')
box('Market header',(0,-11,3.2),(5.4,.45,.55),'Golden accent')
cr=bpy.data.curves.new('Grocery signage','FONT'); cr.body='THE DAILY BREAD'; cr.align_x='CENTER'; cr.size=.36; cr.extrude=.005
ob=bpy.data.objects.new('Grocery signage',cr); S.collection.objects.link(ob); ob.location=(0,-11.27,3.16); ob.rotation_euler=(math.pi/2,0,0); cr.materials.append(bpy.data.materials['Deep navy'])
S.objects['Market counter'].location.y=-13.0
S.objects['Bread price'].location.y=-13.5
# No permanently printed price contradicts the animated editorial counter.
S.objects['Bread price'].data.body='FRESH BREAD'; S.objects['Bread price'].data.size=.4
# Let branch banknotes extend below the foliage, rather than hiding inside crowns.
for o in S.objects:
 if o.name.startswith('Faceted crown'): o.scale=(.76,.76,.76)
 if o.name.startswith('Branch note'):
  o.location.z-=.4
  # Scaling animations are adjusted directly and remain fully editable.
  for fc in o.animation_data.action.fcurves:
   if fc.data_path=='scale':
    factor=1.5 if fc.array_index<2 else 1
    for k in fc.keyframe_points: k.co.y*=factor; k.handle_left.y*=factor; k.handle_right.y*=factor
# More useful protagonist position in front of the grocery.
root=S.objects['Citizen 00']
for fc in root.animation_data.action.fcurves:
 if fc.data_path=='location' and fc.array_index==1:
  for k in fc.keyframe_points:
   t=(k.co.x-1)/30; u=max(0,min(1,(t-25)/9)); u=u*u*(3-2*u)
   k.co.y=-2.5-u*11.7; k.handle_left.y=k.co.y; k.handle_right.y=k.co.y
# Keep the wheelbarrow outside shelves.
S.objects['Wheelbarrow rig'].location.y=-14.3
# Native resolution, fast antialiasing; geometry and shadows retained.
S.display.render_aa='FXAA'
S.frame_set(1020); S.render.filepath=str(R/'renders'/'market_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender'/'MONEY_CITY.blend'))
bpy.ops.render.render(write_still=True)
for f in [120,1800,2040]:
 S.frame_set(f); S.render.filepath=str(R/'renders'/f'check_{f}.png'); bpy.ops.render.render(write_still=True)
