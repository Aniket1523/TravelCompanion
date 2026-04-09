# Architecture Overview

## System Components

### 1. Frontend (Next.js)

- Hosted on Vercel
- Server-side rendered pages for SEO and performance
- Handles user-facing flows: seeker requests, helper availability, match status
- Communicates with backend exclusively via REST API

### 2. Backend (FastAPI)

- Core application logic and API layer
- Handles authentication, flight management, matching, and journey tracking
- Structured as:
  - `routers/` -- HTTP endpoint definitions
  - `services/` -- Business logic (matching algorithms, validation, etc.)
  - `models/` -- Pydantic models for request/response schemas

### 3. Database (Supabase / PostgreSQL)

- Managed PostgreSQL via Supabase
- Stores: users, flights, seeker requests, helper availability, matches, reviews
- Row Level Security (RLS) enabled on all tables
- All schema changes via migrations

### 4. AI Layer (Future)

- Smart matching: rank helpers by language, rating, experience
- Travel guidance: step-by-step airport instructions
- Multilingual support via LLM translation

---

## Data Flow

### Seeker Request Flow

```
Seeker (Frontend)
    |
    v
POST /seeker/request  (Backend Router)
    |
    v
SeekerService.create_request()  (Service Layer)
    |
    v
Supabase (Database)
    |
    v
POST /match/run  (Triggered manually or via automation)
    |
    v
MatchService.find_matches()  (Service Layer)
    |
    v
Returns matched helper(s) → Notification sent
```

### Helper Registration Flow

```
Helper (Frontend)
    |
    v
POST /helper/availability  (Backend Router)
    |
    v
HelperService.register_availability()  (Service Layer)
    |
    v
Supabase (Database)
```

### Match Retrieval

```
User (Frontend)
    |
    v
GET /matches  (Backend Router)
    |
    v
MatchService.get_matches()  (Service Layer)
    |
    v
Supabase (Database) → Returns match list
```

---

## Future: Event-Driven Design

As the platform scales, the architecture will evolve toward event-driven patterns:

- **Event bus**: Flight submissions and match completions emit events
- **Async workers**: Background jobs handle matching, notifications, and status updates
- **Webhooks**: Real-time notifications to users via WhatsApp/SMS (Twilio)
- **CQRS**: Separate read/write paths for high-traffic endpoints (match queries vs. submissions)

This will enable:
- Decoupled services that scale independently
- Real-time journey tracking updates
- Integration with airline APIs and third-party services
- Retry and dead-letter queue patterns for reliability
