# AGENT.md -- Engineering Rules for Developers and AI Agents

This document defines rules and conventions that all contributors (human and AI) must follow when working on the Travel Companion Platform.

---

## Engineering Principles

- **API-first design**: Define API contracts before implementation. Backend exposes RESTful endpoints; frontend consumes them.
- **Modular architecture**: Each domain (auth, flights, matching, etc.) lives in its own module with clear boundaries.
- **No direct DB access outside service layer**: All database operations go through the `services/` layer. Routers call services; services call the database. Never query the database directly from a router or model.
- **Separation of concerns**: Routers handle HTTP, services handle business logic, models define data shapes.
- **Fail fast, fail loud**: Return clear error messages with appropriate HTTP status codes. Do not silently swallow errors.

---

## Git Rules

- **No direct push to `main`**: The `main` branch is protected. All changes go through feature branches.
- **Use feature branches**: Branch naming convention: `feature/<short-description>`, `fix/<short-description>`, `chore/<short-description>`.
- **PR required for merge**: Every merge to `main` requires a Pull Request with at least one review.
- **Commit messages**: Use conventional commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`).
- **Keep PRs small**: One feature or fix per PR. Avoid bundling unrelated changes.

---

## Testing Rules

Every feature must include:

- **Unit tests**: Test individual functions and service methods in isolation.
- **Basic integration test**: Test the API endpoint end-to-end (request in, response out).
- Tests live in the `/tests` directory, mirroring the backend structure.
- Use `pytest` for all Python tests.
- Frontend tests use the testing framework provided by Next.js.

---

## AI Usage Rules

When using AI agents (Claude, Copilot, etc.) to contribute to this codebase:

- **Follow existing structure strictly**: Place files in the correct directories. Follow naming conventions already in use.
- **Do not duplicate logic**: Before writing new code, check if similar functionality already exists in `services/` or `routers/`.
- **Do not hallucinate schema or APIs**: Only reference tables, columns, and endpoints that are defined in `docs/API_CONTRACT.md` or exist in the codebase. If something doesn't exist yet, create it properly through the correct layers.
- **Do not create files outside the established structure**: No random utility files at the root. Follow the monorepo layout.
- **Read before writing**: Always read existing code in a file before modifying it.

---

## Database Rules

- **Use migrations only**: All schema changes must go through Supabase migrations. Never modify the database schema manually or through direct SQL in application code.
- **RLS must be enabled on all tables**: Every table must have Row Level Security policies defined. No table should be publicly accessible without RLS.
- **No raw SQL in routers**: Database queries belong in the service layer. Use parameterized queries to prevent SQL injection.
- **Schema changes require documentation**: Update `docs/API_CONTRACT.md` and relevant docs when the schema changes.

---

## Code Style

### Backend (Python)
- Formatter: `black`
- Linter: `ruff`
- Type hints required on all function signatures

### Frontend (JavaScript/TypeScript)
- Linter: `eslint`
- Use functional components and hooks (no class components)

---

## Environment

- Never commit `.env` files. Use `.env.example` as a template.
- All secrets and keys go in environment variables, never in code.
