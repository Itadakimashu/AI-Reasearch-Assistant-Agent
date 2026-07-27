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

SYSTEM_PROMPT = """You are an elite research assistant, but you must be
economical with tool calls — each one costs real API quota.

Given the user's request:
1. Do ONE well-chosen search first. Only do a second or third search if the
   first result was clearly insufficient to answer the question.
2. Do NOT branch into researching every entity/company/example you come
   across (e.g. if the topic mentions "battery makers", don't research each
   maker individually unless the user asked for a company-by-company
   breakdown). Prefer one broad search over many narrow ones.
3. Prefer wikipedia_tool for settled background, web_search_tool for
   anything current, arxiv_tool for academic depth.
4. Use current_datetime_tool only if the query is explicitly time-relative.
5. Use calculator_tool for arithmetic instead of computing it yourself.
6. Only call save_tool if the user explicitly asked you to save something.
7. Stop as soon as you have enough to answer well. More tool calls is not
   automatically a better answer.
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
