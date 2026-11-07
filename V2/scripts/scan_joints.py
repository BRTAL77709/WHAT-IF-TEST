import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]; S=bpy.context.scene
names=lambda prefix: sorted([o for o in S.objects if o.name.startswith(prefix)],key=lambda o: int(o.name.rsplit('.',1)[-1]) if o.name.rsplit('.',1)[-1].isdigit() else -1)
upper=names('V2 Upper arm'); lower=names('V2 Forearm'); hands=names('V2 Contact hand'); thighs=names('V2 Thigh'); shins=names('V2 Shin'); feet=names('V2 Planted shoe')
maximum=0; worst=[]
for frame in range(1,(S.frame_end if '--all' in sys.argv else min(S.frame_end,240))+1):
 S.frame_set(frame); deps=bpy.context.evaluated_depsgraph_get()
 for a,b,h in zip(upper,lower,hands):
  A=a.evaluated_get(deps).matrix_world; B=b.evaluated_get(deps).matrix_world; H=h.evaluated_get(deps).matrix_world.translation
  err=max((A@Vector((0,0,.5))-B@Vector((0,0,-.5))).length,(B@Vector((0,0,.5))-H).length)
  if err>maximum: maximum=err;worst.append({'frame':frame,'part':b.name,'error_m':err})
 for a,b,shoe in zip(thighs,shins,feet):
  A=a.evaluated_get(deps).matrix_world; B=b.evaluated_get(deps).matrix_world; H=shoe.evaluated_get(deps).matrix_world.translation+Vector((0,0,.07))
  err=max((A@Vector((0,0,.5))-B@Vector((0,0,-.5))).length,(B@Vector((0,0,.5))-H).length)
  if err>maximum: maximum=err;worst.append({'frame':frame,'part':b.name,'error_m':err})
report={'maximum_evaluated_joint_gap_m':maximum,'worst':worst[-10:]}; (R/'reports'/('full_joint_continuity.json' if '--all' in sys.argv else 'test_joint_continuity.json')).write_text(json.dumps(report,indent=2)); print(json.dumps(report))
