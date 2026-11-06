# WHAT IF MONEY GREW ON TREES?

Original 78-second vertical miniature-city film. All geometry, animation, currency, music and sound effects are created procedurally for this project. No unrelated project assets are used.

## Deliverables

- `final/WHAT_IF_MONEY_GREW_ON_TREES_FINAL_1080x1920.mp4` — H.264, 1080 × 1920, 30 fps, stereo AAC, burned English captions and a selectable English subtitle stream.
- `blender/MONEY_CITY.blend` — editable city, articulated characters, procedural animation baked into keyframes, and ten camera sequences in one continuous 2,340-frame timeline.
- `scripts/` — complete generation, refinement, render, audio, typography, assembly and validation source.
- `audio/` — individual speech phrases, full narration, original music, original effects, and stereo mix.
- `scenes/scene_01.mp4` through `scene_10.mp4` — full-resolution scene renders with chapter graphics; final narration, counters and captions are applied during mastering.
- `renders/frame_0001.png` through `frame_2340.png` — native-resolution source frames retained in the working repository. These large frame sequences are omitted from the delivery ZIP; scene movie renders are included.
- `final/narration.txt`, `final/subtitles.srt`, `final/subtitles_and_counters.ass` — narration and actual speech-segment timings.
- `reports/` — inventory, generation/render logs, audio timings, encoded-video contact sheet and machine-readable QC.

## Existing tools, no new installation

The selected Codex environment already supplies Blender 4.3.2, Python 3.12 with NumPy/SciPy/Pillow, FFmpeg/FFprobe 7.1.5, the Flite speech filter and its CMU `slt` voice, and DejaVu Sans fonts. The inventory in `reports/environment_inventory.json` records the accessible binaries and Python packages. Nothing needs reinstalling.

The two available cloud skills were discovered and reused. No additional executor skills were available. No environment draft was updated or published during video production.

## Open and edit

Open `blender/MONEY_CITY.blend` with the existing Blender. It has ordinary, editable geometry and keyframes; no auto-run script, external texture download or plugin is required to play its animation. The camera is orthographic and uses ten deliberately blocked dolly/orbit-style views. All shots retain the same road network, building positions and central tree. Workbench studio lighting, shadows, cavity shading and FXAA support CPU-only rendering at native resolution.

No separate worktree is needed: every cloud task already has an isolated environment. Work inside the existing selected repository. Never read, import or modify unrelated projects.

## Reproduce from source

Run from `/workspace/WHAT-IF-TEST`. The following rebuilds the project Blender file; preserve any manual edits first. The refinements are ordered steps on the freshly generated file, not independent idempotent commands.

```sh
blender -b -t 4 --python WHAT_IF_MONEY_GREW_ON_TREES/scripts/build_world.py
blender -b WHAT_IF_MONEY_GREW_ON_TREES/blender/MONEY_CITY.blend -t 4 --python WHAT_IF_MONEY_GREW_ON_TREES/scripts/refine_world.py
blender -b WHAT_IF_MONEY_GREW_ON_TREES/blender/MONEY_CITY.blend -t 4 --python WHAT_IF_MONEY_GREW_ON_TREES/scripts/finish_world.py
blender -b WHAT_IF_MONEY_GREW_ON_TREES/blender/MONEY_CITY.blend -t 4 --python WHAT_IF_MONEY_GREW_ON_TREES/scripts/optimize_world.py
python WHAT_IF_MONEY_GREW_ON_TREES/scripts/make_audio.py
python WHAT_IF_MONEY_GREW_ON_TREES/scripts/graphics.py
python WHAT_IF_MONEY_GREW_ON_TREES/scripts/produce.py
```

`produce.py` uses four Blender workers with one software-render thread each to respect the current four-CPU quota. It resumes existing image outputs only with the same Blender-file SHA-256. After changing the Blender file, archive/remove this project's generated `renders/frame_*.png` and `renders/source_hash.txt` before starting a new render. Do not mix frames from different versions. Shader cache files stay inside this project.

To reassemble the existing frame sequence without rerendering:

```sh
python WHAT_IF_MONEY_GREW_ON_TREES/scripts/assemble.py
python WHAT_IF_MONEY_GREW_ON_TREES/scripts/validate.py
```

The first command renders chapter title plates into ten scene movies, uses short fade transitions, concatenates scenes, burns counters and English captions, includes selectable subtitles, normalizes the stereo mix, and writes the final MP4. Validation checks actual full-file decoding, frame count, native size, frame rate, duration, codecs, subtitle bounds, unique source images and unclipped source audio. It extracts its contact sheet from the encoded MP4.

## Story and scope

The cash-harvest counter is fictional. The sequence `$2 → $20 → $200 → $2,000` is explicitly marked as an illustrative accelerated scenario, not a prediction. The story explains that unlimited currency without corresponding real production can undermine purchasing power.

The supplied external reference was blocked by the network policy (403 CONNECT denial), so it was not viewed. The written brief guided all original production choices. Voice synthesis is local Flite `slt`; money physics and human motion are stylized, deterministic procedural animation rather than cloth/foot-contact simulations. The film uses studio rendering rather than path tracing. See `reports/quality_control.json` for validated technical evidence and limitations.

## Rights and provenance

All city geometry, fictional currency patterns, graphics, animation, composition and effects are original to this production. The score and effects are synthesized by `make_audio.py`; there are no sampled copyrighted music tracks. Speech is generated with the preinstalled open-source Flite engine and its included CMU voice. DejaVu Sans is used for graphics and captions under its existing free font license. No paid APIs or subscriptions are used.
