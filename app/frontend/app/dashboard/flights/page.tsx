"use client";

import { FormEvent, useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { CardSkeleton } from "@/components/ui/skeleton";
import { ToastContainer } from "@/components/ui/toast";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import type { UserFlight } from "@/lib/types";

export default function FlightsPage() {
  const [flights, setFlights] = useState<UserFlight[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const { toasts, addToast, removeToast } = useToast();

  const [form, setForm] = useState({
    flight_number: "",
    source: "",
    destination: "",
    departure_date: "",
    pnr: "",
  });

  const loadFlights = async () => {
    try {
      const data = await api.getFlights();
      setFlights(data);
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to load flights", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFlights();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.createFlight(form);
      addToast("Flight added successfully", "success");
      setForm({
        flight_number: "",
        source: "",
        destination: "",
        departure_date: "",
        pnr: "",
      });
      setShowForm(false);
      await loadFlights();
    } catch (err) {
      addToast(err instanceof Error ? err.message : "Failed to add flight", "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 mb-1">My Flights</h1>
          <p className="text-slate-500">
            Register your trips to join flight groups and find companions.
          </p>
        </div>
        <Button onClick={() => setShowForm((v) => !v)}>
          <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={showForm ? "M6 18L18 6M6 6l12 12" : "M12 4v16m8-8H4"} />
          </svg>
          {showForm ? "Cancel" : "Add flight"}
        </Button>
      </div>

      {showForm && (
        <Card>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Flight number"
                  placeholder="6E 1234"
                  value={form.flight_number}
                  onChange={(e) => setForm({ ...form, flight_number: e.target.value })}
                  required
                />
                <Input
                  label="PNR"
                  placeholder="ABCD12"
                  value={form.pnr}
                  onChange={(e) => setForm({ ...form, pnr: e.target.value })}
                  required
                />
                <Input
                  label="From"
                  placeholder="BLR"
                  value={form.source}
                  onChange={(e) =>
                    setForm({ ...form, source: e.target.value.toUpperCase() })
                  }
                  required
                  maxLength={3}
                />
                <Input
                  label="To"
                  placeholder="DEL"
                  value={form.destination}
                  onChange={(e) =>
                    setForm({ ...form, destination: e.target.value.toUpperCase() })
                  }
                  required
                  maxLength={3}
                />
                <Input
                  label="Departure date"
                  type="date"
                  value={form.departure_date}
                  onChange={(e) => setForm({ ...form, departure_date: e.target.value })}
                  required
                  className="sm:col-span-2"
                />
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
                  Add flight
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            title="No flights yet"
            description="Add your first flight to start connecting with fellow travelers."
            action={<Button onClick={() => setShowForm(true)}>Add your first flight</Button>}
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {flights.map((uf) => (
            <Card key={uf.id} hover>
              <CardContent>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 text-white flex items-center justify-center">
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900">
                        {uf.flight?.flight_number ?? "Flight"}
                      </div>
                      <div className="text-xs text-slate-400 font-mono">PNR {uf.pnr}</div>
                    </div>
                  </div>
                  <Badge variant="info">Registered</Badge>
                </div>

                <div className="flex items-center gap-3 text-sm">
                  <div className="flex-1">
                    <div className="text-lg font-bold text-slate-900">
                      {uf.flight?.source ?? "—"}
                    </div>
                    <div className="text-xs text-slate-500">Origin</div>
                  </div>
                  <div className="flex-1 text-center">
                    <svg className="w-6 h-6 text-slate-300 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  </div>
                  <div className="flex-1 text-right">
                    <div className="text-lg font-bold text-slate-900">
                      {uf.flight?.destination ?? "—"}
                    </div>
                    <div className="text-xs text-slate-500">Destination</div>
                  </div>
                </div>

                {uf.flight?.departure_date && (
                  <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-slate-500">
                    Departs {uf.flight.departure_date}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}
