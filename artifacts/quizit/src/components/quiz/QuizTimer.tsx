import { cn } from "@/lib/utils";

export function QuizTimer({ secondsLeft, total }: { secondsLeft: number; total: number }) {
  const pct = total > 0 ? Math.max(0, Math.min(1, secondsLeft / total)) : 0;
  const urgent = secondsLeft <= 5;
  return (
    <div className="flex items-center gap-2" aria-label={`${secondsLeft} seconds left`}>
      <div className="h-1.5 w-20 overflow-hidden rounded-full bg-surface sm:w-28">
        <div
          className={cn("h-full rounded-full transition-[width] duration-1000 ease-linear", urgent ? "bg-destructive" : "bg-primary")}
          style={{ width: `${pct * 100}%` }}
        />
      </div>
      <span className={cn("numeric w-8 text-right text-sm font-bold", urgent ? "text-destructive" : "text-foreground")}>
        {Math.max(0, secondsLeft)}s
      </span>
    </div>
  );
}
