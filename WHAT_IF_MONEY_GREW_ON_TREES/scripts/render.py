from pathlib import Path
import bpy,sys,time
R=Path(__file__).resolve().parents[1]; S=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
a=int(args[0]) if args else 1; b=int(args[1]) if len(args)>1 else 2340
S.render.image_settings.file_format='PNG'; S.render.image_settings.compression=15
for frame in range(a,b+1):
 path=R/'renders'/f'frame_{frame:04}.png'
 if path.exists(): continue
 S.frame_set(frame); S.render.filepath=str(path); bpy.ops.render.render(write_still=True)
 print('PROGRESS',frame,'/',b,flush=True)
