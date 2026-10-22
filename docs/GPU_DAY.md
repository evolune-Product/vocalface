# GPU day plan: from "does it run live?" to a demo video

Written Oct 22 2026. Prices are from the providers' own pages that day (excluding 18% GST, about Rs 90 per US dollar) and change.
Everything about speed below is the FlashHead authors' claim until the benchmark in step 1 has been run by us.

## Why two rentals instead of one blind day
Building the live path (a FlashHead face server, chunked audio hand-off, a session recorder) takes several days of work on the Mac and costs nothing. A rented GPU cannot speed that up, and an idle GPU bills by the hour. So:

| Step | GPU time | Rs (L40S, before GST) | Decides |
|---|---|---|---|
| 1. Benchmark | 3-4 h | about 300-400 (budget 1,000 with retries) | Is Lite real time? How many streams per GPU? Is it worth building the live path? |
| 2. Build the live path (Mac only) | none | 0 | |
| 3. Live day | 12-24 h | 1,200-2,500 | Full conversation, latency numbers, the demo recording |

Never leave it running overnight by accident: one L40S on 24x7 is about Rs 74,000 a month.

## Which GPU
- First choice: L40S 48 GB (E2E Networks, Delhi NCR or Chennai, Rs 102/h). Same chip family as the RTX 4090 the authors benchmarked on. Speed is expected to be similar but is not measured.
- To test the authors' exact claim: one hour on an RTX 4090 (RunPod or Vast.ai, about $0.3-0.75/h). Servers are outside India, so do not quote latency numbers from it.
- L4 (Rs 49/h) is probably too slow. H100 (Rs 380/h) is only for the higher-quality Pro model or later training.

## Step 1: the benchmark (what the owner does, what Claude does)
Owner:
1. Create the account (company name, KYC; start early, approval may take time) and check for startup credits (E2E startup programme, NVIDIA Inception partner credits).
2. Launch one Ubuntu GPU instance with an SSH key. To let Claude run it: Claude creates a throwaway key pair on the Mac, the owner pastes only the public key into the provider, and sends the instance IP. Never send passwords or tokens in chat.
3. When Claude says "done", delete the instance in the console.

Claude runs `bash infra/gpu_flashhead_setup.sh` (about 1 hour including the 14 GB download) and reads `flashhead_bench_lite.json`.

Go / no-go (Lite, one stream, on the L40S):
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
5. Stop the instance. Save every log and recording.

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
