# WHAT IF MONEY GREW ON TREES — V2

V2 is an actual motion rebuild of the existing low-poly miniature city, on branch `what-if-v2-production`. V1's committed download, Blender project and audio mix are protected by the checksums in `reports/V1_preservation.json`. No NOIRFRAME files or other repositories are used.

## What changed

- Perspective macro, action tracking, market close-ups, reaction reverses, productive-work views, and a final pullback replace the repeated aerial framing. There is one establishing aerial.
- Seven characters have world-space root paths. Analytic two-segment leg/arm IK, fixed stance anchors, lifting feet, weight shifts, and head/eye turns replace cycling limbs on stationary roots.
- A folded fictional banknote grows from a reachable branch. The primary grasp is constrained to the visible hand. The buyer carries cash, a loaf passes between seller and buyer, the seller touches the physical price board, and workers harvest, build and deliver.
- Camera positions and queue routes were revised after visual previews revealed occlusions. Keyframes at exact shot boundaries prevent interpolating cameras through geometry during edits.
- V2 uses a verified, local Kokoro neural voice (`af_heart`) at normal speed 1.0. No speech is accelerated to fit a slot. Captions use the actual generated phrase start/end times.
- New scene-specific score sections and Foley replace V1's generic repeating cue pattern. Footstep events come from the motion timeline; plucks, the handoff, price changes, harvest and delivery have specific cues.
- Large constant title/counter plates are removed. Bread prices are physical shop signs. English dialogue captions remain in the lower safe zone.

## Deliverables

- `final/WHAT_IF_MONEY_GREW_ON_TREES_V2.mp4`: native full-quality H.264/AAC master.
- `final/WHAT_IF_MONEY_GREW_ON_TREES_V2_DOWNLOAD.mp4`: smaller full-resolution download copy.
- Repository delivery target: `downloads/WHAT_IF_MONEY_GREW_ON_TREES_V2.mp4` on the V2 branch. V1's filename is preserved.
- `test/V2_MOTION_AUDIO_TEST_8s.mp4`: the rendered eight-second prototype validated before full rendering.
- `blender/V2_CITY.blend`: full editable geometry and baked animation at every output frame. It needs no auto-run handler or external textures.
- `scripts/`: complete build, narration, mixing, rendering, editing and verification source.
- `audio/`: neural speech phrases, narration, score, Foley, final mix and a V1-then-V2 same-question voice comparison.
- `final/subtitles.srt`, `final/subtitles.ass`, `final/narration.txt`: speech-derived captions and narration.
- `reports/`: contact sheets, exact audio event times, model provenance, motion metrics, decode tests, loudness and image checks. Read `QUALITY_CONTROL.md` for completed checks and limits.

## Tools and provenance

Existing tools reused: Blender 4.3.2, FFmpeg/FFprobe 7.1.5, Python, NumPy, SciPy and Pillow. No Kokoro/Piper installation or voice models existed during inventory. Only the missing Kokoro engine and dependencies were installed into this project's `.venv`; existing installations were not replaced.

Kokoro ONNX is MIT licensed; its maintainer documents the Kokoro model as Apache-2.0. The two downloaded files come from the maintainer's documented `model-files-v1.1` GitHub release. Their SHA-256 hashes were checked against the release's published `digest` fields before use. Details and source URLs are in `reports/tts_model_provenance.json`. Copies of the maintainer's license and README are retained in the local model folder. No paid services or untrusted model mirrors are used. All score and Foley are synthesized specifically for V2; no sampled commercial music or recordings are included.

## Run locally in the selected repository

Work from `/workspace/WHAT-IF-TEST`, inside the existing checkout. Cloud tasks already run in isolation; do not create a worktree or access unrelated projects. Keep the original `WHAT_IF_MONEY_GREW_ON_TREES/` and V1 download unchanged.

For existing prepared tools/models, no installation is needed. To recreate only the missing V2 voice environment:

```sh
python -m venv V2/.venv
V2/.venv/bin/python -m pip install -r V2/tts-requirements.lock.txt
python V2/scripts/prepare_tts.py
```

The voice-model fetcher retains TLS verification and checks pinned SHA-256 hashes. The large weights and toolchain are excluded from Git and delivery archives; generated narration WAVs are retained.

To rebuild from the original local V1 Blender asset (preserve manual edits to V2 first):

```sh
blender -b WHAT_IF_MONEY_GREW_ON_TREES/blender/MONEY_CITY.blend -t 2 --python-exit-code 1 --python V2/scripts/build.py -- --test
V2/.venv/bin/python V2/scripts/tts.py
python V2/scripts/audio.py --test
python V2/scripts/run_render.py --test
```

Run `scan_joints.py` on the test Blender file before rendering; the evaluated segment endpoints must stay connected on all frames. Inspect the encoded test contact sheet and audio. The checked test is retained separately. Then:

```sh
blender -b WHAT_IF_MONEY_GREW_ON_TREES/blender/MONEY_CITY.blend -t 2 --python-exit-code 1 --python V2/scripts/build.py
python V2/scripts/audio.py
python V2/scripts/run_render.py
```

Run `scan_joints.py -- --all` on the full Blender file before starting the full render. The full motion metrics must exist before the full mix is generated, so footstep Foley uses the final timeline. Rendering uses four one-thread CPU workers within the four-CPU quota, native resolution and FXAA. Every V2 frame is rendered independently; no V1 image sequence is reused. Redundant constant animation keys and background-object overhead are removed without reducing the output resolution.

A scene SHA marker prevents mixing cached frames from different Blender versions. After changing geometry/animation, archive/remove only this project's `renders/frame_*.png` and `renders/source_sha256.txt` before rendering a new version. Do not alter V1 frames. The editable delivery Blender file can also render directly without rebuilding V1.

## Acceptance limits

There is no audio-listening/perception tool in this session. Waveform, subtitle timing, clipping, sample peak, true peak, integrated loudness and synchronization checks are performed, but a human pronunciation/prosody and first/middle/end listening review remains unverified. The A/B narration file and test clip are supplied for that review. This is explicitly not claimed as a passed listening test.

Character motion uses stylized analytic IK, not a full biomechanical solver. Money uses lightweight procedural motion, not cloth simulation. Workbench studio shadows and perspective preserve the existing low-poly identity on CPU; there is no path-traced depth-of-field rendering. These limits are documented in the QC report rather than hidden behind a success claim.
