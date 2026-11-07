import bpy,json,hashlib,math,sys
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1]; S=bpy.context.scene; S.frame_set(1)
def natural(o):
 n=o.name.rsplit('.',1); return int(n[1]) if len(n)>1 and n[1].isdigit() else 0
def group(n): return sorted([o for o in S.objects if o.name==n or o.name.startswith(n+'.')],key=natural)
rigs=[]
for i in range(7):
 rigs.append({'root':f'V2 Actor {i} ROOT','torso':group('V2 Jacket')[i].name,'head':group('V2 Head')[i].name,'hair':group('V2 Hair')[i].name,'eyes':[x.name for x in group('V2 Eye')[2*i:2*i+2]],'legs':[[group(n)[2*i+j].name for n in ['V2 Thigh','V2 Shin','V2 Planted shoe']] for j in range(2)],'arms':[[group(n)[2*i+j].name for n in ['V2 Upper arm','V2 Forearm','V2 Contact hand']] for j in range(2)]})
(R/'reports/rig_map.json').write_text(json.dumps(rigs,indent=2))
meshhash={}
for d in bpy.data.meshes:
 v=np.empty(len(d.vertices)*3,dtype=np.float32); d.vertices.foreach_get('co',v)
 topology=[tuple(p.vertices) for p in d.polygons]
 meshhash[d.name]=hashlib.sha256(v.tobytes()+json.dumps(topology).encode()).hexdigest()
objects=[]
for o in S.objects:
 entry={'name':o.name,'type':o.type,'data':o.data.name if o.data else None,'parent':o.parent.name if o.parent else None,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'dimensions':list(o.dimensions),'animated':bool(o.animation_data and o.animation_data.action),'constraints':[{'type':c.type,'target':c.target.name if hasattr(c,'target') and c.target else None} for c in o.constraints],'materials':[m.name for m in o.data.materials] if o.type in ['MESH','FONT'] else []}
 if o.type=='FONT': entry['text']=o.data.body
 objects.append(entry)
manifest={'source':bpy.data.filepath,'world_up':'Z','character_forward':'local +Y','frames':[1,2340],'fps':30,'objects':objects,'mesh_sha256':meshhash,'materials':{m.name:list(m.diffuse_color) for m in bpy.data.materials},'camera':{'name':S.camera.name,'clip_start':S.camera.data.clip_start,'clip_end':S.camera.data.clip_end,'sensor_width':S.camera.data.sensor_width},'collections':[c.name for c in bpy.data.collections]}
(R/'reports/V2_source_manifest.json').write_text(json.dumps(manifest,indent=2))
selected=[o for o in S.objects if o.name.startswith('V2') and (o.animation_data or o.parent)]
N=len(selected); transforms=np.zeros((2340,N,10),np.float32)
for f in range(1,2341):
 S.frame_set(f)
 for j,o in enumerate(selected):
  p,q,s=o.matrix_world.decompose(); transforms[f-1,j]=[*p,*q,*s]
 if f%300==0: print('AUDIT_FRAME',f,flush=True)
np.savez_compressed(R/'reports/V2_transforms.npz',names=[o.name for o in selected],transforms=transforms)
print('AUDIT_COMPLETE',len(S.objects),len(selected),flush=True)
