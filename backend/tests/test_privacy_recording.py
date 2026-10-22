"""Privacy controls (recording, zero data retention, AI disclosure) and conversation recordings."""
import asyncio
import base64
import io
import json
import shutil
import subprocess
from pathlib import Path

import pytest
from sqlmodel import Session, select

from app import db, jobs, llm_backends as lb, recording, signing
from app.models_features import ObjectiveProgress, TranscriptTurn
from app.models_privacy import ConversationRecording

from .test_realtime import FakeLLM, collect, env, speak  # noqa: F401

needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


def H(key):
    return {"x-api-key": key}


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    from app import safety

    monkeypatch.setattr(jobs, "DATA_DIR", tmp_path / "data")
    monkeypatch.setenv("VOCALFACE_RL_SIGNUP", "1000/60")
    monkeypatch.setenv("VOCALFACE_RL_IP", "100000/60")
    monkeypatch.setenv("VOCALFACE_RL_KEY", "100000/60")
    safety.limiter.reset()
    lb.set_completer(None)
    yield
    recording.wait_all(60)
    lb.set_completer(None)
    safety.limiter.reset()


class Clock:
    def __init__(self):
        self.t = 100.0

    def __call__(self):
        return self.t


def _jpeg(color, size=(64, 48)) -> bytes:
    from PIL import Image

    b = io.BytesIO()
    Image.new("RGB", size, color).save(b, "JPEG")
    return b.getvalue()


def _b64(x: bytes) -> str:
    return base64.b64encode(x).decode()


def _probe(path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


# ---------------------------------------------------------------- timeline (no ffmpeg needed)
def test_agent_audio_queues_segments_follow_audio_and_interruption_cuts(tmp_path):
    clk = Clock()
    r = recording.Recorder(tmp_path / "r", 0, cid="c_1", clock=clk)
    r.on_json({"type": "idle_loop", "fps": 25, "frames": [_b64(_jpeg((0, 0, 255)))] * 3})
    clk.t += 1.0
    r.on_json({"type": "video_segment", "fps": 25, "frames": [_b64(_jpeg((255, 0, 0)))] * 25})
    r.on_agent_audio(b"\x01\x00" * 24000)  # 1.0 s, sent at t=1.0
    r.on_agent_audio(b"\x01\x00" * 24000)  # sent at the same moment: the client plays it after the first
    assert [a[0] for a in r.agent] == [1.0, 2.0]
    assert r.segments[0]["t"] == 1.0  # the segment plays with the audio piece that followed it
    clk.t += 0.5  # t = 1.5: the user barges in
    r.on_json({"type": "interrupted"})
    assert [round(a[1], 3) for a in r.agent] == [0.5]  # first piece cut, the queued one dropped
    assert r.segments[0]["end"] == 1.5
    man = r.close()
    assert man["duration"] >= 1.5 and len(man["idle"]["frames"]) == 3


def test_mic_chunks_are_placed_by_arrival_without_overlap(tmp_path):
    clk = Clock()
    r = recording.Recorder(tmp_path / "m", 0, clock=clk)
    clk.t += 0.5
    r.on_mic(bytes(3200))  # 100 ms arriving at 0.5 s -> 0.4 .. 0.5 s
    r.on_mic(bytes(3200))  # same instant: right after, never on top
    assert r.mic == [[6400, 1600], [8000, 1600]]


def test_captions_follow_speech_and_playback(tmp_path):
    clk = Clock()
    r = recording.Recorder(tmp_path / "c", 0, clock=clk)
    clk.t += 1
    r.on_json({"type": "speech_start"})
    clk.t += 2
    r.on_json({"type": "transcript", "role": "user", "text": "hello there"})
    r.on_agent_audio(b"\x01\x00" * 48000)  # 2 s
    r.on_json({"type": "transcript", "role": "agent", "text": "Hi!"})
    u, a = r.close()["captions"]
    assert (u["start"], u["end"], u["who"]) == (1.0, 3.0, "user")
    assert (a["start"], a["end"], a["who"]) == (3.0, 5.0, "agent")


def test_a_part_stops_recording_at_the_limit_and_taps_never_raise(tmp_path):
    clk = Clock()
    r = recording.Recorder(tmp_path / "x", 0, clock=clk, max_s=2)
    r.on_mic(bytes(640))
    clk.t += 3
    r.on_mic(bytes(640))
    r.on_json({"type": "video_segment", "frames": ["not base64 !!"]})
    r.on_json("not a dict")
    assert len(r.mic) == 1 and r.truncated
    r.close()
    r.on_mic(bytes(640))  # after close: ignored, no error
    assert len(r.mic) == 1


def test_jpeg_size_parser():
    assert recording._jpeg_size(_jpeg((1, 2, 3), (64, 48))) == (64, 48)
    assert recording._jpeg_size(b"nope") is None


def test_signed_paths_cover_recordings_only():
    assert signing.valid_file_path("/v1/files/recordings/c_1a2b3c/recording.mp4")
    assert signing.valid_file_path("/v1/files/recordings/c_1a2b3c/captions.vtt")
    assert not signing.valid_file_path("/v1/files/recordings/c_1a2b3c/part000.mic.raw")
    assert not signing.valid_file_path("/v1/files/recordings/../etc/recording.mp4")


# ---------------------------------------------------------------- composition (ffmpeg)
@needs_ffmpeg
def test_compose_video_parts_and_join_with_captions(tmp_path):
    clk = Clock()
    d = tmp_path / "rec"
    r = recording.Recorder(d, 0, cid="c_ab", clock=clk)
    r.on_json({"type": "idle_loop", "fps": 25, "frames": [_b64(_jpeg((0, 0, 255)))] * 4})
    clk.t += 0.2
    r.on_mic(b"\x00\x10" * 3200)
    r.on_json({"type": "video_segment", "fps": 25, "frames": [_b64(_jpeg((255, 0, 0)))] * 25})
    r.on_agent_audio(b"\x00\x20" * 24000)
    r.on_json({"type": "transcript", "role": "agent", "text": "Hi there."})
    r.close()
    out = recording.compose_part(d, 0)
    p = _probe(out["path"])
    kinds = sorted(s["codec_type"] for s in p["streams"])
    assert kinds == ["audio", "video"] and abs(float(p["format"]["duration"]) - out["duration"]) < 0.3
    assert next(s for s in p["streams"] if s["codec_type"] == "video")["width"] == 64
    # a reconnect adds a second part (no face frames this time: rendered on a plain frame of the same size)
    r2 = recording.Recorder(d, 1, cid="c_ab", clock=clk)
    clk.t += 1.0
    r2.on_mic(b"\x00\x10" * 16000)
    r2.on_json({"type": "speech_start"})
    r2.on_json({"type": "transcript", "role": "user", "text": "and again"})
    r2.close()
    recording.compose_part(d, 1)
    final, vtt, total = recording.join_parts(d, "video")
    assert final.name == "recording.mp4"
    assert abs(float(_probe(final)["format"]["duration"]) - total) < 0.5
    text = vtt.read_text()
    assert text.startswith("WEBVTT") and "<v Agent>Hi there." in text and "<v User>and again" in text


@needs_ffmpeg
def test_compose_audio_only_part(tmp_path):
    clk = Clock()
    d = tmp_path / "aud"
    r = recording.Recorder(d, 0, cid="c_cd", kind="audio", clock=clk)
    clk.t += 0.5
    r.on_mic(b"\x00\x10" * 8000)
    r.on_agent_audio(b"\x00\x20" * 12000)
    r.close()
    out = recording.compose_part(d, 0)
    assert out["path"].endswith(".m4a")
    assert [s["codec_type"] for s in _probe(out["path"])["streams"]] == ["audio"]


# ---------------------------------------------------------------- API
def _pid(c, key):
    return c.get("/v1/personas", headers=H(key)).json()[0]["id"]


def test_privacy_defaults_update_validation_audit_and_ownership(env):
    c, key, _ = env
    pid = _pid(c, key)
    d = c.get(f"/v1/personas/{pid}/privacy", headers=H(key)).json()
    assert (d["record_conversations"], d["zero_data_retention"], d["ai_disclosure"]) == (False, False, "badge")
    r = c.put(f"/v1/personas/{pid}/privacy", json={"record_conversations": True, "ai_disclosure": "spoken"}, headers=H(key)).json()
    assert r["record_conversations"] is True and r["ai_disclosure"] == "spoken"
    assert c.put(f"/v1/personas/{pid}/privacy", json={"ai_disclosure": "loud"}, headers=H(key)).status_code == 422
    log = c.get("/v1/audit", headers=H(key)).json()
    assert any(e["action"] == "privacy.updated" and "record_conversations=True" in e["detail"] for e in log)
    r = c.put(f"/v1/personas/{pid}/privacy", json={"zero_data_retention": True}, headers=H(key)).json()
    assert r["recording_active"] is False and any("Zero data retention" in n for n in r["notes"])
    other = c.post("/v1/signup", json={"email": "other@b.c"}).json()["api_key"]
    assert c.get(f"/v1/personas/{pid}/privacy", headers=H(other)).status_code == 404
    assert c.put(f"/v1/personas/{pid}/privacy", json={"record_conversations": False}, headers=H(other)).status_code == 404


def test_recording_endpoint_404_when_not_recorded(env):
    c, key, cid = env
    assert c.get(f"/v1/conversations/{cid}/recording", headers=H(key)).status_code == 404
    assert c.get("/v1/conversations/c_000000000000/recording", headers=H(key)).status_code == 404


def test_default_ready_event_shows_the_ai_badge_and_no_recording(env):
    c, key, cid = env
    with c.websocket_connect(f"/v1/conversations/{cid}/stream?api_key={key}") as ws:
        ready = ws.receive_json()
    assert ready["type"] == "ready" and ready["ai_disclosure"] == "badge" and ready["recording"] is False
    assert ready["zero_data_retention"] is False


@needs_ffmpeg
def test_recorded_call_end_to_end(env):
    c, key, _ = env
    pid = _pid(c, key)
    c.put(f"/v1/personas/{pid}/privacy", json={"record_conversations": True, "ai_disclosure": "spoken"}, headers=H(key))
    c.post("/v1/webhooks", json={"url": "http://x.test/h", "events": ["conversation.recording_ready"]}, headers=H(key))
    cc = c.post("/v1/conversations", json={"persona_id": pid}, headers=H(key)).json()["id"]
    with c.websocket_connect(f"/v1/conversations/{cc}/stream?api_key={key}") as ws:
        ready = ws.receive_json()
        assert ready["recording"] is True and ready["ai_disclosure"] == "spoken"
        opening = collect(ws, "agent_done")  # disclosure + recording notice, spoken before anything else
        assert any("I'm an AI assistant" in m["text"] and "being recorded" in m["text"] for m in opening if m.get("text"))
        speak(ws)
        collect(ws, "agent_done")
    recording.wait_all(60)
    rec = c.get(f"/v1/conversations/{cc}/recording", headers=H(key)).json()
    assert rec["status"] == "ready", rec
    assert rec["kind"] == "audio" and rec["duration_s"] > 0 and rec["parts"] == 1
    f = c.get(rec["recording_url"])
    assert f.status_code == 200 and f.headers["content-type"].startswith("audio/mp4") and len(f.content) > 500
    v = c.get(rec["captions_url"]).text
    assert v.startswith("WEBVTT") and "hello there" in v and "being recorded" in v
    assert c.get(f"/v1/files/recordings/{cc}/recording.m4a").status_code == 403  # unsigned
    signed = c.post("/v1/files/sign", json={"path": f"/v1/files/recordings/{cc}/recording.m4a"}, headers=H(key))
    assert signed.status_code == 200 and c.get(signed.json()["url"]).status_code == 200
    other = c.post("/v1/signup", json={"email": "o2@b.c"}).json()["api_key"]
    assert c.post("/v1/files/sign", json={"path": f"/v1/files/recordings/{cc}/recording.m4a"}, headers=H(other)).status_code == 404
    from app.models_features import WebhookDelivery

    with Session(db.engine) as s:
        assert s.exec(select(WebhookDelivery).where(WebhookDelivery.event == "conversation.recording_ready")).first()
    assert c.delete(f"/v1/conversations/{cc}/recording", headers=H(key)).json() == {"deleted": True}
    assert c.get(f"/v1/conversations/{cc}/recording", headers=H(key)).status_code == 404
    assert not recording.rec_dir(jobs.DATA_DIR, cc).exists()


@needs_ffmpeg
def test_account_deletion_removes_recordings(env):
    c, key, _ = env
    pid = _pid(c, key)
    c.put(f"/v1/personas/{pid}/privacy", json={"record_conversations": True}, headers=H(key))
    cc = c.post("/v1/conversations", json={"persona_id": pid}, headers=H(key)).json()["id"]
    with c.websocket_connect(f"/v1/conversations/{cc}/stream?api_key={key}") as ws:
        ws.receive_json()
        collect(ws, "agent_done")  # the recording notice
    recording.wait_all(60)
    assert recording.rec_dir(jobs.DATA_DIR, cc).exists()
    r = c.post("/v1/account/delete-my-data", json={"confirm": "delete-my-data"}, headers=H(key))
    assert r.status_code == 200
    assert not recording.rec_dir(jobs.DATA_DIR, cc).exists()
    with Session(db.engine) as s:
        assert s.get(ConversationRecording, cc) is None


def test_zero_data_retention_keeps_no_content(env):
    c, key, _ = env
    pid = _pid(c, key)
    c.put(f"/v1/personas/{pid}/config", json={"objectives": [{"name": "greet", "description": "Say hello",
                                                               "output_variables": ["word"]}]}, headers=H(key))
    c.put(f"/v1/personas/{pid}/privacy", json={"zero_data_retention": True, "record_conversations": True}, headers=H(key))

    async def judge(system, prompt):
        if "evaluator" in system:
            return '{"objectives":[{"name":"greet","completed":true,"evidence":"user said hello there","variables":{"word":"hello"}}]}'
        return "A summary that must not be stored."

    lb.set_completer(judge)
    cc = c.post("/v1/conversations", json={"persona_id": pid}, headers=H(key)).json()["id"]
    with c.websocket_connect(f"/v1/conversations/{cc}/stream?api_key={key}") as ws:
        ready = ws.receive_json()
        assert ready["zero_data_retention"] is True and ready["recording"] is False
        speak(ws)
        collect(ws, "agent_done")
    import time

    deadline = time.time() + 5  # the in-call objective judge runs in the background
    while time.time() < deadline:
        with Session(db.engine) as s:
            if s.exec(select(ObjectiveProgress).where(ObjectiveProgress.conversation_id == cc)).first():
                break
        time.sleep(0.05)
    assert c.get(f"/v1/conversations/{cc}/transcript", headers=H(key)).json()["turns"] == []
    assert c.post(f"/v1/conversations/{cc}/end", headers=H(key)).status_code == 200
    assert not c.get(f"/v1/conversations/{cc}/summary", headers=H(key)).json()["summary"]
    assert c.get(f"/v1/personas/{pid}/memories", headers=H(key)).json() == []
    assert c.get(f"/v1/conversations/{cc}/recording", headers=H(key)).status_code == 404
    with Session(db.engine) as s:
        assert s.exec(select(TranscriptTurn).where(TranscriptTurn.conversation_id == cc)).all() == []
        o = s.exec(select(ObjectiveProgress).where(ObjectiveProgress.conversation_id == cc)).first()
        assert o is not None and o.completed and o.evidence == "" and json.loads(o.variables) == {}


@needs_ffmpeg
def test_provenance_tags_generated_video_and_recording(tmp_path):
    from app import provenance

    src = tmp_path / "v.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=64x48:rate=25:duration=1",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-shortest", str(src)], check=True)
    size_before = src.stat().st_size
    assert provenance.tag_mp4(src, "generated")
    tags = provenance.read_tags(src)
    assert "AI-generated" in tags.get("comment", "") and tags.get("vocalface_provenance") == "generated"
    assert abs(src.stat().st_size - size_before) < 4096  # a stream copy, not a re-encode
    assert provenance.tag_mp4(tmp_path / "missing.mp4") is False


@needs_ffmpeg
def test_finished_recording_is_tagged(env):
    c, key, _ = env
    pid = _pid(c, key)
    c.put(f"/v1/personas/{pid}/privacy", json={"record_conversations": True}, headers=H(key))
    cc = c.post("/v1/conversations", json={"persona_id": pid}, headers=H(key)).json()["id"]
    with c.websocket_connect(f"/v1/conversations/{cc}/stream?api_key={key}") as ws:
        ws.receive_json()
        collect(ws, "agent_done")
    recording.wait_all(60)
    from app import provenance

    final = recording.final_path(jobs.DATA_DIR, cc, "audio")
    assert final.exists() and provenance.read_tags(final).get("vocalface_provenance") == "recording"


def _protect_run(notice_chunks: int, feed_quiet: int):
    """Session-level: a protected notice of `notice_chunks` x 0.2 s; the user talks over it for 0.6 s, then is quiet."""
    from app.pipeline.session import Session

    from .test_realtime import LOUD, QUIET

    events = []

    async def sj(m):
        events.append(("json", m.get("type"), m.get("text")))

    async def sb(b):
        events.append(("bytes", len(b), None))

    class Stt:
        async def transcribe(self, pcm, sr):
            return "hello there"

    class Llm:
        async def stream(self, system, history, user):
            yield "Hi, how can I help?"

    class Tts:
        async def synthesize(self, text, voice):
            for _ in range(notice_chunks if "recorded" in text else 2):
                await asyncio.sleep(0.005)
                yield b"\x01\x00" * 4800

    prov = type("P", (), {"stt": Stt(), "llm": Llm(), "tts": Tts()})()

    async def run():
        sess = Session(prov, "sys", "v", sj, sb)
        sess.protect_reply = True
        await sess.say("This conversation is being recorded.")
        await asyncio.sleep(0.05)
        for _ in range(30):  # the user talks over the notice (600 ms)
            await sess.feed(LOUD)
        # then quiet, streamed like a real client (the mic never stops sending): the turn ends while the notice is
        # still playing, and the answer has to come after it
        for _ in range(feed_quiet):
            await sess.feed(QUIET)
            await asyncio.sleep(0.004)
            if sum(1 for e in events if e[1] == "agent_done") >= 2:
                break
        return sess

    asyncio.run(run())
    return events


@pytest.fixture()
def _no_echo_model(monkeypatch):
    """The echo model rightly treats a synthetic square wave during agent audio as echo; these tests need it to be 'speech'."""
    from app.pipeline import echo, session as sess_mod
    from app.pipeline.session import Providers

    monkeypatch.setattr(echo, "ENABLED", False)
    sess_mod.set_provider_factory(lambda spec="": Providers(None, None, None))  # => the dependency-free energy VAD
    yield
    sess_mod.set_provider_factory(None)


def test_protected_notice_is_never_cut_off_and_the_user_is_answered_after_it(_no_echo_model):
    ev = _protect_run(notice_chunks=15, feed_quiet=1500)  # 3 s notice; the turn ends while it is still playing
    kinds = [e[1] for e in ev if e[0] == "json"]
    texts = [e[2] for e in ev if e[0] == "json" and e[1] == "transcript"]
    assert "interrupted" not in kinds
    assert texts[0] == "This conversation is being recorded."  # the notice reached the transcript in full
    assert texts[1:3] == ["hello there", "Hi, how can I help?"]  # and the user's turn was answered after it


def test_unprotected_greeting_can_still_be_interrupted(_no_echo_model):
    from app.pipeline.session import Session

    from .test_realtime import LOUD

    events = []

    async def sj(m):
        events.append(m.get("type"))

    async def sb(b):
        pass

    class Tts:
        async def synthesize(self, text, voice):
            for _ in range(40):
                await asyncio.sleep(0.01)
                yield b"\x01\x00" * 4800

    prov = type("P", (), {"stt": None, "llm": None, "tts": Tts()})()

    async def run():
        sess = Session(prov, "sys", "v", sj, sb)
        await sess.say("Welcome to our store, let me tell you about everything we sell.")
        await asyncio.sleep(0.05)
        for _ in range(30):
            await sess.feed(LOUD)
        await asyncio.sleep(0.05)

    asyncio.run(run())
    assert "interrupted" in events
