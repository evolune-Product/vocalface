"""stdio MCP server. Configure with VOCALFACE_API_KEY (required) and VOCALFACE_API_URL (default https://api.vocalface.com).

    claude mcp add vocalface -e VOCALFACE_API_KEY=mk_... -- vocalface-mcp
"""
from __future__ import annotations

import functools
import os
from typing import Optional

try:  # MCP Python SDK 2.x
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # 1.x
    from mcp.server.fastmcp import FastMCP as _Server

from . import tools

mcp = _Server("vocalface", instructions=(
    "VocalFace runs real-time, face-to-face AI agents (personas) and makes talking-head videos. Typical flow: "
    "list_personas or create_persona, optionally add_knowledge, then create_talk_link and give the user the URL. "
    "Read what was said with list_conversations and get_transcript."))
_client = None


def vf():
    global _client
    if _client is None:
        from vocalface_sdk import VocalFace

        key = os.environ.get("VOCALFACE_API_KEY", "").strip()
        if not key:
            raise RuntimeError("Set VOCALFACE_API_KEY (an API key from the VocalFace dashboard) in the MCP server's environment.")
        _client = VocalFace(api_key=key, base_url=os.environ.get("VOCALFACE_API_URL", "https://api.vocalface.com").rstrip("/"))
    return _client


def _safe(fn):
    """API errors come back as {"error": "..."} the assistant can read and act on, not as an opaque tool failure."""
    @functools.wraps(fn)
    def inner(*a, **k):
        try:
            return fn(*a, **k)
        except RuntimeError as e:
            return {"error": str(e)}
        except Exception as e:  # noqa: BLE001
            from vocalface_sdk import VocalFaceError

            if isinstance(e, VocalFaceError):
                return {"error": f"VocalFace API error {e.status}: {e.detail}"}
            raise
    return inner


@mcp.tool()
@_safe
def list_personas() -> dict:
    """List the account's personas (agents): id, name, face replica, voice and language model."""
    return {"personas": tools.list_personas(vf())}


@mcp.tool()
@_safe
def create_persona(name: str, system_prompt: str, replica_id: Optional[str] = None, voice: Optional[str] = None,
                   greeting: Optional[str] = None) -> dict:
    """Create a persona. system_prompt says who the agent is and how it talks; replica_id gives it a face (see
    list_replicas); greeting is spoken first when a call starts."""
    return tools.create_persona(vf(), name, system_prompt, replica_id, voice, greeting)


@mcp.tool()
@_safe
def add_knowledge(persona_id: str, title: str, text: str) -> dict:
    """Add a text document the persona can answer from (retrieved during calls, with citations)."""
    return tools.add_knowledge(vf(), persona_id, title, text)


@mcp.tool()
@_safe
def create_talk_link(persona_id: str, label: str = "", max_minutes: float = 10, expires_hours: Optional[float] = 24) -> dict:
    """Make a link anyone can open in a browser to talk to the persona face to face. Capped per call (max_minutes,
    up to 60) and expiring (expires_hours); revoke it from the dashboard."""
    return tools.create_talk_link(vf(), persona_id, label, max_minutes, expires_hours)


@mcp.tool()
@_safe
def list_conversations(limit: int = 20) -> dict:
    """Most recent conversations first: id, persona, status, start time, seconds used."""
    return {"conversations": tools.list_conversations(vf(), limit)}


@mcp.tool()
@_safe
def get_transcript(conversation_id: str) -> dict:
    """What was said in a conversation (User/Agent lines) plus the summary, when there is one."""
    return tools.get_transcript(vf(), conversation_id)


@mcp.tool()
@_safe
def list_replicas() -> dict:
    """Face replicas on the account (made from a consented video or a photo in the dashboard)."""
    return {"replicas": tools.list_replicas(vf())}


@mcp.tool()
@_safe
def create_video(replica_id: str, script: str) -> dict:
    """Render a talking-head video of a replica saying `script` (uses video credits). Poll get_video for the result."""
    return tools.create_video(vf(), replica_id, script)


@mcp.tool()
@_safe
def get_video(video_id: str) -> dict:
    """Status of a video and, when ready, its URL."""
    return tools.get_video(vf(), video_id)


@mcp.tool()
@_safe
def get_usage() -> dict:
    """Remaining conversation credits."""
    return tools.get_usage(vf())


@mcp.tool()
@_safe
def set_privacy(persona_id: str, record_conversations: Optional[bool] = None, zero_data_retention: Optional[bool] = None,
                ai_disclosure: Optional[str] = None) -> dict:
    """Privacy for a persona: record conversations (announced to participants), keep no conversation content
    (zero data retention, wins over recording), and how the agent discloses it is an AI ('off', 'badge', 'spoken')."""
    return tools.set_privacy(vf(), persona_id, record_conversations, zero_data_retention, ai_disclosure)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
