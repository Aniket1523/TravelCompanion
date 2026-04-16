"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { CardSkeleton } from "@/components/ui/skeleton";
import { ToastContainer } from "@/components/ui/toast";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import type { SeekerRequest, UserFlight } from "@/lib/types";

const statusVariant: Record<
  SeekerRequest["status"],
  "info" | "success" | "default"
> = {
  open: "info",
  matched: "success",
  completed: "default",
};

export default function SeekerPage() {
  const [requests, setRequests] = useState<SeekerRequest[]>([]);
  const [flights, setFlights] = useState<UserFlight[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({ flight_id: "", notes: "" });
  const { toasts, addToast, removeToast } = useToast();

  const load = async () => {
    try {
      const [reqs, fls] = await Promise.all([
        api.getSeekerRequests(),
        api.getFlights(),
      ]);
      setRequests(reqs);
      setFlights(fls);
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to load", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.flight_id) {
      addToast("Please select a flight", "error");
      return;
    }
    setSubmitting(true);
    try {
      await api.createSeekerRequest({
        flight_id: form.flight_id,
        notes: form.notes || undefined,
      });
      addToast("Request created", "success");
      // Fire-and-forget matching trigger; log failure but don't block UX.
      api.runMatching(form.flight_id).catch((e) => {
        console.warn("runMatching failed after seeker request", e);
      });
      setForm({ flight_id: "", notes: "" });
      setShowForm(false);
      await load();
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to create request", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = async (id: string) => {
    try {
      await api.cancelSeekerRequest(id);
      addToast("Request cancelled", "success");
      await load();
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to cancel", "error");
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 mb-1">Seek Help</h1>
          <p className="text-slate-500">
            Let experienced flyers on your flight know you&apos;d appreciate a hand.
          </p>
        </div>
        {flights.length > 0 && (
          <Button onClick={() => setShowForm((v) => !v)}>
            <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={showForm ? "M6 18L18 6M6 6l12 12" : "M12 4v16m8-8H4"} />
            </svg>
            {showForm ? "Cancel" : "New request"}
          </Button>
        )}
      </div>

      {showForm && flights.length > 0 && (
        <Card>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  Flight
                </label>
                <select
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:outline-none text-sm bg-white"
                  value={form.flight_id}
                  onChange={(e) => setForm({ ...form, flight_id: e.target.value })}
                  required
                >
                  <option value="">Select a flight…</option>
                  {flights.map((uf) => {
                    const label = uf.flight
                      ? `${uf.flight.flight_number} · ${uf.flight.source} → ${uf.flight.destination} · ${uf.flight.departure_date}`
                      : `Flight (PNR ${uf.pnr})`;
                    return (
                      <option key={uf.id} value={uf.flight_id}>
                        {label}
                      </option>
                    );
                  })}
                </select>
              </div>
              <Input
                label="Notes (optional)"
                placeholder="e.g., First time flying, need help with check-in"
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
              />
              <div className="flex gap-3 justify-end">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowForm(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" loading={submitting}>
                  Create request
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <div className="space-y-4">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : flights.length === 0 ? (
        <Card>
          <EmptyState
            icon={
              <svg className="w-14 h-14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            }
            title="Add a flight first"
            description="You need to register a flight before creating help requests."
            action={
              <Link href="/dashboard/flights">
                <Button>Go to flights</Button>
              </Link>
            }
          />
        </Card>
      ) : requests.length === 0 ? (
        <Card>
          <EmptyState
            icon={
              <svg className="w-14 h-14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093M12 17h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
            title="No requests yet"
            description="Create a request to let helpers on your flight know you're looking for a companion."
            action={<Button onClick={() => setShowForm(true)}>Create request</Button>}
          />
        </Card>
      ) : (
        <div className="space-y-4">
          {requests.map((req) => (
            <Card key={req.id} hover>
              <CardContent>
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <Badge variant={statusVariant[req.status]}>
                        {req.status}
                      </Badge>
                      {req.created_at && (
                        <span className="text-xs text-slate-400">
                          {new Date(req.created_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-slate-700">
                      {req.notes || <span className="text-slate-400 italic">No notes</span>}
                    </p>
                  </div>
                  {req.status === "open" && (
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleCancel(req.id)}
                    >
                      Cancel
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}
