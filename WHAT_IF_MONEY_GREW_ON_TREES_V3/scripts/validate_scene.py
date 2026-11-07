import bpy,json,math,hashlib,csv
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]; S=bpy.context.scene; S.frame_set(1); original=json.loads((R/'reports/V2_source_manifest.json').read_text()); rigs=json.loads((R/'reports/rig_map.json').read_text()); plan=np.load(R/'reports/repaired_plan.npz'); O={o.name:o for o in S.objects}
# Verify original identities, vertices, topology, materials, static transforms and typeface assets.
for d in bpy.data.meshes:
 if d.name not in original['mesh_sha256']: continue
 v=np.empty(len(d.vertices)*3,dtype=np.float32); d.vertices.foreach_get('co',v)
 h=hashlib.sha256(v.tobytes()+json.dumps([tuple(p.vertices) for p in d.polygons]).encode()).hexdigest()
 assert h==original['mesh_sha256'][d.name],d.name
for m in bpy.data.materials:
 if m.name in original['materials']: assert list(m.diffuse_color)==original['materials'][m.name],m.name
assert set(O)==set(x['name'] for x in original['objects'])
for x in original['objects']:
 o=O[x['name']]
 assert (o.data.name if o.data else None)==x['data']
 assert (o.parent.name if o.parent else None)==x['parent']
 if x['name'].startswith('Static environment /'):
  assert np.allclose(o.location,x['location']) and np.allclose(o.scale,x['scale']) and np.allclose(o.rotation_euler,x['rotation'])
 if o.type=='FONT': assert o.data.body==x['text']
verts=[]; polys=[]
for o in S.objects:
 if o.type=='MESH' and o.name.startswith('Static environment /'):
  off=len(verts); verts.extend([o.matrix_world@v.co for v in o.data.vertices]); polys.extend([tuple(off+j for j in p.vertices) for p in o.data.polygons])
bvh=BVHTree.FromPolygons(verts,polys)
selected=[o for o in S.objects if o.name.startswith('V2') and (o.animation_data or o.parent)]; names=[o.name for o in selected]; a=np.zeros((2340,len(selected),10),np.float32)
jointgap=0.; limb_error=0.; contacts=[]; grip=[]; footdrift=[]; camera=[]; bodyflags=[]; rows=[]; prevfeet={}; nearestpair=1e9; minpairframe=0
for f in range(1,2341):
 S.frame_set(f); graph=bpy.context.evaluated_depsgraph_get(); objs={n:O[n].evaluated_get(graph) for n in O};
 for j,o in enumerate(selected):
  p,q,s=objs[o.name].matrix_world.decompose(); a[f-1,j]=[*p,*q,*s]
 for i,r in enumerate(rigs):
  root=objs[r['root']].matrix_world.translation
  for limbkind,length in [('legs',.46),('arms',.43)]:
   for side in range(2):
    upper,lower,end=[objs[n] for n in r[limbkind][side]]
    p=upper.matrix_world@Vector((0,0,-.5)); q=upper.matrix_world@Vector((0,0,.5)); b=lower.matrix_world@Vector((0,0,-.5)); c=lower.matrix_world@Vector((0,0,.5))
    jointgap=max(jointgap,(q-b).length); limb_error=max(limb_error,abs((q-p).length-length),abs((c-b).length-length))
    if limbkind=='legs':
     shoe=end.matrix_world.translation
     if f>1 and plan['stance'][f-1,i,side] and plan['stance'][f-2,i,side]: footdrift.append((shoe-prevfeet[i,side]).length)
     prevfeet[i,side]=shoe.copy()
  # Character body screening at torso, shins (near-surface flags require review).
  for h in [.45,1.16]:
   point=root+Vector((0,0,h)); hit=bvh.find_nearest(point)
   if hit[0] is not None and hit[3]<.12 and abs(hit[1].z)<.6: bodyflags.append({'frame':f,'actor':i,'height':h,'distance':hit[3],'signed_normal':(point-hit[0]).dot(hit[1])})
 t=(f-1)/30
 if 28<=t<30.4: contacts.append({'frame':f,'contact':'seller_loaf','error':(objs['V2 Bread inventory'].matrix_world.translation-objs[rigs[2]['arms'][1][2]].matrix_world.translation).length})
 if 30.4<=t<34.4: contacts.append({'frame':f,'contact':'buyer_loaf','error':(objs['V2 Bread inventory'].matrix_world.translation-objs[rigs[0]['arms'][0][2]].matrix_world.translation).length})
 if 57.2<=t<63.2: contacts.append({'frame':f,'contact':'farmer_crop','error':(objs['V2 Hand-picked crop'].matrix_world.translation-objs[rigs[3]['arms'][1][2]].matrix_world.translation).length})
 if 40<=t<47.2:
  target=objs['V2 Physical price flip rig'].matrix_world@Vector((0,-.01,-.37)); contacts.append({'frame':f,'contact':'seller_price_sign','error':(target-objs[rigs[2]['arms'][0][2]].matrix_world.translation).length})
 for i,grab,note in [(0,166,'V2 Hero banknote GRIP CORNER'),(1,367,'V2 Harvester banknote GRIP CORNER')]:
  if f>=grab: grip.append((objs[note].matrix_world.translation-objs[rigs[i]['arms'][1][2]].matrix_world.translation).length)
 for i in range(7):
  for j in range(i+1,7):
   d=(objs[rigs[i]['root']].matrix_world.translation-objs[rigs[j]['root']].matrix_world.translation).length
   if d<nearestpair: nearestpair=d; minpairframe=f
 point=objs[S.camera.name].matrix_world.translation; hit=bvh.find_nearest(point)
 if hit[0] is not None and hit[3]<.08: camera.append({'frame':f,'distance':hit[3]})
 rows.append({'frame':f,'time':(f-1)/30,'joint_gap_max_so_far':jointgap,'limb_length_error_max_so_far':limb_error})
 if f%300==0: print('V3_VALIDATED_FRAME',f,flush=True)
np.savez_compressed(R/'reports/V3_transforms.npz',names=names,transforms=a)
summary={'status':'TECHNICAL PASS' if jointgap<.001 and limb_error<.001 and max(grip)<.001 and max(footdrift)<.001 and nearestpair>.48 and not camera else 'TECHNICAL FAIL','assets_preserved':True,'mesh_topology_positions_materials_unchanged':True,'object_names_parents_unchanged':True,'static_layout_unchanged':True,'max_joint_gap_m':jointgap,'max_limb_length_error_m':limb_error,'max_held_note_grip_distance_m':max(grip),'max_stance_drift_per_frame_m':max(footdrift),'minimum_actor_root_separation_m':nearestpair,'minimum_actor_root_separation_frame':minpairframe,'camera_near_surface_frames':camera,'body_near_surface_flags':bodyflags,'screening_limits':'Nearest surfaces are screening flags, not certified full swept-volume collisions. All-frame transform and joint checks do not certify every stylized pose or artistic criterion.'}
(R/'reports/contact_diagnostics.json').write_text(json.dumps({'measurements':contacts,'max_contact_error_m':max(c['error'] for c in contacts)},indent=2))
assert max(c['error'] for c in contacts)<.01
(R/'reports/scene_validation.json').write_text(json.dumps(summary,indent=2))
with open(R/'reports/frame_diagnostics.csv','w') as file:
 w=csv.DictWriter(file,fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
print('SCENE_VALIDATION',json.dumps({k:v for k,v in summary.items() if not isinstance(v,list)}),flush=True)
# Contact/action previews before expensive full rendering.
for f in [145,166,220,840,913,1020,1300,1440,1717,1800,1880,1900,2050,2250]:
 S.frame_set(f); S.render.filepath=str(R/'test'/f'preview_{f:04}.png'); bpy.ops.render.render(write_still=True)
