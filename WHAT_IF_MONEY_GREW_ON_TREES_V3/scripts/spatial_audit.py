import bpy,json,math
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]; S=bpy.context.scene; S.frame_set(1)
verts=[]; faces=[]
for o in S.objects:
 if not o.name.startswith('Static environment /') or o.type!='MESH': continue
 off=len(verts); verts.extend([o.matrix_world@v.co for v in o.data.vertices]); faces.extend([tuple(off+i for i in p.vertices) for p in o.data.polygons])
bvh=BVHTree.FromPolygons(verts,faces)
z=np.load(R/'reports/V2_transforms.npz'); names=list(z['names']); arr=z['transforms']; events=[]; cam=[]
for i in range(7):
 p=arr[:,names.index(f'V2 Actor {i} ROOT'),:3]
 for f in range(0,2340,3):
  for h in [.45,1.05,1.6]:
   q=Vector(p[f])+Vector((0,0,h)); hit=bvh.find_nearest(q)
   if hit[0] is not None and hit[3]<.16:
    events.append({'frame':f+1,'actor':i,'height':h,'surface_distance':hit[3],'normal_dot':(q-hit[0]).dot(hit[1])}); break
for f in range(2340):
 p=Vector(arr[f,names.index(S.camera.name),:3]); hit=bvh.find_nearest(p)
 if hit[0] is not None and hit[3]<.08: cam.append({'frame':f+1,'surface_distance':hit[3]})
# True floor heights queried against the existing triangles (no remodeled ground).
floors=[]
for i in range(7):
 p=arr[:,names.index(f'V2 Actor {i} ROOT'),:3]; row=[]
 for v in p:
  q,n,ind,d=bvh.ray_cast(Vector((float(v[0]),float(v[1]),.9)),Vector((0,0,-1)),2)
  row.append(float(q.z) if q is not None else 0.)
 floors.append(row)
np.save(R/'reports/V2_actual_ground.npy',np.array(floors))
(R/'reports/V2_spatial_audit.json').write_text(json.dumps({'near_surface_actor_samples':events,'camera_near_surface_frames':cam,'scope':'Static environment triangle BVH. Near-surface is a screening flag, not proof of interpenetration. Samples every 3 frames for actors, every frame for camera.'},indent=2))
print('SPATIAL_AUDIT',len(events),len(cam),flush=True)
