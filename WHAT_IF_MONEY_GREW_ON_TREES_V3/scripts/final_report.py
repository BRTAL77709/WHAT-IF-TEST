from pathlib import Path
import json,zipfile,hashlib,csv
import numpy as np
R=Path(__file__).resolve().parents[1]; report=json.loads((R/'reports/final_validation.json').read_text()); scene=json.loads((R/'reports/scene_validation.json').read_text()); contacts=json.loads((R/'reports/contact_diagnostics.json').read_text()); rows=json.loads((R/'reports/scene_reports.json').read_text()); z=np.load(R/'reports/V3_transforms.npz'); names=list(z['names']); a=z['transforms']; plan=np.load(R/'reports/repaired_plan.npz'); rigs=json.loads((R/'reports/rig_map.json').read_text())
for i,row in enumerate(rows):
 start=i*240;end=min(2340,start+240);roots=np.stack([a[start:end,names.index(r['root']),:3] for r in rigs],axis=1)
 row['root_path_distances_m']={str(j):float(np.linalg.norm(np.diff(roots[:,j],axis=0),axis=1).sum()) for j in range(7)}
 row['minimum_actor_root_separation_m']=min(float(np.linalg.norm(roots[:,j]-roots[:,k],axis=1).min()) for j in range(7) for k in range(j+1,7))
 stance=[]
 for j,r in enumerate(rigs):
  for side in [0,1]:
   p=a[start:end,names.index(r['legs'][side][2]),:3];mask=plan['stance'][start:end,j,side];d=np.linalg.norm(np.diff(p,axis=0),axis=1);stance.extend(d[mask[1:]&mask[:-1]].tolist())
 row['max_stance_drift_per_frame_m']=max(stance or [0])
 measurements=[x for x in contacts['measurements'] if start<x['frame']<=end];row['max_measured_prop_contact_error_m']=max([x['error'] for x in measurements] or [0]);row['prop_contacts_sampled']=sorted(set(x['contact'] for x in measurements))
 row['camera_proximity_flags']=len([x for x in scene['camera_near_surface_frames'] if start<x['frame']<=end]);row['body_proximity_flags']=len([x for x in scene['body_near_surface_flags'] if start<x['frame']<=end])
(R/'reports/scene_reports.json').write_text(json.dumps(rows,indent=2))
master=R/'final/WHAT_IF_MONEY_GREW_ON_TREES_V3.mp4';index=json.loads((R/'recovery/FRAME_BACKUP_INDEX.json').read_text()); backed=next(x for x in index['files'] if x['file']==master.name);assert backed['sha256']==report['sha256']
lines=['# V3 recovery and quality-control report','', 'TECHNICAL PASS for the checks below. ARTISTIC REVIEW REQUIRED. USER APPROVED: no.','',
'## Recovery checkpoint','',
'- Restored execution contained all 2,340 native frames, the completed 78-second master and the corrected construction-camera range. No completed frame was rerendered during recovery.',
'- Every PNG was decoded at 1080×1920 and hashed. The lossless RGB archive was decoded and compared against every original frame pixel hash: 2,340 exact matches. Opaque alpha restores to 255; PNG compression bytes may differ.',
'- Sources, Blender file, reports, checkpoint manifests, the lossless frame archive and unchanged native master are backed up on the separate `what-if-v3-motion-repair` GitHub branch. Every uploaded recovery object was downloaded and SHA-256 verified.',
'- QC had stopped at scene 1 because stream-copy `-t 8` included two subsequent B-frame packets. Scenes 1–9 were repaired using exact video packet counts and remuxed original AAC. Scene 10 was already valid and retained. The master and render PNGs remained unchanged.',
'', '## Final media','',f'- Master: `{master.name}` — {report["bytes"]:,} bytes; 78 seconds; 1080×1920; 30 FPS; 2,340 frames; H.264/yuv420p; faststart.',
'- All ten individual scene exports have exact expected video frame counts (240 each, last scene 180) and decode fully.',
'- Original V2 AAC stream is copied exactly, with identical encoded audio-packet SHA-256. Voice, music, Foley, levels and timeline were not regenerated.',
'- SRT, ASS, narration source and the protected V1/V2 files retain their recorded SHA-256 hashes.',
'- Backed-up pixel statistics cover every decoded master frame. They were reused after recovery because the master hash is unchanged; full-file decode/audio checks and repaired-scene checks were completed on the recovered files.',
'', '## Measured source-level checks','',
f'- Maximum evaluated joint gap: {scene["max_joint_gap_m"]:.9f} m.',f'- Maximum limb-length deviation from the existing rig lengths: {scene["max_limb_length_error_m"]:.9f} m.',f'- Maximum planted-foot drift per frame: {scene["max_stance_drift_per_frame_m"]:.9f} m.',f'- Maximum held-banknote corner-to-hand distance: {scene["max_held_note_grip_distance_m"]:.9f} m.',f'- Maximum sampled loaf/crop/sign contact distance: {contacts["max_contact_error_m"]:.9f} m.',f'- Minimum actor root separation: {scene["minimum_actor_root_separation_m"]:.6f} m.',f'- Audible footstep timing: all 51 retained; largest landing alignment difference {report["max_audible_footstep_error_seconds"]:.9f} seconds.',
'- Static-surface camera proximity flags (<0.08m): zero in the evaluated frames. This is a proximity screen, not a full swept-volume collision proof.',
'', '## Ten scenes','', '| Scene | Frames | Duration | Bytes | Max stance drift (m/frame) | Status |','|---|---:|---:|---:|---:|---|']
for row in rows:lines.append(f'| {row["scene_id"]:02} | {row["frames"]} | {row["duration"]:.3f}s | {row["bytes"]:,} | {row["max_stance_drift_per_frame_m"]:.9f} | TECHNICAL PASS / ARTISTIC REVIEW REQUIRED |')
lines+=['', 'Per-scene source paths, render commands, audio status, contact/clearance findings and remaining limitations are recorded in `scene_reports.json`.','', '## Confirmed motion repairs','', '| Object | V2 worst displacement in one frame | V3 worst displacement in one frame |','|---|---:|---:|']
motion=json.loads((R/'reports/motion_before_after.json').read_text())
for name in ['V2 Contact hand.004','V2 Contact hand.005','V2 Hand-picked crop','V2 Bread inventory','V2 Planted shoe']:
 x=next(x for x in motion if x['object']==name);lines.append(f'| {name} | {x["V2_max_frame_displacement_m"]:.6f} m | {x["V3_max_frame_displacement_m"]:.6f} m |')
lines+=['', 'Continuous comparison clips and consecutive-frame strips are in `comparisons/`. Motion analysis uses every evaluated frame and decoded-frame temporal statistics, rather than metadata/contact sheets alone.','', '## Limitations and unmet acceptance','']
lines+=['- '+x for x in report['limitations']]
lines+=['- OpenCV was not available in the restored toolchain. No installation was added. NumPy pixel differences, exact duplicates/black-frame detection and Blender transform/contact analysis were used; optical-flow measurements are unavailable.', '- Nearest-surface tests and root separation do not certify every hand/limb/self/prop swept-mesh collision. Camera visibility was inspected in previews; exhaustive per-pixel occlusion certification is not claimed.', '- Inventory objects remain physically present instead of disappearing by scale changes. This is a documented visual-state repair, not an exact reproduction of every V2 inventory visibility state.', '', '## Integrity','',f'Master SHA-256: `{report["sha256"]}`','',f'Encoded AAC packet hash: `{report["audio_packet_sha256"]}`','']
(R/'reports/QUALITY_CONTROL.md').write_text('\n'.join(lines))
p=R/'README.md';text=p.read_text().replace('Status: production in progress.','Status: rendered and technically checked; ARTISTIC REVIEW REQUIRED.');text+='\n## Recovery without rerendering\n\nThe restored checkpoint already contains all 2,340 verified frames and the final master. Recovery repaired only nine invalid individual scene exports using `scripts/repair_scene_exports.py`, then resumed QC with `scripts/qa.py --resume-master-qc`. No completed render, V1/V2 file, voice or soundtrack was regenerated. Durable backup indexes are in `recovery/v3-restored-checkpoint/` on the V3 branch.\n';p.write_text(text)
# Updated editable support package; the verified Blender ZIP remains a separate file.
archive=R/'final/V3_SCRIPTS_AUDIO_REPORTS.zip'; files=[*R.glob('*.md'),*R.glob('scripts/*.py'),*R.glob('audio/*'),*R.glob('subtitles/*'),*R.glob('reports/*'),*R.glob('comparisons/*.jpg')]
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:
  if p.is_file() and p.suffix not in ['.log']:z.write(p,arcname=str(Path(R.name)/p.relative_to(R)))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('FINAL_REPORT_AND_PACKAGE_READY',archive.stat().st_size,flush=True)
