import { Link } from "wouter";
import { BarChart3, Flame, RotateCcw, Swords, Target, Trophy, Zap } from "lucide-react";
import { useGetMyAnalytics } from "@workspace/api-client-react";
import { PageHeader } from "@/components/common/PageHeader";
import { AnimatedNumber } from "@/components/common/AnimatedNumber";
import { ErrorState, LoadingState } from "@/components/common/StateBlocks";
import { HoverCard, Reveal, StaggerGroup, StaggerItem } from "@/components/common/Motion";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/stores/auth";

export default function Arena() {
  const { user } = useAuth();
  const { data, isPending, isError, refetch } = useGetMyAnalytics();

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Arena"
        title={`Welcome back, ${user?.name?.split(" ")[0] ?? "player"}`}
        description="Keep your streak alive — practice a weak topic, or find a duel."
      />

      <StaggerGroup className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StaggerItem>
          <StatCard icon={Trophy} label="Rating" value={user?.user_rating ?? 1000} tone="primary" sub={user?.league} />
        </StaggerItem>
        <StaggerItem>
          <StatCard icon={Flame} label="Streak" value={user?.current_streak ?? 0} tone="warning" suffix=" days" />
        </StaggerItem>
        <StaggerItem>
          <StatCard icon={Zap} label="Total XP" value={user?.total_xp ?? 0} tone="highlight" />
        </StaggerItem>
        <StaggerItem>
          <StatCard icon={BarChart3} label="Accuracy" value={data?.accuracy ?? 0} tone="secondary" suffix="%" />
        </StaggerItem>
      </StaggerGroup>

      <div className="grid gap-4 sm:grid-cols-2">
        <HoverCard>
          <ActionCard
            icon={Swords}
            title="Find a duel"
            body="Get matched with someone at your rating and answer head-to-head, live."
            cta="Queue up"
            href="/duel/matchmaking"
            featured
          />
        </HoverCard>
        <HoverCard>
          <ActionCard
            icon={Target}
            title="Practice"
            body="Drill any topic, or let QuizIt pick questions you've gotten wrong before."
            cta="Start practicing"
            href="/practice"
          />
        </HoverCard>
      </div>

      {!isPending && data && (data.due_for_review > 0 || data.recommended_topic) ? (
        <Reveal delay={0.15} className="surface-panel flex flex-wrap items-center justify-between gap-4 p-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-warning/10 text-warning">
              <RotateCcw className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-foreground">
                {data.due_for_review > 0
                  ? `${data.due_for_review} question${data.due_for_review === 1 ? "" : "s"} due for review`
                  : `Your weakest topic: ${data.recommended_topic}`}
              </p>
              <p className="text-xs text-muted-foreground">Spaced repetition keeps your weak spots from coming back on test day.</p>
            </div>
          </div>
          <Link href="/practice?mode=weak_topics">
            <Button variant="outline" size="sm">
              Review now
            </Button>
          </Link>
        </Reveal>
      ) : null}

      {isPending ? <LoadingState label="Loading your stats…" /> : null}
      {isError ? <ErrorState message="Couldn't load your stats." onRetry={() => void refetch()} /> : null}
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  suffix = "",
  tone,
  sub,
}: {
  icon: typeof Trophy;
  label: string;
  value: number;
  suffix?: string;
  tone: "primary" | "warning" | "highlight" | "secondary";
  sub?: string;
}) {
  const toneClass = {
    primary: "bg-primary/10 text-primary",
    warning: "bg-warning/10 text-warning",
    highlight: "bg-highlight/10 text-highlight",
    secondary: "bg-secondary/10 text-secondary",
  }[tone];

  return (
    <div className="surface-panel p-4 transition-shadow hover:shadow-md">
      <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${toneClass}`}>
        <Icon className="h-4.5 w-4.5" />
      </div>
      <AnimatedNumber value={value} suffix={suffix} className="mt-3 block text-2xl font-bold text-foreground" />
      <p className="label-micro mt-0.5">
        {label}
        {sub ? ` · ${sub}` : ""}
      </p>
    </div>
  );
}

function ActionCard({
  icon: Icon,
  title,
  body,
  cta,
  href,
  featured,
}: {
  icon: typeof Swords;
  title: string;
  body: string;
  cta: string;
  href: string;
  featured?: boolean;
}) {
  return (
    <div className={`glass-panel flex h-full flex-col justify-between p-6 transition-shadow ${featured ? "glow-primary" : "hover:shadow-md"}`}>
      <div>
        <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${featured ? "bg-primary text-primary-foreground" : "bg-primary/10 text-primary"}`}>
          <Icon className="h-5 w-5" />
        </div>
        <h3 className="mt-4 text-lg font-semibold text-foreground">{title}</h3>
        <p className="mt-1.5 text-sm text-muted-foreground">{body}</p>
      </div>
      <Link href={href}>
        <Button className={`mt-5 w-full ${featured ? "glow-primary" : ""}`} variant={featured ? "default" : "outline"}>
          {cta}
        </Button>
      </Link>
    </div>
  );
}
