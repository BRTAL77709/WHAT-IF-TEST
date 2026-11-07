# WHAT-IF-TEST V2 — Production brief and acceptance criteria

Status: V2 rendered and technically validated; human listening review remains unverified. See V2/reports/QUALITY_CONTROL.md.
Branch: `what-if-v2-production` (keep `main` and the V1 download intact).

## Goal
Upgrade the existing 78-second vertical 1080x1920, 30fps, low-poly 3D film. Preserve its original concept, English economic explanation, established visual identity and source assets. Improve scene-specific storytelling, grounded character motion, cinematography, narration and sound. Use only free/local tools. Do not access or modify NOIRFRAME.

## Confirmed V1 implementation issues to address
- `scripts/make_audio.py` uses FFmpeg's Flite `slt` voice. Replace with a more natural **locally available** English TTS (prefer Kokoro if installed and license-compatible; fallback Piper; retain Flite only as last resort). Do not download untrusted models or require paid API keys.
- Current music and effects are procedurally synthesized, with generic repeating cue patterns. Build scene-matched sound effects, distinct transitions and a controlled cinematic music arc, with audible narration throughout.
- The Blender README describes ten orthographic camera shots around the same city. Vary framing and story action with close-ups, character reaction shots and physical interactions; avoid repetitive aerials and static infographic-like shots.
- The existing audio pipeline has fixed 78-second slots and automatic speech speedup. Preserve intelligibility, natural pauses and accurate subtitle alignment; avoid forced fast narration.

## Story beats and target shots
| Time | Visual action | Audio direction |
|---|---|---|
| 0–8s | Macro of cash emerging from a tree; character notices, reaches and reacts; strong first 2-second hook | Curious question, leaf/cash growth Foley, musical reveal |
| 8–22s | Multiple people harvest money; hands actually grasp cash, walk away and exchange reactions | Cash rustle, footsteps, subtle crowd; excitement |
| 22–38s | Wide city establishing shot then street-level variety; people spend/queue; goods remain limited | Busy market ambiance, tension begins |
| 38–55s | Market counter with bread and visible price tags $2→$20→$200→$2,000 (illustrative); buyer reacts | Price-change ticks, impacts, tense music; clear economic explanation |
| 55–70s | Farm, housing, workers, delivery and limited inventory; contrast nominal cash with real goods | More grounded environments, thoughtful narration |
| 70–78s | Return to cash tree; compelling choice/question; YES / NO on screen | Musical resolution, clear question, gentle CTA |

Timing is a starting guide, not a mandate to truncate sentences. Keep a coherent 78-second cut if possible.

## Animation and camera QA
- Character root translation must visibly move through world space, not merely cycle limbs in place.
- Feet plant and lift plausibly; hands maintain contact with money/props while grabbing and releasing.
- Avoid intersections, clipping, floating objects, teleporting props, abrupt camera cuts and repeated identical city angles.
- Mix close/mid/wide views; motivated dolly, tracking and subtle orbits. Preserve readability in vertical 9:16 safe zones.
- Ensure captions never cover critical action or price information.

## Audio QA
- Listen to and compare V1 and V2 narration. Correct pronunciation, prosody, emphasis and sentence pacing.
- Add sound only where visually motivated. Use legal original or properly licensed assets, documenting provenance.
- Narration centered and intelligible; music ducked beneath speech; no clipping; check true peak and loudness with FFmpeg loudnorm/ebur128.
- Verify synchronization of speech, captions, money rustles, footsteps, market Foley and inflation price cues.
- Export stereo AAC with H.264 video; test first/middle/end sections by listening.

## Implementation instructions for Codex
1. Inspect existing Blender scripts, audio pipeline, narration, subtitles, and original MP4 before modifying.
2. Preserve V1 deliverables and create separate V2 output directories/files; do not overwrite the committed V1 MP4.
3. Inventory local Blender, FFmpeg, TTS voices/models and CPU/GPU resources; choose realistic local settings.
4. Build one polished 5–8 second motion-and-audio test first. Verify the test visually and aurally before full render.
5. Rebuild/reuse existing low-poly assets, animate story-specific interactions, then render all ten sections.
6. Produce a new narration and sound mix; regenerate subtitles from actual speech timings.
7. Export `WHAT_IF_MONEY_GREW_ON_TREES_V2.mp4`, validate full-file decode, 1080×1920, 30fps, audio presence, subtitle synchronization and 78s target.
8. Return before/after contact sheets, sample clip, QC report, file size and download location. Report any unmet criteria explicitly.
9. Never touch NOIRFRAME or unrelated repositories. No paid tools, no new token requests unless a verified authentication error requires one.

## Current progress
- V1 video is confirmed in `main/downloads/WHAT_IF_MONEY_GREW_ON_TREES.mp4`.
- V2 development branch created.
- The eight-second test and full V2 render are complete; neural narration, scene-specific sound and technical QC are generated in V2/.
