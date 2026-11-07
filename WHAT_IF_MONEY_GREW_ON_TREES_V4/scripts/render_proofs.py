import bpy,json,hashlib
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];V3=R.parent/'WHAT_IF_MONEY_GREW_ON_TREES_V3';S=bpy.context.scene;S.render.image_settings.compression=60
proof=[]
for f in [30,270,367,840,913,1033,1630,1663,2056]:
 S.frame_set(f);p=R/'test'/f'proof_{f:04}.png';S.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 if f==30:
  im1=bpy.data.images.load(str(p),check_existing=False);im2=bpy.data.images.load(str(V3/'renders'/f'frame_{f:04}.png'),check_existing=False);a=np.array(im1.pixels[:],dtype=np.float32);b=np.array(im2.pixels[:],dtype=np.float32);assert np.array_equal(a,b),'Opening macro cache changed: invalidate all reused frames';proof.append({'frame':f,'V3_V4_native_pixels_identical':True})
(R/'reports/native_proof.json').write_text(json.dumps(proof,indent=2));print('NATIVE_OPENING_PROOF_PASS',flush=True)
