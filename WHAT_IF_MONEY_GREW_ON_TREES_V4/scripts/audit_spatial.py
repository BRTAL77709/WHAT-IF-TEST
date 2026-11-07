import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;S.frame_set(1);V3=R.parent/'WHAT_IF_MONEY_GREW_ON_TREES_V3';rigs=json.loads((V3/'reports/rig_map.json').read_text());verts=[];faces=[]
for o in S.objects:
 if o.type=='MESH' and o.name.startswith('Static environment /'):
  offset=len(verts);verts.extend([o.matrix_world@v.co for v in o.data.vertices]);faces.extend([tuple(offset+j for j in p.vertices) for p in o.data.polygons])
bvh=BVHTree.FromPolygons(verts,faces);foot=[];bread=[];visibility=[];camera=[]
for f in range(1,2341):
 S.frame_set(f);t=(f-1)/30;graph=bpy.context.evaluated_depsgraph_get();cam=S.camera;origin=cam.matrix_world.translation
 for i,r in enumerate(rigs):
  for side in [0,1]:
   o=S.objects[r['legs'][side][2]]
   for sx,sy in [(-.5,-.5),(-.5,.5),(.5,-.5),(.5,.5)]:
    p=o.matrix_world@Vector((sx,sy,-.5));hit,n,idx,d=bvh.ray_cast(p+Vector((0,0,.35)),Vector((0,0,-1)),1)
    if hit is not None and abs(n.z)>.8 and hit.z-p.z>.015:foot.append({'frame':f,'actor':i,'side':side,'penetration_m':float(hit.z-p.z),'corner':[sx,sy]})
 if f in [1,721,1021,1441,1921]:
  for o in S.objects:
   if o.name.startswith('V2 Bread inventory'):
    bounds=[o.matrix_world@Vector(v) for v in o.bound_box];bottom=min(v.z for v in bounds);p=o.matrix_world.translation;hit,n,idx,d=bvh.ray_cast(Vector((p.x,p.y,bottom+.02)),Vector((0,0,-1)),1)
    if hit is not None:bread.append({'frame':f,'object':o.name,'bottom_z':bottom,'support_z':hit.z,'gap_m':bottom-hit.z})
 actor=0 if (3.1<=t<8 or 24<=t<56 or 64<=t<68 or 69.2<=t<72) else 1 if 8<=t<16 else 3 if 56<=t<58.6 else 4 if 58.6<=t<61.2 else None
 if actor is not None:
  target=S.objects[rigs[actor]['head']];position=target.matrix_world.translation;uv=world_to_camera_view(S,cam,position);direction=position-origin
  hit,point,normal,index,obj,matrix=S.ray_cast(graph,origin,direction.normalized(),distance=direction.length)
  if not (0<=uv.x<=1 and 0<=uv.y<=1 and uv.z>0) or (hit and obj.name.startswith('Static environment /')):
   visibility.append({'frame':f,'actor':actor,'in_frame':bool(0<=uv.x<=1 and 0<=uv.y<=1 and uv.z>0),'first_hit':obj.name if hit else None,'target_uv':[float(uv.x),float(uv.y)]})
 camera.append({'frame':f,'position':list(origin),'rotation':list(cam.rotation_euler),'lens_mm':cam.data.lens,'horizontal_fov_degrees':math.degrees(cam.data.angle_x),'near_clip':cam.data.clip_start,'far_clip':cam.data.clip_end})
 if f%300==0:print('SPATIAL_CHECK',f,flush=True)
(R/'reports'/('V4_spatial_findings.json' if '--v4' in sys.argv else 'V3_spatial_findings.json')).write_text(json.dumps({'foot_corner_penetrations':foot,'bread_support_samples':bread,'intended_head_visibility_flags':visibility,'scope':'All-frame foot corner/static-surface ray tests and intended subject head visibility; surface screening is not full swept collision proof.'},indent=2));(R/'reports'/('V4_camera_timeline.json' if '--v4' in sys.argv else 'V3_camera_timeline.json')).write_text(json.dumps(camera,indent=2));print('FINDINGS',len(foot),len(visibility),flush=True)
