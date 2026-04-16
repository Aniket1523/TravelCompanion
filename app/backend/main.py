from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import FRONTEND_URL
from exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from logging_config import logger
from rate_limit import limiter
from routers import auth, flights, helper, matches, seeker

app = FastAPI(
    title="Travel Companion Platform",
    description="API for matching travelers on the same flight",
    version="0.2.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# SlowAPIMiddleware activates Limiter.default_limits for every request and
# enforces per-route @limiter.limit decorators.
app.add_middleware(SlowAPIMiddleware)

# CORS: allow explicit frontend origin (not wildcard with credentials)
allowed_origins = [FRONTEND_URL]
if FRONTEND_URL != "http://localhost:3000":
    allowed_origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Domain exception handlers
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.message})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": exc.message})


@app.exception_handler(AuthenticationError)
async def auth_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(status_code=401, content={"detail": exc.message})


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.message})


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    # Preserve intended HTTP responses — do not bury them as generic 500s.
    if isinstance(exc, (StarletteHTTPException, FastAPIHTTPException)):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    if isinstance(exc, RateLimitExceeded):
        # slowapi's own handler is registered above; let it run.
        raise exc
    logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again later."},
    )


app.include_router(auth.router)
app.include_router(flights.router)
app.include_router(seeker.router)
app.include_router(helper.router)
app.include_router(matches.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
