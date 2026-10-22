// Honest comparison pages for people searching "<vendor> alternative". Claims about vendors are deliberately general and
// hedged: they come from each vendor's public positioning, not from testing. Re-check before publishing changes.
export type Alt = {
  slug: string; name: string; kind: string; theyDo: string; strengths: string[]; vocalWins: string[]; theyWin: string[];
};

export const alternatives: Alt[] = [
  {
    slug: "tavus", name: "Tavus", kind: "conversational video platform",
    theyDo: "Tavus is a hosted platform and API for real-time conversational video agents and AI-generated video with replicas of real people.",
    strengths: ["A mature hosted service you do not have to operate", "Live face quality is ahead of what we ship today", "Established API and customer base"],
    vocalWins: ["Open-core: self-host the whole stack and keep data on your own machines", "Every stage (speech, language model, voice, face) is swappable", "A spoken, revocable consent step with an audit log is built in", "The self-hosted voice path has no per-minute vendor fee"],
    theyWin: ["Live face realism today", "No infrastructure to run", "Track record at scale"],
  },
  {
    slug: "heygen", name: "HeyGen", kind: "AI avatar video platform",
    theyDo: "HeyGen is a hosted platform for making avatar videos from text, and for real-time interactive avatars (LiveAvatar).",
    strengths: ["Polished studio-style editor for marketing video", "Large template and avatar library", "No setup"],
    vocalWins: ["Self-hostable and API-first for developers", "Real-time two-way voice conversations with an agent, not only scripted video", "Bring your own models and keep data in your environment", "Consent-gated replicas with an audit log"],
    theyWin: ["Editor polish and content library", "Output quality for scripted marketing video", "Ease of use for non-developers"],
  },
  {
    slug: "d-id", name: "D-ID", kind: "talking-avatar API",
    theyDo: "D-ID offers hosted APIs and tools for animating a face from a photo and for conversational avatar agents.",
    strengths: ["Quick photo-to-talking-head generation as a hosted API", "Established developer product", "No GPU to manage"],
    vocalWins: ["Open-core and self-hostable", "Local and open models for the whole voice path", "Knowledge from your documents with citations, guardrails and tools in one platform", "Consent step and audit log for replicas of real people"],
    theyWin: ["Hosted convenience", "Maturity of the avatar output", "Support and service levels"],
  },
  {
    slug: "synthesia", name: "Synthesia", kind: "enterprise AI video platform",
    theyDo: "Synthesia is a hosted AI video platform where business teams create presenter-style videos with avatars from scripts.",
    strengths: ["Enterprise features and compliance posture", "Polished presenter video for training and communications", "Large customer base"],
    vocalWins: ["Real-time conversational agents, not only pre-rendered presenter video", "Self-host option for strict data-control requirements", "Developer API and embeddable widget", "Swap any model in the stack"],
    theyWin: ["Enterprise readiness and certifications", "Production quality for scripted corporate video", "Customer success and support"],
  },
  {
    slug: "anam", name: "Anam", kind: "real-time AI avatar API",
    theyDo: "Anam is a hosted API for real-time AI personas generated from a single photo, used as a complete agent or as the face for your own voice pipeline.",
    strengths: ["Real-time personas from one photo", "Integrations with agent frameworks", "Hosted, so nothing to run"],
    vocalWins: ["Self-hostable: run the whole stack, face included, on machines you control", "Consent-gated replicas of real people, with a spoken phrase, face and voice checks and an audit log", "Swap the speech, language-model and voice stages freely", "Recording, zero data retention and AI disclosure are switches on your own deployment"],
    theyWin: ["Lower published latency and a mature hosted service", "Compliance work it publishes, such as HIPAA support", "Ready-made integrations with LiveKit, Pipecat and other agent frameworks"],
  },
  {
    slug: "simli", name: "Simli", kind: "real-time avatar video API",
    theyDo: "Simli is a real-time avatar API that turns streamed audio into a talking face, designed as the video stage of a voice agent you already run.",
    strengths: ["Very low published latency for the video stage", "Low per-minute prices", "Agent-framework integrations"],
    vocalWins: ["The whole agent, not only the face: speech, language model, voice, knowledge, tools and analytics in one platform", "Self-hostable end to end", "Consent-gated replicas with an audit log", "Recording and zero data retention controls"],
    theyWin: ["A very fast, focused video stage", "Low prices for the face layer alone", "Ready-made LiveKit and Pipecat integrations"],
  },
  {
    slug: "lemonslice", name: "LemonSlice", kind: "live avatar API",
    theyDo: "LemonSlice turns a single image, including illustrated or cartoon characters, into a live talking avatar for real-time agents.",
    strengths: ["Many character styles from one image", "Low entry price", "Body and gesture motion"],
    vocalWins: ["Self-hostable and API-first", "Consent-gated replicas of real people", "Swappable models across the whole stack", "Privacy controls you own: recording, zero data retention, AI disclosure"],
    theyWin: ["Non-photoreal characters from one image", "Low entry price for a hosted service", "Body and gesture motion beyond the head"],
  },
  {
    slug: "beyond-presence", name: "Beyond Presence", kind: "real-time avatar and agent API",
    theyDo: "Beyond Presence offers speech-to-video and managed-agent APIs for real-time AI avatars.",
    strengths: ["Very low published latency", "Managed agents", "Agent-framework integrations"],
    vocalWins: ["Self-hostable: keep audio, video and transcripts in your own environment", "Consent-gated replicas with an audit log", "Swap any model in the stack", "Built-in knowledge with citations, tools, webhooks and analytics"],
    theyWin: ["Very low published latency for the face", "Managed agents for teams that do not want to run anything", "Ready-made LiveKit and Pipecat integrations"],
  },
];
/** "A Tavus alternative" but "An Anam alternative". */
export const article = (name: string) => (/^[AEIOU]/i.test(name) ? "An" : "A");
export const findAlt = (slug: string) => alternatives.find((a) => a.slug === slug);
