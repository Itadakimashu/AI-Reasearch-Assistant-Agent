# 🔎 Research Agent

A modular, tool-using AI research agent built with **LangChain** + **Google Gemini**.
Give it a query — it gathers information using the right tools, then returns a
validated, structured report: topic, summary, key findings, sources, tools used,
and a confidence rating.

---

## ✨ Features

- **Real tool-calling agent loop** — powered by LangChain's LangGraph-based
  `create_agent`, not a naive single-shot prompt. The agent calls tools,
  reads results, and keeps going until it actually has enough information.
- **Multiple research tools out of the box**
  - 🌐 Live web search (DuckDuckGo)
  - 📚 Wikipedia (direct MediaWiki API, no flaky third-party wrapper)
  - 🎓 arXiv academic paper search
  - 🧮 Safe arithmetic calculator (AST-whitelisted, no `eval`/`exec`)
  - 🕒 Current date/time (for recency-aware reasoning)
  - 💾 File save tool (agent can persist findings mid-conversation)
- **Structured, validated output** via Pydantic — no more parsing free text.
- **Export to Markdown or JSON** with a single CLI flag.
- **Modular by design** — add a new tool in one file, register it in one place.
- **Centralized config & logging** — everything driven by a single `.env`.

---

## 📁 Project structure

```
research_agent/
├── main.py              # CLI entry point
├── config.py             # env-driven settings (single source of truth)
├── schemas.py             # ResearchResponse pydantic model
├── core/
│   └── agent.py            # tool-calling agent + structured output pipeline
├── tools/
│   ├── __init__.py           # tool registry — add new tools here
│   ├── web_search.py
│   ├── wikipedia_tool.py
│   ├── arxiv_tool.py
│   ├── calculator.py
│   ├── datetime_tool.py
│   └── save_tool.py
├── utils/
│   ├── logger.py
│   └── export.py             # markdown/json report export
├── requirements.txt
└── .env.example
```

---

## 🚀 Getting started

### Prerequisites

- Python 3.10+
- A [Google AI Studio](https://aistudio.google.com/apikey) API key

### Installation

```bash
git clone https://github.com/<your-username>/research-agent.git
cd research-agent

python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env            # then edit .env and add your GOOGLE_API_KEY
```

### Usage

```bash
# Interactive mode
python main.py

# One-shot query
python main.py "impact of quantum computing on modern cryptography"

# Export the report
python main.py "state of solid-state batteries in 2026" --export md
python main.py "state of solid-state batteries in 2026" --export json
python main.py "state of solid-state batteries in 2026" --export both
```

Example output:

```
=== Research Report ===
Topic:      Impact of quantum computing on modern cryptography
Confidence: medium

Summary:
Quantum computing threatens widely-used public-key schemes such as RSA and
ECC via Shor's algorithm, driving active migration toward post-quantum
cryptographic standards...

Key Findings:
  - NIST finalized several post-quantum cryptography standards
  - Symmetric-key cryptography is comparatively less at risk
  - Migration timelines vary significantly by industry

Sources:
  - Wikipedia: Post-quantum cryptography
  - NIST.gov — Post-Quantum Cryptography Standardization

Tools Used: wikipedia_tool, web_search_tool
```

---

## ⚙️ Configuration

All configuration lives in `.env`:

| Variable         | Default            | Description                                  |
| ---------------- | ------------------ | -------------------------------------------- |
| `GOOGLE_API_KEY` | _(required)_       | Gemini API key                               |
| `MODEL_NAME`     | `gemini-3.5-flash` | Chat model used by the agent                 |
| `OUTPUT_DIR`     | `outputs`          | Where `save_tool` and `--export` write files |
| `MAX_ITERATIONS` | `8`                | Max tool-calling loop iterations             |
| `VERBOSE`        | `false`            | Verbose agent tracing in the console         |
| `LOG_LEVEL`      | `INFO`             | Python logging level                         |

---

## 🧩 Adding a new tool

1. Create `tools/my_tool.py`:

   ```python
   from langchain_core.tools import tool

   @tool
   def my_tool(query: str) -> str:
       """One clear sentence describing what this does and when to use it —
       the LLM reads this docstring to decide when to call it."""
       ...
       return result
   ```

2. Register it in `tools/__init__.py`'s `get_all_tools()` list.

That's it — the agent, CLI, and export pipeline all pull from the same registry.

---

## 🛠️ Troubleshooting

| Problem                                       | Fix                                                                                           |
| --------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `outputs/` folder stays empty                 | Pass `--export md\|json\|both`, or explicitly ask the agent to save something                 |
| `ModuleNotFoundError: ddgs`                   | `pip install -U ddgs` (newer `langchain-community` needs this instead of `duckduckgo-search`) |
| `EnvironmentError: GOOGLE_API_KEY is not set` | Make sure `.env` exists in the project root and is named exactly `.env`                       |
| Agent hits max iterations                     | Raise `MAX_ITERATIONS` in `.env` or narrow the query                                          |

See [`GUIDE.md`](./GUIDE.md) for a more detailed walkthrough.

---

## 🗺️ Roadmap

- [ ] Conversation memory for multi-turn research sessions
- [ ] Additional tools (e.g. news API, code execution sandbox)
- [ ] Streaming CLI output
- [ ] Web UI

---

## 🤝 Contributing

Issues and PRs are welcome. If you're adding a tool, please include a clear
docstring (it's what the agent uses to decide when to call it) and a short
note in the README's feature list.

---
