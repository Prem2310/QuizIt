import { useLocation } from "wouter";
import { Bell, Check, Swords, UserPlus, X } from "lucide-react";
import {
  useAcceptChallenge,
  useAcceptFriendRequest,
  useDeclineChallenge,
  useDeclineFriendRequest,
} from "@workspace/api-client-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";
import { useIncomingActivity } from "@/hooks/useIncomingActivity";
import { getErrorMessage } from "@/lib/errors";
import { initialsOf } from "@/components/layout/AppShell";

export function NotificationsMenu({ className }: { className?: string }) {
  const { challenges, requests, count, invalidate } = useIncomingActivity();
  const [, navigate] = useLocation();
  const acceptChallenge = useAcceptChallenge();
  const declineChallenge = useDeclineChallenge();
  const acceptRequest = useAcceptFriendRequest();
  const declineRequest = useDeclineFriendRequest();

  async function onAcceptChallenge(id: number) {
    try {
      const result = await acceptChallenge.mutateAsync({ challengeId: id });
      invalidate();
      if (result.duel_match_id) navigate(`/duel/${result.duel_match_id}`);
    } catch (err) {
      toast({ title: "Couldn't accept challenge", description: getErrorMessage(err), variant: "destructive" });
    }
  }

  async function onDeclineChallenge(id: number) {
    try {
      await declineChallenge.mutateAsync({ challengeId: id });
      invalidate();
    } catch (err) {
      toast({ title: "Couldn't decline challenge", description: getErrorMessage(err), variant: "destructive" });
    }
  }

  async function onAcceptRequest(id: number) {
    try {
      await acceptRequest.mutateAsync({ requestId: id });
      invalidate();
      toast({ title: "Friend added" });
    } catch (err) {
      toast({ title: "Couldn't accept request", description: getErrorMessage(err), variant: "destructive" });
    }
  }

  async function onDeclineRequest(id: number) {
    try {
      await declineRequest.mutateAsync({ requestId: id });
      invalidate();
    } catch (err) {
      toast({ title: "Couldn't decline request", description: getErrorMessage(err), variant: "destructive" });
    }
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <button type="button" className={`relative rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-card hover:text-foreground ${className ?? ""}`} aria-label="Notifications">
          <Bell className="h-4.5 w-4.5" />
          {count > 0 ? (
            <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-destructive px-1 text-[9px] font-bold text-destructive-foreground">
              {count > 9 ? "9+" : count}
            </span>
          ) : null}
        </button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-80 border-border bg-popover p-0">
        <div className="max-h-96 overflow-y-auto">
          {count === 0 ? (
            <p className="p-6 text-center text-sm text-muted-foreground">You're all caught up.</p>
          ) : (
            <div className="divide-y divide-border">
              {challenges.map((c) => (
                <div key={`ch-${c.id}`} className="flex items-center gap-3 p-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                    {initialsOf(c.challenger.name)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-foreground">
                      <Swords className="mr-1 inline h-3 w-3 text-primary" /> {c.challenger.name} challenged you
                    </p>
                    <p className="truncate text-xs text-muted-foreground">{c.topic_name ?? "Mixed topics"} · {c.num_questions} questions</p>
                  </div>
                  <div className="flex shrink-0 gap-1">
                    <Button size="icon" className="h-7 w-7" disabled={acceptChallenge.isPending} onClick={() => void onAcceptChallenge(c.id)}>
                      <Check className="h-3.5 w-3.5" />
                    </Button>
                    <Button size="icon" variant="outline" className="h-7 w-7" disabled={declineChallenge.isPending} onClick={() => void onDeclineChallenge(c.id)}>
                      <X className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              ))}
              {requests.map((r) => (
                <div key={`fr-${r.id}`} className="flex items-center gap-3 p-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-secondary/10 text-xs font-bold text-secondary">
                    {initialsOf(r.requester.name)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-foreground">
                      <UserPlus className="mr-1 inline h-3 w-3 text-secondary" /> {r.requester.name} added you
                    </p>
                    <p className="truncate text-xs text-muted-foreground">@{r.requester.username}</p>
                  </div>
                  <div className="flex shrink-0 gap-1">
                    <Button size="icon" className="h-7 w-7" disabled={acceptRequest.isPending} onClick={() => void onAcceptRequest(r.id)}>
                      <Check className="h-3.5 w-3.5" />
                    </Button>
                    <Button size="icon" variant="outline" className="h-7 w-7" disabled={declineRequest.isPending} onClick={() => void onDeclineRequest(r.id)}>
                      <X className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
