import { commits } from "@/lib/commits";
import { SITE } from "@/lib/site";

export const dynamic = "force-static";
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

export function GET() {
  const items = [...commits].reverse().map(([h, d, s]) =>
    `<item><title>${esc(s)}</title><link>${SITE}/changelog#${h}</link><guid isPermaLink="false">vocalface-${h}</guid>` +
    `<pubDate>${new Date(`${d}T12:00:00Z`).toUTCString()}</pubDate><description>${esc(s)}</description></item>`).join("");
  const xml = `<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>` +
    `<title>VocalFace changelog</title><link>${SITE}/changelog</link><description>Product changes to VocalFace, newest first.</description>` +
    `<language>en</language><atom:link href="${SITE}/changelog/rss.xml" rel="self" type="application/rss+xml"/>${items}</channel></rss>`;
  return new Response(xml, { headers: { "content-type": "application/rss+xml; charset=utf-8" } });
}
