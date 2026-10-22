import "./globals.css";
import type { Metadata } from "next";
import { JsonLd, organization, website } from "@/lib/seo";
import { SITE as site } from "@/lib/site";
import { Instrument_Serif, Inter, JetBrains_Mono } from "next/font/google";

const display = Instrument_Serif({ subsets: ["latin"], weight: "400", style: ["normal", "italic"], variable: "--font-display" });
const sans = Inter({ subsets: ["latin"], variable: "--font-sans" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

const desc = "Real-time face-to-face AI agents, digital replicas and video generation. Open-core, self-hostable, built to cost less.";
export const metadata: Metadata = {
  metadataBase: new URL(site),
  title: { default: "VocalFace - conversational video AI you can own", template: "%s" },
  description: desc,
  applicationName: "VocalFace",
  authors: [{ name: "Evolune EdgeTech LLP" }],
  keywords: ["conversational video AI", "AI avatar API", "real-time AI video agent", "digital twin replica", "talking head video generation", "open source AI avatar", "self-hosted video AI", "Tavus alternative", "HeyGen alternative", "voice cloning", "consent-based AI avatar"],
  robots: { index: true, follow: true, googleBot: { index: true, follow: true, "max-image-preview": "large", "max-snippet": -1, "max-video-preview": -1 } },
  verification: { google: process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION, other: process.env.NEXT_PUBLIC_BING_SITE_VERIFICATION ? { "msvalidate.01": process.env.NEXT_PUBLIC_BING_SITE_VERIFICATION } : undefined },
  alternates: { canonical: "/" },
  openGraph: { type: "website", siteName: "VocalFace", title: "VocalFace - conversational video AI you can own", description: desc },
  twitter: { card: "summary_large_image", title: "VocalFace - conversational video AI you can own", description: desc },
};
export const viewport = { themeColor: "#090b10" };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${sans.variable} ${mono.variable}`}>
      <body className="antialiased"><JsonLd data={[organization, website]} />{children}</body>
    </html>
  );
}
