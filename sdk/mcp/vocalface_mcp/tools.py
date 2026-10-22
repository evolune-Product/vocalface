"""The MCP tools as plain functions over the Python SDK, so they can be tested without an MCP runtime.

Every function takes a `VocalFace` client first and returns JSON-serialisable data that is short enough for a chat:
long fields are trimmed and lists are capped. Nothing here deletes data or spends money beyond what the tool says
(create_video uses video credits).
"""
from __future__ import annotations

from typing import Any, Optional


def _persona_row(p: dict) -> dict:
    return {"id": p["id"], "name": p["name"], "replica_id": p.get("replica_id"), "voice": p.get("tts_voice"),
            "llm": p.get("llm")}


def list_personas(vf) -> list[dict]:
    return [_persona_row(p) for p in vf.list_personas()][:100]


def create_persona(vf, name: str, system_prompt: str, replica_id: Optional[str] = None, voice: Optional[str] = None,
                   greeting: Optional[str] = None) -> dict:
    kw: dict[str, Any] = {}
    if voice:
        kw["tts_voice"] = voice
    p = vf.create_persona(name, system_prompt, replica_id=replica_id, **kw)
    if greeting:
        vf.set_persona_config(p["id"], greeting=greeting)
    return {**_persona_row(p), "greeting": greeting or ""}


def add_knowledge(vf, persona_id: str, title: str, text: str) -> dict:
    d = vf.add_knowledge_text(persona_id, title, text)
    return {"doc_id": d.get("id"), "title": d.get("title", title), "chunks": d.get("n_chunks")}


def create_talk_link(vf, persona_id: str, label: str = "", max_minutes: float = 10, expires_hours: Optional[float] = 24) -> dict:
    """A guest page anyone with the link can open to talk to the persona face to face, with usage caps."""
    opts: dict[str, Any] = {"label": label[:80], "max_seconds": int(max(1, min(max_minutes, 60)) * 60)}
    if expires_hours:
        opts["expires_in_hours"] = float(expires_hours)
    link = vf.create_share_link(persona_id, **opts)
    return {"url": link["url"], "token": link["token"], "max_seconds": link["max_seconds"], "expires_at": link.get("expires_at"),
            "note": "Open the URL in Chrome or Safari, allow the microphone, and press Start conversation."}


def list_conversations(vf, limit: int = 20) -> list[dict]:
    rows = sorted(vf.list_conversations(), key=lambda c: c.get("started_at") or "", reverse=True)
    return [{"id": c["id"], "persona_id": c["persona_id"], "status": c["status"], "started_at": c.get("started_at"),
             "seconds_used": c.get("seconds_used", 0)} for c in rows[: max(1, min(limit, 100))]]


def get_transcript(vf, conversation_id: str, max_chars: int = 12000) -> dict:
    t = vf.get_transcript(conversation_id)
    lines = [f"{'User' if x['role'] == 'user' else 'Agent'}: {x['text']}" for x in t.get("turns", [])]
    text = "\n".join(lines)
    return {"conversation_id": conversation_id, "turns": len(lines), "summary": t.get("summary", ""),
            "transcript": text[-max_chars:], "truncated": len(text) > max_chars}


def list_replicas(vf) -> list[dict]:
    return [{"id": r["id"], "name": r["name"], "status": r["status"]} for r in vf.list_replicas()][:100]


def create_video(vf, replica_id: str, script: str) -> dict:
    """Script in, talking-head video out (rendered in the background; poll get_video)."""
    v = vf.create_video(replica_id, script[:5000])
    return {"video_id": v["id"], "status": v["status"]}


def get_video(vf, video_id: str) -> dict:
    v = vf.get_video(video_id)
    out = {"video_id": v["id"], "status": v["status"]}
    if v.get("output_url"):
        out["url"] = v["output_url"]
    return out


def get_usage(vf) -> dict:
    u = vf.usage()
    return {"credits_seconds": u.get("credits_seconds"), "credits_minutes": round((u.get("credits_seconds") or 0) / 60, 1)}


def set_privacy(vf, persona_id: str, record_conversations: Optional[bool] = None, zero_data_retention: Optional[bool] = None,
                ai_disclosure: Optional[str] = None) -> dict:
    body = {k: v for k, v in {"record_conversations": record_conversations, "zero_data_retention": zero_data_retention,
                              "ai_disclosure": ai_disclosure}.items() if v is not None}
    p = vf.set_privacy(persona_id, **body)
    return {k: p[k] for k in ("persona_id", "record_conversations", "zero_data_retention", "ai_disclosure", "recording_active", "notes")}
