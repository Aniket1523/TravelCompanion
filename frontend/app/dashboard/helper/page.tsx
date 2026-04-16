"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { CardSkeleton } from "@/components/ui/skeleton";
import { ToastContainer } from "@/components/ui/toast";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import type { HelperAvailability, UserFlight } from "@/lib/types";

export default function HelperPage() {
  const [availabilities, setAvailabilities] = useState<HelperAvailability[]>([]);
  const [flights, setFlights] = useState<UserFlight[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [selectedFlightId, setSelectedFlightId] = useState("");
  const { toasts, addToast, removeToast } = useToast();

  const load = async () => {
    try {
      const [avs, fls] = await Promise.all([
        api.getHelperAvailability(),
        api.getFlights(),
      ]);
      setAvailabilities(avs);
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
    if (!selectedFlightId) {
      addToast("Please select a flight", "error");
      return;
    }
    setSubmitting(true);
    try {
      await api.createHelperAvailability({
        flight_id: selectedFlightId,
        is_available: true,
      });
      addToast("You're now available to help", "success");
      // Fire-and-forget matching trigger; log failure but don't block UX.
      api.runMatching(selectedFlightId).catch((e) => {
        console.warn("runMatching failed after helper availability", e);
      });
      setSelectedFlightId("");
      setShowForm(false);
      await load();
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to update", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggle = async (av: HelperAvailability) => {
    try {
      const nextAvailable = !av.is_available;
      await api.updateHelperAvailability(av.id, nextAvailable);
      addToast(
        nextAvailable ? "Marked as available" : "Marked as unavailable",
        "success"
      );
      // Re-enabling availability = new matchable state; trigger matching.
      if (nextAvailable) {
        api.runMatching(av.flight_id).catch((e) => {
          console.warn("runMatching failed after helper toggle", e);
        });
      }
      await load();
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to update", "error");
    }
  };

  const getFlightDetails = (flightId: string) => {
    return flights.find((uf) => uf.flight_id === flightId)?.flight;
  };

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 mb-1">Offer Help</h1>
          <p className="text-slate-500">
            Let travelers on your flight know you&apos;re available to lend a hand.
          </p>
        </div>
        {flights.length > 0 && (
          <Button onClick={() => setShowForm((v) => !v)}>
            <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={showForm ? "M6 18L18 6M6 6l12 12" : "M12 4v16m8-8H4"} />
            </svg>
            {showForm ? "Cancel" : "Offer on a flight"}
          </Button>
        )}
      </div>

      {showForm && flights.length > 0 && (
        <Card>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  Which flight?
                </label>
                <select
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:outline-none text-sm bg-white"
                  value={selectedFlightId}
                  onChange={(e) => setSelectedFlightId(e.target.value)}
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
              <div className="flex gap-3 justify-end">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowForm(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" loading={submitting}>
                  Mark available
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
            description="You need to register a flight before offering to help."
            action={
              <Link href="/dashboard/flights">
                <Button>Go to flights</Button>
              </Link>
            }
          />
        </Card>
      ) : availabilities.length === 0 ? (
        <Card>
          <EmptyState
            icon={
              <svg className="w-14 h-14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            }
            title="Not offering help yet"
            description="Pick a flight and mark yourself available to connect with seekers."
            action={<Button onClick={() => setShowForm(true)}>Offer on a flight</Button>}
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {availabilities.map((av) => {
            const flight = getFlightDetails(av.flight_id);
            return (
              <Card key={av.id}>
                <CardContent>
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-700 text-white flex items-center justify-center">
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                        </svg>
                      </div>
                      <div>
                        <div className="font-semibold text-slate-900">
                          {flight?.flight_number ?? "Flight"}
                        </div>
                        <div className="text-xs text-slate-500">
                          {flight?.source} → {flight?.destination}
                        </div>
                      </div>
                    </div>
                    <Badge variant={av.is_available ? "success" : "default"}>
                      {av.is_available ? "Available" : "Paused"}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                    <span className="text-xs text-slate-500">
                      {flight?.departure_date && `Departs ${flight.departure_date}`}
                    </span>
                    <Button
                      size="sm"
                      variant={av.is_available ? "secondary" : "primary"}
                      onClick={() => handleToggle(av)}
                    >
                      {av.is_available ? "Pause" : "Resume"}
                    </Button>
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
