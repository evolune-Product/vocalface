import type { MetadataRoute } from "next";
const site = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";
// Public marketing pages are open to search and AI crawlers on purpose (answer engines can only cite what they can read).
// /pitch is not disallowed here: it carries a noindex tag, and crawlers must be able to fetch the page to see that.
const AI = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "CCBot"];
export default function robots(): MetadataRoute.Robots {
  const priv = ["/dashboard", "/signup", "/api/"];
  return { rules: [{ userAgent: "*", allow: "/", disallow: priv }, ...AI.map((userAgent) => ({ userAgent, allow: "/", disallow: priv }))], sitemap: `${site}/sitemap.xml`, host: site };
}
