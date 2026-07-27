"""arXiv lookup tool for academic / scientific papers."""
from langchain_community.tools import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper
from langchain_core.tools import tool

from utils.logger import get_logger

logger = get_logger(__name__)
_api_wrapper = ArxivAPIWrapper(top_k_results=3, doc_content_chars_max=1500)
_arxiv = ArxivQueryRun(api_wrapper=_api_wrapper)


@tool
def arxiv_tool(query: str) -> str:
    """Search arXiv for academic papers on a scientific, mathematical, or
    technical topic. Use this when the user needs peer-reviewed / cutting-edge
    research rather than general background."""
    logger.debug("arxiv_tool called with query=%r", query)
    try:
        return _arxiv.run(query)
    except Exception as exc:
        logger.exception("arxiv_tool failed")
        return f"Arxiv search failed: {exc}"
