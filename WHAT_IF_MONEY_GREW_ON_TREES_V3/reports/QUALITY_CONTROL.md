# V3 recovery and quality-control report

TECHNICAL PASS for the checks below. ARTISTIC REVIEW REQUIRED. USER APPROVED: no.

## Recovery checkpoint

- Restored execution contained all 2,340 native frames, the completed 78-second master and the corrected construction-camera range. No completed frame was rerendered during recovery.
- Every PNG was decoded at 1080×1920 and hashed. The lossless RGB archive was decoded and compared against every original frame pixel hash: 2,340 exact matches. Opaque alpha restores to 255; PNG compression bytes may differ.
- Sources, Blender file, reports, checkpoint manifests, the lossless frame archive and unchanged native master are backed up on the separate `what-if-v3-motion-repair` GitHub branch. Every uploaded recovery object was downloaded and SHA-256 verified.
- QC had stopped at scene 1 because stream-copy `-t 8` included two subsequent B-frame packets. Scenes 1–9 were repaired using exact video packet counts and remuxed original AAC. Scene 10 was already valid and retained. The master and render PNGs remained unchanged.

## Final media

- Master: `WHAT_IF_MONEY_GREW_ON_TREES_V3.mp4` — 63,804,547 bytes; 78 seconds; 1080×1920; 30 FPS; 2,340 frames; H.264/yuv420p; faststart.
- All ten individual scene exports have exact expected video frame counts (240 each, last scene 180) and decode fully.
- Original V2 AAC stream is copied exactly, with identical encoded audio-packet SHA-256. Voice, music, Foley, levels and timeline were not regenerated.
- SRT, ASS, narration source and the protected V1/V2 files retain their recorded SHA-256 hashes.
- Backed-up pixel statistics cover every decoded master frame. They were reused after recovery because the master hash is unchanged; full-file decode/audio checks and repaired-scene checks were completed on the recovered files.

## Measured source-level checks

- Maximum evaluated joint gap: 0.000053408 m.
- Maximum limb-length deviation from the existing rig lengths: 0.000003494 m.
- Maximum planted-foot drift per frame: 0.000000238 m.
- Maximum held-banknote corner-to-hand distance: 0.000000000 m.
- Maximum sampled loaf/crop/sign contact distance: 0.000000119 m.
- Minimum actor root separation: 0.682386 m.
- Audible footstep timing: all 51 retained; largest landing alignment difference 0.000000000 seconds.
- Static-surface camera proximity flags (<0.08m): zero in the evaluated frames. This is a proximity screen, not a full swept-volume collision proof.

## Ten scenes

| Scene | Frames | Duration | Bytes | Max stance drift (m/frame) | Status |
|---|---:|---:|---:|---:|---|
| 01 | 240 | 8.000s | 6,812,952 | 0.000000179 | TECHNICAL PASS / ARTISTIC REVIEW REQUIRED |
| 02 | 240 | 8.000s | 6,892,327 | 0.000000238 | TECHNICAL PASS / ARTISTIC REVIEW REQUIRED |
| 03 | 240 | 8.000s | 9,094,475 | 0.000000179 | TECHNICAL PASS / ARTISTIC REVIEW REQUIRED |
| 04 | 240 | 8.000s | 7,310,227 | 0.000000179 | TECHNICAL PASS / ARTISTIC REVIEW REQUIRED |
| 05 | 240 | 8.000s | 5,708,592 | 0.000000179 | TECHNICAL PASS / ARTISTIC REVIEW REQUIRED |
| 06 | 240 | 8.000s | 5,447,234 | 0.000000179 | TECHNICAL PASS / ARTISTIC REVIEW REQUIRED |
| 07 | 240 | 8.000s | 4,367,333 | 0.000000238 | TECHNICAL PASS / ARTISTIC REVIEW REQUIRED |
| 08 | 240 | 8.000s | 6,355,985 | 0.000000179 | TECHNICAL PASS / ARTISTIC REVIEW REQUIRED |
| 09 | 240 | 8.000s | 4,496,278 | 0.000000238 | TECHNICAL PASS / ARTISTIC REVIEW REQUIRED |
| 10 | 180 | 6.000s | 7,349,201 | 0.000000238 | TECHNICAL PASS / ARTISTIC REVIEW REQUIRED |

Per-scene source paths, render commands, audio status, contact/clearance findings and remaining limitations are recorded in `scene_reports.json`.

## Confirmed motion repairs

| Object | V2 worst displacement in one frame | V3 worst displacement in one frame |
|---|---:|---:|
| V2 Contact hand.004 | 1.193524 m | 0.060296 m |
| V2 Contact hand.005 | 1.095974 m | 0.058952 m |
| V2 Hand-picked crop | 0.780891 m | 0.042989 m |
| V2 Bread inventory | 2.194359 m | 0.049792 m |
| V2 Planted shoe | 0.435196 m | 0.208484 m |

Continuous comparison clips and consecutive-frame strips are in `comparisons/`. Motion analysis uses every evaluated frame and decoded-frame temporal statistics, rather than metadata/contact sheets alone.

## Limitations and unmet acceptance

- No claim of exhaustive every-pixel artistic acceptance or full swept mesh collision proof.
- Human continuous-motion and soundtrack listening acceptance remain unverified. No user approval is claimed.
- Existing Workbench FXAA, lighting and materials retained; no path tracing or added motion blur.
- Shelf inventory props are kept physically present instead of disappearing by scale changes; the existing narration, price sequence and 78-second story are preserved.
- OpenCV was not available in the restored toolchain. No installation was added. NumPy pixel differences, exact duplicates/black-frame detection and Blender transform/contact analysis were used; optical-flow measurements are unavailable.
- Nearest-surface tests and root separation do not certify every hand/limb/self/prop swept-mesh collision. Camera visibility was inspected in previews; exhaustive per-pixel occlusion certification is not claimed.
- Inventory objects remain physically present instead of disappearing by scale changes. This is a documented visual-state repair, not an exact reproduction of every V2 inventory visibility state.

## Integrity

Master SHA-256: `1f758e17b4c5bea1a53646d42744fba2b8d3e621aeaa069ce6188d963d8f3e44`

Encoded AAC packet hash: `SHA256=d36ffca59b9b5446ddf6fbcc880937f8ccac90a141c495eb170988c2f19cd4dd`

## GitHub delivery constraint

The Git Blobs API rejected the native 63,804,547-byte single file with HTTP 422: "Sorry, your input was too large to process." It was not repeatedly retried. The original master is unchanged and durably stored in four byte-verified parts. A 19,820,517-byte download copy was encoded from the native master; it retains all 2,340 frames at 1080×1920/30fps and the exact original AAC stream. Its full-file decode passed and its public GitHub download matches SHA-256 `a61b14bc672683a04c075a409a770c61cb3b3ef575e79709a66a7d6a779204bb`. See `download_copy_validation.json` and `github_delivery.json`.
