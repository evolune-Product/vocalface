"""Persona privacy policy: conversation recording, zero data retention and AI disclosure.

AI disclosure follows the transparency idea in Article 50 of the EU AI Act (people should know they are talking to an AI):
'badge' shows an on-screen notice in every VocalFace client, 'spoken' also has the agent say one sentence before its
greeting, 'off' leaves disclosure to the customer. This is a product control, not legal advice.

Zero data retention always wins over recording: a persona with both switched on records nothing.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

log = logging.getLogger("vocalface.privacy")

DISCLOSURES = ("off", "badge", "spoken")
SPOKEN_DISCLOSURE = "Just so you know, I'm an AI assistant."
RECORDING_NOTICE = "This conversation is being recorded."


@dataclass(frozen=True)
class Policy:
    record: bool = False
    announce: bool = True
    zdr: bool = False
    disclosure: str = "badge"

    @property
    def recording(self) -> bool:
        return self.record and not self.zdr

    @property
    def retain(self) -> bool:
        return not self.zdr


DEFAULT = Policy()


def ensure(engine=None) -> None:
    from sqlmodel import SQLModel

    from . import db
    from .models_privacy import ConversationRecording, PersonaPrivacy

    SQLModel.metadata.create_all(engine or db.engine, tables=[PersonaPrivacy.__table__, ConversationRecording.__table__])


def load(s, persona_id: str) -> Policy:
    """The persona's policy, or the defaults. Never raises: a broken lookup must not block a call (it falls back to the
    defaults, which record nothing)."""
    try:
        from .models_privacy import PersonaPrivacy

        row = s.get(PersonaPrivacy, persona_id)
    except Exception:  # noqa: BLE001 - e.g. table missing on an old database
        try:
            ensure()
            from .models_privacy import PersonaPrivacy

            row = s.get(PersonaPrivacy, persona_id)
        except Exception:  # noqa: BLE001
            log.exception("privacy policy lookup failed; using defaults")
            return DEFAULT
    if row is None:
        return DEFAULT
    disclosure = row.ai_disclosure if row.ai_disclosure in DISCLOSURES else "badge"
    return Policy(bool(row.record_conversations), bool(row.announce_recording), bool(row.zero_data_retention), disclosure)


def opening_lines(p: Policy) -> str:
    """Spoken before the persona's greeting (or alone, when the persona has none)."""
    parts = []
    if p.disclosure == "spoken":
        parts.append(SPOKEN_DISCLOSURE)
    if p.recording and p.announce:
        parts.append(RECORDING_NOTICE)
    return " ".join(parts)


def client_flags(p: Policy, recording_active: bool) -> dict:
    """Additive fields for the realtime `ready` event; clients show the AI badge and the recording indicator from them."""
    return {"ai_disclosure": p.disclosure, "recording": bool(recording_active), "zero_data_retention": p.zdr}
