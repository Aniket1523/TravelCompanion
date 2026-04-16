# Project Review: Travel Companion Platform

**Reviewer**: Senior System Architect (AI-assisted)
**Date**: 2026-04-13
**Scope**: Full-stack technical review (database, API, tests, CI/CD, docs)
**Codebase**: ~925 lines backend, ~247 lines tests, 6 Supabase tables

---

## 1. Project Overview

### Problem
Air travel is overwhelming for elderly travelers, first-time flyers, and non-tech-savvy passengers. Airline assistance services are limited, inconsistent, and impersonal. There is no structured peer-to-peer platform for flight-based travel assistance.

### Core Idea
Match travelers on the same flight: **seekers** (who need help) with **helpers** (experienced flyers willing to assist). The platform handles flight registration, help requests, availability, and automated matching.

### Current Scope (MVP)
- Supabase database with 6 tables, RLS, and migrations
- FastAPI backend with 8 endpoints across 4 domains
- Next.js frontend with placeholder homepage (two buttons, no logic)
- 13 passing unit tests
- GitHub Actions CI/CD pipeline
- Documentation: README, AGENT.md, ARCHITECTURE.md, API_CONTRACT.md

---

## 2. Architecture Summary

### High-Level Architecture

```
Next.js (Vercel)  ──→  FastAPI Backend  ──→  Supabase (Postgres + Auth)
                           │
                    ┌──────┼──────┐
                    │      │      │
                 Routers  Services  DB Client
                 (HTTP)   (Logic)   (Supabase SDK)
```

### Components

| Component | Tech | Status |
|-----------|------|--------|
| Frontend | Next.js 16, TypeScript | Placeholder only (title + 2 buttons) |
| Backend | FastAPI, Python | 8 endpoints implemented |
| Database | Supabase (Postgres 17) | 6 tables, RLS, indexes, migrations |
| Auth | Supabase Auth + JWT | Token validation exists, no login endpoint |
| CI/CD | GitHub Actions | Lint + test on PR |
| Hosting | Vercel (frontend) | Configured via vercel.json |

### Data Flow

```
User submits flight info
    → POST /flights (router)
        → flight_service.create_or_get_flight() (service)
            → Supabase flights table (DB, via user-scoped client)
        → flight_service.create_user_flight()
            → Supabase user_flights table

Seeker requests help
    → POST /seeker/request
        → seeker_service.create_seeker_request()
            → Supabase seeker_requests table

Helper marks availability
    → POST /helper/availability
        → helper_service.create_helper_availability()
            → Supabase helper_availability table

Match triggered
    → POST /matches/run
        → match_service.run_matching() (service_role client, bypasses RLS)
            → Reads seeker_requests + helper_availability across all users
            → Creates matches in Supabase matches table
            → Updates seeker_requests status to 'matched'
```

---

## 3. Database Design Review

### Table Structure

| Table | Purpose | PK | Notable Constraints |
|-------|---------|-----|---------------------|
| profiles | User identity + role | id (FK → auth.users) | role CHECK (seeker, helper) |
| flights | Flight definitions | id (uuid) | UNIQUE (number, source, dest, date) |
| user_flights | User ↔ flight link + PNR | id (uuid) | UNIQUE (user_id, flight_id) |
| seeker_requests | Help requests | id (uuid) | status CHECK (open, matched, completed) |
| helper_availability | Helper availability flags | id (uuid) | UNIQUE (user_id, flight_id) |
| matches | Seeker ↔ helper pairings | id (uuid) | status CHECK (pending, accepted, rejected, completed) |

### Normalization: Good

- Flights are properly separated from user_flights. A flight is defined once (number + route + date) and linked to users via a join table. PNRs are per-user-flight, not on the flight itself. This is correct 3NF.
- No data duplication across tables.

### Relationships: Correct

- All FKs reference `auth.users(id)` or `flights(id)` with `ON DELETE CASCADE` where appropriate.
- `matches` references both `seeker_id` and `helper_id` → `auth.users(id)` — correct for a two-party match.

### Constraints: Solid

- Unique constraints prevent duplicate registrations (user+flight, helper+flight).
- Check constraints enforce valid status values and roles.
- `flight_number + source + destination + departure_date` uniqueness prevents flight duplication.

### Indexing: Adequate for MVP

| Index | Covers |
|-------|--------|
| idx_flights_lookup | (flight_number, departure_date) — flight search |
| idx_user_flights_user | (user_id) — user's flights lookup |
| idx_matches_flight | (flight_id) — matches per flight |

**Missing indexes for scale:**
- `matches(seeker_id)` and `matches(helper_id)` — user's match lookup
- `seeker_requests(flight_id, status)` — matching engine query
- `helper_availability(flight_id, is_available)` — matching engine query

### What's Good
- Flight deduplication logic is sound
- PNR correctly lives in user_flights, not flights
- Schema is clean and minimal — no over-engineering

### What Needs Attention
- `profiles.role` is single-value — a user cannot be both seeker and helper on different flights. This is a design limitation that will surface quickly.
- No `updated_at` columns on any table — no audit trail for state changes.
- `seeker_requests` allows multiple open requests per user-flight (no unique constraint on user_id + flight_id + status='open').

---

### RLS Review

**Status: All 6 tables have RLS enabled.**

| Table | SELECT | INSERT | UPDATE | DELETE | Notes |
|-------|--------|--------|--------|--------|-------|
| profiles | Own only | Own only | Own only | None | No DELETE — intentional |
| flights | All authenticated | None (service_role) | None | None | Read-only for users — correct |
| user_flights | Own only | Own only | Own only | Own only | ALL policy — good |
| seeker_requests | Own only | Own only | Own only | None | Missing DELETE policy |
| helper_availability | Own only | Own only | Own only | Own only | ALL policy — good |
| matches | Seeker or helper | None (service_role) | Seeker or helper | None | INSERT via service_role — correct |

**Security Assessment: Strong for MVP.**

Verified via simulated queries (see database setup phase):
- Seeker cannot see helper's profile
- Helper cannot see seeker's requests
- Both can see a shared match
- No cross-user data leaks detected

**Gaps:**
1. `flights` has no INSERT policy for users — flights must be created via service_role or through the backend (which uses anon key + RLS). The `create_or_get_flight` service currently tries to insert with the user-scoped client, which will **fail** on a fresh flight since there's no INSERT policy on flights. This is a **latent bug** — it works in tests because tests mock the service layer.
2. No DELETE policies on `seeker_requests` or `matches` — users cannot cancel requests or remove matches.
3. `get_user_matches` in the service layer relies entirely on RLS for filtering (no explicit WHERE clause). While correct, this is opaque — an explicit filter would be defense-in-depth.

---

## 4. API Layer Review

### Endpoint Design

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | /flights | Yes | Create/reuse flight + link user |
| GET | /flights | Yes | Get user's flights |
| POST | /seeker/request | Yes | Create help request |
| GET | /seeker/requests | Yes | Get user's requests |
| POST | /helper/availability | Yes | Register availability |
| GET | /helper/availability | Yes | Get user's availability |
| POST | /matches/run | Yes | Trigger matching engine |
| GET | /matches | Yes | Get user's matches |
| GET | /health | No | Health check |

**Design: Clean and RESTful.** Endpoints are logically grouped by domain.

### Separation of Concerns: Good

```
Router (HTTP layer)         → Service (business logic)        → DB (Supabase client)
- Request validation         - Duplicate checks                - Query execution
- Auth extraction            - Data transformation             - RLS enforcement
- Response formatting        - Status updates                  
```

No business logic in routers. No HTTP concerns in services (except: services raise `HTTPException` — see weakness below).

### Validation: Adequate

Pydantic models enforce:
- `flight_number`: min 2, max 10 chars
- `pnr`: min 3, max 20 chars
- `source`/`destination`: min 2, max 10 chars
- `notes`: max 500 chars
- Required fields enforced via `Field(...)`

**Missing validation:**
- `flight_id` is accepted as string but not validated as UUID format
- No validation that a flight exists before creating a seeker request or helper availability
- No validation that the user is actually registered on the flight before requesting help

### Error Handling: Basic

- 409 for duplicate entries (flights, requests, availability)
- 404 for missing flight in match runner
- 422 for invalid Pydantic input (automatic)
- 401 for missing/invalid auth token

**Not handled:**
- Supabase connection failures (will return 500 with unhelpful stack trace)
- RLS permission denials (will return cryptic Supabase error)
- Race conditions on concurrent flight creation

### Anti-Patterns Found

1. **Services raise HTTPException** — Services should raise domain exceptions; routers should convert them to HTTP responses. Currently the service layer is coupled to FastAPI.
2. **Client instantiation in every router** — `get_supabase_client(user["access_token"])` is repeated in every handler. Should be a FastAPI dependency.
3. **No response envelope** — List endpoints return raw arrays. No metadata (total count, pagination info).

---

## 5. Code Quality & Structure

### Folder Structure: Clean

```
app/backend/
├── main.py           # App entry + router registration
├── config.py         # Environment variables
├── db.py             # Supabase client factory
├── auth.py           # JWT auth dependency
├── models/           # Pydantic request/response schemas
├── services/         # Business logic (1 file per domain)
└── routers/          # HTTP endpoints (1 file per domain)
```

Each domain (flights, seeker, helper, matches) has exactly one model, one service, and one router file. Consistent and easy to navigate.

### Naming Conventions: Consistent

- Files: snake_case
- Classes: PascalCase (Pydantic models)
- Functions: snake_case
- Endpoints: lowercase with slashes
- Database: snake_case tables and columns

### Modularity: Good

Adding a new domain (e.g., reviews, chat) would follow the same pattern: add model + service + router + register in main.py. No complex inheritance or shared state.

### Maintainability Concerns

- All files use `from __future__ import annotations` + `typing.List` in decorators — Python 3.8 compatibility tax. Upgrading Python would simplify every file.
- Import paths are bare (e.g., `from auth import get_current_user`) — relies on sys.path manipulation. Not a proper Python package.
- No `__init__.py` at the `app/backend/` level — it's not a package, it's a directory of scripts.

---

## 6. Testing & CI/CD

### Test Coverage

| Test File | Tests | What's Tested |
|-----------|-------|---------------|
| test_health.py | 2 | Health endpoint returns 200 + correct body |
| test_flights.py | 3 | Create flight, get flights, invalid body (422) |
| test_seeker.py | 2 | Create request, get requests |
| test_helper.py | 2 | Create availability, get availability |
| test_matches.py | 4 | Run match, no-helpers case, get as seeker, get as helper |

**Total: 13 tests, all passing in 0.23s.**

### Testing Strategy: Mock-based unit tests

All tests mock the service layer and auth dependency. This means:
- Fast execution (no DB needed)
- Tests verify router behavior and response shaping
- Tests do NOT verify business logic or database interaction

### What's Missing (Critical)

1. **No service-layer tests** — The matching algorithm (`run_matching`) is the core business logic and has ZERO direct tests. All match tests mock the service.
2. **No integration tests** — Nothing verifies the actual Supabase interaction.
3. **No edge case tests** — Duplicate prevention (409), self-matching prevention, concurrent requests.
4. **No auth failure tests** — What happens with expired/malformed tokens.
5. **No negative tests** — Creating a request for a non-existent flight, matching on a flight with no participants.

### CI/CD Pipeline

```yaml
on: pull_request to main
jobs:
  - Lint Backend (ruff + black)
  - Lint Frontend (next lint)
  - Test Backend (pytest)
```

**Good:** Runs on every PR. Fails on lint or test failure.
**Missing:** No frontend tests, no type checking (mypy), no coverage reporting, no deployment step.

---

## 7. Strengths

1. **Clean layered architecture** — Routers → Services → DB is consistently followed across all 4 domains. No shortcuts, no spaghetti.

2. **RLS-first security model** — Every table has RLS enabled. User-scoped Supabase clients enforce isolation at the database level. The service_role client is only used for the matching engine (privileged cross-user operation). This is the correct approach.

3. **Flight deduplication** — `create_or_get_flight` reuses existing flight records. The unique constraint on (number, source, destination, date) prevents data bloat. PNR is correctly separated into user_flights.

4. **Matching engine design** — Despite being v1, the matching engine correctly:
   - Prevents self-matching
   - Skips existing match pairs
   - Updates seeker status atomically
   - Removes matched helpers from the pool (1:1 matching)
   - Uses service_role for cross-user reads

5. **Documentation** — README, AGENT.md, ARCHITECTURE.md, and API_CONTRACT.md provide good context. AGENT.md establishes clear rules for both humans and AI agents.

6. **Monorepo structure** — Frontend and backend coexist cleanly. CI/CD handles both.

7. **Database schema quality** — Proper normalization, correct FK cascades, check constraints on all status fields, indexes on key lookup paths.

---

## 8. Weaknesses / Risks

### Design Flaws

1. **API contract diverges from implementation** — `docs/API_CONTRACT.md` describes richer schemas (needs arrays, language matching, experience levels, match scores) that don't exist in code. Anyone building against the contract will hit integration failures. This is the highest-priority documentation debt.

2. **No auth endpoints** — Token validation exists but there's no way for a user to obtain a token. POST /auth/login is documented but not implemented. The system is currently unusable end-to-end.

3. **flights table INSERT will fail via user client** — The flights table has no INSERT RLS policy for authenticated users. The `create_or_get_flight` service uses the user-scoped client, which means creating a new flight will be blocked by RLS. This is a latent production bug hidden by mocked tests.

4. **Single-role limitation** — `profiles.role CHECK (seeker, helper)` prevents a user from being a helper on one flight and a seeker on another. This will constrain the platform quickly.

### Missing Features (for MVP completeness)

- No way to cancel a seeker request
- No way to update helper availability
- No way to accept/reject a match (status update endpoint)
- No pagination on any list endpoint
- No user profile management endpoints

### Technical Risks

1. **Python 3.8 dependency** — The system runs on Python 3.8.2, requiring `from __future__ import annotations`, `typing.List` in decorators, and `eval_type_backport` for Pydantic. This is fragile and unnecessary — Python 3.8 is EOL.

2. **No logging** — Zero logging across the entire backend. Production debugging will be blind.

3. **No error recovery** — Supabase connection failures, timeout errors, and RLS denials all surface as unhandled 500 errors.

4. **No rate limiting** — POST /matches/run is an expensive operation (reads seekers + helpers + existing matches, then inserts). No throttling means a bad actor can DoS the system.

5. **CORS allows all origins with credentials** — `allow_origins=["*"]` + `allow_credentials=True` is technically invalid per the CORS spec. Browsers will reject this.

### Scaling Concerns

- Matching is O(seekers x helpers) with no indexing or batching
- No connection pooling for Supabase clients
- No caching layer
- Every request creates a new Supabase client instance

---

## 9. Improvement Recommendations

### High Priority

1. **Fix flights INSERT RLS policy** — Add an INSERT policy for authenticated users on the flights table, or switch `create_or_get_flight` to use the service_role client. Without this, flight creation is broken in production.

2. **Implement auth endpoints** — At minimum: POST /auth/signup, POST /auth/login (OTP or email/password via Supabase Auth). Without this, the API is unusable.

3. **Update API_CONTRACT.md** — Align with actual implementation. Mark unimplemented fields as "Phase 2". This prevents frontend integration confusion.

4. **Add service-layer tests** — Write direct tests for `run_matching()` with real data structures (not mocked). This is the core business logic with zero test coverage.

5. **Add logging** — At minimum: structured logging for match creation (audit trail), auth failures, and unhandled exceptions.

### Medium Priority

6. **Add match lifecycle endpoints** — PATCH /matches/{id} to accept/reject. PATCH /seeker/request/{id} to cancel.

7. **Add pagination** — All GET list endpoints should accept `limit` and `offset` query parameters.

8. **Fix CORS configuration** — Replace `allow_origins=["*"]` with explicit frontend origin.

9. **Add rate limiting** — At least on POST /matches/run (expensive) and POST /auth/login (brute force risk).

10. **Upgrade Python** — Move to 3.11+. Removes `__future__` imports, `typing.List`, and `eval_type_backport`. Cleaner code, better performance.

### Low Priority

11. **Add structured error handling** — Domain exceptions in services, HTTP mapping in routers.

12. **Use FastAPI dependency injection for DB client** — Remove `get_supabase_client(user["access_token"])` repetition from every router.

13. **Add `updated_at` columns** — Timestamp triggers for audit trails.

14. **Enhance matching algorithm** — Language matching, experience scoring, helper rating system.

15. **Add coverage reporting** — `pytest-cov` in CI pipeline with minimum threshold.

---

## 10. Readiness Assessment

### Ready for matching improvements?
**Yes, with caveats.** The matching engine is cleanly isolated in `match_service.py`. The interface is stable (takes service_client + flight_id, returns matches). You can enhance the algorithm (scoring, language matching, ratings) without touching routers or other services. However, the `profiles` table needs richer data (languages, experience) and the `seeker_requests` table needs a `needs` array to support criteria-based matching — these require schema migrations.

### Ready for UI development?
**No.** Two blockers:
1. No auth endpoints — frontend can't obtain tokens
2. Flights INSERT will fail via user client — the primary user flow is broken

Fix these two issues and the frontend can begin integrating against the API.

### Ready for AI features?
**Not yet.** Prerequisites:
1. Richer user profiles (languages, experience level, travel history)
2. Richer seeker requests (needs array, preferences)
3. A scoring interface in the match service that can be swapped for an AI model
4. The current v1 matching engine is a good placeholder — it's easy to replace the inner loop with an AI scoring function when ready.

---

## 11. Final Verdict

### Quality Assessment: **Mid-to-Senior level**

The architecture is clean, the layering is disciplined, and the database design is correct. These are senior-level decisions. The codebase is consistent, follows its own documented rules, and avoids common traps (no business logic in routers, no direct DB access from endpoints, RLS on every table).

What keeps it from "senior" overall:
- Latent production bugs (flights INSERT, CORS)
- Missing auth endpoints (system is end-to-end unusable)
- API contract / implementation drift
- No logging or error recovery
- Test coverage only at the mock layer (no business logic tests)
- Python 3.8 compatibility burden

### What Would Make It Top-Tier

1. **Zero contract drift** — API_CONTRACT.md matches implementation exactly, auto-generated from OpenAPI spec
2. **Full test pyramid** — Unit tests for services, integration tests against test database, contract tests for API
3. **Observable** — Structured logging, request tracing, error reporting (Sentry or equivalent)
4. **Production-hardened** — Rate limiting, proper CORS, env var validation, connection pooling
5. **CI/CD with deployment** — Auto-deploy to staging on PR merge, production on release tag
6. **Auth complete** — Login, signup, refresh, logout, role management

The foundation is solid. The architecture will scale. Fix the critical issues listed in Section 9 (High Priority), and this becomes a strong MVP ready for real users.
