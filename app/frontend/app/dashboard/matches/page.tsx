"use client";

import { useEffect, useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { CardSkeleton } from "@/components/ui/skeleton";
import { ToastContainer } from "@/components/ui/toast";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Match, UserFlight } from "@/lib/types";

type Filter = "all" | "pending" | "accepted" | "completed" | "rejected";

const statusVariant: Record<
  Match["status"],
  "info" | "success" | "default" | "danger"
> = {
  pending: "info",
  accepted: "success",
  completed: "default",
  rejected: "danger",
};

export default function MatchesPage() {
  const { userId } = useAuth();
  const [matches, setMatches] = useState<Match[]>([]);
  const [flights, setFlights] = useState<UserFlight[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<Filter>("all");
  const { toasts, addToast, removeToast } = useToast();

  const load = async () => {
    try {
      const [ms, fs] = await Promise.all([api.getMatches(), api.getFlights()]);
      setMatches(ms);
      setFlights(fs);
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to load", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleRunMatching = async () => {
    if (flights.length === 0) {
      addToast("Add a flight first", "error");
      return;
    }
    try {
      const results = await Promise.all(
        flights.map((uf) => api.runMatching(uf.flight_id).catch(() => null))
      );
      const created = results.reduce(
        (sum, r) => sum + (r?.matches_created ?? 0),
        0
      );
      addToast(
        created > 0
          ? `Found ${created} new match${created === 1 ? "" : "es"}`
          : "No new matches",
        created > 0 ? "success" : "info"
      );
      await load();
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Matching failed", "error");
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const getFlightFor = (flightId: string) =>
    flights.find((uf) => uf.flight_id === flightId)?.flight;

  const handleUpdate = async (
    match: Match,
    status: "accepted" | "rejected" | "completed"
  ) => {
    try {
      await api.updateMatch(match.id, status);
      addToast(`Match ${status}`, "success");
      await load();
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to update", "error");
    }
  };

  const filtered = useMemo(
    () => (filter === "all" ? matches : matches.filter((m) => m.status === filter)),
    [matches, filter]
  );

  const filters: { key: Filter; label: string }[] = [
    { key: "all", label: "All" },
    { key: "pending", label: "Pending" },
    { key: "accepted", label: "Accepted" },
    { key: "completed", label: "Completed" },
    { key: "rejected", label: "Rejected" },
  ];

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 mb-1">Matches</h1>
          <p className="text-slate-500">
            Your connections with travelers on the same flight.
          </p>
        </div>
        <Button variant="secondary" onClick={handleRunMatching}>
          <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Find matches now
        </Button>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 flex-wrap">
        {filters.map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition cursor-pointer ${
              filter === f.key
                ? "bg-primary-600 text-white shadow-sm"
                : "bg-white border border-slate-200 text-slate-600 hover:bg-slate-50"
            }`}
          >
            {f.label}
            {f.key !== "all" && (
              <span className="ml-1.5 opacity-70">
                {matches.filter((m) => m.status === f.key).length}
              </span>
            )}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-4">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : filtered.length === 0 ? (
        <Card>
          <EmptyState
            icon={
              <svg className="w-14 h-14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            }
            title={filter === "all" ? "No matches yet" : `No ${filter} matches`}
            description={
              filter === "all"
                ? "Once you register a flight and create a request or offer to help, matches will appear here."
                : "Try a different filter to see other matches."
            }
          />
        </Card>
      ) : (
        <div className="space-y-4">
          {filtered.map((match) => {
            const flight = getFlightFor(match.flight_id);
            const isHelper = match.helper_id === userId;
            const isSeeker = match.seeker_id === userId;

            return (
              <Card key={match.id} hover>
                <CardContent>
                  <div className="flex items-start justify-between gap-4 flex-wrap mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 text-white flex items-center justify-center">
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                      </div>
                      <div>
                        <div className="font-semibold text-slate-900">
                          {flight?.flight_number ?? "Flight match"}
                        </div>
                        <div className="text-xs text-slate-500">
                          {flight?.source && flight?.destination
                            ? `${flight.source} → ${flight.destination}`
                            : "—"}
                          {flight?.departure_date && ` · ${flight.departure_date}`}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {isHelper && <Badge variant="info">You&apos;re helping</Badge>}
                      {isSeeker && <Badge variant="info">You&apos;re seeking</Badge>}
                      <Badge variant={statusVariant[match.status]}>
                        {match.status}
                      </Badge>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-4 border-t border-slate-100">
                    {match.status === "pending" && isHelper && (
                      <>
                        <Button
                          size="sm"
                          onClick={() => handleUpdate(match, "accepted")}
                        >
                          Accept
                        </Button>
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => handleUpdate(match, "rejected")}
                        >
                          Decline
                        </Button>
                      </>
                    )}
                    {match.status === "pending" && isSeeker && (
                      <span className="text-xs text-slate-500 py-1.5">
                        Waiting for helper response…
                      </span>
                    )}
                    {match.status === "accepted" && (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleUpdate(match, "completed")}
                      >
                        Mark completed
                      </Button>
                    )}
                    {match.status === "completed" && (
                      <span className="text-xs text-slate-500 py-1.5">
                        Journey completed · Thanks for traveling together
                      </span>
                    )}
                    {match.status === "rejected" && (
                      <span className="text-xs text-slate-500 py-1.5">
                        This match was declined
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}
