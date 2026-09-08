/**
 * Central runtime configuration.
 * VITE_API_BASE_URL points at the existing FastAPI backend (e.g. http://localhost:8000).
 */
const RAW_BASE = (import.meta.env["VITE_API_BASE_URL"] as string | undefined) ?? "";

export const API_BASE_URL = RAW_BASE.replace(/\/+$/, "") || "http://localhost:8000";

/** Derive the websocket origin from the API base so we never hardcode localhost. */
export function wsUrl(path: string): string {
  const base = API_BASE_URL.replace(/^http/, "ws");
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

export const WS_PATHS = {
  /** WS /api/ws/matchmaking — join the queue, get paired (cookie authenticated). */
  matchmaking: "/api/ws/matchmaking",
  /** WS /api/ws/duels/{id} — the live duel game loop (cookie authenticated). */
  duel: (duelId: number | string) => `/api/ws/duels/${duelId}`,
} as const;
