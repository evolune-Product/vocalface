# Search, answer-engine and AI-search visibility (SEO / AEO / GEO)

Nobody can promise a ranking. What the site does: be fully crawlable, say clearly what VocalFace is, and answer the questions people ask. Everything below that needs your accounts is the part that actually moves rankings.

## Built into the site
- Per-page titles, descriptions, canonical URLs, Open Graph and Twitter cards; a branded share image.
- Structured data (JSON-LD): Organization (with parent Evolune EdgeTech LLP), WebSite, SoftwareApplication, FAQPage on home / alternatives / guide, BreadcrumbList, Article.
- `robots.txt` allows search and AI crawlers (GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, Applebot-Extended and others) and blocks only /dashboard, /signup and /api. `/pitch` is `noindex` and not in the sitemap.
- `sitemap.xml` lists every public page with priorities.
- `public/llms.txt`: a plain summary for AI answer engines (what it is, who it is for, honest limits, key pages).
- Intent pages: `/alternatives/<tavus|heygen|d-id|synthesia>`, `/alternatives`, `/guides/what-is-conversational-video-ai`, `/compare`. These target "X alternative", "open source AI avatar" and "what is conversational video AI".
- Honest wording on purpose: search and AI engines, and investors, reward claims that are checkable.

## October 22 2026 additions
- **Fixed a live bug:** vocalface.com was built without `NEXT_PUBLIC_SITE_URL`, so canonical links, the sitemap, robots.txt, share images and JSON-LD all pointed at `http://localhost:3000` (Google cannot use any of them). `web/lib/site.ts` now falls back to `https://vocalface.com` in every production build. The live server must be rebuilt and redeployed for the fix to take effect; then re-submit the sitemap in Search Console.
- New pages: alternatives for Anam, Simli, LemonSlice and Beyond Presence; the buyer's guide `/guides/choosing-a-real-time-ai-avatar-api` (FAQ + Article JSON-LD, sources cited); `/docs/mcp`.
- Per-page share images for alternatives and guides (`opengraph-image.tsx`), a curated changelog with an RSS feed (`/changelog/rss.xml`), homepage FAQ answers for recordings, AI disclosure and MCP.
- A demo-video slot (`web/components/site/DemoVideo.tsx`): drop `web/public/demo/vocalface-demo.mp4` (+ `poster.jpg`, optional `demo.json`) and the landing page shows it with VideoObject structured data.
- IndexNow: the key file `web/public/3107ea5174655a05ff476d4710f37c77.txt` ships with the site; after each deploy run `node web/scripts/indexnow.mjs` to tell Bing (and the AI products it feeds) about every URL in the sitemap.
- Not done on purpose: no "open source" claims in new pages, because the repository has no licence file yet (see the open decision in the October 22 report).

## You must do these (needs your accounts)
1. **Deploy on the real domain.** `NEXT_PUBLIC_SITE_URL=https://vocalface.com` (already in `netlify.toml`). Canonicals and the sitemap use it.
2. **Google Search Console**: add the domain, verify (set `NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION` in Netlify or use DNS), submit `https://vocalface.com/sitemap.xml`, then "Request indexing" for `/`, `/alternatives`, the guide.
3. **Bing Webmaster Tools**: import from Search Console (set `NEXT_PUBLIC_BING_SITE_VERIFICATION` if asked). Bing feeds several AI search products.
4. **GitHub repo**: set the description and topics (`conversational-ai`, `ai-avatar`, `video-generation`, `digital-human`, `lip-sync`, `voice-cloning`, `self-hosted`, `open-source`, `tavus-alternative`) and add the website URL `https://vocalface.com`.
5. **Backlinks** (the biggest ranking factor, and ours is zero): launch on Product Hunt, Hacker News (Show HN), r/selfhosted, r/LocalLLaMA, AlternativeTo (list VocalFace as an alternative to Tavus, HeyGen, D-ID), awesome-lists on GitHub, Dev.to or Hashnode write-ups, and your Inception / Claude for Startups directory listings if they offer one.
6. **Brand consistency**: use the same name, one-line description and logo on LinkedIn, X, GitHub and the company page. Link each back to the site.
7. **Ship content regularly**: one honest benchmark post (for example the GPU latency test) is worth more than any tag. Add it under `/docs` or a `/blog`.

## Check after launch
- Search Console: coverage, queries, impressions (takes weeks).
- Rich Results Test and Schema Markup Validator on `/` and an alternatives page.
- Ask ChatGPT, Claude, Perplexity and Google "open source Tavus alternative" monthly and record whether VocalFace is cited.
- Keep competitor pages accurate. They are based on public positioning, not testing; recheck before editing.
