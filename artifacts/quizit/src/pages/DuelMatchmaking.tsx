import { useEffect, useRef, useState } from "react";
import { useLocation } from "wouter";
import { motion } from "framer-motion";
import { Swords, X } from "lucide-react";
import { useListTopics } from "@workspace/api-client-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Reveal } from "@/components/common/Motion";
import { Button } from "@/components/ui/button";
import { initialsOf } from "@/components/layout/AppShell";
import { createMatchmakingService } from "@/lib/realtime";
import { useAuth } from "@/stores/auth";
import type { ConnectionState, MatchFoundPayload } from "@/types";

type Phase = "idle" | "searching" | "matched" | "error";

export default function DuelMatchmaking() {
  const { user } = useAuth();
  const [, navigate] = useLocation();
  const topicsQuery = useListTopics();

  const [topicId, setTopicId] = useState<number | null>(null);
  const [phase, setPhase] = useState<Phase>("idle");
  const [connection, setConnection] = useState<ConnectionState>("IDLE");
  const [match, setMatch] = useState<MatchFoundPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const serviceRef = useRef<ReturnType<typeof createMatchmakingService> | null>(null);

  useEffect(() => () => serviceRef.current?.dispose(), []);

  function start() {
    setError(null);
    setPhase("searching");
    const service = createMatchmakingService(
      {
        onConnection: setConnection,
        onMatchFound: (payload) => {
          setMatch(payload);
          setPhase("matched");
          window.setTimeout(() => navigate(`/duel/${payload.duelId}`), 900);
        },
        onError: (message) => {
          setError(message);
          setPhase("error");
        },
      },
      topicId,
    );
    serviceRef.current = service;
    service.start();
  }

  function cancel() {
    serviceRef.current?.cancel();
    serviceRef.current = null;
    setPhase("idle");
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <PageHeader eyebrow="Duel" title="Find an opponent" description="Get matched with someone near your rating." />

      {phase === "idle" || phase === "error" ? (
        <Reveal className="glass-panel space-y-5 p-6">
          <div>
            <p className="label-micro mb-2">Topic (optional)</p>
            <div className="flex flex-wrap gap-1.5">
              <button
                type="button"
                onClick={() => setTopicId(null)}
                className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${topicId === null ? "border-primary bg-primary/10 text-primary" : "border-border text-muted-foreground"}`}
              >
                Any topic
              </button>
              {topicsQuery.data?.map((topic) => (
                <button
                  key={topic.id}
                  type="button"
                  onClick={() => setTopicId(topic.id)}
                  className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${topicId === topic.id ? "border-primary bg-primary/10 text-primary" : "border-border text-muted-foreground"}`}
                >
                  {topic.name}
                </button>
              ))}
            </div>
          </div>
          {error ? <p className="text-sm text-destructive">{error}</p> : null}
          <Button size="lg" className="w-full glow-primary" onClick={start}>
            <Swords className="h-4 w-4" /> Queue up
          </Button>
        </Reveal>
      ) : null}

      {phase === "searching" ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-panel flex flex-col items-center gap-5 p-10 text-center"
        >
          <div className="relative flex h-20 w-20 items-center justify-center rounded-full bg-primary/10">
            <div className="pulse-ring absolute inset-0 rounded-full" />
            <span className="text-lg font-bold text-primary">{user ? initialsOf(user.name) : "?"}</span>
          </div>
          <div>
            <p className="text-sm font-semibold text-foreground">Searching for an opponent…</p>
            <p className="mt-1 text-xs text-muted-foreground">{connection === "OPEN" ? "Connected — widening search…" : "Connecting…"}</p>
          </div>
          <Button variant="outline" onClick={cancel}>
            <X className="h-4 w-4" /> Cancel
          </Button>
        </motion.div>
      ) : null}

      {phase === "matched" && match ? (
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="glass-panel glow-primary flex flex-col items-center gap-3 p-10 text-center">
          <Swords className="h-8 w-8 text-primary" />
          <p className="text-lg font-bold text-foreground">Opponent found!</p>
          <p className="text-sm text-muted-foreground">
            {match.opponent?.name ?? "Opponent"} · {Math.round(match.opponent?.rating ?? 0)} rating
          </p>
        </motion.div>
      ) : null}
    </div>
  );
}
