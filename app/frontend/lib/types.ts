export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user_id: string;
}

export interface Flight {
  id: string;
  flight_number: string;
  source: string;
  destination: string;
  departure_date: string;
  created_at?: string;
  updated_at?: string;
}

export interface UserFlight {
  id: string;
  user_id: string;
  flight_id: string;
  pnr: string;
  created_at?: string;
  updated_at?: string;
  flight?: Flight;
}

export interface SeekerRequest {
  id: string;
  user_id: string;
  flight_id: string;
  notes?: string;
  status: "open" | "matched" | "completed";
  created_at?: string;
  updated_at?: string;
}

export interface HelperAvailability {
  id: string;
  user_id: string;
  flight_id: string;
  is_available: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Match {
  id: string;
  seeker_id: string;
  helper_id: string;
  flight_id: string;
  status: "pending" | "accepted" | "rejected" | "completed";
  created_at?: string;
  updated_at?: string;
}

export interface ApiError {
  detail: string;
}
