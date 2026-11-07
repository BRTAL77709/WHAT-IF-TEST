# V2 render and quality-control report

Final native master: 45,914,979 bytes.
Download version: 18,751,354 bytes.

- 78-second timeline; 2,340 individually rendered frames, 1080 × 1920, 30 FPS; stereo AAC.
- Full master and compressed-file decoding passed.
- Seven characters have measured world-space root paths; stance-floor and reach measurements are in `full_QC.json`.
- The eight-second motion/audio test was rendered, decoded, visually inspected and technically checked before the full batch.
- The hero banknote grasp was checked on the evaluated Blender scene: zero distance between its grip point and the constrained hand on the sampled held frames.
- Normal-speed local neural Kokoro narration; no forced speech speedup. Captions are based on actual generated speech segments.
- Scene-matched original score and Foley; footsteps, collection, handoff and price changes have recorded animation/event times.
- Integrated loudness: -17.1 LUFS; true peak: -1.5 dBFS; decoded sample peak: 0.843723.
- Sustained frozen detections: ['58.7']; black detections: []. Short intended scene fades are included. The 58.7–61.13s builder shot triggers the global low-motion threshold; decoded-frame comparisons confirm localized movement (builder_motion_audit.json).
- V1 download, source Blender file and audio mix retain their original SHA-256 hashes.

## Unmet / limited criteria

Not performed: this tool session has no audio playback/perception tool. Technical waveform, clipping, loudness and sync checks performed; human listening remains an unmet acceptance criterion.
- Stylized analytic two-segment IK, not a full biomechanical or cloth simulation.
- Workbench studio shadows and perspective cameras on CPU, not path-traced depth of field.

## Visual inspection evidence

Contact sheets are extracted from the encoded MP4s. `BEFORE_AFTER_CONTACT_SHEET.jpg` pairs V1 and V2 views; `FULL_ENCODED_CONTACT_SHEET.jpg` covers the V2 scenes. Review them along with the actual test and final clip. No purely technical test is claimed to certify every subjective animation or sound-quality judgment.

## Integrity

Master SHA-256: `329e114314980aa9a5c0db0ca88db6c84e8d1996da16bc493f0f5d4793fa64ce`

Download SHA-256: `37f04ab73bda65fd33a294f86cb55bd557a52fd8f474f3a29217e23cd460b654`
