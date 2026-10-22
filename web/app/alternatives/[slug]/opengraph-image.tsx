import { alternatives, article, findAlt } from "@/lib/alternatives";
import { OG_SIZE, ogCard } from "@/lib/og";

export const size = OG_SIZE;
export const contentType = "image/png";
export const alt = "VocalFace alternative comparison";
export const generateStaticParams = () => alternatives.map((a) => ({ slug: a.slug }));

export default function Image({ params }: { params: { slug: string } }) {
  const a = findAlt(params.slug);
  return ogCard("VocalFace", `${a ? article(a.name) : "A"} ${a?.name ?? "hosted platform"} alternative you can self-host`, "Honest comparison: where it fits, and where they are ahead.");
}
