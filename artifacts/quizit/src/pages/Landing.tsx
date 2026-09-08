import { Link } from "wouter";
import { motion } from "framer-motion";
import { BarChart3, Flame, GraduationCap, Swords, Target, Trophy } from "lucide-react";
import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/button";
import { AnimatedNumber } from "@/components/common/AnimatedNumber";
import { useAuth } from "@/stores/auth";

const FEATURES = [
  {
    icon: Swords,
    title: "1v1 duels",
    body: "Queue up and face a classmate of similar rating in a live, timed head-to-head. Fastest correct answer wins the point.",
  },
  {
    icon: Target,
    title: "Weak-topic drills",
    body: "Every miss is tracked. QuizIt resurfaces the questions you got wrong sooner, so you actually fix your weak spots.",
  },
  {
    icon: Trophy,
    title: "Rating & leagues",
    body: "Climb from Novice to Diamond on an Elo rating. Compare yourself globally or just against your own college.",
  },
  {
    icon: BarChart3,
    title: "Real progress data",
    body: "Topic-by-topic accuracy, streaks and XP — see exactly where you stand before the real placement test.",
  },
];

export default function Landing() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-background">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5 sm:px-6">
        <Link href="/" aria-label="Go to homepage">
          <Logo />
        </Link>
        <nav className="flex items-center gap-2">
          {isAuthenticated ? (
            <Link href="/arena">
              <Button size="sm">Go to Arena</Button>
            </Link>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  Log in
                </Button>
              </Link>
              <Link href="/signup">
                <Button size="sm" className="glow-primary">
                  Sign up free
                </Button>
              </Link>
            </>
          )}
        </nav>
      </header>

      <main>
        <section className="relative overflow-hidden px-4 pb-20 pt-14 sm:px-6 sm:pt-20">
          <div
            aria-hidden
            className="pointer-events-none absolute -top-32 left-1/2 h-96 w-[36rem] -translate-x-1/2 rounded-full bg-primary/15 blur-[100px]"
          />
          <div className="relative mx-auto max-w-3xl text-center">
            <motion.p
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="label-micro inline-flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1"
            >
              <GraduationCap className="h-3.5 w-3.5 text-primary" /> Built for placement prep
            </motion.p>
            <motion.h1
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.05 }}
              className="mt-5 text-balance font-display text-4xl font-bold leading-[1.08] tracking-tight text-foreground sm:text-6xl"
            >
              Practice aptitude.
              <br />
              <span className="text-gradient-primary">Duel your classmates.</span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.12 }}
              className="mx-auto mt-5 max-w-xl text-balance text-base text-muted-foreground sm:text-lg"
            >
              Thousands of real placement-test questions across quant, verbal and reasoning. Drill your weak
              topics on repeat, then prove it in a live 1v1 duel.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.18 }}
              className="mt-8 flex flex-wrap items-center justify-center gap-3"
            >
              <Link href={isAuthenticated ? "/practice" : "/signup"}>
                <Button size="lg" className="glow-primary">
                  Start practicing
                </Button>
              </Link>
              <Link href={isAuthenticated ? "/duel/matchmaking" : "/signup"}>
                <Button size="lg" variant="outline">
                  <Swords className="h-4 w-4" /> Find a duel
                </Button>
              </Link>
            </motion.div>

            <div className="mx-auto mt-14 grid max-w-lg grid-cols-3 gap-6">
              {[
                { value: 13600, label: "Questions", suffix: "+" },
                { value: 6, label: "Topic areas", suffix: "" },
                { value: 1000, label: "Starting rating", suffix: "" },
              ].map((stat) => (
                <div key={stat.label}>
                  <AnimatedNumber value={stat.value} suffix={stat.suffix} className="text-2xl font-bold text-foreground sm:text-3xl" />
                  <p className="label-micro mt-1">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-20 sm:px-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.2 + i * 0.06 }}
                className="glass-panel p-5"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  <feature.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-4 text-base font-semibold text-foreground">{feature.title}</h3>
                <p className="mt-1.5 text-sm text-muted-foreground">{feature.body}</p>
              </motion.div>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-4xl px-4 pb-24 sm:px-6">
          <div className="glass-panel glow-primary-lg flex flex-col items-center gap-4 p-10 text-center">
            <Flame className="h-8 w-8 text-warning" />
            <h2 className="font-display text-2xl font-bold text-foreground sm:text-3xl">
              Your placement test won't wait. Neither should you.
            </h2>
            <p className="max-w-md text-sm text-muted-foreground">
              Free to use. No credit card. Just questions, a rating, and people to beat.
            </p>
            <Link href={isAuthenticated ? "/arena" : "/signup"}>
              <Button size="lg" className="glow-primary">
                {isAuthenticated ? "Enter the arena" : "Create your free account"}
              </Button>
            </Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-border px-4 py-8 sm:px-6">
        <div className="mx-auto flex max-w-6xl flex-col items-center gap-3 text-center text-xs text-muted-foreground sm:flex-row sm:justify-between sm:text-left">
          <Logo compact />
          <p>
            Question bank sourced from{" "}
            <a
              href="https://www.indiabix.com"
              target="_blank"
              rel="noreferrer"
              className="font-medium text-foreground underline-offset-4 hover:underline"
            >
              IndiaBix
            </a>
            . All credit for question content belongs to IndiaBix.
          </p>
          <p>© {new Date().getFullYear()} QuizIt</p>
        </div>
      </footer>
    </div>
  );
}
