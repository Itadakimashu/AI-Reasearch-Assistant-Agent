"""Real-time web search tool backed by DuckDuckGo."""
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

from utils.logger import get_logger

logger = get_logger(__name__)
_search = DuckDuckGoSearchRun()


@tool
def web_search_tool(query: str) -> str:
    """Search the live web for current events, news, or any information not
    well covered by an encyclopedia. Use this for anything time-sensitive."""
    logger.debug("web_search_tool called with query=%r", query)
    try:
        return _search.run(query)
    except Exception as exc:
        logger.exception("web_search_tool failed")
        return f"Web search failed: {exc}"
