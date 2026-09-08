import { cn } from "@/lib/utils";

const SIZE = 56;
const STROKE = 5;
const RADIUS = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

/** Game-HUD style countdown ring — replaces the plain progress bar in Practice/Duel. */
export function CircularTimer({ secondsLeft, total, size = SIZE }: { secondsLeft: number; total: number; size?: number }) {
  const clamped = Math.max(0, secondsLeft);
  const fraction = total > 0 ? Math.max(0, Math.min(1, clamped / total)) : 0;
  const urgent = clamped <= Math.min(5, Math.ceil(total * 0.2));
  const scale = size / SIZE;
  const offset = CIRCUMFERENCE * (1 - fraction);

  return (
    <div className={cn("relative shrink-0", urgent && clamped > 0 && "animate-pulse")} style={{ width: size, height: size }} role="timer" aria-label={`${clamped} seconds left`}>
      <svg width={size} height={size} viewBox={`0 0 ${SIZE} ${SIZE}`} className="-rotate-90">
        <circle cx={SIZE / 2} cy={SIZE / 2} r={RADIUS} fill="none" stroke="var(--color-surface)" strokeWidth={STROKE} />
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke={urgent ? "var(--color-destructive)" : "var(--color-primary)"}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 1s linear, stroke 0.3s ease" }}
        />
      </svg>
      <span
        className={cn("numeric absolute inset-0 flex items-center justify-center font-bold text-foreground", urgent && "text-destructive")}
        style={{ fontSize: 15 * scale }}
      >
        {clamped}
      </span>
    </div>
  );
}
