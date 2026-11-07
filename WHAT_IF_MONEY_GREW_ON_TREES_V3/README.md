# WHAT IF MONEY GREW ON TREES — V3 motion repair

Status: rendered and technically checked; ARTISTIC REVIEW REQUIRED. Final status is recorded in `reports/final_validation.json`; no user approval is claimed.

This directory repairs the actual V2 Blender scene. It does not construct replacement buildings, trees, characters, materials, typography or a new soundtrack. V1 and V2 files are protected by SHA-256 manifests. The existing 78-second script, narration, music, Foley, subtitles and price sequence remain the source.

## Source and reproduction

- Source baseline: `../V2/blender/V2_CITY.blend`, produced by `../V2/scripts/build.py` and the V2 render/encode scripts. The exact source inventory, geometry hashes, original object hierarchy and coordinate information are in `reports/V2_source_manifest.json`.
- `scripts/audit.py` and `scripts/spatial_audit.py` inspect the baseline. `scripts/plan_motion.py` prepares repaired paths/stance/swing timing. `scripts/repair.py` edits animation on the loaded V2 scene; it creates no geometry or materials. `scripts/camera_clearance.py` applies the demonstrated construction-shot visibility correction.
- Run in this WHAT-IF-TEST checkout with the existing Blender, Python, NumPy/SciPy/Pillow and FFmpeg. No installation, TTS, new music or paid service is required.

```sh
python WHAT_IF_MONEY_GREW_ON_TREES_V3/scripts/plan_motion.py
blender -b V2/blender/V2_CITY.blend -t 2 --python WHAT_IF_MONEY_GREW_ON_TREES_V3/scripts/repair.py
blender -b WHAT_IF_MONEY_GREW_ON_TREES_V3/blender/WHAT_IF_MONEY_GREW_ON_TREES_V3.blend -t 2 --python WHAT_IF_MONEY_GREW_ON_TREES_V3/scripts/camera_clearance.py
blender -b WHAT_IF_MONEY_GREW_ON_TREES_V3/blender/WHAT_IF_MONEY_GREW_ON_TREES_V3.blend -t 2 --python WHAT_IF_MONEY_GREW_ON_TREES_V3/scripts/validate_scene.py
python WHAT_IF_MONEY_GREW_ON_TREES_V3/scripts/run_render.py
python WHAT_IF_MONEY_GREW_ON_TREES_V3/scripts/encode.py
python WHAT_IF_MONEY_GREW_ON_TREES_V3/scripts/qa.py
```

The editable final blend already contains the baked repairs and does not require handlers or auto-run Python. The source baseline and scripts are needed only to rebuild the animation. Fresh rendering uses the final scene fingerprint; existing frames from a different fingerprint are rejected. The cloud production's selective camera rerender is separately recorded in `reports/render_provenance.json`.

## Actual repairs

- Replace stop/restart foot snaps with continuous scheduled swings and fixed world-space stance anchors; keep limb lengths fixed with two-segment IK.
- Retain all 51 audible footstep timestamps and the existing bill plucks, 30.4s bread handoff and 42/44/46s sign changes.
- Smooth body turns and head offsets; tie counter-swing to the feet. Correct shelf/bench/crowd blocking without moving scenery.
- Replace discontinuous hand targets, crop release and loaf disposal with continuous reaches, transfers, deposit and recovery.
- Keep the rigid housing beam at fixed length, use two hands and place it at the reachable lower frame instead of stretching it to an unreachable overhead support.
- Simulate the existing falling bills with gravity, drag, separate detachment times and triangle-ray collision/settling. No extra money objects are added.
- Correct delivery and final pullback camera clearance and the farm/construction visibility defects. Preserve the remaining V2 camera language, lenses and editorial cut times.
- Retain shelf props physically instead of hiding inventory through scale-to-zero changes. This removes a source-level popping defect; the narration and illustrative price progression remain unchanged.

## Deliverables and honest scope

`final/WHAT_IF_MONEY_GREW_ON_TREES_V3.mp4` is the native H.264/yuv420p master, with stream-copied original AAC. `scenes/` contains ten individual source-quality exports. `audio/V2_ORIGINAL_SOUNDTRACK.m4a` is the preserved soundtrack; `subtitles/` contains unchanged subtitle/narration source. `comparisons/` holds continuous V2/V3 comparison clips and consecutive-frame evidence.

Read `reports/QUALITY_CONTROL.md`, `scene_reports.json`, `scene_validation.json`, `frame_diagnostics.csv`, and `pixel_frame_diagnostics.csv` for measurements and limitations. TECHNICAL PASS applies to the stated checks only. ARTISTIC REVIEW REQUIRED remains distinct from USER APPROVED. Nearest-surface/root-clearance screening does not certify every swept mesh collision or every artistic pixel. No human listening or continuous-playback acceptance is claimed.

## Recovery without rerendering

The restored checkpoint already contains all 2,340 verified frames and the final master. Recovery repaired only nine invalid individual scene exports using `scripts/repair_scene_exports.py`, then resumed QC with `scripts/qa.py --resume-master-qc`. No completed render, V1/V2 file, voice or soundtrack was regenerated. Durable backup indexes are in `recovery/v3-restored-checkpoint/` on the V3 branch.

## Verified downloads

See [DOWNLOADS.md](DOWNLOADS.md) for the complete film, full-quality master recovery, ten scene exports, editable Blender source, comparisons and persistent recovery backups.
