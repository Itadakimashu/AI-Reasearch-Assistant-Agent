"""CLI entry point for the modular research agent.

Usage:
    python main.py "impact of quantum computing on cryptography"
    python main.py "impact of quantum computing on cryptography" --export both
    python main.py                     # prompts interactively
"""
import argparse
import sys

from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings
from core.agent import run_research
from schemas import ResearchResponse
from utils.export import export_json, export_markdown
from utils.logger import get_logger

logger = get_logger(__name__)


def build_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model=settings.model_name)


def print_report(response: ResearchResponse) -> None:
    print("\n=== Research Report ===")
    print(f"Topic:      {response.topic}")
    print(f"Confidence: {response.confidence}")
    print(f"\nSummary:\n{response.summary}")

    if response.key_findings:
        print("\nKey Findings:")
        for item in response.key_findings:
            print(f"  - {item}")

    if response.sources:
        print("\nSources:")
        for item in response.sources:
            print(f"  - {item}")

    if response.tools_used:
        print(f"\nTools Used: {', '.join(response.tools_used)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Modular AI research agent.")
    parser.add_argument(
        "query",
        nargs="*",
        help="Research query. If omitted, you'll be prompted interactively.",
    )
    parser.add_argument(
        "--export",
        choices=["md", "json", "both", "none"],
        default="none",
        help="Export the structured report to a file after running.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    query = " ".join(args.query).strip() or input("What can I help you research? ").strip()

    if not query:
        print("No query provided. Exiting.")
        sys.exit(1)

    llm = build_llm()
    print("\n--- Running Research System ---")

    try:
        response = run_research(query, llm)
    except Exception as exc:  # noqa: BLE001 - top-level CLI boundary
        logger.exception("Research run failed")
        print(f"\nAn error occurred: {exc}")
        sys.exit(1)

    print_report(response)

    if args.export in ("md", "both"):
        path = export_markdown(response)
        print(f"\nExported Markdown report to: {path}")
    if args.export in ("json", "both"):
        path = export_json(response)
        print(f"Exported JSON report to: {path}")


if __name__ == "__main__":
    main()
