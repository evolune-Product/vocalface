# MCP server: use VocalFace from Claude, Cursor and other AI assistants

VocalFace ships a Model Context Protocol (MCP) server. Any MCP client, such as Claude Code, Claude Desktop or Cursor, can then create and run face-to-face AI agents for you: make a persona, give it knowledge, open a talk link, read the transcript afterwards, render a talking-head video, and set privacy controls.

## Install

```bash
pip install ./sdk/python ./sdk/mcp
```

From a checkout of the VocalFace repository, Python 3.10 or newer. It works with the MCP Python SDK 1.x and 2.x.

## Connect it

Get an API key from the dashboard (API keys). For Claude Code:

```bash
claude mcp add vocalface -e VOCALFACE_API_KEY=mk_... -- vocalface-mcp
```

For Claude Desktop or Cursor, add a server entry with the command `vocalface-mcp` and the environment variables `VOCALFACE_API_KEY` and, for a self-hosted install, `VOCALFACE_API_URL`.

## Tools

- `list_personas`, `create_persona`, `add_knowledge`
- `create_talk_link`: a link anyone can open in a browser to talk to the agent face to face, with per-call and expiry caps
- `list_conversations`, `get_transcript`
- `list_replicas`, `create_video`, `get_video`
- `get_usage`
- `set_privacy`: recording, zero data retention, AI disclosure

Errors come back as readable messages, and the server never deletes data.

## Example

Ask your assistant: "Create a VocalFace persona called Maya who explains our pricing, add this page as her knowledge, and give me a talk link that expires in two hours." It calls `create_persona`, `add_knowledge` and `create_talk_link`, then hands you the link.
