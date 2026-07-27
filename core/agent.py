"""Core research pipeline.

Important design note
----------------------
The original prototype did `llm.bind_tools(tools).with_structured_output(schema)`
and called it once. That does NOT work as an agent: `with_structured_output`
forces the model to emit the schema on the very first turn, so the model
never actually gets to call a tool, see its result, and reason over it.

This version uses `langchain.agents.create_agent` (the LangGraph-based agent
API in modern LangChain), which runs a proper tool-calling loop AND handles
structured final output correctly - the model keeps calling tools until it
has enough information, and only then is asked to emit the `ResearchResponse`
schema, via a dedicated structured-output pass under the hood.

We additionally track every tool call ourselves from the returned message
history, so `tools_used` reflects what was actually invoked rather than
something the model recalls (and might get wrong) after the fact.
"""
from langchain.agents import create_agent
from langchain_core.messages import AIMessage

from schemas import ResearchResponse
from tools import get_all_tools
from utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an elite research assistant.

Given the user's request:
1. Decide which tool(s) are actually needed. Prefer wikipedia_tool for
   settled background/history, web_search_tool for anything current or
   time-sensitive, and arxiv_tool for academic/scientific depth.
2. Use current_datetime_tool if the query is time-relative (e.g. "latest",
   "this year", "recent").
3. Use calculator_tool for any arithmetic instead of computing it yourself.
4. Only call save_tool if the user explicitly asked you to save/export
   something.
5. Gather enough information to give a well-grounded, non-superficial
   answer. Keep track of concrete URLs/sources you learn about along the
   way so you can cite them in the final report. Do not invent sources.
"""


def build_agent(llm):
    """Build the LangGraph tool-calling agent, wired to emit a
    ResearchResponse as its structured final output."""
    tools = get_all_tools()
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        response_format=ResearchResponse,
    )


def _extract_tools_used(messages) -> list[str]:
    """Walk the message history and collect the names of every tool the
    agent actually called, in order, deduplicated."""
    tools_used: list[str] = []
    for message in messages:
        if isinstance(message, AIMessage) and message.tool_calls:
            for call in message.tool_calls:
                name = call.get("name") if isinstance(call, dict) else getattr(call, "name", None)
                if name:
                    tools_used.append(name)
    return list(dict.fromkeys(tools_used))


def run_research(query: str, llm) -> ResearchResponse:
    """Run the full research pipeline for a single query and return a
    validated ResearchResponse."""
    logger.info("Starting research for query: %s", query)
    agent = build_agent(llm)

    result = agent.invoke({"messages": [{"role": "user", "content": query}]})

    response: ResearchResponse = result["structured_response"]
    tools_used = _extract_tools_used(result.get("messages", []))
    if tools_used:
        response.tools_used = tools_used

    logger.info("Research complete. Tools used: %s", response.tools_used)
    return response
