# API Contract

Base URL: `/`

All endpoints return JSON. Authentication is via Bearer token (Supabase JWT) unless noted otherwise.

Rate limit: 60 requests/minute per IP (configurable via `RATE_LIMIT` env var).

---

## POST /auth/signup

Register a new user via email/password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "refresh-token-here",
  "user_id": "uuid"
}
```

**Errors:**
- `409` — Email already registered
- `422` — Invalid email (min 5 chars) or password (min 6 chars)

---

## POST /auth/login

Authenticate with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "refresh-token-here",
  "user_id": "uuid"
}
```

**Errors:**
- `401` — Invalid email or password

---

## POST /auth/refresh

Refresh an expired access token.

**Request:**
```json
{
  "refresh_token": "refresh-token-here"
}
```

**Response (200):**
```json
{
  "access_token": "new-access-token",
  "refresh_token": "new-refresh-token",
  "user_id": "uuid"
}
```

---

## POST /auth/logout

Sign out the current user. Requires auth.

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

---

## POST /flights

Create or reuse a flight, then link the authenticated user to it with their PNR. Requires auth.

**Request:**
```json
{
  "flight_number": "AI101",
  "source": "BLR",
  "destination": "DEL",
  "departure_date": "2026-06-15",
  "pnr": "PNR001"
}
```

**Validation:**
- `flight_number`: 2-10 chars
- `source`, `destination`: 2-10 chars
- `pnr`: 3-20 chars

**Response (201):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "flight_id": "uuid",
  "pnr": "PNR001",
  "created_at": "2026-06-01T12:00:00",
  "updated_at": "2026-06-01T12:00:00",
  "flight": {
    "id": "uuid",
    "flight_number": "AI101",
    "source": "BLR",
    "destination": "DEL",
    "departure_date": "2026-06-15",
    "created_at": "2026-06-01T12:00:00",
    "updated_at": "2026-06-01T12:00:00"
  }
}
```

**Errors:**
- `409` — Already registered for this flight
- `422` — Invalid body

---

## GET /flights

Get all flights for the authenticated user. Requires auth.

**Query Parameters:**
- `limit` (optional, default 50, max 100)
- `offset` (optional, default 0)

**Response (200):**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "flight_id": "uuid",
    "pnr": "PNR001",
    "created_at": "2026-06-01T12:00:00",
    "updated_at": "2026-06-01T12:00:00",
    "flight": {
      "id": "uuid",
      "flight_number": "AI101",
      "source": "BLR",
      "destination": "DEL",
      "departure_date": "2026-06-15",
      "created_at": "2026-06-01T12:00:00",
      "updated_at": "2026-06-01T12:00:00"
    }
  }
]
```

---

## POST /seeker/request

Create a help request for a flight. Requires auth.

**Request:**
```json
{
  "flight_id": "uuid",
  "notes": "Need help with check-in"
}
```

**Validation:**
- `notes`: optional, max 500 chars

**Response (201):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "flight_id": "uuid",
  "notes": "Need help with check-in",
  "status": "open",
  "created_at": "2026-06-01T12:00:00",
  "updated_at": "2026-06-01T12:00:00"
}
```

**Errors:**
- `409` — Already have an open request for this flight

---

## GET /seeker/requests

Get all help requests for the authenticated seeker. Requires auth.

**Query Parameters:**
- `limit` (optional, default 50, max 100)
- `offset` (optional, default 0)

**Response (200):** Array of seeker request objects.

---

## DELETE /seeker/request/{request_id}

Cancel an open seeker request. Requires auth.

**Response (200):**
```json
{
  "id": "uuid",
  "status": "cancelled"
}
```

**Errors:**
- `404` — Request not found
- `409` — Only open requests can be cancelled

---

## POST /helper/availability

Register helper availability for a flight. Requires auth.

**Request:**
```json
{
  "flight_id": "uuid",
  "is_available": true
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "flight_id": "uuid",
  "is_available": true,
  "created_at": "2026-06-01T12:00:00",
  "updated_at": "2026-06-01T12:00:00"
}
```

**Errors:**
- `409` — Already have availability set for this flight

---

## PATCH /helper/availability/{availability_id}

Update helper availability. Requires auth.

**Request:**
```json
{
  "is_available": false
}
```

**Response (200):** Updated availability object.

**Errors:**
- `404` — Availability entry not found

---

## GET /helper/availability

Get all availability entries for the authenticated helper. Requires auth.

**Query Parameters:**
- `limit` (optional, default 50, max 100)
- `offset` (optional, default 0)

**Response (200):** Array of helper availability objects.

---

## POST /matches/run

Trigger the matching engine for a specific flight. Requires auth.

Uses service_role client to read across users and create matches.

**Request:**
```json
{
  "flight_id": "uuid"
}
```

**Response (200):**
```json
{
  "matches_created": 1,
  "matches": [
    {
      "id": "uuid",
      "seeker_id": "uuid",
      "helper_id": "uuid",
      "flight_id": "uuid",
      "status": "pending",
      "created_at": "2026-06-01T12:00:00",
      "updated_at": "2026-06-01T12:00:00"
    }
  ]
}
```

**Errors:**
- `404` — Flight not found

---

## GET /matches

Get matches for the authenticated user (as seeker or helper). Requires auth.

**Query Parameters:**
- `limit` (optional, default 50, max 100)
- `offset` (optional, default 0)

**Response (200):** Array of match objects.

---

## PATCH /matches/{match_id}

Update match status. Requires auth. Only participants can update.

**Request:**
```json
{
  "status": "accepted"
}
```

**Valid transitions:**
- `pending` -> `accepted` or `rejected`
- `accepted` -> `completed`

**Response (200):** Updated match object.

**Errors:**
- `404` — Match not found
- `409` — Invalid status transition

---

## GET /health

Health check endpoint (no auth required).

**Response (200):**
```json
{
  "status": "ok"
}
```
