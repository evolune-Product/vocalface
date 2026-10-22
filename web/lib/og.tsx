import { ImageResponse } from "next/og";
import { readFileSync } from "fs";
import { join } from "path";

export const OG_SIZE = { width: 1200, height: 630 };

/** Share card in the site's style: emblem on the right, a kicker, a headline and one line underneath. */
export function ogCard(kicker: string, headline: string, sub: string) {
  const emblem = `data:image/png;base64,${readFileSync(join(process.cwd(), "public/brand/emblem-og.png")).toString("base64")}`;
  const size = headline.length > 48 ? 60 : 72;
  return new ImageResponse(
    (<div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", padding: 80, background: "#090b10", color: "#fff", position: "relative" }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={emblem} width={520} height={260} alt="" style={{ position: "absolute", right: 30, top: 170, opacity: 0.9 }} />
      <div style={{ fontSize: 34, color: "#7dd3fc", display: "flex" }}>{kicker}</div>
      <div style={{ fontSize: size, lineHeight: 1.05, marginTop: 22, maxWidth: 680, display: "flex" }}>{headline}</div>
      <div style={{ fontSize: 28, color: "#b9b5c7", marginTop: 30, maxWidth: 700, display: "flex" }}>{sub}</div>
    </div>), OG_SIZE);
}
