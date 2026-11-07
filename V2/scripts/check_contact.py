import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]; S=bpy.context.scene; obj=S.objects['V2 Hero banknote GRIP CORNER']; constraint=obj.constraints['Maintain physical hand contact']; hand=constraint.target
checks=[]
for frame in [166,180,200,230]:
 S.frame_set(frame); deps=bpy.context.evaluated_depsgraph_get(); a=obj.evaluated_get(deps).matrix_world.translation; b=hand.evaluated_get(deps).matrix_world.translation; error=(a-b).length; assert error<.0001; checks.append({'frame':frame,'grip_corner_to_hand_m':error})
(R/'reports'/'test_evaluated_contact.json').write_text(json.dumps(checks,indent=2)); print('CONTACT CONSTRAINT VERIFIED',checks)
