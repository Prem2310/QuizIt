import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  getGetIncomingChallengesQueryKey,
  getGetIncomingFriendRequestsQueryKey,
  useGetIncomingChallenges,
  useGetIncomingFriendRequests,
} from "@workspace/api-client-react";
import { toast } from "@/hooks/use-toast";
import { useAuth } from "@/stores/auth";

const POLL_MS = 5000;

/** Polls for incoming duel challenges and friend requests while the user is signed in,
 * and toasts once when a genuinely new item shows up (not on every poll tick). */
export function useIncomingActivity() {
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();
  const seenChallengeIds = useRef<Set<number> | null>(null);
  const seenRequestIds = useRef<Set<number> | null>(null);

  const challenges = useGetIncomingChallenges({
    query: { queryKey: getGetIncomingChallengesQueryKey(), enabled: isAuthenticated, refetchInterval: POLL_MS },
  });
  const requests = useGetIncomingFriendRequests({
    query: { queryKey: getGetIncomingFriendRequestsQueryKey(), enabled: isAuthenticated, refetchInterval: POLL_MS },
  });

  useEffect(() => {
    if (!challenges.data) return;
    const ids = new Set(challenges.data.map((c) => c.id));
    if (seenChallengeIds.current) {
      const fresh = challenges.data.find((c) => !seenChallengeIds.current!.has(c.id));
      if (fresh) {
        toast({ title: "Duel challenge", description: `${fresh.challenger.name} wants to duel you.` });
      }
    }
    seenChallengeIds.current = ids;
  }, [challenges.data]);

  useEffect(() => {
    if (!requests.data) return;
    const ids = new Set(requests.data.map((r) => r.id));
    if (seenRequestIds.current) {
      const fresh = requests.data.find((r) => !seenRequestIds.current!.has(r.id));
      if (fresh) {
        toast({ title: "Friend request", description: `${fresh.requester.name} wants to be friends.` });
      }
    }
    seenRequestIds.current = ids;
  }, [requests.data]);

  function invalidate() {
    void queryClient.invalidateQueries({ queryKey: getGetIncomingChallengesQueryKey() });
    void queryClient.invalidateQueries({ queryKey: getGetIncomingFriendRequestsQueryKey() });
  }

  return {
    challenges: challenges.data ?? [],
    requests: requests.data ?? [],
    count: (challenges.data?.length ?? 0) + (requests.data?.length ?? 0),
    invalidate,
  };
}
