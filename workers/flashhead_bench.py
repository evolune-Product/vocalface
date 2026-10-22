#!/usr/bin/env python
"""Real-time benchmark for SoulX-FlashHead: can this GPU generate talking-head video faster than it plays?

It replays FlashHead's own streaming loop (the one in gradio_app_streaming.py) on a speech file and times every chunk:
one chunk = frame_num - motion_frames_num frames generated from a rolling 8 s audio window (Lite: 24 frames = 0.96 s; Pro: 28 frames = 1.12 s at 25 fps).
Real time means one chunk is produced in less time than it lasts.

What it reports (JSON + a printed table):
  * cold start: model load and the warm-up chunks (torch.compile on CUDA can take minutes), which decides how long a new GPU worker needs
  * per chunk: audio embedding, denoise + decode, JPEG encoding (what the live path must also do), median / p95 / worst
  * first-chunk latency: one chunk of audio in hand -> its JPEG frames ready (the floor on "time to first lips" for a reply)
  * streams: K conversations sharing one GPU, round-robin; a stream is sustained if a full round takes < one chunk duration
  * peak GPU memory

Run it from the repo root (or anywhere; paths are resolved before it changes directory):
  python workers/flashhead_bench.py --fh-dir workers/SoulX-FlashHead --image face.png --audio speech_16k.wav --model_type lite
On the Apple-silicon dev Mac use the .venv-flash interpreter; it will be ~20x too slow for real time but exercises every code path.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import platform
import re
import statistics
import sys
import time
from collections import deque


def _abs(p: str) -> str:
    return os.path.abspath(os.path.expanduser(p))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fh-dir", default="workers/SoulX-FlashHead", help="the SoulX-FlashHead checkout (contains flash_head/)")
    ap.add_argument("--ckpt_dir", default="models/SoulX-FlashHead-1_3B", help="path, or relative to --fh-dir")
    ap.add_argument("--wav2vec_dir", default="models/wav2vec2-base-960h", help="path, or relative to --fh-dir")
    ap.add_argument("--model_type", choices=["lite", "pro"], default="lite")
    ap.add_argument("--image", default="examples/girl.png", help="tight, front-facing face image (path, or relative to --fh-dir)")
    ap.add_argument("--audio", default="examples/podcast_sichuan_16k.wav", help="speech wav (any rate; resampled to 16 kHz)")
    ap.add_argument("--chunks", type=int, default=24, help="measured chunks for the single-stream run")
    ap.add_argument("--warmup", type=int, default=3, help="chunks run first and not counted (torch.compile happens here)")
    ap.add_argument("--streams", default="1,2,3,4", help="comma list of concurrent stream counts to test")
    ap.add_argument("--rounds", type=int, default=6, help="round-robin rounds measured per stream count")
    ap.add_argument("--seed", type=int, default=9999)
    ap.add_argument("--out", default="flashhead_bench.json")
    a = ap.parse_args()

    fh = _abs(a.fh_dir)
    out_path = _abs(a.out)

    def rel(p: str) -> str:
        """A path that exists as given (absolute, or relative to where you ran this) wins; otherwise it is relative to --fh-dir."""
        p = os.path.expanduser(p)
        return p if os.path.isabs(p) or os.path.exists(p) else os.path.join(fh, p)

    image, audio_path = _abs(rel(a.image)), _abs(rel(a.audio))
    def in_fh(p: str) -> str:
        p = os.path.expanduser(p)
        return p if os.path.isabs(p) else (os.path.join(fh, p) if os.path.exists(os.path.join(fh, p)) else p)

    ckpt, w2v = _abs(in_fh(a.ckpt_dir)), _abs(in_fh(a.wav2vec_dir))
    for label, p in (("FlashHead dir", fh), ("image", image), ("audio", audio_path), ("checkpoint", ckpt), ("wav2vec", w2v)):
        if not os.path.exists(p):
            print(f"missing {label}: {p}", file=sys.stderr)
            return 2
    os.chdir(fh)  # flash_head reads flash_head/configs/infer_params.yaml relative to the working directory
    sys.path.insert(0, fh)
    with contextlib.suppress(ImportError):
        import mac_compat  # noqa: F401  (only present in the Apple-silicon port: stubs CUDA-only imports)

    import numpy as np
    import torch

    cuda = torch.cuda.is_available()
    mps = (not cuda) and bool(getattr(torch.backends, "mps", None)) and torch.backends.mps.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda else ("Apple MPS" if mps else "CPU")

    def sync() -> None:
        if cuda:
            torch.cuda.synchronize()
        elif mps:
            torch.mps.synchronize()

    def peak_gb() -> float | None:
        try:
            if cuda:
                return round(torch.cuda.max_memory_allocated() / 1e9, 2)
            if mps:
                return round(torch.mps.driver_allocated_memory() / 1e9, 2)
        except Exception:  # noqa: BLE001
            pass
        return None

    import librosa
    from flash_head.inference import get_audio_embedding, get_base_data, get_infer_params, get_pipeline, run_pipeline

    def attention_backend() -> str:
        """Which attention kernel FlashHead picked (same priority order as flash_head_model.flash_attention)."""
        try:
            from flash_head.src.modules import flash_head_model as m
        except Exception:  # noqa: BLE001
            return "unknown"
        for flag, name in (("SAGE_ATTN_AVAILABLE", "sageattention"), ("FLASH_ATTN_3_AVAILABLE", "flash-attn 3"),
                           ("FLASH_ATTN_2_AVAILABLE", "flash-attn 2")):
            if getattr(m, flag, False):
                return name
        return "PyTorch SDPA (no flash/sage kernel installed)"

    print(f"device: {device_name} | torch {torch.__version__} | model: {a.model_type}", flush=True)
    t_load = time.time()
    pipeline = get_pipeline(world_size=1, ckpt_dir=ckpt, model_type=a.model_type, wav2vec_dir=w2v)
    get_base_data(pipeline, cond_image_path_or_dir=image, base_seed=a.seed, use_face_crop=False)
    sync()
    load_s = time.time() - t_load

    p = get_infer_params()
    sr, fps = p["sample_rate"], p["tgt_fps"]
    frame_num, motion = p["frame_num"], p["motion_frames_num"]
    slice_len = frame_num - motion
    chunk_s = slice_len / fps
    cache_len = sr * p["cached_audio_duration"]
    audio_end_idx = p["cached_audio_duration"] * fps
    audio_start_idx = audio_end_idx - frame_num
    slice_samples = slice_len * sr // fps

    speech, _ = librosa.load(audio_path, sr=sr, mono=True)
    need = (a.warmup + a.chunks + max(int(x) for x in a.streams.split(",")) * a.rounds + 8) * slice_samples
    if len(speech) < need:
        speech = np.tile(speech, int(np.ceil(need / max(1, len(speech)))))
    rem = len(speech) % slice_samples
    if rem:
        speech = speech[: len(speech) - rem]
    slices = speech.reshape(-1, slice_samples)

    init_motion = pipeline.latent_motion_frames.clone()

    class Stream:
        """One conversation's state: its rolling audio window and the motion latents carried from chunk to chunk."""

        def __init__(self, offset: int = 0):
            self.dq = deque([0.0] * cache_len, maxlen=cache_len)
            self.motion = init_motion.clone()
            self.i = offset

        def step(self):
            pipeline.latent_motion_frames = self.motion
            self.dq.extend(slices[self.i % len(slices)].tolist())
            self.i += 1
            t0 = time.perf_counter()
            emb = get_audio_embedding(pipeline, np.array(self.dq), audio_start_idx, audio_end_idx)
            sync()
            t1 = time.perf_counter()
            video = run_pipeline(pipeline, emb)[motion:]
            sync()
            t2 = time.perf_counter()
            self.motion = pipeline.latent_motion_frames
            return video, t1 - t0, t2 - t1

    try:
        import cv2

        def jpeg_ms(video) -> float:
            arr = video.clamp(0, 255).to(torch.uint8).cpu().numpy()
            t = time.perf_counter()
            for f in arr:
                cv2.imencode(".jpg", f[:, :, ::-1], [cv2.IMWRITE_JPEG_QUALITY, 80])
            return (time.perf_counter() - t) * 1000
    except ImportError:
        from PIL import Image

        def jpeg_ms(video) -> float:
            arr = video.clamp(0, 255).to(torch.uint8).cpu().numpy()
            t = time.perf_counter()
            for f in arr:
                Image.fromarray(f).save(io.BytesIO(), "JPEG", quality=80)
            return (time.perf_counter() - t) * 1000

    step_re = {k: re.compile(rf"{pat}: ([0-9.]+)s") for k, pat in
               {"denoise_step": r"model denoise per step", "vae_decode": r"decode video frames",
                "colour": r"color correction", "motion_encode": r"encode motion frames"}.items()}

    def quiet_step(stream: Stream):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            res = stream.step()
        return res, buf.getvalue()

    # ---- warm-up (torch.compile on CUDA happens here) ----
    print(f"model load {load_s:.1f} s; warming up {a.warmup} chunk(s)...", flush=True)
    t_w = time.time()
    warm = Stream()
    for _ in range(a.warmup):
        quiet_step(warm)
    warm_s = time.time() - t_w
    if cuda:
        torch.cuda.reset_peak_memory_stats()

    # ---- single stream: per-chunk timings ----
    print(f"measuring {a.chunks} chunk(s), one stream...", flush=True)
    s1 = Stream(offset=a.warmup)
    rows, parts = [], {k: [] for k in step_re}
    for n in range(a.chunks):
        (video, emb_t, gen_t), log = quiet_step(s1)
        enc = jpeg_ms(video) / 1000
        rows.append({"embed_s": emb_t, "generate_s": gen_t, "jpeg_s": enc, "gpu_s": emb_t + gen_t, "total_s": emb_t + gen_t + enc})
        for k, rx in step_re.items():
            vals = [float(x) for x in rx.findall(log)]
            if vals:
                parts[k].append(sum(vals) / len(vals) if k == "denoise_step" else sum(vals))
        print(f"  chunk {n + 1:>2}/{a.chunks}: embed {emb_t * 1000:6.0f} ms | generate {gen_t * 1000:6.0f} ms | jpeg {enc * 1000:5.0f} ms", flush=True)

    def pct(vals, q):
        s = sorted(vals)
        return s[min(len(s) - 1, int(round(q * (len(s) - 1))))]

    def summary(key):
        v = [r[key] for r in rows]
        return {"median": round(statistics.median(v), 4), "p95": round(pct(v, 0.95), 4), "worst": round(max(v), 4)}

    single = {"embed_s": summary("embed_s"), "generate_s": summary("generate_s"), "jpeg_s": summary("jpeg_s"),
              "gpu_s": summary("gpu_s"), "total_s": summary("total_s"),
              "breakdown_median_s": {k: round(statistics.median(v), 4) for k, v in parts.items() if v}}
    p95 = single["total_s"]["p95"]
    margin = chunk_s / p95 if p95 else 0.0
    verdict = ("REAL TIME with headroom" if margin >= 1.25 else "BORDERLINE (just real time)" if margin >= 1.0 else "TOO SLOW for live")
    first_chunk_s = round(single["total_s"]["median"], 3)

    # ---- K streams sharing the GPU (round-robin, state swapped per chunk) ----
    streams_out, sustained = [], 0
    for k in sorted({int(x) for x in a.streams.split(",") if x.strip()}):
        try:
            ss = [Stream(offset=a.warmup + 100 * j) for j in range(k)]
            rounds = []
            for _ in range(a.rounds):
                t = time.perf_counter()
                for st in ss:
                    (video, _, _), _log = quiet_step(st)
                    jpeg_ms(video)
                rounds.append(time.perf_counter() - t)
            med, w = statistics.median(rounds), pct(rounds, 0.95)
            ok = w <= chunk_s
            streams_out.append({"streams": k, "round_median_s": round(med, 3), "round_p95_s": round(w, 3),
                                "per_stream_fps_equiv": round(slice_len / w, 1), "sustained": ok})
            print(f"  {k} stream(s): round p95 {w:.2f} s vs {chunk_s:.2f} s budget -> {'sustained' if ok else 'NOT sustained'}", flush=True)
            if ok:
                sustained = k
            else:
                break  # more streams only get slower
        except Exception as e:  # noqa: BLE001  (out of memory etc.)
            streams_out.append({"streams": k, "error": f"{type(e).__name__}: {str(e)[:160]}"})
            break

    report = {
        "device": device_name, "torch": torch.__version__, "python": platform.python_version(), "model_type": a.model_type,
        "resolution": [p["width"], p["height"]], "fps": fps, "frames_per_chunk": slice_len, "chunk_s": round(chunk_s, 3),
        "attention": attention_backend(), "cold_start": {"model_load_s": round(load_s, 1), "warmup_s": round(warm_s, 1), "warmup_chunks": a.warmup},
        "single_stream": single, "realtime_margin_x": round(margin, 2), "verdict": verdict,
        "first_chunk_latency_s": first_chunk_s, "max_sustained_streams": sustained, "streams": streams_out,
        "peak_gpu_gb": peak_gb(), "image": os.path.basename(image), "audio": os.path.basename(audio_path),
        "note": "Measured chunks use a looped speech file; real conversations also run STT, the LLM and TTS on the same GPU.",
    }
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print("\n=== FlashHead real-time benchmark ===")
    print(f"device            {device_name}   ({a.model_type}, {p['width']}x{p['height']} @ {fps} fps)")
    print(f"attention         {report['attention']}")
    print(f"cold start        load {load_s:.0f} s + warm-up {warm_s:.0f} s")
    print(f"one chunk         {chunk_s:.2f} s of video; generated in median {single['total_s']['median']:.2f} s, p95 {p95:.2f} s (incl. JPEG)")
    print(f"real-time margin  {margin:.2f}x  -> {verdict}")
    print(f"first chunk       about {first_chunk_s:.2f} s from {chunk_s:.2f} s of audio in hand to {slice_len} JPEG frames ready")
    print(f"streams           {sustained} sustained at real time on this GPU")
    print(f"peak GPU memory   {report['peak_gpu_gb']} GB")
    print(f"saved             {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
