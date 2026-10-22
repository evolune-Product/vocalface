# GPU day plan: from "does it run live?" to a demo video

Written Oct 22 2026. Prices are from the providers' own pages that day (excluding 18% GST, about Rs 90 per US dollar) and change.
Everything about speed below is the FlashHead authors' claim until the benchmark in step 1 has been run by us.

## Why two rentals instead of one blind day
Building the live path (a FlashHead face server, chunked audio hand-off, a session recorder) takes several days of work on the Mac and costs nothing. A rented GPU cannot speed that up, and an idle GPU bills by the hour. So:

| Step | GPU time | Rs (RunPod, about Rs 90 per dollar) | Decides |
|---|---|---|---|
| 1. Benchmark (RTX 4090) | 3-4 h | about 320-360 (budget 1,000 with retries) | Is Lite real time? How many streams per GPU? Is it worth building the live path? |
| 2. Build the live path (Mac only) | none | 0 | |
| 3. Live day (L40S or 4090) | 12-24 h | about 1,200-2,400 | Full conversation, latency numbers, the demo recording |

Never leave it running overnight by accident: one L40S on 24x7 is about Rs 72,000 a month.

## Which provider and card (provider pages read Oct 22 2026; about Rs 90 per US dollar; no GST)
| Provider | Cards and price per hour | Start-up friction |
|---|---|---|
| **RunPod, Secure Cloud** (use this first) | RTX 4090 $0.89 (about Rs 80), L40S $1.09 (Rs 98), RTX 5090 $1.19, A100 80GB $1.79, H100 $2.89-3.99 | Prepaid credits from about $10 by card or crypto, billed per second, no KYC mentioned, pod stops itself when the balance hits zero, direct SSH as root. Regions: India not listed, so latency from India is higher |
| E2E Networks (India) | L40S Rs 102, A100 Rs 179-189, H100 Rs 379 | Organisations need PAN, GSTIN, billing address and a payment verification; activation time not stated; pays by UPI or card; startup credits up to Rs 5 lakh. Do the signup in parallel for credits and for India-hosted pilots |
| JarvisLabs (servers in India) | A100 40GB $0.89, L4 $0.44, H100 $3.49 (their pricing page; L40S and 4090 not listed there) | Prepaid dollar wallet by card only (no UPI), billed per minute, instances are containers |

Decision: RunPod for both the benchmark and the live day. The RTX 4090 is the card the authors benchmarked, so step 1 tests their claim directly; the L40S (same chip family, 48 GB) is the live-day candidate if the 4090 passes. E2E and JarvisLabs matter later, for credits and India-hosted pilots, not for a one-day recording. L4 is probably too slow. H100 is for the higher-quality Pro model or training.

Latency note: a pod outside India adds one network round trip (roughly 0.2-0.3 s) to anything measured from your Mac. The demo reports the server-side time separately and says where the GPU was.

## How Claude gets in without any secret (the hand-off)
Claude can open SSH connections from the Mac (checked Oct 22: outbound port 22 and odd ports such as 17445 are open). A throwaway key pair already exists at `~/.ssh/vocalface_gpu`; the private half never leaves the Mac.
Owner, about 15 minutes:
1. Sign up at runpod.io and add $10-15 of credit. That balance is the hard spending cap: when it reaches zero, running pods stop.
2. Settings, SSH Public Keys: paste the single line from `~/.ssh/vocalface_gpu.pub` (it starts `ssh-ed25519`).
3. Deploy a pod: Secure Cloud, RTX 4090, template "RunPod PyTorch 2.x", container disk 80 GB, a CUDA 12.4 or newer filter if offered, public IP and SSH enabled.
4. Connect tab, "SSH over exposed TCP": copy the line `ssh root@IP -p PORT ...` and paste it to Claude. It contains no secret.
5. When Claude says "done": Terminate the pod (not just Stop; stopped pods still bill for storage).
Never paste: passwords, API keys, or any key file except that one `.pub` line. Claude copies the two scripts it needs over SSH (no GitHub login needed), uses only the public example face and speech for the benchmark, and copies the results back.
Safety net: Claude will try to set a self-stop timer on the pod; if the provider does not allow it, deleting the pod is on the owner.

## Step 1: the benchmark (what the owner does, what Claude does)
Owner: the five steps in the hand-off above. Claude then runs the setup (about 1 hour including the 14 GB download), reading `flashhead_bench_lite.json`.

Go / no-go (Lite, one stream, on the RTX 4090; the same thresholds apply to the L40S):
| Result | Meaning | Next |
|---|---|---|
| p95 chunk time under 0.75 s (margin 1.25x or more) and 2+ streams sustained | real time with headroom | build the live path |
| p95 under 0.96 s (margin 1.0-1.25x), 1 stream | borderline | build it for one stream; try the 4090 and an H100 for comparison |
| p95 over 0.96 s | too slow on this card | stop; try an H100 or a different approach before spending more |

Chunk length: Lite makes 24 frames (0.96 s) per chunk, Pro 28 frames (1.12 s). The benchmark prints the exact figure.

## Step 3: the live day (after the live path exists)
Hour by hour (about 12 h of work, book 24 h so a hiccup does not force a second rental):
1. 0-1 h: setup, benchmark again, start the face server, run one scripted conversation with a text-to-speech "customer" to check the whole chain.
2. 1-3 h: the owner talks to it live through an SSH tunnel (the browser sees localhost). Measure end-of-speech to first lips, interruptions, 3 concurrent conversations.
3. 3-6 h: fix what broke. Tune chunk size, idle loop, crossfades.
4. 6-10 h: record the demo (below). Run a 30-minute soak test.
5. Save every log and recording, then terminate the instance.

## The demo video: what is honest to show
- A real, unedited live conversation (60-90 s): the owner speaks, the face answers. Keep the real pauses.
- A latency chip computed from real timestamps, and one caption: "Live session on one rented NVIDIA L40S in India; STT, LLM, TTS and face all on that GPU" (state the actual GPU and region).
- The photo or video of the person must be the owner's own face (consent) or a clearly fictional person.
- Say what it is not: one stream, one scripted scenario, quality below the best hosted platforms. The site and the pitch page already say so.
- Keep the 3 concurrent-conversation result as a second short clip only if it held.

Where it goes: a demo section on the landing page (self-hosted mp4 plus poster, VideoObject structured data), the same file on YouTube for search, and the /pitch page. Update /pitch "What exists today" with the measured numbers, and `docs/UNIT_ECONOMICS.md` (replace the assumed figures).

## Before approaching funders or customers
- Put the measured numbers on /pitch and remove the line "real-time face quality has not been measured".
- Licences: counsel review of the FlashHead weights, the bundled VAE and wav2vec2; replace Wav2Lip and LivePortrait (`docs/LICENSES.md`).
- Company structure: ask counsel whether Evolune EdgeTech LLP can issue the equity or SAFE-style instruments investors and accelerators usually require; many expect a Pvt Ltd or a US C-corp. Settle that before investor conversations.
- A design-partner conversation with a real prospect is worth more than the video. Use the video to get those calls.
