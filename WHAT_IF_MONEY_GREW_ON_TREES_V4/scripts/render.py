import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;args=sys.argv[sys.argv.index('--')+1:];a,b=map(int,args[:2]);manifest=json.loads((R/'reports/render_manifest.json').read_text());assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==manifest['source_blend_sha256'];S.render.image_settings.file_format='PNG';S.render.image_settings.compression=60
for f in range(a,b+1):
 row=manifest['frames'][f-1];p=Path(row['path'])
 if row['status'] in ['reused_verified_V3','rendered_verified'] and p.exists():continue
 if p.exists():
  # Only a completed hash recorded by the checkpoint is accepted, never an unverified partial file.
  if row.get('png_sha256') and hashlib.sha256(p.read_bytes()).hexdigest()==row['png_sha256']:continue
  p.unlink()
 S.frame_set(f);S.render.filepath=str(p);bpy.ops.render.render(write_still=True);print('V4_FRAME',f,flush=True)
