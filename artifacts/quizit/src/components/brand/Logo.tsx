import { cn } from "@/lib/utils";

/** Original QuizIt wordmark — geometric Q built from a square + notch. */
export function LogoMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" aria-hidden="true" className={cn("h-7 w-7", className)}>
      <rect x="2.5" y="2.5" width="27" height="27" rx="8" fill="none" stroke="var(--color-primary)" strokeWidth="3" />
      <rect x="17" y="17" width="12" height="12" rx="4" fill="var(--color-primary-bright)" />
      <rect x="9" y="9" width="7" height="7" rx="2" fill="var(--color-primary)" opacity="0.55" />
    </svg>
  );
}

export function Logo({ className, compact = false }: { className?: string; compact?: boolean }) {
  return (
    <span className={cn("flex items-center gap-2", className)}>
      <LogoMark />
      {!compact && (
        <span className="font-display text-lg font-bold tracking-[0.18em] text-foreground">
          QUIZ<span className="text-primary">IT</span>
        </span>
      )}
    </span>
  );
}
