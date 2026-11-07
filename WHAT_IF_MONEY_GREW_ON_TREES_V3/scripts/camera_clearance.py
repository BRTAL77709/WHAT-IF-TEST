import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]; S=bpy.context.scene; cam=S.camera; source=Path(bpy.data.filepath); before=hashlib.sha256(source.read_bytes()).hexdigest()
# Correct the proven construction foreground-note occlusion only; preserve every other curve.
for f in range(1759,1837):
 cp=Vector((2.2,-.6,3.2)); target=Vector((4.5,2.65,1.5)); rot=(target-cp).to_track_quat('-Z','Y').to_euler()
 for fc in cam.animation_data.action.fcurves:
  if fc.data_path not in ['location','rotation_euler']: continue
  value=(cp if fc.data_path=='location' else rot)[fc.array_index]
  point=next((p for p in fc.keyframe_points if abs(p.co.x-f)<.01),None)
  if point: point.co.y=value
  else: fc.keyframe_points.insert(f,value,options={'FAST'})
for fc in cam.animation_data.action.fcurves:
 for p in fc.keyframe_points: p.interpolation='LINEAR'
 fc.update()
bpy.context.preferences.filepaths.save_version=0; S.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=str(source))
after=hashlib.sha256(source.read_bytes()).hexdigest()
(R/'reports/selective_camera_repair.json').write_text(json.dumps({'old_source_sha256':before,'new_source_sha256':after,'changed_objects':[cam.name],'changed_properties':['location','rotation_euler'],'affected_frames':[1759,1836],'reason':'Preview demonstrated foreground tree banknote occluding the construction worker. Corrected camera instead of moving protected geometry.','render_cache_rule':'Base render remains valid outside this shot because only these camera keys changed. Replace all affected frames with the new source before final assembly.'},indent=2))
S.frame_set(1800); S.render.filepath=str(R/'test/construction_camera_corrected.png'); bpy.ops.render.render(write_still=True)
