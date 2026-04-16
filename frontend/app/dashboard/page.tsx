"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { Match, SeekerRequest, UserFlight } from "@/lib/types";

interface Stats {
  flights: number;
  requests: number;
  matches: number;
  pending: number;
}

export default function DashboardOverview() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentFlights, setRecentFlights] = useState<UserFlight[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const [flights, reqs, matches] = await Promise.all([
          api.getFlights(),
          api.getSeekerRequests().catch(() => [] as SeekerRequest[]),
          api.getMatches().catch(() => [] as Match[]),
        ]);
        setStats({
          flights: flights.length,
          requests: reqs.length,
          matches: matches.length,
          pending: matches.filter((m) => m.status === "pending").length,
        });
        setRecentFlights(flights.slice(0, 3));
      } catch {
        setStats({ flights: 0, requests: 0, matches: 0, pending: 0 });
      }
    })();
  }, []);

  const statCards = [
    {
      label: "My Flights",
      value: stats?.flights ?? "—",
      href: "/dashboard/flights",
      color: "from-primary-500 to-primary-700",
      icon: (
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
      ),
    },
    {
      label: "Help Requests",
      value: stats?.requests ?? "—",
      href: "/dashboard/seeker",
      color: "from-blue-500 to-blue-700",
      icon: (
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093M12 17h.01" />
      ),
    },
    {
      label: "Total Matches",
      value: stats?.matches ?? "—",
      href: "/dashboard/matches",
      color: "from-emerald-500 to-emerald-700",
      icon: (
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      ),
    },
    {
      label: "Pending",
      value: stats?.pending ?? "—",
      href: "/dashboard/matches",
      color: "from-amber-500 to-amber-600",
      icon: (
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      ),
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 mb-1">Welcome back</h1>
        <p className="text-slate-500">
          Here&apos;s what&apos;s happening across your flights.
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => (
          <Link key={card.label} href={card.href}>
            <Card hover className="h-full">
              <CardContent>
                <div
                  className={`inline-flex w-10 h-10 rounded-xl bg-gradient-to-br ${card.color} items-center justify-center mb-4`}
                >
                  <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    {card.icon}
                  </svg>
                </div>
                <div className="text-2xl font-bold text-slate-900 mb-0.5">
                  {card.value}
                </div>
                <div className="text-sm text-slate-500">{card.label}</div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {/* Quick actions */}
      <div>
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Quick actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link href="/dashboard/flights">
            <Card hover>
              <CardContent className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-xl bg-primary-50 text-primary-600 flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-1">Add a flight</h3>
                  <p className="text-sm text-slate-500">
                    Register your next trip to join a flight group.
                  </p>
                </div>
              </CardContent>
            </Card>
          </Link>
          <Link href="/dashboard/seeker">
            <Card hover>
              <CardContent className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-1">Request help</h3>
                  <p className="text-sm text-slate-500">
                    Need a travel companion? Create a request.
                  </p>
                </div>
              </CardContent>
            </Card>
          </Link>
          <Link href="/dashboard/helper">
            <Card hover>
              <CardContent className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-1">Offer help</h3>
                  <p className="text-sm text-slate-500">
                    Experienced traveler? Mark yourself available.
                  </p>
                </div>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>

      {/* Recent flights */}
      {recentFlights.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Recent flights</h2>
            <Link
              href="/dashboard/flights"
              className="text-sm font-medium text-primary-600 hover:underline"
            >
              View all
            </Link>
          </div>
          <div className="space-y-3">
            {recentFlights.map((uf) => (
              <Card key={uf.id}>
                <CardContent className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-primary-50 text-primary-600 flex items-center justify-center flex-shrink-0">
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900">
                        {uf.flight?.flight_number ?? "Flight"}
                      </div>
                      <div className="text-sm text-slate-500">
                        {uf.flight?.source} → {uf.flight?.destination}
                        {uf.flight?.departure_date && ` · ${uf.flight.departure_date}`}
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-slate-400 font-mono">PNR {uf.pnr}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
