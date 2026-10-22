"""Conversation recordings: what the participant heard and saw, as one MP4 (or M4A for a persona without a face) plus
WebVTT captions.

Opt-in per persona (`PUT /v1/personas/{id}/privacy`, record_conversations). While a call runs, the realtime handler taps
streams it already has: mic PCM in (16 kHz), agent PCM out (24 kHz), the avatar's video segments and idle loop (JPEG
frames), interruptions and transcript lines. Audio and frames are spooled to disk as they arrive, never held in RAM.

When the socket closes the part is composed on a worker thread, on the client's timeline:
  * agent audio plays back-to-back from the moment each piece was sent (the client queues it),
  * an interruption drops whatever was still queued at that moment,
  * a video segment plays with the audio piece that follows it (the protocol sends the segment first),
  * the idle loop (ping-pong, like the client) fills the time between segments.
A reconnect starts another part; the recording file is always every part joined. Zero data retention wins: a persona with
it switched on is never recorded (privacy.Policy.recording).
"""
from __future__ import annotations

import base64
import json
import logging
import math
import os
import shutil
import struct
import subprocess
import threading
import time
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

log = logging.getLogger("vocalface.recording")

FPS = 25
MIC_SR, AGENT_SR = 16000, 24000
MAX_S = float(os.environ.get("VOCALFACE_RECORDING_MAX_S", "3600"))  # one part never records more than this
DEFAULT_SIZE = (640, 360)  # a video part without any face frame (face service down) is rendered on a plain frame this size
_threads: list[threading.Thread] = []
_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def ffmpeg_bin() -> Optional[str]:
    return shutil.which(os.environ.get("VOCALFACE_FFMPEG", "ffmpeg"))


def rec_dir(data_dir: Path, cid: str) -> Path:
    return Path(data_dir) / "recordings" / cid


def final_path(data_dir: Path, cid: str, kind: str) -> Path:
    return rec_dir(data_dir, cid) / ("recording.mp4" if kind == "video" else "recording.m4a")


def captions_path(data_dir: Path, cid: str) -> Path:
    return rec_dir(data_dir, cid) / "captions.vtt"


def _lock(cid: str) -> threading.Lock:
    with _locks_guard:
        return _locks.setdefault(cid, threading.Lock())


# ------------------------------------------------------------------------------------------------ live tap
class Recorder:
    """Spools one live connection (a part) to disk. Called from the realtime handler's event loop only."""

    def __init__(self, out_dir: Path, part: int, cid: str = "", kind: str = "video",
                 clock: Callable[[], float] = time.monotonic, max_s: float = MAX_S):
        self.dir, self.part, self.cid, self.kind = Path(out_dir), part, cid, kind
        self._clock, self.max_s = clock, max_s
        self.t0 = clock()
        self.dir.mkdir(parents=True, exist_ok=True)
        stem = self.dir / f"part{part:03d}"
        self._mic = open(f"{stem}.mic.raw", "wb")
        self._agent = open(f"{stem}.agent.raw", "wb")
        self._frames = open(f"{stem}.frames.bin", "wb")
        self.mic: list[list[int]] = []        # [start sample @16 kHz on the timeline, n samples], in file order
        self._mic_end = 0
        self.agent: list[list[float]] = []    # [start s, duration s, file offset, n bytes], trimmed by interruptions
        self._agent_end = 0.0                 # when the queued agent audio finishes playing (s since t0)
        self._agent_off = 0
        self.segments: list[dict] = []        # {"t": start s, "fps": f, "frames": [[offset, len], ...], "end": cut s?}
        self._pending: Optional[dict] = None  # a video segment waiting for the audio piece it belongs to
        self.idle: Optional[dict] = None      # {"fps": f, "frames": [[offset, len], ...]}
        self._frames_off = 0
        self.captions: list[dict] = []        # {"start", "end", "who": "user"|"agent", "text"}
        self._speech_at: Optional[float] = None
        self._agent_text_from: Optional[float] = None
        self.truncated = False
        self.closed = False

    # ---- helpers ----
    def _t(self) -> float:
        return self._clock() - self.t0

    def _live(self) -> bool:
        if self.closed:
            return False
        if self._t() > self.max_s:
            self.truncated = True
            return False
        return True

    def _store_frames(self, frames_b64: list) -> list[list[int]]:
        out = []
        for f in frames_b64:
            try:
                b = base64.b64decode(f) if isinstance(f, str) else bytes(f)
            except (ValueError, TypeError):
                continue
            self._frames.write(b)
            out.append([self._frames_off, len(b)])
            self._frames_off += len(b)
        return out

    # ---- taps ----
    def on_mic(self, pcm: bytes) -> None:
        if not pcm or not self._live():
            return
        n = len(pcm) // 2
        end = int(round(self._t() * MIC_SR))  # a chunk arrives right after it was captured
        start = max(self._mic_end, end - n)
        self._mic.write(pcm[: n * 2])
        self.mic.append([start, n])
        self._mic_end = start + n

    def on_agent_audio(self, pcm: bytes) -> None:
        if not pcm or not self._live():
            return
        nbytes = len(pcm) // 2 * 2
        dur = nbytes / 2 / AGENT_SR
        start = max(self._t(), self._agent_end)
        self._agent.write(pcm[:nbytes])
        self.agent.append([start, dur, self._agent_off, nbytes])
        self._agent_off += nbytes
        self._agent_end = start + dur
        if self._agent_text_from is None:
            self._agent_text_from = start
        if self._pending is not None:
            seg, self._pending = self._pending, None
            seg["t"] = start
            self.segments.append(seg)

    def on_json(self, msg: dict) -> None:
        if not isinstance(msg, dict) or not self._live():
            return
        t = msg.get("type")
        if t == "video_segment" and msg.get("frames"):
            self._pending = {"fps": float(msg.get("fps") or FPS), "frames": self._store_frames(msg["frames"])}
        elif t == "idle_loop" and msg.get("frames"):
            self.idle = {"fps": float(msg.get("fps") or FPS), "frames": self._store_frames(msg["frames"])}
        elif t == "interrupted":
            self._interrupt(self._t())
        elif t == "speech_start":
            if self._speech_at is None:
                self._speech_at = self._t()
        elif t == "transcript":
            text = str(msg.get("text") or "").strip()
            if not text:
                return
            now = self._t()
            if msg.get("role") == "user":
                start = self._speech_at if self._speech_at is not None else max(0.0, now - 3.0)
                self.captions.append({"start": start, "end": max(now, start + 0.5), "who": "user", "text": text})
                self._speech_at = None
            else:
                start = self._agent_text_from if self._agent_text_from is not None else self._agent_end
                self.captions.append({"start": start, "end": max(self._agent_end, start + 0.5), "who": "agent", "text": text})
                self._agent_text_from = None

    def _interrupt(self, at: float) -> None:
        """The client drops queued agent audio now: cut every span and segment at `at`."""
        kept = []
        for span in self.agent:
            start, dur = span[0], span[1]
            if start >= at:
                continue
            if start + dur > at:
                span[1] = at - start
            kept.append(span)
        self.agent = kept
        self._agent_end = min(self._agent_end, at)
        self.segments = [s for s in self.segments if s["t"] < at]
        for s in self.segments:
            if s["t"] + len(s["frames"]) / s["fps"] > at:
                s["end"] = at
        self._pending = None
        self._agent_text_from = None
        for c in self.captions:
            if c["who"] == "agent" and c["end"] > at > c["start"]:
                c["end"] = at

    def wrap(self, send_json, send_bytes):
        """Taps for the handler's outgoing JSON and agent-audio senders. A tap failure never affects the call."""
        async def j(msg: dict) -> None:
            try:
                self.on_json(msg)
            except Exception:  # noqa: BLE001
                log.exception("recording tap (json) failed")
            await send_json(msg)

        async def b(data: bytes) -> None:
            try:
                self.on_agent_audio(data)
            except Exception:  # noqa: BLE001
                log.exception("recording tap (audio) failed")
            await send_bytes(data)

        return j, b

    def close(self) -> dict:
        """Flush, close the spool files and write the part manifest. Idempotent."""
        if self.closed:
            return json.loads((self.dir / f"part{self.part:03d}.json").read_text())
        self.closed = True
        if self._pending is not None:  # a segment whose audio never went out was never shown
            self._pending = None
        for f in (self._mic, self._agent, self._frames):
            try:
                f.close()
            except OSError:
                pass
        ends = [self._mic_end / MIC_SR, self._agent_end] + [c["end"] for c in self.captions]
        ends += [s.get("end", s["t"] + len(s["frames"]) / s["fps"]) for s in self.segments]
        duration = min(max(ends + [1.0]), self.max_s)
        man = {"part": self.part, "kind": self.kind, "duration": round(duration, 3), "truncated": self.truncated,
               "mic": self.mic, "agent": self.agent, "segments": self.segments, "idle": self.idle, "captions": self.captions}
        (self.dir / f"part{self.part:03d}.json").write_text(json.dumps(man))
        return man


# ------------------------------------------------------------------------------------------------ composition
def _jpeg_size(b: bytes) -> Optional[tuple[int, int]]:
    """(width, height) from the JPEG SOF marker, without decoding."""
    i = 2
    while i + 9 < len(b):
        if b[i] != 0xFF:
            i += 1
            continue
        marker = b[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack(">HH", b[i + 5:i + 9])
            return w, h
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        seg_len = struct.unpack(">H", b[i + 2:i + 4])[0]
        i += 2 + seg_len
    return None


def _fit(b: bytes, size: tuple[int, int]) -> Optional[bytes]:
    """Re-encode a frame whose size differs from the part's reference size (rare: a quality-tier change)."""
    try:
        import io

        from PIL import Image

        im = Image.open(io.BytesIO(b)).convert("RGB").resize(size)
        out = io.BytesIO()
        im.save(out, "JPEG", quality=85)
        return out.getvalue()
    except Exception:  # noqa: BLE001
        return None


def _plain_frame(size: tuple[int, int]) -> bytes:
    import io

    from PIL import Image

    out = io.BytesIO()
    Image.new("RGB", size, (16, 18, 24)).save(out, "JPEG", quality=80)
    return out.getvalue()


def _write_wav(path: Path, sr: int, spans: list, raw: Path, n_total: int, placement: Callable[[list], tuple[int, int, int]]) -> None:
    """Stream a gap-filled mono int16 WAV: spans are non-overlapping and in order; `placement(span)` gives
    (start sample, file offset in bytes, n samples to copy)."""
    zero = bytes(2 * 4096)
    with wave.open(str(path), "wb") as w, open(raw, "rb") as src:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        cur = 0
        for span in spans:
            start, off, n = placement(span)
            start = max(start, cur)
            if start >= n_total or n <= 0:
                continue
            gap = start - cur
            while gap > 0:
                k = min(gap, 4096)
                w.writeframes(zero[: 2 * k])
                gap -= k
            n = min(n, n_total - start)
            src.seek(off)
            w.writeframes(src.read(2 * n))
            cur = start + n
        rest = max(0, n_total - cur)
        while rest > 0:
            k = min(rest, 4096)
            w.writeframes(zero[: 2 * k])
            rest -= k


def _vtt_time(s: float) -> str:
    s = max(0.0, s)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{sec:06.3f}"


def _vtt_cues(captions: list[dict], offset: float) -> list[str]:
    cues = []
    for c in sorted(captions, key=lambda c: c["start"]):
        who = "User" if c["who"] == "user" else "Agent"
        text = c["text"].replace("-->", "->")
        cues.append(f"{_vtt_time(c['start'] + offset)} --> {_vtt_time(c['end'] + offset)}\n<v {who}>{text}")
    return cues


def _frame_plan(man: dict, n_frames: int):
    """Yield (offset, length) of the JPEG to show for each output frame, or None when nothing was ever shown."""
    segs = sorted(man["segments"], key=lambda s: s["t"])
    idle = (man.get("idle") or {}).get("frames") or []
    L = len(idle)
    period = max(1, 2 * L - 2)
    si, last = 0, None
    for i in range(n_frames):
        t = i / FPS
        while si < len(segs) and segs[si].get("end", segs[si]["t"] + len(segs[si]["frames"]) / segs[si]["fps"]) <= t:
            si += 1
        cur = None
        if si < len(segs) and segs[si]["t"] <= t:
            s = segs[si]
            k = min(len(s["frames"]) - 1, int((t - s["t"]) * s["fps"]))
            cur = s["frames"][k]
        elif L:
            j = i % period
            cur = idle[j if j < L else period - j]
        if cur is None:
            cur = last
        last = cur
        yield cur


def compose_part(out_dir: Path, part: int, ffmpeg: Optional[str] = None) -> dict:
    """Render one part to part{n}.mp4 (or .m4a) from its spool files and manifest. Returns {path, duration, kind}."""
    ffmpeg = ffmpeg or ffmpeg_bin()
    if not ffmpeg:
        raise RuntimeError("ffmpeg is not installed on the server")
    out_dir = Path(out_dir)
    stem = out_dir / f"part{part:03d}"
    man = json.loads(Path(f"{stem}.json").read_text())
    T = float(man["duration"])
    mic_wav, agent_wav = Path(f"{stem}.mic.wav"), Path(f"{stem}.agent.wav")
    mic_offsets, off = [], 0
    for start, n in man["mic"]:
        mic_offsets.append((start, off, n))
        off += 2 * n
    _write_wav(mic_wav, MIC_SR, mic_offsets, Path(f"{stem}.mic.raw"), max(1, int(math.ceil(T * MIC_SR))), lambda s: s)
    _write_wav(agent_wav, AGENT_SR, man["agent"], Path(f"{stem}.agent.raw"), max(1, int(math.ceil(T * AGENT_SR))),
               lambda s: (int(round(s[0] * AGENT_SR)), int(s[2]), int(round(s[1] * AGENT_SR))))
    mix = ("[{m}:a]aresample=24000[mic];[mic][{a}:a]amix=inputs=2:duration=longest:normalize=0,"
           "alimiter=limit=0.95[aout]")
    if man.get("kind", "video") == "video":
        out = Path(f"{stem}.mp4")
        frames_bin = Path(f"{stem}.frames.bin")
        n_frames = max(1, int(math.ceil(T * FPS)))
        plan = list(_frame_plan(man, n_frames))
        first = None
        with open(frames_bin, "rb") as fb:
            for ref in plan:
                if ref is not None:
                    fb.seek(ref[0])
                    first = _jpeg_size(fb.read(ref[1]))
                    break
        ref_file = out_dir / "video_size.json"  # every part of one conversation uses one size, so parts can be joined
        conv_size = tuple(json.loads(ref_file.read_text())) if ref_file.exists() else None
        size = conv_size or first or DEFAULT_SIZE
        size = (max(2, size[0] // 2 * 2), max(2, size[1] // 2 * 2))
        if conv_size is None and first:
            ref_file.write_text(json.dumps(list(size)))
        plain = _plain_frame(size)
        cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "pipe:0",
               "-i", str(mic_wav), "-i", str(agent_wav),
               "-filter_complex", f"[0:v]scale={size[0]}:{size[1]},format=yuv420p[vout];" + mix.format(m=1, a=2),
               "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
               "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", "-t", f"{T:.3f}", str(out)]
        errf = open(f"{stem}.ffmpeg.log", "w+b")  # a file, not a pipe: a chatty ffmpeg must not block while we feed it
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=errf)
        try:
            with open(frames_bin, "rb") as fb:
                cache: dict[tuple, bytes] = {}
                for ref in plan:
                    if ref is None:
                        data = plain
                    else:
                        key = tuple(ref)
                        data = cache.get(key)
                        if data is None:
                            fb.seek(ref[0])
                            data = fb.read(ref[1])
                            sz = _jpeg_size(data)
                            if sz and (sz[0] // 2 * 2, sz[1] // 2 * 2) != size:
                                data = _fit(data, size) or plain
                            if len(cache) < 512:
                                cache[key] = data
                    proc.stdin.write(data)
            proc.stdin.close()
        except BrokenPipeError:
            pass
        code = proc.wait()
        errf.seek(0)
        err = errf.read().decode(errors="replace")
        errf.close()
        Path(f"{stem}.ffmpeg.log").unlink(missing_ok=True)
        if code != 0:
            raise RuntimeError(f"ffmpeg failed: {err[-400:]}")
    else:
        out = Path(f"{stem}.m4a")
        cmd = [ffmpeg, "-y", "-loglevel", "error", "-i", str(mic_wav), "-i", str(agent_wav), "-filter_complex", mix.format(m=0, a=1),
               "-map", "[aout]", "-c:a", "aac", "-b:a", "96k", "-t", f"{T:.3f}", str(out)]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {r.stderr.decode(errors='replace')[-400:]}")
    for p in (mic_wav, agent_wav):
        p.unlink(missing_ok=True)
    return {"path": str(out), "duration": T, "kind": man.get("kind", "video")}


def join_parts(out_dir: Path, kind: str, ffmpeg: Optional[str] = None) -> tuple[Path, Path, float]:
    """All composed parts -> recording.mp4|m4a + captions.vtt. Returns (file, captions, total seconds)."""
    ffmpeg = ffmpeg or ffmpeg_bin()
    out_dir = Path(out_dir)
    ext = "mp4" if kind == "video" else "m4a"
    mans = sorted((json.loads(p.read_text()) for p in out_dir.glob("part*.json")), key=lambda m: m["part"])
    parts = [out_dir / f"part{m['part']:03d}.{ext}" for m in mans if (out_dir / f"part{m['part']:03d}.{ext}").exists()]
    mans = [m for m in mans if (out_dir / f"part{m['part']:03d}.{ext}").exists()]
    if not parts:
        raise RuntimeError("no composed part")
    final = out_dir / f"recording.{ext}"
    tmp = out_dir / f"recording.tmp.{ext}"
    if len(parts) == 1:
        shutil.copyfile(parts[0], tmp)
    else:
        lst = out_dir / "parts.txt"
        lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
        r = subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                            "-movflags", "+faststart", str(tmp)], capture_output=True, cwd=str(out_dir))
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg concat failed: {r.stderr.decode(errors='replace')[-400:]}")
    os.replace(tmp, final)
    cues, offset = [], 0.0
    for m in mans:
        cues += _vtt_cues(m["captions"], offset)
        offset += float(m["duration"])
    vtt = out_dir / "captions.vtt"
    vtt.write_text("WEBVTT\n\n" + "\n\n".join(cues) + ("\n" if cues else ""))
    return final, vtt, offset


# ------------------------------------------------------------------------------------------------ lifecycle
def start_for(s, conv, persona, data_dir: Path, policy=None) -> Optional[Recorder]:
    """A Recorder for this connection when the persona records (and retention allows), else None. Creates or extends the
    conversation's recording row. A server without ffmpeg records nothing and says why on the row."""
    from . import privacy
    from .models_privacy import ConversationRecording

    policy = policy or privacy.load(s, persona.id)
    if not policy.recording:
        return None
    privacy.ensure()
    row = s.get(ConversationRecording, conv.id)
    from . import jobs

    has_face = bool(persona.replica_id) and (jobs.replica_dir(persona.replica_id) / "source.mp4").exists()
    if row is None:
        row = ConversationRecording(conversation_id=conv.id, account_id=conv.account_id, persona_id=persona.id,
                                    kind="video" if has_face else "audio")
    if not ffmpeg_bin():
        row.status, row.error = "error", "ffmpeg is not installed on the server, so nothing was recorded"
        s.add(row)
        s.commit()
        return None
    part = row.parts
    row.parts, row.status, row.error = part + 1, "recording", ""
    s.add(row)
    s.commit()
    return Recorder(rec_dir(data_dir, conv.id), part, cid=conv.id, kind=row.kind)


def finish(rec: Recorder, data_dir: Path) -> dict:
    """Close the part, compose it, rebuild the joined file, publish it, update the row and send the webhook.
    Runs on a worker thread. Never raises; returns what happened."""
    from sqlmodel import Session

    from . import db, signing, storage, webhooks
    from .models_privacy import ConversationRecording

    cid = rec.cid
    with _lock(cid):
        try:
            rec.close()
            with Session(db.engine) as s:
                row = s.get(ConversationRecording, cid)
                if row is not None:
                    row.status = "processing"
                    s.add(row)
                    s.commit()
            compose_part(rec.dir, rec.part)
            for ext in ("mic.raw", "agent.raw", "frames.bin"):
                (rec.dir / f"part{rec.part:03d}.{ext}").unlink(missing_ok=True)
            final, vtt, total = join_parts(rec.dir, rec.kind)
            for p in (final, vtt):
                try:
                    storage.publish(p)
                except Exception:  # noqa: BLE001 - local copy still serves
                    log.exception("recording publish failed")
            with Session(db.engine) as s:
                row = s.get(ConversationRecording, cid)
                if row is None:  # deleted while composing: drop what we just wrote
                    shutil.rmtree(rec.dir, ignore_errors=True)
                    return {"status": "deleted"}
                row.status, row.error = "ready", ""
                row.duration_s, row.size_bytes = round(total, 2), final.stat().st_size
                row.ready_at = datetime.now(timezone.utc)
                s.add(row)
                s.commit()
                path = file_route(cid, row.kind)
                webhooks.emit(row.account_id, "conversation.recording_ready", {
                    "conversation_id": cid, "persona_id": row.persona_id, "kind": row.kind, "duration_s": row.duration_s,
                    "parts": row.parts, "recording_url": signing.sign_path(path),
                    "captions_url": signing.sign_path(f"/v1/files/recordings/{cid}/captions.vtt")}, session=s)
            return {"status": "ready", "path": str(final), "duration": total}
        except Exception as e:  # noqa: BLE001
            log.exception("recording %s failed", cid)
            try:
                with Session(db.engine) as s:
                    row = s.get(ConversationRecording, cid)
                    if row is not None:
                        row.status, row.error = "error", f"{type(e).__name__}: {e}"[:300]
                        s.add(row)
                        s.commit()
            except Exception:  # noqa: BLE001
                pass
            return {"status": "error", "error": str(e)}


def finish_in_background(rec: Recorder, data_dir: Path) -> threading.Thread:
    th = threading.Thread(target=finish, args=(rec, data_dir), name=f"recording-{rec.cid}", daemon=True)
    th.start()
    _threads.append(th)
    del _threads[:-64]
    return th


def wait_all(timeout: float = 60.0) -> None:
    """Tests and graceful shutdown: wait for compositions in flight."""
    end = time.monotonic() + timeout
    for th in list(_threads):
        th.join(max(0.0, end - time.monotonic()))


def file_route(cid: str, kind: str) -> str:
    return f"/v1/files/recordings/{cid}/recording.{'mp4' if kind == 'video' else 'm4a'}"


def delete(data_dir: Path, cid: str) -> int:
    """Remove a conversation's recording files (local and remote). -> number of remote objects removed."""
    from . import storage

    d = rec_dir(data_dir, cid)
    n = 0
    for p in (final_path(data_dir, cid, "video"), final_path(data_dir, cid, "audio"), captions_path(data_dir, cid)):
        try:
            n += storage.remove(p)
        except Exception:  # noqa: BLE001
            pass
    shutil.rmtree(d, ignore_errors=True)
    return n
