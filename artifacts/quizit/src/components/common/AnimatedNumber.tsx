import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

interface Props {
  value: number;
  from?: number;
  durationMs?: number;
  className?: string;
  suffix?: string;
  decimals?: number;
}

/** Animated counter that respects prefers-reduced-motion. */
export function AnimatedNumber({ value, from, durationMs = 900, className, suffix = "", decimals = 0 }: Props) {
  const start = from ?? 0;
  const [display, setDisplay] = useState(start);
  const frame = useRef<number>(0);

  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) {
      setDisplay(value);
      return;
    }
    const begin = performance.now();
    const initial = start;
    const step = (now: number) => {
      const t = Math.min(1, (now - begin) / durationMs);
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(initial + (value - initial) * eased);
      if (t < 1) frame.current = requestAnimationFrame(step);
    };
    frame.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame.current);
  }, [value, start, durationMs]);

  return (
    <span className={cn("numeric", className)}>
      {display.toFixed(decimals)}
      {suffix}
    </span>
  );
}
