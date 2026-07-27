"""Export a ResearchResponse into human-readable Markdown or machine-readable JSON."""
import json
import os
from datetime import datetime

from config import settings
from schemas import ResearchResponse


def _timestamped_path(topic: str, extension: str) -> str:
    slug = "".join(c if c.isalnum() else "_" for c in topic.lower())[:40].strip("_") or "research"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(settings.output_dir, f"{slug}_{stamp}.{extension}")


def export_markdown(response: ResearchResponse) -> str:
    path = _timestamped_path(response.topic, "md")
    lines = [
        f"# {response.topic}",
        "",
        f"**Confidence:** {response.confidence}",
        "",
        "## Summary",
        response.summary,
        "",
        "## Key Findings",
        *[f"- {item}" for item in response.key_findings],
        "",
        "## Sources",
        *[f"- {item}" for item in response.sources],
        "",
        "## Tools Used",
        *[f"- {item}" for item in response.tools_used],
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def export_json(response: ResearchResponse) -> str:
    path = _timestamped_path(response.topic, "json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(response.model_dump(), f, ensure_ascii=False, indent=2)
    return path
