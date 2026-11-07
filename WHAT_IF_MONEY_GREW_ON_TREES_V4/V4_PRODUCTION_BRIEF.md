# CODEX — WHAT-IF-TEST V4
## COMPLETE CINEMATIC CONTINUITY, ANIMATION & PHYSICS REPAIR
### PRESERVE ALL APPROVED ASSETS, STORY AND AUDIO

You are the animation director, technical director, Blender engineer, cinematographer, continuity supervisor and quality-control engineer responsible for repairing the existing WHAT-IF-TEST V3.

Repository:
https://github.com/BRTAL77709/WHAT-IF-TEST

Input: The actual completed V3 video and its source files.

Output: `WHAT_IF_MONEY_GREW_ON_TREES_V4.mp4`

Target: 1080×1920, 30 FPS, approximately 78 seconds.

**THIS IS AN EXECUTION TASK, NOT A PLANNING TASK.**

## 1. ABSOLUTE PRESERVATION RULE

Do not change:

- Buildings, roads, sidewalks or environment geometry
- Character models, proportions, colors or clothing
- Trees, shops, vehicles or existing props
- Low-poly 3D art direction
- Story, narration script or spoken words
- Existing voice identity and recordings
- Music, sound effects or audio mix
- Intended economic explanation
- Approved character identities and scene locations

Do not generate a new movie from scratch.

Do not import anything from NOIRFRAME.

Do not replace approved assets with AI-generated images.

Repair the existing film and preserve its identity.

## 2. CRITICAL FINDING — VERIFY V3 TIMELINE FIRST

A preliminary visual inspection of the supplied V3 MP4 shows possible severe narrative-order problems.

Examples requiring investigation:

- The final YES / NO question appears around 18 seconds.
- Shop and bread scenes appear at several widely separated timestamps.
- The price-sign and market sequences may be assembled in the wrong order.
- The visual progression may not consistently match the existing narration.

These are preliminary observations, not proof of the underlying cause.

Inspect the actual V3 video, scene scripts, frame sequences, render manifests, subtitle timing and audio waveform.

Determine whether the problem is caused by:

1. Incorrect scene ordering.
2. Incorrect render-segment mapping.
3. Reused or stale cached frames.
4. Scene scripts rendering to the wrong output files.
5. Incorrect timestamp calculations.
6. Incorrect FFmpeg concatenation.
7. Incorrect subtitle or audio synchronization.
8. Camera selection errors.
9. Source timeline defects.

Fix the verified root cause.

**Do not rewrite the story to match broken scene ordering. Repair the visual sequence to match the original story and narration.**

## 3. BUILD A FRAME-ACCURATE MASTER TIMELINE

At 30 FPS, a 78-second film contains 2,340 frames.

Build a definitive timeline mapping:

- Frame number
- Timestamp
- Original narration segment
- Intended visual action
- Scene ID
- Camera ID
- Character IDs
- Relevant props
- Existing audio event
- Subtitle segment
- Render output path

Use actual source narration and subtitle timestamps.

Do not invent dialogue or arbitrary timing.

Establish a single source of truth for scene ordering.

Every shot must correspond to the correct part of the existing narration.

The opening question belongs in the opening.

The ending question belongs at the conclusion.

Price inflation visuals must occur when inflation is discussed.

Real wealth visuals must occur when production, goods and services are discussed.

Do not place ending graphics in the middle of the film.

## 4. REPAIR ALL CHARACTER MOTION

Every moving character must physically travel through world space.

Repair:

- Root motion
- Walking
- Running
- Starting and stopping
- Foot planting
- Body weight transfer
- Pelvis rotation
- Torso rotation
- Head turning
- Arm movement
- Hand reaching
- Object gripping
- Carrying money
- Releasing objects
- Emotional reactions

No running in place.

No foot sliding.

No floating characters.

No sudden teleportation.

No frozen bodies with moving arms.

No hands passing through cash stacks or counters.

Use IK/FK constraints and procedural animation where supported by the existing rigs.

Preserve every character's visual appearance.

## 5. REPAIR ALL OBJECT INTERACTIONS

For each visible interaction, enforce:

APPROACH → CONTACT → GRIP → MANIPULATION → RELEASE → RECOVERY

Money must not teleport from trees into hands.

Cash stacks must remain attached to carrying hands.

Bread must remain correctly positioned on shelves, counters or in hands.

Characters must contact actual surfaces.

Objects must not penetrate solid geometry.

Use world-space constraints and continuous trajectories.

Repair the underlying Blender source, not only the rendered appearance.

## 6. REPAIR CAMERA BEHAVIOR

Audit every camera throughout the film.

Correct:

- Camera clipping
- Cameras passing through buildings
- Incorrect tracking
- Sudden camera teleportation
- Unmotivated camera rotation
- Subjects leaving the frame unintentionally
- Inconsistent world positions
- Abrupt changes in perspective
- Broken transitions
- Camera movement that hides defective animation

Preserve approved shot composition when correct.

Use motivated cinematic movement rather than adding random shake.

Keep characters, money and price signs readable within the vertical frame.

## 7. SCENE-BY-SCENE MOTION INSPECTION

Inspect all existing scenes, including:

### Money tree discovery

Check bill growth, character reaction, reaching, contact, detachment and collection.

### Money harvesting

Check walking paths, hand contacts, cash movement and believable character reactions.

### City money rush

Check actual world-space travel, crowd spacing and prop interactions.

### Shop scenes

Check customer and shopkeeper positioning, counter contact and bread placement.

### Inflation scenes

Preserve the original price values and narration timing. Repair price-sign placement, character reactions and continuity.

### Real wealth scenes

Repair the actual movements of workers, farmers, vehicles and existing objects without redesigning their environments.

### Ending

Return the original ending question to its correct narrative position. Preserve the exact existing words and graphic style.

Do not introduce new story beats.

## 8. AUDIO MUST REMAIN UNCHANGED

Extract and preserve the original V3 audio.

Do not regenerate the voice.

Do not rewrite narration.

Do not replace music.

Do not replace sound effects.

Do not change the approved sound mix.

Adjust the visual timeline to match the existing audio.

Preserve synchronization.

Prefer copying the original audio stream into the final MP4.

Verify that the soundtrack has not been accidentally altered.

## 9. FRAME-BY-FRAME AND PIXEL-LEVEL QA

Inspect the full 2,340-frame timeline.

Use automated checks for:

- Missing frames
- Duplicated frames
- Frozen motion
- Black frames
- Sudden image discontinuities
- Camera jumps
- Object popping
- Clipping
- Shadow flicker
- Geometry intersections
- Unexpected scene changes
- Incorrect text timing

For critical actions, inspect consecutive frames and actual continuous motion.

Track character root positions, foot contacts, hand-object distances, camera trajectories and prop positions.

Distinguish intentional static moments from animation failures.

Do not claim pixel-perfect results solely because the MP4 decodes successfully.

## 10. PROTECT WORK AGAINST CODEX QUOTA LOSS

This is mandatory.

The previous production workflow encountered interrupted execution and temporary-storage problems.

Never depend exclusively on `/tmp`.

Before rendering:

1. Save source repairs to a persistent project directory.
2. Commit code, scripts, configuration and small reports to GitHub.
3. Create a render manifest with every scene and frame range.
4. Record which frames are valid and which require replacement.
5. Save resumable checkpoints.
6. Back up render outputs to available persistent storage.

During rendering:

- Save progress after each completed scene or render batch.
- Preserve valid frames.
- Avoid rerendering completed verified work.
- Commit source changes regularly.
- Keep a precise next-step instruction in a recovery file.
- Verify backups actually exist.

If GitHub rejects large render files, use an available authorized persistent artifact destination.

Do not claim files are backed up until verified.

If the quota expires or the environment disconnects, the next Codex session must be able to resume without recreating completed work.

## 11. AUTOMATED REPAIR LOOP

Execute:

INSPECT → IDENTIFY DEFECT → FIX SOURCE → RENDER TEST → VERIFY MOTION → ACCEPT OR REPAIR AGAIN

Apply this loop to every scene.

Do not render the complete film before validating the corrected timeline and representative physical interactions.

After validation, render the complete V4 using resumable batches.

## 12. FINAL DELIVERY

Deliver:

- `WHAT_IF_MONEY_GREW_ON_TREES_V4.mp4`
- Updated Blender source
- Updated animation scripts
- Master frame-accurate timeline
- Render manifest
- Scene-by-scene quality-control report
- Before/after motion comparison
- Preserved audio verification
- Recovery checkpoint documentation

Verify:

- Full 78-second playback
- 1080×1920
- 30 FPS
- H.264 video
- Original audio preserved
- Correct scene order
- Correct subtitle timing
- No missing frames
- No unintended frozen shots
- No critical camera clipping
- No obvious broken object contacts
- No unresolved critical animation failures

Report any remaining limitations rather than claiming perfection.

## FINAL COMMAND

START EXECUTION NOW.

DO NOT REBUILD THE WORLD.

DO NOT REDESIGN BUILDINGS.

DO NOT CHANGE CHARACTERS.

DO NOT REWRITE THE STORY.

DO NOT REPLACE THE VOICE.

DO NOT REPLACE MUSIC OR SOUND EFFECTS.

DO NOT RESTART FROM V1.

USE THE EXISTING V3 SOURCE.

FIX THE ACTUAL MOTION.

FIX THE ACTUAL TIMELINE.

FIX THE ACTUAL CAMERA DEFECTS.

FIX THE ACTUAL OBJECT INTERACTIONS.

VERIFY EVERY SCENE.

SAVE PERSISTENT CHECKPOINTS.

RENDER AND VERIFY THE COMPLETE V4.

**THE GOAL IS THE SAME FILM, EXECUTED CORRECTLY — NOT A DIFFERENT FILM.**