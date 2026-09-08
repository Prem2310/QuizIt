import { useEffect, useRef, useState } from "react";

/** Per-question countdown. Restarts whenever `resetKey` changes. */
export function useCountdownTimer(seconds: number, resetKey: string, onExpire: () => void, active = true) {
  const [left, setLeft] = useState(seconds);
  const expireRef = useRef(onExpire);
  expireRef.current = onExpire;

  useEffect(() => {
    setLeft(seconds);
    if (!active) return;
    const id = setInterval(() => {
      setLeft((v) => {
        if (v <= 1) {
          clearInterval(id);
          expireRef.current();
          return 0;
        }
        return v - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [seconds, resetKey, active]);

  return left;
}
