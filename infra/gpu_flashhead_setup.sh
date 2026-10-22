#!/usr/bin/env bash
# One-command FlashHead setup + real-time benchmark on a rented NVIDIA box (Ubuntu 22.04/24.04, CUDA 12.x driver, >=24 GB VRAM:
# L40S, RTX 4090, A100, H100). Run from the repo root:
#   bash infra/gpu_flashhead_setup.sh [path/to/face.png] [path/to/speech.wav]
# NOT TESTED ON CUDA: written on an Apple-silicon Mac. Expect small fixes; each step prints what it is doing so a failure is easy to find.
# Billing: the GPU bills from the moment the instance starts. Read docs/GPU_DAY.md first and delete the instance when done.
set -euo pipefail
FACE="${1:-}"; WAV="${2:-}"
FH=workers/SoulX-FlashHead
STEP() { echo; echo "==> $*"; }
command -v nvidia-smi >/dev/null || { echo "no NVIDIA GPU/driver found"; exit 1; }
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"

STEP "system packages"
$SUDO apt-get update -y >/dev/null && $SUDO apt-get install -y ffmpeg git libgl1 python3-venv python3-pip >/dev/null || echo "apt step had problems; continuing"

STEP "FlashHead code"
[ -d "$FH" ] || git clone --depth 1 https://github.com/Soul-AILab/SoulX-FlashHead "$FH"

STEP "python environment"
PYBIN="$(command -v python3.10 || command -v python3.11 || command -v python3)"
echo "using $PYBIN ($($PYBIN --version))"
$PYBIN -m venv workers/.venv-flash-gpu
PY=workers/.venv-flash-gpu/bin/python
$PY -m pip install -q -U pip
$PY -m pip install -q torch==2.7.1 torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cu128
$PY -m pip install -q -r "$FH/requirements.txt"
# Faster attention if a prebuilt wheel exists. Capped at 10 minutes so a source build cannot burn GPU money; falls back to PyTorch SDPA.
timeout 600 $PY -m pip install -q flash_attn==2.8.0.post2 --no-build-isolation || echo "flash_attn not installed: PyTorch attention will be used (slower)"
timeout 300 $PY -m pip install -q sageattention || echo "sageattention not installed (optional)"
$PY -m pip install -q -U huggingface_hub

STEP "model weights (about 14 GB)"
mkdir -p "$FH/models"
$PY - <<'PYEOF'
import os
from huggingface_hub import snapshot_download
fh = "workers/SoulX-FlashHead/models"
snapshot_download("Soul-AILab/SoulX-FlashHead-1_3B", local_dir=f"{fh}/SoulX-FlashHead-1_3B")
snapshot_download("facebook/wav2vec2-base-960h", local_dir=f"{fh}/wav2vec2-base-960h")
print("weights downloaded")
PYEOF

FACE="${FACE:-$FH/examples/girl.png}"; WAV="${WAV:-$FH/examples/podcast_sichuan_16k.wav}"
nvidia-smi > gpu_info.txt

STEP "1/3 real-time benchmark (Lite): per-chunk time, first-chunk latency, concurrent streams, peak memory"
$PY workers/flashhead_bench.py --fh-dir "$FH" --image "$FACE" --audio "$WAV" --model_type lite --out flashhead_bench_lite.json

STEP "2/3 one rendered clip to look at (compare with the Mac render)"
( cd "$FH" && "$OLDPWD/$PY" generate_video.py --ckpt_dir models/SoulX-FlashHead-1_3B --wav2vec_dir models/wav2vec2-base-960h \
    --model_type lite --cond_image "$OLDPWD/$FACE" --audio_path "$OLDPWD/$WAV" --audio_encode_mode stream \
    --save_file "$OLDPWD/flashhead_lite.mp4" ) 2>&1 | tail -3

# The higher-quality Pro model: set RUN_PRO=1. The README needs two RTX 5090 for real time, so expect "TOO SLOW" on one card.
if [ "${RUN_PRO:-0}" = "1" ]; then
  STEP "3/3 Pro benchmark"
  $PY workers/flashhead_bench.py --fh-dir "$FH" --image "$FACE" --audio "$WAV" --model_type pro --streams 1 --chunks 8 --out flashhead_bench_pro.json
fi

echo
echo "Done. Send back: flashhead_bench_lite.json, gpu_info.txt, flashhead_lite.mp4 (and the pro json if you ran it)."
echo "Real time means: p95 chunk time is below the chunk length (0.96 s for Lite). 'Streams' = conversations one GPU can carry."
echo "REMINDER: stop and DELETE the instance in the provider console now. Idle GPUs keep billing."
