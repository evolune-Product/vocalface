import { SITE } from "./site";
export { SITE };
export const ORG = "Evolune EdgeTech LLP";

export function JsonLd({ data }: { data: object | object[] }) {
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }} />;
}

export const organization = {
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": `${SITE}/#org`,
  name: "VocalFace",
  legalName: ORG,
  url: SITE,
  logo: `${SITE}/brand/emblem-og.png`,
  description: "VocalFace is an open-core platform for real-time conversational video AI agents, consent-based digital replicas and talking-head video generation.",
  parentOrganization: { "@type": "Organization", name: ORG },
  sameAs: ["https://github.com/evolune-Product/vocalface"],
};

export const website = { "@context": "https://schema.org", "@type": "WebSite", "@id": `${SITE}/#site`, url: SITE, name: "VocalFace", publisher: { "@id": `${SITE}/#org` }, inLanguage: "en" };

export const software = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "VocalFace",
  applicationCategory: "DeveloperApplication",
  operatingSystem: "Web, macOS, Linux",
  description: "Open-core, self-hostable platform for conversational video AI: talk face to face with AI agents, make consent-based digital replicas and generate talking-head videos through an API.",
  url: SITE,
  publisher: { "@id": `${SITE}/#org` },
  offers: { "@type": "Offer", price: "0", priceCurrency: "USD", description: "Free plan with 10 minutes, no card needed" },
};

export const faqLd = (items: readonly (readonly [string, string])[]) => ({
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: items.map(([q, a]) => ({ "@type": "Question", name: q, acceptedAnswer: { "@type": "Answer", text: a } })),
});

export const crumbs = (items: [string, string][]) => ({
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: items.map(([name, path], i) => ({ "@type": "ListItem", position: i + 1, name, item: `${SITE}${path}` })),
});
