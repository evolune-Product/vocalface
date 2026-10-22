# VocalFace MCP server

Lets AI assistants (Claude Code, Claude Desktop, Cursor, or any MCP client) build and run VocalFace agents: create a persona, give it knowledge, open a face-to-face talk link, read transcripts, make talking-head videos and set privacy controls.

## Install

```bash
pip install ./sdk/python ./sdk/mcp      # from a checkout of this repository (Python 3.10+)
```

Works with the MCP Python SDK 1.x and 2.x.

## Configure

The server needs an API key from the VocalFace dashboard (Dashboard, API keys). It talks to `https://api.vocalface.com` unless `VOCALFACE_API_URL` points elsewhere (for example a self-hosted `http://localhost:8000`). A read-only key is enough for listing and reading.

**Claude Code**

```bash
claude mcp add vocalface -e VOCALFACE_API_KEY=mk_... -- vocalface-mcp
```

**Claude Desktop / Cursor** (`claude_desktop_config.json` or `.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "vocalface": {
      "command": "vocalface-mcp",
      "env": { "VOCALFACE_API_KEY": "mk_...", "VOCALFACE_API_URL": "https://api.vocalface.com" }
    }
  }
}
```

## Tools

| Tool | What it does |
|---|---|
| `list_personas` | The account's agents: id, name, face, voice, model |
| `create_persona` | New agent from a name and a system prompt; optional face (`replica_id`), voice and greeting |
| `add_knowledge` | A text document the agent answers from, with citations |
| `create_talk_link` | A link anyone can open to talk to the agent face to face; per-call minutes and expiry capped |
| `list_conversations` | Recent conversations |
| `get_transcript` | What was said, plus the summary |
| `list_replicas` | Faces on the account |
| `create_video`, `get_video` | Script in, talking-head video out (uses video credits) |
| `get_usage` | Remaining conversation credits |
| `set_privacy` | Recording, zero data retention, AI disclosure |

API errors come back as `{"error": "VocalFace API error 404: ..."}` so the assistant can explain or retry. The server never deletes anything.

## Example prompt

> Create a VocalFace persona called Maya who answers questions about our pricing page, add this text as her knowledge, and give me a talk link that expires in two hours.
