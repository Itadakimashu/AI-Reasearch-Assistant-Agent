from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from datetime import datetime

search = DuckDuckGoSearchRun()
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

@tool
def search_tool(query: str) -> str:
    """Search the web for real-time information regarding a specific query or topic."""
    return search.run(query)

@tool
def wikipedia_tool(query: str) -> str:
    """Queries Wikipedia for historical and baseline academic overviews."""
    return wiki_tool.run(query)

@tool
def save_tool(data: str, filename: str = "research_output.txt") -> str:
    """Saves compiled research data into a local text file file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    return f"Data successfully saved to {filename}"
