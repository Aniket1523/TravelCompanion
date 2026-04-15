# Travel Companion Platform

An AI-assisted peer-to-peer platform that matches travelers on the same flight so experienced travelers (helpers) can assist those who need support (seekers).

## Problem Statement

Air travel is increasingly complex and overwhelming for elderly individuals, first-time flyers, non-tech-savvy passengers, and travelers facing language barriers. They struggle with check-in processes, airport navigation, digital tools, staff communication, and unexpected disruptions. Existing airline assistance services are limited, inconsistent, and impersonal.

## Solution

A peer-to-peer travel companion platform that connects:

- **Seekers** -- Elderly or first-time travelers who need support
- **Helpers** -- Frequent travelers willing to assist

The platform matches users on the same flight, connects them before travel, and the helper assists throughout the journey: from airport entry through boarding to arrival.

## Project Vision

To build a **global human assistance network for travel**, where no one has to travel alone or feel lost -- regardless of age, language, or experience. This is not just a product; it is a trust-based ecosystem solving a deeply human problem.

### Key Use Cases

- NRI families booking travel for elderly parents traveling alone
- First-time flyers needing guidance
- International travelers facing language barriers
- Families with infants needing an extra hand
- Passengers needing light (non-medical) assistance

### Business Model

- Per-trip commission on successful matches
- Premium verified/professional helpers
- Subscription plans for frequent users (e.g., NRI families)
- Airline and travel platform partnerships
- Add-ons: insurance, lounge access, travel services

## High-Level Architecture

```
Frontend (Next.js / Vercel)
        |
        v
Backend API (FastAPI)
        |
        v
Database (Supabase / PostgreSQL)
        |
        v
AI Matching Layer (future)
```

## Tech Stack

| Layer      | Technology         |
|------------|--------------------|
| Frontend   | Next.js            |
| Backend    | FastAPI (Python)   |
| Database   | Supabase (Postgres)|
| Hosting    | Vercel (frontend)  |
| CI/CD      | GitHub Actions     |
| Auth       | Supabase Auth      |

## Setup Instructions

### Prerequisites

- Node.js >= 18
- Python >= 3.11
- npm or yarn

### Backend

```bash
cd app/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd app/frontend
npm install
npm run dev
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### Running Tests

```bash
cd tests
pip install -r requirements.txt
pytest
```

## Project Structure

```
/
├── app/
│   ├── frontend/       # Next.js application
│   └── backend/        # FastAPI application
│       ├── routers/    # API route handlers
│       ├── services/   # Business logic layer
│       └── models/     # Data models
├── tests/              # Test suite
├── docs/               # Project documentation
└── .github/workflows/  # CI/CD pipelines
```

## Contributing

- No direct pushes to `main` -- use feature branches
- All merges require a Pull Request
- Every feature must include unit and integration tests

See [docs/AGENT.md](docs/AGENT.md) for full engineering guidelines.
