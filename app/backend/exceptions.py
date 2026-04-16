"""Domain exceptions for the Travel Companion Platform.

Services raise these exceptions. Routers catch them and convert to HTTP responses.
This keeps the service layer decoupled from FastAPI.
"""


class AppError(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    """Resource not found."""

    pass


class ConflictError(AppError):
    """Duplicate or conflicting resource."""

    pass


class AuthenticationError(AppError):
    """Authentication failed."""

    pass


class ValidationError(AppError):
    """Business rule validation failed."""

    pass
