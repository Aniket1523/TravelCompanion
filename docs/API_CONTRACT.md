# API Contract

Base URL: `/api/v1`

All endpoints return JSON. Authentication is via Bearer token (Supabase JWT) unless noted otherwise.

---

## POST /auth/login

Authenticate a user via OTP-based login.

**Request:**
```json
{
  "phone": "+919876543210",
  "otp": "123456"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "phone": "+919876543210",
    "role": "seeker | helper",
    "name": "Ravi Kumar"
  }
}
```

**Error (401):**
```json
{
  "detail": "Invalid OTP"
}
```

---

## POST /flights

Register a flight for the authenticated user.

**Request:**
```json
{
  "flight_number": "AI101",
  "date": "2025-06-15",
  "departure_airport": "BLR",
  "arrival_airport": "DEL",
  "departure_time": "2025-06-15T06:00:00Z",
  "arrival_time": "2025-06-15T08:30:00Z"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "flight_number": "AI101",
  "date": "2025-06-15",
  "departure_airport": "BLR",
  "arrival_airport": "DEL",
  "departure_time": "2025-06-15T06:00:00Z",
  "arrival_time": "2025-06-15T08:30:00Z",
  "user_id": "uuid",
  "created_at": "2025-06-01T12:00:00Z"
}
```

---

## POST /seeker/request

Create a help request for a seeker on a specific flight.

**Request:**
```json
{
  "flight_id": "uuid",
  "needs": ["airport_navigation", "check_in_help", "language_support"],
  "languages_spoken": ["hindi", "english"],
  "special_notes": "My father is 72 and unfamiliar with airports."
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "flight_id": "uuid",
  "user_id": "uuid",
  "needs": ["airport_navigation", "check_in_help", "language_support"],
  "languages_spoken": ["hindi", "english"],
  "special_notes": "My father is 72 and unfamiliar with airports.",
  "status": "pending",
  "created_at": "2025-06-01T12:00:00Z"
}
```

---

## POST /helper/availability

Register a helper's availability for a specific flight.

**Request:**
```json
{
  "flight_id": "uuid",
  "languages_spoken": ["hindi", "english", "kannada"],
  "experience_level": "frequent_flyer",
  "can_assist_with": ["airport_navigation", "check_in_help", "boarding", "language_support"]
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "flight_id": "uuid",
  "user_id": "uuid",
  "languages_spoken": ["hindi", "english", "kannada"],
  "experience_level": "frequent_flyer",
  "can_assist_with": ["airport_navigation", "check_in_help", "boarding", "language_support"],
  "status": "available",
  "created_at": "2025-06-01T12:00:00Z"
}
```

---

## POST /match/run

Trigger the matching engine for a specific flight. Finds compatible helper-seeker pairs.

**Request:**
```json
{
  "flight_id": "uuid"
}
```

**Response (200):**
```json
{
  "matches_created": 2,
  "matches": [
    {
      "id": "uuid",
      "seeker_request_id": "uuid",
      "helper_availability_id": "uuid",
      "score": 0.92,
      "status": "proposed"
    }
  ]
}
```

---

## GET /matches

Retrieve matches for the authenticated user (as seeker or helper).

**Query Parameters:**
- `status` (optional): `proposed | accepted | in_progress | completed`
- `flight_id` (optional): filter by flight

**Response (200):**
```json
{
  "matches": [
    {
      "id": "uuid",
      "flight": {
        "flight_number": "AI101",
        "date": "2025-06-15",
        "departure_airport": "BLR",
        "arrival_airport": "DEL"
      },
      "seeker": {
        "name": "Ravi Kumar",
        "needs": ["airport_navigation", "check_in_help"]
      },
      "helper": {
        "name": "Priya Sharma",
        "experience_level": "frequent_flyer"
      },
      "score": 0.92,
      "status": "accepted",
      "journey_status": "matched",
      "created_at": "2025-06-01T12:00:00Z"
    }
  ]
}
```

**Journey Status Values:** `matched | met_at_airport | boarded | landed`

---

## GET /health

Health check endpoint (no auth required).

**Response (200):**
```json
{
  "status": "ok"
}
```
