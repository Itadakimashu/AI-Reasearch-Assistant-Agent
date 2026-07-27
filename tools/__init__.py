"""Tool registry for the research agent.

To add a new tool: write a `@tool`-decorated function in its own module in
this package (following the pattern in the existing files), then add it to
the list in `get_all_tools()` below. Nothing else needs to change - the
agent, the CLI, and the structuring step all pick tools up from here.
"""
from tools.arxiv_tool import arxiv_tool
from tools.calculator import calculator_tool
from tools.datetime_tool import current_datetime_tool
from tools.save_tool import save_tool
from tools.web_search import web_search_tool
from tools.wikipedia_tool import wikipedia_tool


def get_all_tools() -> list:
    """Return the list of tools available to the research agent."""
    return [
        web_search_tool,
        wikipedia_tool,
        arxiv_tool,
        calculator_tool,
        current_datetime_tool,
        save_tool,
    ]
