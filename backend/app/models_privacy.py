"""Privacy controls per persona and conversation recordings (new tables only, nothing altered)."""
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Column
from sqlmodel import Field, SQLModel

from .db import now


class PersonaPrivacy(SQLModel, table=True):
    """How a persona treats the people it talks to. No row = the defaults below (no recording, normal retention,
    an on-screen AI badge)."""
    persona_id: str = Field(primary_key=True)
    account_id: str = Field(index=True)
    record_conversations: bool = False   # keep what the participant heard and saw (MP4, or M4A without a face) + captions
    announce_recording: bool = True      # the agent says so first, and every client shows a "Recording" indicator
    zero_data_retention: bool = False    # no transcript, citations, summary, memory, insights, recording or tool arguments kept
    ai_disclosure: str = "badge"         # off | badge | spoken (badge + one spoken sentence before the greeting)
    updated_at: datetime = Field(default_factory=now)


class ConversationRecording(SQLModel, table=True):
    """One recording per conversation. A reconnect adds a part; the file is always all parts joined."""
    conversation_id: str = Field(primary_key=True)
    account_id: str = Field(index=True)
    persona_id: str = Field(index=True)
    status: str = "recording"            # recording | processing | ready | error
    kind: str = "video"                  # video (mp4) | audio (m4a)
    parts: int = 0
    duration_s: float = 0.0
    size_bytes: int = Field(default=0, sa_column=Column(BigInteger, nullable=False, default=0))
    error: str = ""
    created_at: datetime = Field(default_factory=now)
    ready_at: Optional[datetime] = None
