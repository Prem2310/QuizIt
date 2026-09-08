import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

/** 3 → 2 → 1 → GO overlay before a match starts. */
export function Countdown({ onDone }: { onDone: () => void }) {
  const [n, setN] = useState(3);

  useEffect(() => {
    if (n < 0) {
      onDone();
      return;
    }
    const t = setTimeout(() => setN((v) => v - 1), 750);
    return () => clearTimeout(t);
  }, [n, onDone]);

  const label = n > 0 ? String(n) : "GO";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/92 backdrop-blur-sm">
      <AnimatePresence mode="wait">
        <motion.span
          key={label}
          initial={{ scale: 0.6, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 1.4, opacity: 0 }}
          transition={{ duration: 0.25 }}
          className="numeric text-7xl font-bold text-primary sm:text-8xl"
        >
          {label}
        </motion.span>
      </AnimatePresence>
    </div>
  );
}
