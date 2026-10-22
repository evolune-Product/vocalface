"""The MCP server's tools (sdk/mcp/vocalface_mcp/tools.py) against the real API, without an MCP runtime."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sdk" / "python"))
sys.path.insert(0, str(ROOT / "sdk" / "mcp"))
from vocalface_mcp import tools  # noqa: E402
from vocalface_sdk import VocalFace  # noqa: E402

from .test_api import client  # noqa: E402,F401


def test_mcp_tools_flow(client):
    vf = VocalFace(http_client=client)
    vf.signup("mcp@x.com")
    p = tools.create_persona(vf, "Maya", "You are Maya, a friendly product guide.", greeting="Hi, I'm Maya!")
    assert p["name"] == "Maya" and p["greeting"] == "Hi, I'm Maya!"
    assert vf.get_persona_config(p["id"])["greeting"] == "Hi, I'm Maya!"
    assert [x["id"] for x in tools.list_personas(vf)] == [p["id"]]
    k = tools.add_knowledge(vf, p["id"], "Pricing", "The Pro plan is $79 a month.")
    assert k["doc_id"]
    link = tools.create_talk_link(vf, p["id"], label="demo", max_minutes=120, expires_hours=2)
    assert "/guest/sh_" in link["url"] and link["max_seconds"] == 3600  # capped at 60 minutes
    c = vf.create_conversation(p["id"])
    assert tools.list_conversations(vf, limit=5)[0]["id"] == c["id"]
    t = tools.get_transcript(vf, c["id"])
    assert t == {"conversation_id": c["id"], "turns": 0, "summary": "", "transcript": "", "truncated": False}
    assert tools.get_usage(vf)["credits_minutes"] == 10.0
    priv = tools.set_privacy(vf, p["id"], record_conversations=True, ai_disclosure="spoken")
    assert priv["record_conversations"] is True and priv["ai_disclosure"] == "spoken"
    assert tools.list_replicas(vf) == []
