"""Shared slowapi Limiter instance.

Lives in its own module so routers can import it without creating a circular
dependency with ``main.py``.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from config import RATE_LIMIT

limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])
