import type {
  AuthResponse,
  HelperAvailability,
  Match,
  SeekerRequest,
  UserFlight,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...((options.headers as Record<string, string>) || {}),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_URL}${path}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${res.status}`);
    }

    return res.json();
  }

  // Auth
  async signup(email: string, password: string): Promise<AuthResponse> {
    return this.request<AuthResponse>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    return this.request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async logout(): Promise<void> {
    await this.request("/auth/logout", { method: "POST" });
  }

  async resendConfirmation(email: string): Promise<{ message: string }> {
    return this.request<{ message: string }>("/auth/resend-confirmation", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  }

  // Flights
  async createFlight(data: {
    flight_number: string;
    source: string;
    destination: string;
    departure_date: string;
    pnr: string;
  }): Promise<UserFlight> {
    return this.request<UserFlight>("/flights", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getFlights(): Promise<UserFlight[]> {
    return this.request<UserFlight[]>("/flights");
  }

  // Seeker
  async createSeekerRequest(data: {
    flight_id: string;
    notes?: string;
  }): Promise<SeekerRequest> {
    return this.request<SeekerRequest>("/seeker/request", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getSeekerRequests(): Promise<SeekerRequest[]> {
    return this.request<SeekerRequest[]>("/seeker/requests");
  }

  async cancelSeekerRequest(requestId: string): Promise<void> {
    await this.request(`/seeker/request/${requestId}`, { method: "DELETE" });
  }

  // Helper
  async createHelperAvailability(data: {
    flight_id: string;
    is_available: boolean;
  }): Promise<HelperAvailability> {
    return this.request<HelperAvailability>("/helper/availability", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getHelperAvailability(): Promise<HelperAvailability[]> {
    return this.request<HelperAvailability[]>("/helper/availability");
  }

  async updateHelperAvailability(
    id: string,
    is_available: boolean
  ): Promise<HelperAvailability> {
    return this.request<HelperAvailability>(`/helper/availability/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ is_available }),
    });
  }

  // Matches
  async runMatching(flight_id: string) {
    return this.request<{ matches_created: number; matches: Match[] }>(
      "/matches/run",
      {
        method: "POST",
        body: JSON.stringify({ flight_id }),
      }
    );
  }

  async getMatches(): Promise<Match[]> {
    return this.request<Match[]>("/matches");
  }

  async updateMatch(matchId: string, status: string): Promise<Match> {
    return this.request<Match>(`/matches/${matchId}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
  }
}

export const api = new ApiClient();
