"""Tool exposing the current date/time so the agent can reason about recency."""
from datetime import datetime, timezone

from langchain_core.tools import tool


@tool
def current_datetime_tool(_: str = "") -> str:
    """Return the current UTC date and time. Use this to reason about what
    'today', 'this year', or 'recent' means, or to timestamp findings."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
