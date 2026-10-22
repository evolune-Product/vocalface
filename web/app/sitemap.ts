import type { MetadataRoute } from "next";
import { useCases } from "@/lib/usecases";
import { docPages } from "@/lib/docs";
import { alternatives } from "@/lib/alternatives";
import { SITE as site } from "@/lib/site";
// /pitch is deliberately left out (noindex, shared by link).
export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date();
  const hi = ["/", "/alternatives", "/guides/what-is-conversational-video-ai", "/guides/choosing-a-real-time-ai-avatar-api", "/compare", "/pricing"];
  const paths = ["/", "/pricing", "/docs", "/use-cases", "/security", "/about", "/changelog", "/compare", "/alternatives", "/guides/what-is-conversational-video-ai", "/guides/choosing-a-real-time-ai-avatar-api", "/terms", "/privacy",
    ...alternatives.map((a) => `/alternatives/${a.slug}`), ...docPages.map((d) => `/docs/${d.slug}`), ...useCases.map((u) => `/use-cases/${u.slug}`)];
  return paths.map((p) => ({ url: `${site}${p}`, lastModified, changeFrequency: "weekly", priority: p === "/" ? 1 : hi.includes(p) ? 0.8 : 0.6 }));
}
