# Final Audit Report — TravelCompanion MVP

**Audit date:** 2026-04-17
**Scope:** Full repository at `main` (commit `df08b9e`)
**Method:** Every claim in the Copilot-generated audit was verified against actual source code with file+line citations. Findings below supersede the Copilot report where they disagree.

---

## 1. Executive Summary

The Copilot report was **directionally useful but factually unreliable** on several material points. Two of its three "CRITICAL" issues are overstated: the Flights INSERT RLS policy *does* exist (Copilot claimed it didn't), and the frontend is *fully implemented* (Copilot claimed it was a 2-button placeholder). The third ("profile not created on signup") is genuine.

The real state of the system:

- **Backend (routes, services, auth, matching):** functionally complete, well-structured, correctly layered. Rate limits, CORS, exception routing, RLS-aware client separation all in place.
- **Frontend:** a working Next.js 16 / React 19 app with login, signup, dashboard, flights, seeker, helper, matches pages — all calling the backend via a typed API client.
- **Database:** schema + RLS are 90% correct. Three concrete gaps (no profile auto-create, missing UNIQUE on matches, missing partial UNIQUE on seeker open requests) are real.
- **Deployment:** Railway + Vercel configs are correct *given dashboard settings are applied*. One CORS regex is dangerously broad for production.

**Verdict:** System is **demo-ready after 2 fixes** (signup creates profile, email-confirmation branch in frontend). It is **not production-ready** — at minimum the matching race condition, match-ownership hardening, and CORS regex must be fixed before real users.

---

## 2. Copilot Report Validation

| # | Copilot Claim | Actual Status | Evidence / Notes |
|---|---|---|---|
| 1 | Flights INSERT is broken — no INSERT RLS policy on `flights` | ❌ **INCORRECT** | `docs/schema.sql:154-157` defines `"Authenticated users can insert flights" FOR INSERT TO authenticated WITH CHECK (true)`. INSERT works in production. |
| 2 | Signup does not create a `profiles` row | ✅ **CORRECT** | `backend/services/auth_service.py:9-39` only calls `client.auth.sign_up(...)`. No `auth.users → profiles` trigger in `schema.sql`. Profile row never materializes. |
| 3 | Matching has a race condition (SELECT existing, then INSERT) | ✅ **CORRECT** | `backend/services/match_service.py:49-83` reads `existing_matches` set, then loops `insert`. `schema.sql:83-95` declares no UNIQUE on `(seeker_id, helper_id, flight_id)`. Concurrent runs can duplicate. |
| 4 | No profile creation on signup | ✅ **CORRECT** (duplicate of #2) | Same evidence. |
| 5 | `seeker_requests` has no DB-level unique for open requests | ✅ **CORRECT** | `schema.sql:56-64`: no UNIQUE, no partial index. Only app-level check in `seeker_service.py:13-22`. |
| 6 | List endpoints return raw arrays, no pagination envelope | ✅ **CORRECT** | Minor polish issue. |
| 7 | Match state transitions limited (no rejected→? or completed→?) | ✅ **CORRECT** | `match_service.py:134-140` — `{"pending":["accepted","rejected"], "accepted":["completed"]}`. Terminal states are terminal. Acceptable for MVP. |
| 8 | No validation that user is registered for the flight when creating seeker request | ✅ **CORRECT** (and also applies to helper) | `seeker_service.py:9-30` and `helper_service.py:9-39` never query `user_flights`. |
| 9 | Matching doesn't validate flight/route consistency | ✅ Self-refuted in Copilot's own report. `flight_id` (UUID) is the correct dedup key. No issue. |
| 10 | Python 3.8 compat burden | ⚠️ **PARTIAL** | CI uses Python 3.11 (`.github/workflows/ci.yml:22`). Some files use `from __future__ import annotations`. Not a real "burden." |
| 11 | Bare imports, backend is not a package | ⚠️ **PARTIAL** | Flat imports are intentional. They resolve via `--app-dir backend` at runtime (`railway.json:4`) and `sys.path.insert` in `tests/conftest.py:8`. This is a deliberate pattern, not a bug. |
| 12 | No connection pooling | ✅ **CORRECT** | Per-request `create_client(...)` in `db.py`. Fine for MVP. |
| 13 | Hard deletes instead of soft deletes | ✅ **CORRECT** | Acceptable for MVP. |
| 14 | Matching is O(seekers × helpers) | ✅ **CORRECT** | Acceptable for MVP. |
| 15 | Frontend: "placeholder UI only, 2 buttons, 0% complete, no API integration" | ❌ **INCORRECT — flatly wrong** | See §3. Frontend has 9 routed pages, typed API client (`frontend/lib/api.ts`), auth context with localStorage token persistence (`frontend/lib/auth-context.tsx`), full CRUD for flights/seeker/helper/matches, accept/decline/complete on matches. NEXT_PUBLIC_API_URL is used (`api.ts:9`). |
| 16 | "Match ownership — only participants can update, verified in code" | ⚠️ **PARTIALLY CORRECT** | App-level check exists at `match_service.py:126-132`. But the UPDATE query at `match_service.py:142-144` filters only by `id`, not by `user_id`. RLS policy at `schema.sql:204-209` is the actual enforcement. Defense-in-depth is missing one layer. |
| 17 | "Logging: minimal, missing structured format / request IDs" | ✅ **CORRECT** | `logging_config.py` + scattered `logger.info` calls; no correlation IDs. |
| 18 | "Tests: router-layer mocks only, no service-layer or integration tests" | ⚠️ **PARTIAL** | `tests/test_match_service.py` exists — it's a service-layer test. Still no integration tests against real Supabase. |
| 19 | "CORS configured with explicit origins" | ⚠️ **PARTIAL** | Explicit origins are set, BUT `allow_origin_regex=r"https://.*\.vercel\.app"` (`main.py:49`) allows **any** Vercel subdomain including attackers'. Not production-safe. |

---

## 3. Working Features (verified)

### Auth (backend + frontend)
- `POST /auth/signup` — rate limit 5/min (`routers/auth.py:32`)
- `POST /auth/login` — rate limit 10/min (`routers/auth.py:46`)
- `POST /auth/refresh` — rate limit 30/min (`routers/auth.py:60`)
- `POST /auth/logout` — authenticated, best-effort
- Frontend login+signup pages submit to backend, persist tokens in `localStorage`, redirect to `/dashboard`
- Protected route guard: `frontend/app/dashboard/layout.tsx:17-21` redirects unauthenticated users to `/login`

### Flights
- `POST /flights` / `GET /flights`
- Dedup on `(flight_number, source, destination, departure_date)` — composite UNIQUE at `schema.sql:36`
- Per-user link via `user_flights` with UNIQUE `(user_id, flight_id)` (`schema.sql:50`)
- Frontend flights page has create form + list (`frontend/app/dashboard/flights/page.tsx`)
- Insert works — RLS policy permits it

### Seeker flow
- `POST /seeker/request`, `GET /seeker/requests`, `DELETE /seeker/request/{id}`
- App-level dedup of open requests per flight
- Frontend seeker page creates requests and auto-fires `POST /matches/run` after creation (`seeker/page.tsx:68`)

### Helper flow
- `POST /helper/availability`, `GET /helper/availability`, `PATCH /helper/availability/{id}`
- DB-level UNIQUE `(user_id, flight_id)` (`schema.sql:77`)
- Frontend helper page with pause/resume toggle

### Matching engine
- `POST /matches/run` using service_role client, rate-limited 20/min
- Self-match prevention: `match_service.py:64-66`
- Skips existing pairs (in-memory set read at request start)
- 1:1 greedy pairing, updates seeker status to `matched`
- Frontend "Find matches now" button + auto-trigger on seeker/helper creation

### Match state machine
- Transitions: pending→accepted, pending→rejected, accepted→completed (`match_service.py:134-140`)
- Ownership verified at app layer + enforced by RLS
- Frontend renders role-appropriate buttons (seeker sees "Waiting…" on pending; helper sees Accept/Decline; both see Mark completed when accepted)

### CORS
- Explicit origins set, credentials enabled, correct middleware ordering (CORS outermost) — `backend/main.py:28-53`

### Rate limiting
- slowapi wired with RateLimitExceeded handler; specific decorators on auth/match endpoints

### CI
- `.github/workflows/ci.yml` — three jobs: backend lint (ruff+black), backend tests (pytest w/ PYTHONPATH=backend, 70% coverage gate), frontend lint+build with Node 20

### Deployment
- Railway: `railway.json` with `uvicorn main:app --app-dir backend` — flat imports resolve
- Vercel: minimal `vercel.json`; root directory must be set to `frontend/` in dashboard
- Python detection via flat root `requirements.txt`

---

## 4. Critical Issues (P0 — MUST FIX BEFORE DEMO)

### P0-1. Signup does not create a `profiles` row
**Evidence:** `backend/services/auth_service.py:9-39` — only calls `client.auth.sign_up`, never inserts into `profiles`. `docs/schema.sql` has no trigger on `auth.users`.

**Impact:** Every authenticated user exists in `auth.users` but not in `public.profiles`. Any feature that reads a user's profile (role, full_name, languages) returns nothing. Demo flows that reveal the counterpart user's name will show empty strings.

**Fix (choose one):**
- **A. Backend (recommended):** In `auth_service.signup()`, after `client.auth.sign_up(...)`, call a service_role client to insert a profile row with `id = result.user.id`. Service_role is required because at signup time there is no session yet if email confirmation is on.
- **B. Database trigger (cleanest, survives backend changes):** Add a `handle_new_user()` function and `on auth.users insert` trigger to schema.sql that inserts `(new.id, '', null, null)` into `profiles`. This is the canonical Supabase pattern.

### P0-2. Frontend silently "succeeds" on email-confirmation signup
**Evidence:** `backend/services/auth_service.py:33-37` returns `access_token: ""` when `result.session is None` (email-confirmation-required mode). `frontend/lib/auth-context.tsx:52-58` unconditionally writes the empty string to localStorage and sets `isAuthenticated: true`. User is redirected to `/dashboard`, and the first authenticated request returns 401.

**Impact:** If the Supabase project has email confirmation enabled, signup appears successful but the user is broken. Demo will break on the exact path a new user takes.

**Fix:**
- Backend: return a structured signal in the signup response, e.g. `{"access_token": "", "refresh_token": "", "user_id": "...", "email_confirmation_required": true}`.
- Frontend: if `email_confirmation_required`, redirect to `/signup/check-email` screen instead of `/dashboard`.
- Alternatively: disable email confirmation in Supabase for the demo environment and defer the proper fix to P1.

### P0-3. Railway build was broken until very recently — confirm current deploy is live
**Evidence:** Last three commits were all Railway build fixes (`df08b9e` restores flat root `requirements.txt`; `2be7f7f` and predecessors were failed attempts).

**Impact:** Not a code bug, but a deployment-reality check. Before demo, manually verify:
- Railway deploy on `main` is green with commit `df08b9e` or later
- Railway dashboard env vars include SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
- `/health` returns 200 at the Railway URL
- Vercel dashboard Root Directory = `frontend`, env vars include NEXT_PUBLIC_API_URL pointing at Railway, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY

---

## 5. Important Issues (P1 — FIX BEFORE HANDOVER)

### P1-1. Matching race condition
**Evidence:** `match_service.py:49-83` — SELECT-then-INSERT. `schema.sql:83-95` has no UNIQUE `(seeker_id, helper_id, flight_id)`.
**Impact:** Concurrent `/matches/run` calls for the same flight can create duplicate match rows.
**Fix:** Add `ALTER TABLE matches ADD CONSTRAINT matches_unique_triple UNIQUE (seeker_id, helper_id, flight_id);` — the DB becomes the final authority; app-level dedup set is a nicety, not correctness.

### P1-2. `update_match_status` UPDATE query is not user-scoped
**Evidence:** `match_service.py:142-144` — `update(...).eq("id", match_id)`. User ownership relies entirely on the RLS policy.
**Impact:** Defense-in-depth missing one layer. Any refactor that accidentally swaps the user-scoped client for a service-role client silently drops authorization.
**Fix:** Add `.or_(f"seeker_id.eq.{user_id},helper_id.eq.{user_id}")` to the UPDATE chain so the filter is explicit in app code.

### P1-3. `flights` INSERT loser in a race returns 500, not 409
**Evidence:** `flight_service.py:17-49` — SELECT-then-INSERT with no try/except on unique-violation. Composite UNIQUE (`schema.sql:36`) catches the race at the DB, but the exception propagates as a raw 500.
**Impact:** Users who happen to race see a confusing 500 instead of a clean retry signal. Also lacks CORS headers if the exception escapes to `ServerErrorMiddleware`.
**Fix:** Wrap the INSERT, catch unique-violation from postgrest, re-run the SELECT, and return the existing row. Standard idempotent-create pattern.

### P1-4. No validation that user is registered for a flight before seeker/helper action
**Evidence:** `seeker_service.py:9-30` and `helper_service.py:9-39` never query `user_flights`.
**Impact:** A user can create a seeker request or helper availability for any flight UUID, including flights they never joined. Matching then pairs users who can't actually meet.
**Fix:** Before insert, `SELECT 1 FROM user_flights WHERE user_id = ? AND flight_id = ?`. Raise `ValidationError` if absent.

### P1-5. Matches page shows no counterpart user info
**Evidence:** `frontend/app/dashboard/matches/page.tsx:77-78` — `getFlightFor(flightId)` only resolves flight metadata. Match API response has no nested `seeker` / `helper` user object. Frontend shows "You're helping" / "You're seeking" but never surfaces the counterpart's name, email, or PNR.
**Impact:** The core value proposition of the product (two travelers meeting) is blocked. Demo will feel hollow.
**Fix:** Either (a) backend `GET /matches` joins to `profiles` and returns counterpart full_name, or (b) add `GET /profiles/{user_id}` endpoint and frontend calls it per match.

### P1-6. CORS `allow_origin_regex` is too permissive for production
**Evidence:** `backend/main.py:49` — `allow_origin_regex=r"https://.*\.vercel\.app"`. This matches **any** Vercel subdomain including an attacker's.
**Impact:** Any actor can deploy `https://evil.vercel.app` and make cross-site authenticated requests against this API. With `allow_credentials=True`, cookies/tokens flow.
**Fix:** Scope to your project's preview pattern (e.g., `r"https://travel-companion-sky(-[a-z0-9-]+)?\.vercel\.app"`) or drop the regex entirely and rely on the explicit `allow_origins` list.

### P1-7. No 401 auto-refresh interceptor in frontend
**Evidence:** `frontend/lib/api.ts:36-39` throws on any non-2xx. The refresh_token stored at `auth-context.tsx:47` is never read. No `/auth/refresh` call site anywhere in frontend.
**Impact:** Access tokens expire after ~1 hour; users get opaque 401 toasts and have to manually log out/in.
**Fix:** In `api.ts`, on 401: call `/auth/refresh` with `localStorage.refresh_token`, update `access_token`, retry original request once. Guard with a single-flight lock to prevent stampedes on concurrent expiries.

### P1-8. Supabase env vars default to empty strings (no fail-fast)
**Evidence:** `backend/config.py:7-9` — `SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")`.
**Impact:** A misconfigured Railway deploy boots "successfully" and fails at the first DB call with a cryptic `create_client("","")` error.
**Fix:** After loading, assert all three Supabase vars are non-empty; raise on startup if missing.

### P1-9. `FRONTEND_URL` env var is dead code
**Evidence:** `backend/config.py:11` reads it; `backend/main.py` hardcodes origins instead.
**Impact:** Minor — but implies the CORS allow list can't be updated without a code change.
**Fix:** Either wire `FRONTEND_URL` into the CORS allow_origins list, or remove it from config and `.env.example`.

### P1-10. Signup has no role selection
**Evidence:** `frontend/app/signup/page.tsx` collects only email + password + confirm. `profiles.role` is nullable (`schema.sql:18`), so this compiles, but the product semantics are incomplete.
**Impact:** Users have no role; any role-based matching logic is impossible. For this MVP, a user can be both seeker and helper (the architecture supports it via independent `seeker_requests` and `helper_availability` tables), so this may be an acceptable design choice — but the `profiles.role` column is then unused and should be dropped or documented.

---

## 6. Improvements (P2 — Can Wait)

- **P2-1.** `matches.seeker_id / helper_id / flight_id` FKs lack `ON DELETE` action (schema.sql:85-87). Inconsistent with every other table. Deleting a user will fail if any match references them. Decide: cascade, or soft-delete users.
- **P2-2.** UPDATE RLS policies on `profiles`, `seeker_requests`, `matches` omit `WITH CHECK`. A row owner could theoretically update `user_id` to another UUID on their own row. Add explicit `WITH CHECK` clauses.
- **P2-3.** Missing indexes: `seeker_requests.user_id`, `helper_availability.user_id`. RLS USING filters on these; queries scan.
- **P2-4.** `flights` INSERT policy `WITH CHECK (true)` lets any authenticated user write arbitrary flight metadata. Low risk but unbounded garbage accumulation possible. Consider adding audit fields or restricting via service_role.
- **P2-5.** Duplicated `requirements.txt` at repo root and `backend/`. Drift risk. Keep one; generate the other via CI or symlink. Documented in the commit that introduced them.
- **P2-6.** `railway.json` re-installs deps in `startCommand`. Railpack already installs root `requirements.txt` during build. Redundant; move to `buildCommand` or drop.
- **P2-7.** `NEXT_PUBLIC_API_URL` silently falls back to `http://localhost:8000`. In production a missing env var ships a broken build. Add a startup assertion in `api.ts` in production mode.
- **P2-8.** Dashboard overview swallows errors with `.catch(() => [])` (`dashboard/page.tsx:23-39`). A broken backend silently shows zeros rather than an error state.
- **P2-9.** Notes field on seeker request is a single-line `<Input>` (`seeker/page.tsx:138`). Should be `<textarea>` — backend limit is 500 chars.
- **P2-10.** "Find matches now" in matches page runs matching for every user-flight in parallel (`matches/page.tsx:53`). Unscaled for users with many flights.
- **P2-11.** No structured logging / request IDs. Scattered `logger.info` calls only.
- **P2-12.** No integration tests against real Supabase. Router tests use mocks; there's a service-layer test at `tests/test_match_service.py`, but end-to-end is untested.
- **P2-13.** List endpoints return raw arrays, no `{data, total, limit, offset}` envelope.
- **P2-14.** Pydantic `Python 3.8` compat (`from __future__ import annotations`) — can be cleaned up; CI is already 3.11.

---

## 7. Final Verdict

| Dimension | Status |
|---|---|
| **MVP feature-complete** | ✅ **YES** — backend + frontend cover all MVP flows |
| **Demo-ready** | ⚠️ **YES, after P0 fixes** — profile-on-signup and email-confirmation branch are blocking |
| **Production-ready** | ❌ **NO** — P1-1 (match race), P1-2 (update scoping), P1-6 (CORS regex) must ship first. Realistically P1-5 (counterpart user info) blocks meaningful usage too |

**Copilot report accuracy:** ~60%. Two of its three "critical" findings were wrong (Flights INSERT, Frontend). Its genuine finds (profile creation, matching race, DB constraints) are real and important.

---

## 8. Recommended Fix Plan

Execute in this order. Each step is independently shippable.

### Phase 1 — Unblock demo (est. 2 hours)

1. **Add auth.users trigger for auto profile creation.** Write a migration (call it `004_handle_new_user.sql`) that defines `handle_new_user()` and `on auth.users after insert` trigger inserting `(new.id)` into `profiles`. Apply via Supabase dashboard or `mcp__supabase__apply_migration`.
2. **Fix email-confirmation signup response.** Backend: return `email_confirmation_required: true` when `session is None`. Frontend: branch in `auth-context.signup` — if flag set, route to a "Check your email" screen, don't persist empty tokens.
3. **Verify deploy.** Hit `/health` on Railway, hit `/` on Vercel, complete one full signup → login → add flight → create seeker request → run matching flow end-to-end.

### Phase 2 — Handover-grade hardening (est. 4 hours)

4. **Add UNIQUE `(seeker_id, helper_id, flight_id)` to `matches`.** Closes the race at the DB. Catch the unique-violation in `match_service.create_matches_for_flight` and continue (don't 500).
5. **Scope the UPDATE filter in `update_match_status`.** Add `seeker_id/helper_id` filter to the PostgREST `.update()` chain for defense-in-depth.
6. **Validate user-flight membership.** Add a helper `_assert_user_on_flight(client, user_id, flight_id)` and call from both `seeker_service.create_seeker_request` and `helper_service.create_helper_availability`. Raise `ValidationError` if not registered.
7. **Handle flight-create race.** Catch unique-violation in `create_or_get_flight`, re-run SELECT.
8. **Surface counterpart user info on matches.** Update `Match` response model to include nested `seeker_profile` and `helper_profile` (just `id` + `full_name`). Update `match_service.list_matches` to join. Frontend renders on the card.

### Phase 3 — Production readiness (est. 4 hours)

9. **Scope the CORS regex.** Replace `r"https://.*\.vercel\.app"` with a pattern that matches only your project's preview URLs, or drop the regex and list exact origins.
10. **Add 401 auto-refresh interceptor** in `frontend/lib/api.ts` with single-flight lock.
11. **Fail-fast env validation** in `backend/config.py` — raise at import time if Supabase vars are empty.
12. **Add partial UNIQUE on seeker_requests** — `CREATE UNIQUE INDEX ... ON seeker_requests (user_id, flight_id) WHERE status = 'open';`.
13. **Add missing indexes** on `seeker_requests.user_id`, `helper_availability.user_id`.
14. **Decide matches FK cascade policy.** Either `ON DELETE CASCADE` like the rest, or a documented soft-delete model for users.

### Phase 4 — Polish (can land incrementally)

15. Structured logging with request IDs.
16. Integration test suite against a Supabase test project.
17. Pagination envelopes on list endpoints.
18. Drop dead `FRONTEND_URL` config, collapse duplicated requirements.txt.
19. Role selection on signup if the product decides to use `profiles.role`.

---

**Report generated by:** senior-staff-level audit pass, four parallel code-verification agents + primary-source confirmation of every disputed claim.
**Sources of truth cited:** `backend/services/*`, `backend/routers/*`, `backend/main.py`, `backend/config.py`, `backend/db.py`, `docs/schema.sql`, `frontend/lib/api.ts`, `frontend/lib/auth-context.tsx`, `frontend/app/**/*.tsx`, `railway.json`, `vercel.json`, `.github/workflows/ci.yml`.
