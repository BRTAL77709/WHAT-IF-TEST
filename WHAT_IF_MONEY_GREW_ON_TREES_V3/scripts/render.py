import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]; a,b=map(int,sys.argv[sys.argv.index('--')+1:][:2]); S=bpy.context.scene
S.render.image_settings.file_format='PNG'; S.render.image_settings.compression=8
for f in range(a,b+1):
 p=R/'renders'/f'frame_{f:04}.png'
 if p.exists(): continue
 S.frame_set(f); S.render.filepath=str(p); bpy.ops.render.render(write_still=True); print('V3_FRAME',f,flush=True)
