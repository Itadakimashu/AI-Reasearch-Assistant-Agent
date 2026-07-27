"""Wikipedia lookup tool for encyclopedic / historical background.

Talks to the MediaWiki API directly via `requests` instead of the
third-party `wikipedia` PyPI package. That package doesn't send a
User-Agent header, and Wikimedia increasingly rejects/rate-limits such
requests with a non-JSON response - which surfaces as a confusing
`JSONDecodeError` deep inside the package. Going direct lets us set a
proper User-Agent and handle errors cleanly.
"""
import requests
from langchain_core.tools import tool

from utils.logger import get_logger

logger = get_logger(__name__)

_API_URL = "https://en.wikipedia.org/w/api.php"
_HEADERS = {
    "User-Agent": "ResearchAgent/1.0 (personal project; contact: your-email@example.com)"
}
_TIMEOUT = 10
_MAX_RESULTS = 2
_MAX_CHARS = 1500


def _search_titles(query: str, limit: int = _MAX_RESULTS) -> list[str]:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "format": "json",
    }
    resp = requests.get(_API_URL, params=params, headers=_HEADERS, timeout=_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return [hit["title"] for hit in data.get("query", {}).get("search", [])]


def _get_summary(title: str, max_chars: int = _MAX_CHARS) -> str:
    params = {
        "action": "query",
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "titles": title,
        "format": "json",
    }
    resp = requests.get(_API_URL, params=params, headers=_HEADERS, timeout=_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        extract = page.get("extract", "").strip()
        if extract:
            return extract[:max_chars]
    return ""


@tool
def wikipedia_tool(query: str) -> str:
    """Look up an encyclopedic overview of a topic, person, or event on
    Wikipedia. Best for well-established background and historical facts."""
    logger.debug("wikipedia_tool called with query=%r", query)
    try:
        titles = _search_titles(query)
        if not titles:
            return f"No Wikipedia article found for '{query}'."

        sections = []
        for title in titles:
            summary = _get_summary(title)
            if summary:
                sections.append(f"## {title}\n{summary}")

        if not sections:
            return f"Found matching titles ({', '.join(titles)}) but could not retrieve content."
        return "\n\n".join(sections)

    except requests.exceptions.RequestException as exc:
        logger.exception("wikipedia_tool network/API failure")
        return f"Wikipedia lookup failed (network/API error): {exc}"
    except Exception as exc:
        logger.exception("wikipedia_tool failed")
        return f"Wikipedia lookup failed: {exc}"