import Link from "next/link";
import { FinalCTA, It, PageHead, Prose, Shell } from "@/components/site/Page";
import { JsonLd, crumbs, faqLd } from "@/lib/seo";

const title = "What is conversational video AI? How it works, latency and open-source options";
const description = "Conversational video AI lets you talk face to face with an AI agent in real time. Learn how the speech, language model, voice and face pieces fit together, what latency to expect, and how to build it with open-source parts.";
export const metadata = { title: `${title} - VocalFace`, description, alternates: { canonical: "/guides/what-is-conversational-video-ai" }, openGraph: { title, description, type: "article" } };

const faq = [
  ["What is conversational video AI?", "Conversational video AI is software that lets a person talk face to face with an AI agent in real time. The agent listens, thinks, answers in a voice, and shows a talking face that moves in sync with the speech."],
  ["How does it work?", "Four stages run in a loop: speech-to-text turns your voice into words, a large language model writes the answer, text-to-speech turns the answer into audio, and a face model animates a face from that audio."],
  ["How fast does it need to be?", "People notice delay past roughly one to two seconds between finishing speaking and hearing a reply. Streaming each stage and starting the voice before the full answer is written is how systems stay fast."],
  ["Can I build it with open-source tools?", "Yes. Open speech recognition, local language models, open text-to-speech and open face-animation models can be combined. Quality and speed depend on your hardware, and live face rendering generally needs a modern NVIDIA GPU."],
  ["Is it safe to make a digital replica of a person?", "Only with consent. Good systems require the person to speak a verification phrase, match their voice and face to the training video, allow revocation, and keep an audit log."],
] as const;

export default function Page() {
  return (
    <Shell>
      <JsonLd data={[faqLd(faq), crumbs([["Home", "/"], ["Guides", "/guides/what-is-conversational-video-ai"], ["What is conversational video AI", "/guides/what-is-conversational-video-ai"]]),
        { "@context": "https://schema.org", "@type": "Article", headline: title, description, author: { "@type": "Organization", name: "VocalFace" }, publisher: { "@type": "Organization", name: "Evolune EdgeTech LLP" }, mainEntityOfPage: "/guides/what-is-conversational-video-ai" }]} />
      <PageHead eyebrow="Guide" title={<>What is conversational <It>video</It> AI?</>} lead="A plain-English explainer: how talking to an AI face works, why latency matters, and how to build it with open-source parts." />
      <Prose>
        <h2>The short answer</h2>
        <p>Conversational video AI lets you talk face to face with an AI agent in real time. You speak, the agent understands, answers in a natural voice, and a face on screen moves its lips and expressions in sync. It is the video version of a voice assistant.</p>
        <h2>How it works, step by step</h2>
        <ul>
          <li><strong>Speech to text.</strong> Your voice is turned into words (for example with Whisper-class models).</li>
          <li><strong>Language model.</strong> A large language model writes the reply, optionally using your documents as knowledge.</li>
          <li><strong>Text to speech.</strong> The reply is spoken in a chosen or cloned voice.</li>
          <li><strong>Face animation.</strong> A face model turns that audio into a talking head, from a photo or a short video of a person.</li>
        </ul>
        <h2>Why latency decides whether it feels real</h2>
        <p>Human conversation has gaps of a few hundred milliseconds. Past about one to two seconds, an agent feels slow. Good systems stream every stage and start speaking before the whole answer is written. On our own local stack we measured about 1.4 to 1.9 seconds from the end of speech to the first lip movement; that is one machine, not a guarantee.</p>
        <h2>Open-source versus hosted</h2>
        <p>Hosted platforms run everything for you and lead on live face quality today. Open-core platforms like VocalFace let you self-host, swap any model and keep data in your own environment. See our <Link href="/compare">honest comparison</Link>, the <Link href="/alternatives">alternatives</Link> pages and the <Link href="/guides/choosing-a-real-time-ai-avatar-api">buyer&apos;s checklist</Link>.</p>
        <h2>Consent and safety</h2>
        <p>A digital replica of a real person should exist only with that person&apos;s consent. VocalFace requires a spoken verification phrase, checks that the voice and face match the training video, allows revocation and keeps an audit log. Read more on the <Link href="/security">security page</Link>.</p>
        <h2>Common questions</h2>
        {faq.map(([q, a]) => <div key={q}><h3>{q}</h3><p>{a}</p></div>)}
      </Prose>
      <FinalCTA />
    </Shell>
  );
}
