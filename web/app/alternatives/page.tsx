import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { FinalCTA, It, PageHead, Shell } from "@/components/site/Page";
import { JsonLd, crumbs } from "@/lib/seo";
import { alternatives } from "@/lib/alternatives";

export const metadata = {
  title: "Alternatives to hosted conversational video AI platforms - VocalFace",
  description: "Open-core, self-hostable alternatives to hosted AI video and avatar platforms, with honest comparisons that include where the hosted platforms are ahead.",
  alternates: { canonical: "/alternatives" },
};

export default function Page() {
  return (
    <Shell>
      <JsonLd data={crumbs([["Home", "/"], ["Alternatives", "/alternatives"]])} />
      <PageHead eyebrow="Alternatives" title={<>Open-core <It>alternatives</It> to hosted platforms</>} lead="If you want to self-host, swap models and keep data in your environment, VocalFace is built for that. These pages say honestly where the hosted platforms are ahead." />
      <div className="mx-auto grid w-full max-w-5xl gap-5 px-5 pb-20 sm:grid-cols-2">
        {alternatives.map((a) => (
          <Link key={a.slug} href={`/alternatives/${a.slug}`} className="card group !p-7 transition hover:-translate-y-1">
            <h2 className="font-display text-3xl text-white">{a.name} alternative</h2>
            <p className="mt-2 text-gray-300">{a.theyDo}</p>
            <p className="mt-4 flex items-center gap-1 text-sm text-gray-300">Compare <ArrowRight size={14} className="transition group-hover:translate-x-1" /></p>
          </Link>
        ))}
      </div>
      <FinalCTA />
    </Shell>
  );
}
