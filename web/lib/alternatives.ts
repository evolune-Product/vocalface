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
    theyDo: "HeyGen is a hosted platform for making avatar videos from text and for interactive avatars.",
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
];
export const findAlt = (slug: string) => alternatives.find((a) => a.slug === slug);
