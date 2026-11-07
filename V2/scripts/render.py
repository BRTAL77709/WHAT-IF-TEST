import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]; args=sys.argv[sys.argv.index('--')+1:]; a,b=map(int,args[:2]); folder=args[2] if len(args)>2 else 'renders'
D=R/folder; D.mkdir(parents=True,exist_ok=True); S=bpy.context.scene
S.render.image_settings.file_format='PNG'; S.render.image_settings.compression=8
for frame in range(a,b+1):
 p=D/f'frame_{frame:04}.png'
 if p.exists(): continue
 S.frame_set(frame); S.render.filepath=str(p); bpy.ops.render.render(write_still=True); print('V2_FRAME',frame,flush=True)
