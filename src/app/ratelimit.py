# src/app/rate_limit.py
"""
In-memory request rate limiting for the Gradio application.

Tracks requests per session/IP within a sliding time window to bound
worst-case API cost from a single source. Resets on app restart and is
not shared across multiple instances — acceptable for a single-instance
MVP; revisit if scaling beyond one replica.
"""
import time
from collections import defaultdict

RATE_LIMIT_MAX_REQUESTS = 15
RATE_LIMIT_WINDOW_SECONDS = 300  # 5 minutes

_request_log: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(session_id: str) -> bool:
    """Return True if the session is within the allowed request rate."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    _request_log[session_id] = [t for t in _request_log[session_id] if t > window_start]

    if len(_request_log[session_id]) >= RATE_LIMIT_MAX_REQUESTS:
        return False

    _request_log[session_id].append(now)
    return True