/** Public origin of the marketing site: canonical links, sitemap, robots.txt, Open Graph and JSON-LD all use it.
 *  A production build without NEXT_PUBLIC_SITE_URL must never advertise localhost (the live site did exactly that in
 *  October 2026: canonical, sitemap and share images all pointed at http://localhost:3000), so production builds fall back to
 *  the real domain and only `next dev` uses localhost. */
const PRODUCTION_ORIGIN = "https://vocalface.com";

export const SITE = (process.env.NEXT_PUBLIC_SITE_URL || (process.env.NODE_ENV === "production" ? PRODUCTION_ORIGIN : "http://localhost:3000"))
  .trim()
  .replace(/\/+$/, "");
