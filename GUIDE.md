# Research Agent — Guide

A practical guide to setting up, running, and troubleshooting the research agent.

---

## 1. Setup

```bash
cd research_agent
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
```

Open `.env` and set your key:

```
GOOGLE_API_KEY=your_real_key_here
```

Get a key from [Google AI Studio](https://aistudio.google.com/apikey) if you don't have one.

---

## 2. Running it

**Interactive mode** (prompts you for a query):

```bash
python main.py
```

**One-shot mode:**

```bash
python main.py "impact of quantum computing on modern cryptography"
```

**Save the report to a file:**

```bash
python main.py "state of solid-state batteries in 2026" --export md
python main.py "state of solid-state batteries in 2026" --export json
python main.py "state of solid-state batteries in 2026" --export both
```

Without `--export`, nothing is written to `outputs/` — the report only prints to the console. See §4 if you want every run to save automatically.

---

## 3. What happens under the hood

1. Your query goes to a **LangGraph tool-calling agent** (`core/agent.py`).
2. The agent decides which tools to call — `web_search_tool`, `wikipedia_tool`, `arxiv_tool`, `calculator_tool`, `current_datetime_tool` — and loops, calling more tools as needed, until it has enough information.
3. Once satisfied, the agent produces a validated `ResearchResponse` (topic, summary, key findings, sources, tools used, confidence) — this structuring happens automatically as part of `create_agent`, not as a separate hand-rolled step.
4. `main.py` prints the report and, if `--export` was passed, writes it to `outputs/`.

The `save_tool` is different from `--export`: it's a tool the *agent itself* can choose to call mid-research, e.g. if you say "save this to a file called crypto_notes.md." It writes into the same `outputs/` directory.

---

## 4. Troubleshooting

### `outputs/` folder is empty
This is expected unless:
- You passed `--export md|json|both`, **or**
- You explicitly asked the agent to save something (e.g. "research X and save the results"), which triggers `save_tool`.

To make every run save a Markdown report automatically, change the default in `main.py`:

```python
parser.add_argument(
    "--export",
    choices=["md", "json", "both", "none"],
    default="md",   # was "none"
    ...
)
```

### `JSONDecodeError` inside `wikipedia_tool`
The third-party `wikipedia` PyPI package doesn't send a `User-Agent` header, which Wikimedia increasingly rejects with a non-JSON error page — this surfaces as a confusing `requests.exceptions.JSONDecodeError`. Fix: replace `tools/wikipedia_tool.py` with a direct MediaWiki API call using `requests` and a proper `User-Agent` (already provided in this project — see the file for the implementation). Remove `wikipedia` from `requirements.txt` once you've swapped it in; `requests` is already a dependency.

### `ModuleNotFoundError: No module named 'ddgs'`
Recent `langchain-community` versions use the `ddgs` package instead of the older `duckduckgo-search`. Run:

```bash
pip install -U ddgs
```

`requirements.txt` already lists `ddgs`, so a fresh `pip install -r requirements.txt` covers this.

### `EnvironmentError: GOOGLE_API_KEY is not set`
Your `.env` file is missing, misnamed, or wasn't loaded. Confirm:
- The file is literally named `.env` (not `.env.txt`) and sits in the project root next to `main.py`.
- You're running commands from inside `research_agent/`, not one level up.

### Agent seems to loop forever / hits max iterations
Increase `MAX_ITERATIONS` in `.env` (default `8`), or simplify the query. Very broad, multi-part queries can cause more tool calls than expected.

### Web search results look sparse or empty
DuckDuckGo occasionally rate-limits automated queries. Re-run after a short wait, or narrow the query.

---

## 5. Adding a new tool

1. Create `tools/my_tool.py`:

```python
from langchain_core.tools import tool

@tool
def my_tool(query: str) -> str:
    """One clear sentence describing what this does and when to use it —
    this docstring is what the LLM reads to decide when to call it."""
    ...
    return result
```

2. Register it in `tools/__init__.py`:

```python
from tools.my_tool import my_tool

def get_all_tools() -> list:
    return [
        web_search_tool,
        wikipedia_tool,
        arxiv_tool,
        calculator_tool,
        current_datetime_tool,
        save_tool,
        my_tool,   # add here
    ]
```

Nothing else needs to change — the agent picks it up automatically.

---

## 6. Configuration reference (`.env`)

| Variable | Default | Purpose |
|---|---|---|
| `GOOGLE_API_KEY` | *(required)* | Gemini API key |
| `MODEL_NAME` | `gemini-3.5-flash` | Chat model used by the agent |
| `OUTPUT_DIR` | `outputs` | Where `save_tool` and `--export` write files |
| `MAX_ITERATIONS` | `8` | Max tool-calling loop iterations |
| `VERBOSE` | `false` | Verbose agent tracing in the console |
| `LOG_LEVEL` | `INFO` | Python logging level (`DEBUG`, `INFO`, `WARNING`, ...) |
