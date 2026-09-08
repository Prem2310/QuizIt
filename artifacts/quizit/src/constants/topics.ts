import type { LucideIcon } from "lucide-react";
import { BarChart3, Brain, Calculator, Puzzle, ScrollText, Users } from "lucide-react";

/** Presentational-only icon lookup for the six real topic slugs seeded from IndiaBix. */
export const TOPIC_ICONS: Record<string, LucideIcon> = {
  aptitude: Calculator,
  "data-interpretation": BarChart3,
  "verbal-ability": ScrollText,
  "logical-reasoning": Brain,
  "verbal-reasoning": Users,
  "non-verbal-reasoning": Puzzle,
};

export function iconForTopic(slug: string): LucideIcon {
  return TOPIC_ICONS[slug] ?? Calculator;
}
