# V4 recovery instructions

Work only in `/workspace/WHAT-IF-TEST/WHAT_IF_MONEY_GREW_ON_TREES_V4` and the WHAT-IF-TEST GitHub repository. Preserve V1/V2/V3. Do not rerun V2/V3 production scripts or regenerate audio.

The source baseline is the verified V3 blend. `reports/protected_V3_files.json` records its protected hashes. `reports/MASTER_TIMELINE.csv` maps all 2,340 frames to the actual existing narration/subtitle/audio events.

The preliminary ending-at-18s issue was not reproduced in the actual V3 master. Decoded/OCR evidence and the original ASS show the ending only at 72.2–77.6s. Do not invent a reorder.

Confirmed source repairs in progress: whole-sole curb/crop-bed contact, 5.5cm shelf bread hover, side grips instead of hand centers inside bread, a continuous seller recovery of the reserved loaf before the hungry-customer close-up, harvester framing, and an actual depleted display-bay insert at 68s. Do not silently claim the entire stocked shop is empty.

Before rendering any corrected frames: source validation must pass, save the edited blend, publish source and manifests to `what-if-v4-continuity-repair`, and verify the source archive backup. The existing V3 render archive remains backed up on the V3 branch.

Rendering must follow `reports/render_manifest.json`. Every render batch uses the final source SHA-256; only missing/invalid corrected frames may render. Reused V3 frames retain their original file hashes. Never mix a changed blend into a completed batch without updating the affected frame set and validation.

After each completed scene/batch, save and verify its checkpoint, archive corrected native frames losslessly and persist the archive on GitHub in API-compatible parts. Update this file or `reports/production_checkpoint.json` with the precise next step.

Final assembly must stream-copy `audio/V3_ORIGINAL_SOUNDTRACK.m4a`, preserve subtitle wording/timing, follow numeric absolute frame order, and export exactly 2,340 frames at 1080×1920/30fps. Never claim complete acceptance based on decoding alone.
