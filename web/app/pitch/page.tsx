import Link from "next/link";
import Reveal from "@/components/site/Reveal";
import { It, PageHead, Shell } from "@/components/site/Page";
import { Backing, COMPANY, TrademarkNote } from "@/components/site/Partners";

// Unlisted on purpose: this page is frank about gaps, so it is noindex and not in the sitemap. Share the link with investors.
export const metadata = {
  title: "Investor pitch - VocalFace",
  description: "VocalFace: face-to-face AI agents that teams can use through an API or run themselves, with consent, privacy and AI disclosure built in. What is built, what is measured, what is not, and what comes next.",
  alternates: { canonical: "/pitch" },
  robots: { index: false, follow: false },
};

const contact = process.env.NEXT_PUBLIC_CONTACT_EMAIL;
const shell = "mx-auto w-full max-w-5xl px-5";
const h2 = "font-display text-3xl text-white md:text-4xl";
const a = "underline";
const ext = { target: "_blank", rel: "noreferrer" } as const;

const proof: [string, string][] = [
  ["467", "backend tests passing, plus a 14-step browser end-to-end suite that includes a real recorded call"],
  ["1.4 to 1.9 s", "from the end of speech to first lip movement, warm, on a MacBook (M1 Pro). A measurement, not a guarantee"],
  ["3 weeks", "from the first commit to a tested platform with an API, dashboard, SDKs and privacy controls"],
  ["0", "customers and $0 revenue. We say so up front"],
];

const pillars: [string, string][] = [
  ["Real-time conversations", "Speech in, answer and a talking face out, over one WebSocket. Turn-taking, interruptions, echo handling and live captions are built in."],
  ["Replicas with consent", "A replica from a short video or a single photo, gated by a spoken, revocable consent step with voice and face matching and an audit log."],
  ["Privacy and compliance built in", "Opt-in recordings with captions (announced, signed links only), zero data retention, an AI disclosure badge or spoken line that cannot be talked over, and an AI-generated label inside generated videos and recordings."],
  ["Video generation API", "Script in, talking-head video out. Cloned voice, captions, backgrounds, 16:9 / 9:16 / 1:1, multi-scene."],
  ["Platform for builders", "Knowledge from documents and web pages with citations, guardrails, tools, webhooks, analytics, an embeddable widget, guest and scheduled links, Python and JavaScript SDKs."],
  ["Works with AI assistants", "An MCP server lets Claude, Cursor or any MCP client create agents, open a face-to-face talk link, read transcripts and make videos."],
];

const field: [string, string, string, string][] = [
  ["Hosted conversational video", "Tavus", "Own face, perception and turn-taking models; Zoom, Meet and Teams; enterprise sales", "A self-hosted option, consent and privacy controls in the product, no per-minute vendor fee on the self-hosted voice path"],
  ["Avatar video suites adding live agents", "HeyGen (LiveAvatar), Synthesia, D-ID", "Content libraries, polished studios, distribution", "Developer-first API, self-hosting, every model swappable"],
  ["Real-time avatar APIs", "Anam, Simli, LemonSlice, Beyond Presence, bitHuman", "Latency and price, often as the face for an agent you build yourself", "The whole agent: speech, language model, voice, knowledge, tools, analytics and consent"],
  ["Open-source frameworks", "LiveTalking (about 10k GitHub stars), OpenAvatarChat (about 3.8k)", "Community and many model choices", "A multi-tenant product: accounts, API keys, billing, consent, privacy controls, dashboard and SDKs"],
];

const why: [string, string][] = [
  ["Self-hosting and data control", "Teams that need to keep audio, video and transcripts in their own environment can run the stack. Others use our API. Every stage (speech, model, voice, face) is swappable."],
  ["Consent and compliance first", "Likeness without consent, and AI without disclosure, are procurement blockers. Consent, disclosure, recordings, zero retention and provenance labels are product features here, not add-ons."],
  ["Cost structure", "The voice path has no per-minute vendor fee when self-hosted. The GPU face is the one variable cost; we will publish the measured number after the GPU benchmark."],
  ["Distribution through AI tools", "Developers increasingly build agents with assistants and agent frameworks. The MCP server ships today; LiveKit and Pipecat plugins are next."],
  ["Speed of execution", "The platform went from a first commit to a tested product in about three weeks, with the gaps written down as we go."],
  ["A path to our own model", "The platform and the consented data we collect are ours. Our own fine-tuned face model is a funded next step, not a claim today."],
];

const road: [string, string, string][] = [
  ["Next 30 days", "Prove live video", "Benchmark the face model on a rented NVIDIA RTX 4090 or L40S (under Rs 1,000), build the live path and record an unedited live demo. Ship LiveKit and Pipecat plugins. Replace the two research-licensed legacy components."],
  ["30 to 90 days", "First users", "Pilots with 5 to 10 design partners in one niche (sales demo agents or multilingual tutoring), meeting bots for Zoom and Meet, and legal review of model licences and EU AI Act obligations. Measure retention and willingness to pay."],
  ["3 to 6 months", "Our own model", "Train a face model on consented data. Our estimate: 2 to 4 months and roughly $20k to $60k of GPU for a first usable version. An estimate, not a quote."],
];

const open: [string, string][] = [
  ["Open face-animation model", "face and head motion from audio (Apache-2.0 per its repository)"],
  ["Chatterbox", "voice cloning (MIT)"],
  ["Kokoro", "voices (Apache-2.0)"],
  ["Whisper / faster-whisper", "speech to text (MIT)"],
  ["Silero VAD", "voice activity (MIT)"],
  ["Ollama and open language models", "answers, under each model's own terms"],
];

export default function Page() {
  return (
    <Shell>
      <PageHead eyebrow="Investor pitch" title={<>Conversational video, <It>owned</It> by the teams that use it</>}
        lead={`VocalFace puts a face-to-face AI agent on a website or in an app, through our API or on a team's own servers, with consent, privacy and AI disclosure built in. A product of ${COMPANY}. Updated 22 October 2026.`} />
      <Backing />

      <section className={`${shell} py-16`}>
        <Reveal><h2 className={h2}>The problem</h2>
          <p className="mt-4 max-w-3xl text-lg leading-relaxed text-gray-300">Hosted avatar platforms are closed, priced per minute, and keep your data on their servers. Teams that want a talking agent with a face either pay for every minute, or stitch five open-source models together themselves and own the integration, safety and consent work. Meanwhile the rules have changed: people must now be told when they are talking to an AI, and consent for a real person&apos;s likeness is something buyers ask to see. There is no consent-first option a business can run itself.</p></Reveal>
      </section>

      <section className={`${shell} pb-16`}>
        <Reveal><h2 className={h2}>Why now</h2></Reveal>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          <div className="card !p-6"><h3 className="font-semibold text-white">The rules arrived</h3><p className="mt-2 text-sm leading-relaxed text-gray-300">Since 2 August 2026, Article 50 of the EU AI Act requires telling people they are interacting with an AI system unless it is obvious; machine-readable marking of generated content follows (<a className={a} href="https://www.cooley.com/news/insight/2026/2026-08-03-eu-ai-act-transparency-obligations-take-effect-2-august-2026" {...ext}>Cooley</a>, <a className={a} href="https://datamatters.sidley.com/2026/06/24/eu-ai-act-transparency-obligations-preparing-for-compliance-by-2-august-2026/" {...ext}>Sidley</a>). VocalFace already does both.</p></div>
          <div className="card !p-6"><h3 className="font-semibold text-white">The face is getting cheap</h3><p className="mt-2 text-sm leading-relaxed text-gray-300">Published prices for real-time avatar APIs now run from about $0.01 to $0.20 a minute (vendor-written comparisons, Sep to Oct 2026: <a className={a} href="https://www.heygen.com/blog/best-real-time-ai-avatar-platforms" {...ext}>HeyGen</a>, <a className={a} href="https://lemonslice.com/i/best-avatar-api" {...ext}>LemonSlice</a>). Value is moving to the platform around the face: consent, privacy, knowledge, integrations and where it runs.</p></div>
          <div className="card !p-6"><h3 className="font-semibold text-white">Capital is flowing in</h3><p className="mt-2 text-sm leading-relaxed text-gray-300">Tavus raised a $40M Series B led by CRV in November 2025 (<a className={a} href="https://www.axios.com/pro/enterprise-software-deals/2025/11/12/agentic-ai-tavus-human-40-milion-crv" {...ext}>Axios</a>). Captions rebranded as Mirage and has reported more than $100M raised (<a className={a} href="https://techcrunch.com/2025/09/04/captions-rebrands-as-mirage-expands-beyond-creator-tools-to-ai-video-research" {...ext}>TechCrunch</a>).</p></div>
        </div>
      </section>

      <section className={`${shell} pb-16`}>
        <Reveal><h2 className={h2}>What exists today</h2><p className="mt-3 max-w-3xl text-gray-400">A working product built in October 2026. The website and the API are live at vocalface.com; everything below was measured on our own machines.</p></Reveal>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {proof.map(([n, t]) => <div key={t} className="card !p-6"><p className="font-display text-4xl text-grad">{n}</p><p className="mt-3 text-sm leading-relaxed text-gray-300">{t}</p></div>)}
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {pillars.map(([t, d]) => <div key={t} className="card !p-6"><h3 className="font-semibold text-white">{t}</h3><p className="mt-2 text-sm leading-relaxed text-gray-300">{d}</p></div>)}
        </div>
      </section>

      <section className={`${shell} pb-16`}>
        <Reveal><h2 className={h2}>How the field looks (October 2026)</h2><p className="mt-3 max-w-3xl text-gray-400">From vendors&apos; own pages and vendor-written comparisons, each of which ranks its author first. See also our <Link className={a} href="/alternatives">comparison pages</Link>.</p></Reveal>
        <div className="mt-8 overflow-hidden rounded-3xl border border-white/10 bg-ink-2"><div className="overflow-x-auto"><table className="w-full min-w-[720px] text-left text-sm">
          <caption className="sr-only">Competitor groups, where they lead, and where VocalFace differs</caption>
          <thead><tr className="bg-white/5"><th scope="col" className="p-4 font-medium text-gray-300">Group</th><th scope="col" className="p-4 font-medium text-gray-300">Examples</th><th scope="col" className="p-4 font-medium text-gray-300">Where they lead</th><th scope="col" className="p-4 font-medium text-white">Where VocalFace differs</th></tr></thead>
          <tbody>{field.map(([g, ex, lead, us]) => <tr key={g} className="border-t border-white/10 align-top"><th scope="row" className="p-4 font-medium text-white">{g}</th><td className="p-4 text-gray-300">{ex}</td><td className="p-4 text-gray-300">{lead}</td><td className="p-4 text-gray-200">{us}</td></tr>)}</tbody>
        </table></div></div>
      </section>

      <section className={`${shell} pb-16`}>
        <Reveal><h2 className={h2}>How we chose the face model</h2>
          <p className="mt-4 max-w-3xl leading-relaxed text-gray-300">We tried seven open approaches for the face, including lip-sync models, audio-driven talking-head models, a small video-generation model and a prototype we trained ourselves. We kept the one that preserved identity best and moved the whole face most naturally from audio alone. That was one rater&apos;s judgement on one face, so independent testing is on the plan. It is designed to run in real time on a single modern NVIDIA GPU; we have not yet measured that ourselves. Face models like it are increasingly available to everyone, including inside open-source frameworks, so our edge is the platform around the face, not the face model itself.</p></Reveal>
      </section>

      <section className={`${shell} pb-16`}>
        <Reveal><h2 className={h2}>Why this can win</h2><p className="mt-3 text-gray-400">These are hypotheses we are testing, not facts.</p></Reveal>
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {why.map(([t, d]) => <div key={t} className="card !p-6"><h3 className="font-semibold text-white">{t}</h3><p className="mt-2 text-sm leading-relaxed text-gray-300">{d}</p></div>)}
        </div>
        <p className="mt-6 max-w-3xl text-sm text-gray-400">Hosted leaders are ahead on live face quality today; see <Link className={a} href="/compare">our honest comparison</Link>.</p>
      </section>

      <section className={`${shell} pb-16`}>
        <Reveal><h2 className={h2}>Roadmap and use of funds</h2></Reveal>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {road.map(([when, t, d]) => <div key={when} className="card !p-6"><p className="eyebrow">{when}</p><h3 className="mt-2 font-display text-2xl text-white">{t}</h3><p className="mt-3 text-sm leading-relaxed text-gray-300">{d}</p></div>)}
        </div>
        <p className="mt-6 max-w-3xl text-sm text-gray-400">Funds would go to GPU infrastructure, one machine-learning engineer, legal review, and design-partner pilots. The business model is open-core: a self-hostable core plus a hosted API, with usage-based pricing and a free tier (see <Link className={a} href="/pricing">pricing</Link>). Unit economics are not measured yet and will be published after the GPU tests.</p>
      </section>

      <section className={`${shell} pb-16`}>
        <Reveal><h2 className={h2}>Where we are, honestly</h2></Reveal>
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <div className="card !p-6"><h3 className="font-semibold text-white">Done</h3><ul className="mt-3 space-y-2 text-sm text-gray-300">
            <li>Working real-time voice agent with a lip-synced face, and a generated-video pipeline</li>
            <li>Consent, security and moderation layers, tested</li>
            <li>Privacy controls: recordings with captions, zero data retention, AI disclosure, AI-generated labels</li>
            <li>Dashboard, API, Python and JavaScript SDKs, embeddable widget and an MCP server</li>
            <li>Website and API live at vocalface.com</li>
            <li>Member of the NVIDIA Inception program and Anthropic&apos;s Claude for Startups program</li>
          </ul></div>
          <div className="card !p-6"><h3 className="font-semibold text-white">Not yet</h3><ul className="mt-3 space-y-2 text-sm text-gray-300">
            <li>No customers or revenue</li>
            <li>Live face on an NVIDIA GPU not yet measured (the benchmark is next)</li>
            <li>Real-time face quality is below the best hosted platforms today</li>
            <li>Two legacy research-licensed components (a live lip-sync model and a photo-animation fallback) must be replaced before commercial launch</li>
            <li>The licence for the open core is not published yet</li>
            <li>Not yet tested: phones, live payments, production load</li>
          </ul></div>
        </div>
      </section>

      <section className={`${shell} pb-16`}>
        <Reveal><h2 className={h2}>Built on open source</h2><p className="mt-3 max-w-3xl text-gray-400">We credit what we build on and keep every licence notice. Licences are summarised from each project&apos;s own repository; we will have counsel review them before commercial launch.</p></Reveal>
        <ul className="mt-6 grid gap-3 sm:grid-cols-2">{open.map(([n, d]) => <li key={n} className="rounded-2xl border border-white/10 bg-ink-2 p-4 text-sm"><span className="font-semibold text-white">{n}</span> <span className="text-gray-400">- {d}</span></li>)}</ul>
      </section>

      <section className={`${shell} pb-24`}>
        <div className="card !p-8 text-center">
          <h2 className={h2}>Talk to us</h2>
          <p className="mx-auto mt-3 max-w-xl text-gray-300">We are looking for design partners, GPU and infrastructure support, and early investors who care about consent-first AI video that teams can own.</p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            {contact ? <a className="btn-grad" href={`mailto:${contact}?subject=VocalFace`}>Email us</a> : <Link className="btn-grad" href="/signup">Try the product</Link>}
            <Link className="btn-ghost" href="/docs">Read the docs</Link>
          </div>
          <p className="mt-6 text-xs text-gray-400">&copy; 2026 {COMPANY}. This page describes a pre-revenue product. Statements about the future are plans and estimates, not promises. Competitor facts come from public pages and may be out of date.</p>
          <div className="mt-2 text-xs text-gray-400"><TrademarkNote /></div>
        </div>
      </section>
    </Shell>
  );
}
