# Renting a GPU for an evening: real-time FlashHead test

Goal: find out, with real numbers, whether SoulX-FlashHead runs in real time on one rented NVIDIA GPU, and what a user-minute costs.
**Untested script:** `infra/gpu_flashhead_setup.sh` was written on a Mac with no CUDA. Expect small fixes.

## Before you rent (costs real money; you decide)
- Pick a provider with hourly billing and an Ubuntu 22.04 + CUDA 12.x image (RunPod, Vast.ai, Lambda). An RTX 4090 (24 GB) is the card the FlashHead README quotes: Lite 96 fps / 3 concurrent real-time streams; Pro 10.8 fps (needs 2x RTX 5090 for real time). Those are the authors' numbers, not ours.
- Expect roughly $0.3-$1/hour for a 4090 (check current prices). One evening of testing is a few dollars.
- Stop the instance when done. Idle GPUs bill.

## Indian GPU options (provider pages, read Oct 22 2026; prices change, GST 18% extra)
E2E Networks (Delhi NCR, Chennai; hourly billing, no minimum): L4 24 GB Rs 49/h, L40S 48 GB Rs 102/h, A100 40/80 GB Rs 179/189, RTX PRO 6000 96 GB Rs 237, H100 Rs 379, H200 Rs 503. No RTX 4090/5090 is listed by E2E, and none of the Indian providers we read rents GeForce cards. Cyfuture lists L40S Rs 61/h (April 2026 page). Yotta and Tata publish no prices.
- First test box: L40S (same chip family as the 4090, so similar speed is expected but not measured; memory bandwidth is lower). L4 is probably too slow. To check the authors' exact 4090 claim, rent a 4090 for an hour on RunPod or Vast.ai (about $0.3-0.75/h, servers outside India).
- Pro (higher quality) needs two RTX 5090 for real time per the README; the nearest E2E card is the RTX PRO 6000. Treat as a later test.
- Credits to ask for before paying: E2E startup programme (Explorer tier: up to $5K free credits for early-stage companies), NVIDIA Inception partner credits and GPU pricing (amounts not published), IndiaAI compute portal (up to 40% subsidy; needs DPIIT recognition and, as the portal reads, revenue or funding thresholds: check eligibility).
- Never leave it running: a single L40S on 24x7 is about Rs 74,000 a month before GST.

## Steps (about 1 hour including the ~14 GB download)
1. SSH in, `git clone https://github.com/evolune-Product/vocalface && cd vocalface`
2. `bash infra/gpu_flashhead_setup.sh` (optionally pass your face PNG and a 16 kHz speech WAV).
3. Read the per-step timings. Real time means a chunk of video is produced faster than it plays (25 fps).
4. `scp` flashhead_lite.mp4 / flashhead_pro.mp4 back and compare with the Mac renders.

## What to write down
GPU model, Lite and Pro seconds per generated second, peak VRAM (`nvidia-smi`), and concurrent streams before slowdown. Put them in `docs/UNIT_ECONOMICS.md` replacing the assumed $0.007-0.022/user-minute.

## Then wire it into the live path (not built yet)
FlashHead's streaming mode (`gradio_app_streaming.py`) yields chunks. VocalFace's live protocol sends `video_segment` frames; a new engine in `workers/engines/` would wrap the streaming pipeline. That is real work (days) and only worth it if step 3 shows real time.

## Licence reminder
README says Apache-2.0 (code+weights). Bundled VAE and wav2vec2 have their own licences; have counsel confirm before selling. See `docs/LICENSES.md`.
