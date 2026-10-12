import Link from "next/link";
import { notFound } from "next/navigation";
import { Check, Info, Minus } from "lucide-react";
import { FinalCTA, It, PageHead, Shell } from "@/components/site/Page";
import { JsonLd, crumbs, faqLd } from "@/lib/seo";
import { alternatives, findAlt } from "@/lib/alternatives";

export const dynamicParams = false;
export const generateStaticParams = () => alternatives.map((a) => ({ slug: a.slug }));
export function generateMetadata({ params }: { params: { slug: string } }) {
  const a = findAlt(params.slug); if (!a) return {};
  const title = `${a.name} alternative: open-core and self-hostable - VocalFace`;
  const description = `Looking for a ${a.name} alternative? VocalFace is an open-core, self-hostable platform for real-time conversational video AI, with an honest look at where ${a.name} is ahead.`;
  return { title, description, alternates: { canonical: `/alternatives/${a.slug}` }, openGraph: { title, description, type: "article" } };
}

export default function Page({ params }: { params: { slug: string } }) {
  const a = findAlt(params.slug); if (!a) notFound();
  const faq = [
    [`What is an open-source alternative to ${a.name}?`, `VocalFace is an open-core platform for conversational video AI that you can self-host. It covers real-time voice conversations, consent-based digital replicas and generated talking-head video. Its live face quality is behind hosted leaders like ${a.name} today.`],
    [`Is VocalFace cheaper than ${a.name}?`, `The self-hosted voice stack has no per-minute fee to us or to model vendors, but you pay for your own compute, and GPU face rendering is a real cost we have not yet measured. We would not claim to be cheaper until we publish measured numbers.`],
    [`Does VocalFace match ${a.name} on face quality?`, `No, not today. ${a.name} is a mature hosted product and leads on live face realism. VocalFace's strengths are openness, self-hosting, swappable models and built-in consent.`],
    [`Can I move from ${a.name} to VocalFace?`, `VocalFace has a REST API, Python and JavaScript SDKs, and an embeddable widget. Replicas are created from your own consented video or photo. Check the docs for the current API.`],
  ] as const;
  return (
    <Shell>
      <JsonLd data={[faqLd(faq), crumbs([["Home", "/"], ["Alternatives", "/alternatives"], [`${a.name} alternative`, `/alternatives/${a.slug}`]])]} />
      <PageHead eyebrow="Alternatives" title={<>A <It>{a.name}</It> alternative you can own</>} lead={`${a.theyDo} VocalFace is the open-core option for teams that want to self-host and swap models. Here is an honest comparison.`} />
      <div className="mx-auto w-full max-w-5xl px-5 pb-8">
        <div className="grid gap-5 md:grid-cols-2">
          <div className="card !p-7"><h2 className="font-display text-3xl text-white">Where VocalFace fits</h2><ul className="mt-4 space-y-3 text-gray-300">{a.vocalWins.map((x) => <li key={x} className="flex gap-3"><Check size={18} className="mt-0.5 shrink-0 text-vocalface-rose" />{x}</li>)}</ul></div>
          <div className="card !p-7"><h2 className="font-display text-3xl text-white">Where {a.name} is ahead</h2><ul className="mt-4 space-y-3 text-gray-300">{a.theyWin.map((x) => <li key={x} className="flex gap-3"><Minus size={18} className="mt-0.5 shrink-0 text-gray-400" />{x}</li>)}</ul></div>
        </div>
        <p className="mt-5 flex gap-2 text-xs text-gray-400"><Info size={14} className="mt-0.5 shrink-0" />Based on {a.name}&apos;s public positioning, not on testing. Features and pricing change often, so please verify on their site. {a.name} is a trademark of its owner. VocalFace is not affiliated with or endorsed by {a.name}.</p>
      </div>
      <section className="mx-auto w-full max-w-3xl px-5 pb-16">
        <h2 className="font-display text-3xl text-white">Questions people ask</h2>
        <div className="mt-6 space-y-3">{faq.map(([q, an]) => <details key={q} className="card group !p-5"><summary className="cursor-pointer list-none font-medium text-white">{q}</summary><p className="mt-3 text-gray-300">{an}</p></details>)}</div>
        <p className="mt-8 text-sm text-gray-400">More: <Link className="underline" href="/compare">VocalFace vs hosted platforms</Link>, <Link className="underline" href="/guides/what-is-conversational-video-ai">what is conversational video AI</Link>, <Link className="underline" href="/alternatives">other alternatives</Link>.</p>
      </section>
      <FinalCTA />
    </Shell>
  );
}
