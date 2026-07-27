import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from tools import search_tool, wikipedia_tool, save_tool

load_dotenv()

# 1. Define structured response layout
class ResearchResponse(BaseModel):
    topic: str = Field(description="The core topic or query researched.")
    summary: str = Field(description="A deep, synthesized summary of the findings.")
    sources: list[str] = Field(description="List of URLs or source names used during information gathering.")
    tools_used: list[str] = Field(description="List of tools that were invoked during the research process.")

# 2. Instantiate current active model (Removed deprecated 'temperature' parameter)
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")

# 3. Attach both the available tools AND bind the structured schema
tools = [search_tool, wikipedia_tool, save_tool]
llm_with_tools_and_structure = llm.bind_tools(tools).with_structured_output(ResearchResponse)

# 4. Clean System prompt instructing the LLM to call tools first, then format
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an elite research assistant. Look at the user's request. "
        "First, invoke the necessary tools (like search_tool or wikipedia_tool) to gather information. "
        "If you save information, remember to call save_tool. "
        "Once all information is gathered, compile your research into the requested structured layout."
    ),
    ("human", "{query}")
])

# 5. Build the pipeline
research_chain = prompt | llm_with_tools_and_structure

# 6. Execute
query = input("What can I help you research? ")
print("\n--- Running Research System ---")

try:
    # Model automatically handles routing internally and outputs your Pydantic object
    structured_response = research_chain.invoke({"query": query})
    
    print("\n--- Structured Research Results ---")
    print(f"Topic: {structured_response.topic}")
    print(f"Summary: {structured_response.summary}")
    print(f"Sources: {structured_response.sources}")
    print(f"Tools Used: {structured_response.tools_used}")

except Exception as e:
    print(f"\nAn error occurred: {e}")
