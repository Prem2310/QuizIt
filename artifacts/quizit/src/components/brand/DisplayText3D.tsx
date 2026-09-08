import { useId } from "react";
import { cn } from "@/lib/utils";

type Tone = "primary" | "destructive" | "muted";

const TONE_STOPS: Record<Tone, [string, string]> = {
  primary: ["var(--color-primary-bright)", "var(--color-secondary)"],
  destructive: ["#ffb199", "var(--color-destructive)"],
  muted: ["#f0f0f0", "#a3a3a3"],
};

/**
 * Layered SVG display text for "moment" screens (duel VICTORY/DEFEAT, streak
 * milestones): an offset outline stack behind a gradient-filled, glowing
 * foreground word — the extruded look from the matiks result screen.
 */
export function DisplayText3D({ text, tone = "primary", className }: { text: string; tone?: Tone; className?: string }) {
  const uid = useId();
  const gradientId = `dt3d-grad-${uid}`;
  const glowId = `dt3d-glow-${uid}`;
  const [from, to] = TONE_STOPS[tone];
  const layers = [10, 7, 4];

  return (
    <svg viewBox="0 0 640 150" className={cn("w-full overflow-visible", className)} role="img" aria-label={text}>
      <defs>
        <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: from }} />
          <stop offset="100%" style={{ stopColor: to }} />
        </linearGradient>
        <filter id={glowId} x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation="9" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {layers.map((offset) => (
        <text
          key={offset}
          x="50%"
          y="108"
          textAnchor="middle"
          textLength="580"
          lengthAdjust="spacingAndGlyphs"
          fontFamily="var(--font-display)"
          fontWeight="800"
          fontSize="104"
          fill="none"
          style={{ stroke: "var(--color-border)", strokeWidth: 2.5, opacity: 0.55 }}
          transform={`translate(${offset} ${offset})`}
        >
          {text}
        </text>
      ))}

      <text
        x="50%"
        y="108"
        textAnchor="middle"
        textLength="580"
        lengthAdjust="spacingAndGlyphs"
        fontFamily="var(--font-display)"
        fontWeight="800"
        fontSize="104"
        style={{ fill: `url(#${gradientId})`, stroke: "var(--color-background)", strokeWidth: 2 }}
        filter={`url(#${glowId})`}
      >
        {text}
      </text>
    </svg>
  );
}
