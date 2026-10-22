// Public changelog: product changes in plain language, curated from the git history (internal trials and model
// names are left out on purpose). Newest last; each hash is the commit that shipped it.
export const commits: [string, string, string][] = [
 [
  "9d96f15",
  "2026-10-02",
  "First version: API, accounts, usage metering and the conversation pipeline"
 ],
 [
  "f5e6986",
  "2026-10-02",
  "Local voice loop: speech recognition, a local language model and text-to-speech, streamed sentence by sentence (about 1.5 s to first audio)"
 ],
 [
  "a3fc7f4",
  "2026-10-02",
  "Real-time conversations, dashboard, background workers, knowledge, billing, safety checks and SDKs connected"
 ],
 [
  "e1021fe",
  "2026-10-03",
  "Tested end to end: consent capture, billing page, replica face in the playground, stronger moderation"
 ],
 [
  "3b76149",
  "2026-10-03",
  "New website with pricing, FAQ and live mockups"
 ],
 [
  "972e3b5",
  "2026-10-03",
  "Live lip-synced face streamed over WebSocket"
 ],
 [
  "4d550e2",
  "2026-10-03",
  "Consent verification, security hardening and lower voice latency"
 ],
 [
  "bbe6429",
  "2026-10-03",
  "Faster voice: better turn detection, pipelined speech and preloaded models"
 ],
 [
  "f4fbe7d",
  "2026-10-03",
  "Dashboard for persona settings, transcripts, webhooks, API keys, analytics and bulk video"
 ],
 [
  "b7693af",
  "2026-10-03",
  "Photo avatars, backgrounds, captions, voice cloning, camera perception, database migrations, storage and metrics"
 ],
 [
  "f09e98b",
  "2026-10-03",
  "Licence audit with a commercial-only mode, face-bound consent, onboarding and ready-made agent templates"
 ],
 [
  "06afcc6",
  "2026-10-04",
  "WebSocket security: single-use tickets, connection and message rate limits, per-account session caps"
 ],
 [
  "b284f2e",
  "2026-10-04",
  "Bot-resistant signup"
 ],
 [
  "5b22b35",
  "2026-10-04",
  "Content-Security-Policy and framing rules for every page"
 ],
 [
  "725147f",
  "2026-10-04",
  "Web-page knowledge with citations, pronunciation glossary, interruption tuning and scheduled call links"
 ],
 [
  "9c02ae1",
  "2026-10-04",
  "Sentiment insights and answer citations in the dashboard"
 ],
 [
  "875c941",
  "2026-10-04",
  "New generative face model for videos and photo avatars: whole-face and head motion from audio"
 ],
 [
  "8f1072f",
  "2026-10-05",
  "Automatic tight face crop for photos and video frames"
 ],
 [
  "e695adc",
  "2026-10-07",
  "Mirage is now VocalFace"
 ],
 [
  "15d6f22",
  "2026-10-08",
  "New look to match the VocalFace logo"
 ],
 [
  "8c5bfed",
  "2026-10-12",
  "Comparison pages, a plain-English guide and structured data for search engines and AI assistants"
 ],
 [
  "6cf0205",
  "2026-10-22",
  "Search fix: correct canonical links, sitemap and share images on the live site"
 ],
 [
  "da9e73b",
  "2026-10-22",
  "Privacy controls: opt-in conversation recordings with captions, zero data retention, AI disclosure badge and live captions"
 ],
 [
  "cdec115",
  "2026-10-22",
  "MCP server: build and run agents from Claude, Cursor and other AI assistants"
 ],
 [
  "ede03ba",
  "2026-10-22",
  "Machine-readable AI-generated label in generated videos and recordings"
 ],
 [
  "291b8fc",
  "2026-10-22",
  "Buyer's guide to real-time AI avatar APIs, four more comparison pages and this changelog as an RSS feed"
 ]
];
