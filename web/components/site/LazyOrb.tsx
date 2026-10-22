"use client";
import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";
import type { OrbState } from "./Orb";

const Orb = dynamic(() => import("./Orb"), { ssr: false });

type Props = { state?: OrbState; level?: number; className?: string; autoCycle?: boolean; density?: number };

/** Devices where the animated orb costs more than it adds: reduced motion, data saver, few cores or little memory.
 *  They keep the static glow, which is drawn either way. */
function wantsOrb(): boolean {
  try {
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return false;
    const n = navigator as Navigator & { deviceMemory?: number; connection?: { saveData?: boolean } };
    if (n.connection?.saveData) return false;
    if ((n.hardwareConcurrency || 8) <= 4 || (n.deviceMemory || 8) <= 4) return false;
  } catch { /* unknown: assume capable */ }
  return true;
}

/** Loads three.js only once the orb is near the viewport AND the page has finished loading and the browser is idle, so
 *  the heavy setup never competes with first paint or the first tap. Shows a static gradient until then (no layout
 *  shift); the orb fades in over it. */
export default function LazyOrb({ className = "", ...rest }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [show, setShow] = useState(false);
  useEffect(() => {
    const el = ref.current; if (!el || !wantsOrb()) return;
    try { const c = document.createElement("canvas"); const gl = (c.getContext("webgl2") || c.getContext("webgl")) as WebGLRenderingContext | null; if (!gl) return; gl.getExtension("WEBGL_lose_context")?.loseContext(); } catch { return; }
    let cancelled = false;
    const go = () => { if (!cancelled) setShow(true); };
    const whenIdle = () => {
      const ric = (window as Window & { requestIdleCallback?: (cb: () => void, o?: { timeout: number }) => number }).requestIdleCallback;
      if (ric) ric(go, { timeout: 2500 }); else setTimeout(go, 1200);
    };
    const io = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return;
      io.disconnect();
      if (document.readyState === "complete") whenIdle(); else window.addEventListener("load", whenIdle, { once: true });
    }, { rootMargin: "200px" });
    io.observe(el);
    return () => { cancelled = true; io.disconnect(); window.removeEventListener("load", whenIdle); };
  }, []);
  return (
    <div ref={ref} className={`relative ${className}`} aria-hidden>
      <div className="absolute inset-[18%] rounded-full bg-vocalface-gradient opacity-30 blur-3xl" />
      {show && <div className="orb-fade absolute inset-0"><Orb {...rest} className="absolute inset-0" /></div>}
    </div>
  );
}
