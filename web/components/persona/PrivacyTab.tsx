"use client";
import { useEffect, useState } from "react";
import { BadgeCheck, CircleDot, Save, ShieldOff } from "lucide-react";
import { api, errText } from "@/lib/api";
import { Callout } from "@/components/kit";
import { Section, Toggle, Field, Spinner, toast } from "@/components/ui";

type Privacy = {
  persona_id: string; record_conversations: boolean; announce_recording: boolean; zero_data_retention: boolean;
  ai_disclosure: "off" | "badge" | "spoken"; recording_active: boolean; recording_available: boolean; notes: string[];
};

/** Recording, zero data retention and AI disclosure for one persona (PUT /v1/personas/{id}/privacy). */
export default function PrivacyTab({ pid }: { pid: string }) {
  const [p, setP] = useState<Privacy | null>(null); const [busy, setBusy] = useState(false); const [err, setErr] = useState("");
  useEffect(() => { setP(null); api<Privacy>(`/v1/personas/${pid}/privacy`).then(setP).catch((x) => toast.error(x)); }, [pid]);
  if (!p) return <div className="h-24 animate-pulse rounded-xl bg-white/5" />;
  const upd = (x: Partial<Privacy>) => setP({ ...p, ...x });
  async function save() {
    setBusy(true); setErr("");
    try {
      const body = { record_conversations: p!.record_conversations, announce_recording: p!.announce_recording, zero_data_retention: p!.zero_data_retention, ai_disclosure: p!.ai_disclosure };
      setP(await api<Privacy>(`/v1/personas/${pid}/privacy`, { method: "PUT", body })); toast.success("Privacy settings saved.");
    } catch (x) { setErr(errText(x)); } finally { setBusy(false); }
  }
  return (
    <div className="space-y-5">
      <Section title="AI disclosure" icon={<BadgeCheck size={16} className="text-vocalface-cyan" />} hint="People should know they are talking to an AI. This follows the transparency idea in Article 50 of the EU AI Act; it is a product control, not legal advice.">
        <Field label="How the agent discloses that it is an AI">
          <select className="input" aria-label="AI disclosure" value={p.ai_disclosure} onChange={(e) => upd({ ai_disclosure: e.target.value as Privacy["ai_disclosure"] })}>
            <option value="badge">On-screen badge (default)</option>
            <option value="spoken">Badge, and the agent says so before its greeting</option>
            <option value="off">Off: I disclose it myself</option>
          </select>
        </Field>
      </Section>
      <Section title="Record conversations" icon={<CircleDot size={16} className="text-vocalface-rose" />} hint="Saves what the participant heard and saw: video with the face (audio only without one) plus captions. Off by default.">
        <div className="space-y-3 rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <Toggle checked={p.record_conversations} onChange={(v) => upd({ record_conversations: v })} label="Record every conversation with this persona" />
          <Toggle checked={p.announce_recording} onChange={(v) => upd({ announce_recording: v })} label="Announce it" hint="The agent says &quot;This conversation is being recorded.&quot; first, and every VocalFace page shows a Recording flag. Keep this on unless your own flow tells people." />
          {!p.recording_available && <p className="text-xs text-vocalface-amber">This server has no ffmpeg installed, so recordings cannot be made yet.</p>}
        </div>
      </Section>
      <Section title="Zero data retention" icon={<ShieldOff size={16} className="text-vocalface-mint" />} hint="Nothing about what was said is kept after the call: no transcript, citations, summary, memory, insights, tool arguments or recording. Objectives are kept as done or not done, without quotes or values.">
        <Toggle checked={p.zero_data_retention} onChange={(v) => upd({ zero_data_retention: v })} label="Keep no conversation content" hint="Duration, counts and billing are still kept. Tools you enable still do what they are built to do." />
      </Section>
      {p.notes.length > 0 && <Callout tone="info">{p.notes.join(" ")}</Callout>}
      {err && <Callout tone="bad">{err}</Callout>}
      <button type="button" className="btn-grad w-full" disabled={busy} onClick={save}>{busy ? <Spinner /> : <Save size={15} />}Save privacy settings</button>
    </div>
  );
}
