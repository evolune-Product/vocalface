import { OG_SIZE, ogCard } from "@/lib/og";

export const size = OG_SIZE;
export const contentType = "image/png";
export const alt = "What is conversational video AI?";

export default function Image() {
  return ogCard("VocalFace guide", "What is conversational video AI?", "How talking to an AI face works, latency, and open-source options.");
}
