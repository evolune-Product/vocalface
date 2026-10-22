"""Privacy controls per persona, and conversation recordings.

GET    /v1/personas/{pid}/privacy          policy (defaults when never set) + whether this server can record
PUT    /v1/personas/{pid}/privacy          {record_conversations?, announce_recording?, zero_data_retention?, ai_disclosure?}
GET    /v1/conversations/{cid}/recording   {status, kind, duration_s, parts, size_bytes, error, recording_url?, captions_url?}
DELETE /v1/conversations/{cid}/recording   removes the files and the row
GET    /v1/files/recordings/{cid}/recording.mp4 | recording.m4a | captions.vtt   signed links (POST /v1/files/sign)

Zero data retention wins over recording. Changing the policy is written to the audit log.
"""
from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session

from .. import db as dbm, privacy, recording, signing, storage
from ..auth import current_account
from ..db import Account, Conversation, Persona, get_session
from ..models_privacy import ConversationRecording, PersonaPrivacy
from ..safety import audit

router = APIRouter()


class PrivacyIn(BaseModel):
    record_conversations: Optional[bool] = None
    announce_recording: Optional[bool] = None
    zero_data_retention: Optional[bool] = None
    ai_disclosure: Optional[Literal["off", "badge", "spoken"]] = None


def _persona(s: Session, acc: Account, pid: str) -> Persona:
    p = s.get(Persona, pid)
    if not p or p.account_id != acc.id:
        raise HTTPException(404, "persona not found")
    return p


def _out(pid: str, row: Optional[PersonaPrivacy]) -> dict:
    pol = privacy.Policy() if row is None else privacy.Policy(row.record_conversations, row.announce_recording,
                                                               row.zero_data_retention, row.ai_disclosure)
    can = recording.ffmpeg_bin() is not None
    return {"persona_id": pid, "record_conversations": pol.record, "announce_recording": pol.announce,
            "zero_data_retention": pol.zdr, "ai_disclosure": pol.disclosure,
            "recording_active": pol.recording and can,  # what will actually happen on the next call
            "recording_available": can,
            "notes": [n for n in (
                "Zero data retention is on, so conversations are not recorded." if pol.record and pol.zdr else "",
                "This server has no ffmpeg, so nothing can be recorded." if pol.record and not can else "",
                "Tell participants they are recorded: keep announce_recording on unless your own flow does it."
                if pol.recording and not pol.announce else "") if n]}


@router.get("/personas/{pid}/privacy")
def get_privacy(pid: str, acc: Account = Depends(current_account), s: Session = Depends(get_session)):
    _persona(s, acc, pid)
    privacy.ensure(dbm.engine)
    return _out(pid, s.get(PersonaPrivacy, pid))


@router.put("/personas/{pid}/privacy")
def put_privacy(pid: str, body: PrivacyIn, acc: Account = Depends(current_account), s: Session = Depends(get_session)):
    _persona(s, acc, pid)
    privacy.ensure(dbm.engine)
    row = s.get(PersonaPrivacy, pid) or PersonaPrivacy(persona_id=pid, account_id=acc.id)
    changed = {}
    for k, v in body.model_dump(exclude_none=True).items():
        if getattr(row, k) != v:
            changed[k] = v
            setattr(row, k, v)
    from ..db import now

    row.updated_at = now()
    s.add(row)
    s.commit()
    if changed:
        audit(s, acc.id, "privacy.updated", pid, ", ".join(f"{k}={v}" for k, v in sorted(changed.items())))
    s.refresh(row)
    return _out(pid, row)


def _recording_row(s: Session, acc: Account, cid: str) -> ConversationRecording:
    c = s.get(Conversation, cid)
    if not c or c.account_id != acc.id:
        raise HTTPException(404, "conversation not found")
    privacy.ensure(dbm.engine)
    row = s.get(ConversationRecording, cid)
    if row is None:
        raise HTTPException(404, "this conversation was not recorded")
    return row


@router.get("/conversations/{cid}/recording")
def get_recording(cid: str, acc: Account = Depends(current_account), s: Session = Depends(get_session)):
    row = _recording_row(s, acc, cid)
    out = {"conversation_id": cid, "status": row.status, "kind": row.kind, "parts": row.parts, "duration_s": row.duration_s,
           "size_bytes": row.size_bytes, "error": row.error or None, "created_at": row.created_at, "ready_at": row.ready_at}
    if row.status == "ready":
        out["recording_url"] = signing.sign_path(recording.file_route(cid, row.kind))
        out["captions_url"] = signing.sign_path(f"/v1/files/recordings/{cid}/captions.vtt")
    return out


@router.delete("/conversations/{cid}/recording")
def delete_recording(cid: str, acc: Account = Depends(current_account), s: Session = Depends(get_session)):
    row = _recording_row(s, acc, cid)
    from .. import settings

    recording.delete(settings.data_dir(), cid)
    s.delete(row)
    s.commit()
    audit(s, acc.id, "recording.deleted", cid)
    return {"deleted": True}


_FILES = {"recording.mp4": "video/mp4", "recording.m4a": "audio/mp4", "captions.vtt": "text/vtt"}


@router.get("/files/recordings/{cid}/{name}")
def recording_file(cid: str, name: str, request: Request):
    from .. import settings
    from .photo_replica import _ID

    media = _FILES.get(name)
    if not media or not _ID.match(cid):
        raise HTTPException(404, "not found")
    q = request.query_params  # recordings are people's voices and faces: a signed link is required even in development
    if not signing.verify(f"/v1/files/recordings/{cid}/{name}", q.get("exp"), q.get("sig")):
        raise HTTPException(403, "invalid or expired file link" if "sig" in q else "signed link required; call POST /v1/files/sign")
    return storage.serve(recording.rec_dir(settings.data_dir(), cid) / name, media,
                         headers={"Cache-Control": "private, max-age=300"})
