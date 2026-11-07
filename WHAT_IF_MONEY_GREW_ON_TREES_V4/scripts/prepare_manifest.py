from pathlib import Path
import json,hashlib,os,csv
R=Path(__file__).resolve().parents[1];V3=R.parent/'WHAT_IF_MONEY_GREW_ON_TREES_V3';blend=R/'blender/WHAT_IF_MONEY_GREW_ON_TREES_V4.blend';sha=hashlib.sha256(blend.read_bytes()).hexdigest();validation=json.loads((R/'reports/scene_validation.json').read_text());spatial=json.loads((R/'reports/V4_spatial_findings.json').read_text());assert validation['status']=='TECHNICAL PASS';assert not spatial['foot_corner_penetrations'] and not spatial['intended_head_visibility_flags']
original=json.loads((V3/'reports/recovery_checkpoint.json').read_text());cached={x['file']:x for x in original['frames']};frames=[]
for n in range(1,2341):
 source=V3/'renders'/f'frame_{n:04d}.png';target=R/'renders'/source.name
 # The opening macro has unchanged camera, paper and visible geometry; modified bread lies behind the camera.
 # A native diagnostic frame is compared byte-for-pixel before these frames are accepted for final assembly.
 reused=n<=60
 if reused:
  assert hashlib.sha256(source.read_bytes()).hexdigest()==cached[source.name]['png_sha256']
  if not target.exists():os.link(source,target)
 frames.append({'frame':n,'timestamp':(n-1)/30,'scene':min(10,(n-1)//240+1),'status':'reused_verified_V3' if reused else 'needs_render','path':str(target),'source_blend_sha256':sha if not reused else original['final_scene_sha256'],'png_sha256':cached[source.name]['png_sha256'] if reused else None,'reason':'Unchanged opening macro; native pixel equivalence test required' if reused else 'V4 sole/prop/contact/camera changes and conservative shadow invalidation'})
manifest={'source_blend':str(blend),'source_blend_sha256':sha,'fps':30,'frames_expected':2340,'master_timeline':str(R/'reports/MASTER_TIMELINE.csv'),'frames':frames,'completed_scene_archives':{},'quota_recovery':'Resume needs_render or invalid frames only. Verify per-frame hashes and source fingerprint. Never rerun V3 production.'}
(R/'reports/render_manifest.json').write_text(json.dumps(manifest,indent=2));(R/'renders/source_sha256.txt').write_text(sha);print('MANIFEST_READY',sum(x['status']=='needs_render' for x in frames),'new frames;',sum(x['status'].startswith('reused') for x in frames),'opening frames preserved',flush=True)
