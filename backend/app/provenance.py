"""Machine-readable "AI-generated" labels on media VocalFace produces (the direction of EU AI Act Article 50(2)).

Today this writes standard MP4/M4A metadata tags with a stream copy (no re-encode, about a second). It is a label, not
a cryptographic C2PA manifest: anyone can strip metadata. Generated videos say they are synthetic; recordings say they
are a conversation with an AI agent. Tagging never fails the job that called it.
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger("vocalface.provenance")

GENERATED = "AI-generated video: the face and voice are synthetic, made with VocalFace (vocalface.com)."
RECORDING = "Recording of a conversation with an AI agent, made with VocalFace (vocalface.com)."


def tag_mp4(path: str | Path, kind: str = "generated") -> bool:
    """Rewrite the container metadata in place. kind: generated | recording. -> True when tagged."""
    p = Path(path)
    ff = shutil.which(os.environ.get("VOCALFACE_FFMPEG", "ffmpeg"))
    if not ff or not p.exists():
        return False
    text = GENERATED if kind == "generated" else RECORDING
    tmp = p.with_name(f"{p.stem}.tagging{p.suffix}")
    cmd = [ff, "-y", "-loglevel", "error", "-i", str(p), "-map", "0", "-c", "copy", "-map_metadata", "0",
           "-metadata", f"comment={text}", "-metadata", f"description={text}", "-metadata", "artist=VocalFace AI",
           "-metadata", f"vocalface_provenance={kind}", "-movflags", "+faststart+use_metadata_tags", str(tmp)]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired):
        tmp.unlink(missing_ok=True)
        return False
    if r.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
        log.warning("provenance tag failed for %s: %s", p.name, r.stderr.decode(errors="replace")[-200:])
        tmp.unlink(missing_ok=True)
        return False
    os.replace(tmp, p)
    return True


def read_tags(path: str | Path) -> dict:
    """Container tags as ffprobe reports them ({} when ffprobe is missing)."""
    probe = shutil.which("ffprobe")
    if not probe:
        return {}
    r = subprocess.run([probe, "-v", "error", "-show_entries", "format_tags", "-of", "json", str(path)], capture_output=True, text=True)
    try:
        return {k.lower(): v for k, v in (json.loads(r.stdout).get("format", {}).get("tags") or {}).items()}
    except ValueError:
        return {}
