import fs from "fs";
import path from "path";
import { SITE } from "@/lib/site";
import { JsonLd } from "@/lib/seo";

// Drop the recorded demo into web/public/demo/: vocalface-demo.mp4 (required), poster.jpg (recommended) and, optionally,
// demo.json {"title", "description", "duration": "PT1M20S", "uploadDate": "2026-10-30", "caption": "..."}. Until the mp4
// exists this renders nothing, so the landing page never shows an empty player.
const DIR = path.join(process.cwd(), "public", "demo");

function demo() {
  const mp4 = path.join(DIR, "vocalface-demo.mp4");
  if (!fs.existsSync(mp4)) return null;
  let meta: Record<string, string> = {};
  try { meta = JSON.parse(fs.readFileSync(path.join(DIR, "demo.json"), "utf8")); } catch { /* optional */ }
  const poster = fs.existsSync(path.join(DIR, "poster.jpg")) ? "/demo/poster.jpg" : undefined;
  return {
    src: "/demo/vocalface-demo.mp4", poster,
    title: meta.title || "VocalFace live demo: a face-to-face conversation with an AI agent",
    description: meta.description || "An unedited live conversation with a VocalFace agent: speech in, answer, voice and a talking face out.",
    caption: meta.caption || "Unedited live session. Hardware and region are stated in the video.",
    duration: meta.duration, uploadDate: meta.uploadDate || fs.statSync(mp4).mtime.toISOString().slice(0, 10),
  };
}

export default function DemoVideo() {
  const d = demo();
  if (!d) return null;
  const ld = { "@context": "https://schema.org", "@type": "VideoObject", name: d.title, description: d.description,
    contentUrl: `${SITE}${d.src}`, uploadDate: d.uploadDate, ...(d.poster ? { thumbnailUrl: `${SITE}${d.poster}` } : {}),
    ...(d.duration ? { duration: d.duration } : {}), publisher: { "@type": "Organization", name: "VocalFace" } };
  return (
    <section id="demo" aria-label="Live demo" className="bg-ink px-5 pb-16">
      <JsonLd data={ld} />
      <div className="mx-auto max-w-4xl">
        <video className="w-full rounded-3xl border border-white/10 bg-black" controls preload="metadata" playsInline poster={d.poster} src={d.src}>
          <a href={d.src}>Watch the demo video</a>
        </video>
        <p className="mt-3 text-center text-xs text-gray-400">{d.caption}</p>
      </div>
    </section>
  );
}
