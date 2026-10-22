import Link from "next/link";
import { FinalCTA, It, PageHead, Prose, Shell } from "@/components/site/Page";
import { JsonLd, crumbs, faqLd } from "@/lib/seo";

const path = "/guides/choosing-a-real-time-ai-avatar-api";
const title = "How to choose a real-time AI avatar API in 2026: a buyer's checklist";
const description = "Ten questions that separate a demo from a deployment when you pick a real-time AI avatar or conversational video API: latency, true cost per minute, concurrency, self-hosting, consent, data retention, AI disclosure, integrations and face quality.";
export const metadata = { title: `${title} - VocalFace`, description, alternates: { canonical: path }, openGraph: { title, description, type: "article" } };

const faq = [
  ["What latency should a real-time AI avatar have?", "Measure from the end of the user's speech to the first audio and the first lip movement, on your own network and under load. Vendors publish numbers from under 100 ms to around half a second, but they rarely measure the same thing, and the full loop (speech recognition, language model, voice and face) is what people feel."],
  ["How much does a real-time AI avatar cost per minute?", "Published prices range from a few cents to about a third of a dollar per minute, before your own language model and voice costs. Compare included minutes, overage rates, concurrency caps and minimum billing per conversation, not only the headline price."],
  ["Can I self-host a real-time AI avatar?", "Some platforms are hosted only, a few offer private cloud or on-premises deployment, and open-source frameworks exist. Self-hosting keeps audio, video and transcripts in your environment, but the face model needs a modern NVIDIA GPU for real time."],
  ["Do I have to tell people they are talking to an AI?", "In the EU, Article 50 of the AI Act requires that people are informed when they interact with an AI system unless it is obvious, from 2 August 2026. Look for an on-screen disclosure, an optional spoken one, and machine-readable labels on generated media."],
  ["What should I ask about data retention?", "Ask what is stored after a call (recordings, transcripts, summaries, extracted values), for how long, where, and whether a zero data retention mode exists that keeps none of it."],
] as const;

const qs: [string, string, React.ReactNode][] = [
  ["1", "How fast does it answer, end to end?", <>Ask for time from the end of the user&apos;s speech to the first audio and first lip movement, measured on your network and with several calls running. Vendor numbers (under 100 ms, under 300 ms, around 500 ms) usually describe one stage and are rarely comparable. One study of 178 participants found responsiveness was the strongest predictor of overall experience (<a href="https://meet-cody-website-xr0tt.kinsta.page/blog/real-time-ai-avatar-models-compared/" target="_blank" rel="noreferrer">Cody</a>, a vendor). For reference, our own stack measured 1.4 to 1.9 s from end of speech to first lips on one machine.</>],
  ["2", "What does a minute really cost?", <>Add the avatar price, the language model, the voice, and any minimum per conversation. Compare included minutes, overage rates and what happens when credits run out. For example, Tavus publishes plans with included minutes, per-minute overage of roughly $0.26 to $0.37 depending on the plan, and a 30-second minimum per conversation (<a href="https://www.tavus.io/pricing" target="_blank" rel="noreferrer">tavus.io/pricing</a>, October 2026).</>],
  ["3", "How many conversations can run at once?", <>Concurrency is often capped per plan. Ask for the cap, what a caller sees when it is reached, and how fast capacity grows.</>],
  ["4", "Can you keep data in your own environment?", <>Options run from hosted-only, to private cloud or on-premises, to open-source frameworks you assemble yourself. Self-hosting needs an NVIDIA GPU for a real-time face; the voice path can run on ordinary hardware.</>],
  ["5", "Whose face is it, and can you prove consent?", <>For replicas of real people, ask how consent is captured (a spoken phrase, face and voice matching), how it is revoked, and whether there is an audit log you can show a customer or regulator.</>],
  ["6", "What is kept after the call?", <>Recordings, transcripts, summaries, memories and extracted values are all personal data. Ask what is stored by default, where, for how long, and whether a zero data retention mode exists that keeps none of it.</>],
  ["7", "Does it tell people they are talking to an AI?", <>Article 50 of the EU AI Act requires informing people that they are interacting with an AI system unless it is obvious, from 2 August 2026, and adds machine-readable marking of generated content (<a href="https://www.cooley.com/news/insight/2026/2026-08-03-eu-ai-act-transparency-obligations-take-effect-2-august-2026" target="_blank" rel="noreferrer">Cooley</a>, <a href="https://datamatters.sidley.com/2026/06/24/eu-ai-act-transparency-obligations-preparing-for-compliance-by-2-august-2026/" target="_blank" rel="noreferrer">Sidley</a>). Look for an on-screen badge, an optional spoken disclosure and labels in generated files. This is not legal advice.</>],
  ["8", "Can you bring your own model, voice and knowledge?", <>Check for your own language model, your own or cloned voices with consent, document and web-page knowledge with citations, tool calls, webhooks and an MCP server so assistants such as Claude can operate it.</>],
  ["9", "How does it fit your stack?", <>Transport (WebRTC or WebSocket), SDKs, an embeddable widget, and plugins for agent frameworks such as LiveKit and Pipecat decide how much glue code you write. Meeting bots for Zoom, Meet and Teams matter for sales and interviews.</>],
  ["10", "How good does the face look, and who judged it?", <>Run your own blind test with real users and your own content. Published comparisons are mostly run by vendors and disagree: one 609-conversation test ranked its own product first (<a href="https://www.synthesia.io/post/anam-interactive-avatar-alternatives" target="_blank" rel="noreferrer">Synthesia</a>), and other studies ranked differently.</>],
];

export default function Page() {
  return (
    <Shell>
      <JsonLd data={[faqLd(faq), crumbs([["Home", "/"], ["Guides", "/guides/what-is-conversational-video-ai"], ["Choosing a real-time AI avatar API", path]]),
        { "@context": "https://schema.org", "@type": "Article", headline: title, description, datePublished: "2026-10-22", dateModified: "2026-10-22",
          author: { "@type": "Organization", name: "VocalFace" }, publisher: { "@type": "Organization", name: "Evolune EdgeTech LLP" }, mainEntityOfPage: path }]} />
      <PageHead eyebrow="Buyer's guide" title={<>Choosing a real-time <It>AI avatar</It> API</>} lead="Ten questions that separate a demo from a deployment. Vendor-neutral, with sources. Updated 22 October 2026." />
      <Prose>
        <p>Real-time AI avatars, also called conversational video agents or interactive avatars, let people talk face to face with an AI. Many vendors now offer them, and their claims are hard to compare. These questions are the ones that decide whether a pilot survives contact with real users.</p>
        {qs.map(([n, q, a]) => <div key={n}><h2>{n}. {q}</h2><p>{a}</p></div>)}
        <h2>Where VocalFace fits</h2>
        <p>VocalFace is built for teams that want to self-host or control their data: consent-gated replicas with an audit log, opt-in recordings with captions, zero data retention, an AI disclosure badge, knowledge with citations, webhooks, SDKs and an MCP server. Its live face quality is behind the best hosted platforms today; see the <Link href="/compare">honest comparison</Link> and the <Link href="/alternatives">alternatives</Link> pages.</p>
        <h2>Quick answers</h2>
        {faq.map(([q, a]) => <div key={q}><h3>{q}</h3><p>{a}</p></div>)}
      </Prose>
      <FinalCTA />
    </Shell>
  );
}
