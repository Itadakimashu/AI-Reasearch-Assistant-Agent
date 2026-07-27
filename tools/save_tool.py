"""Tool for persisting research output to disk."""
import json
import os
import re
from datetime import datetime

from langchain_core.tools import tool

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9_.-]+")


def _sanitize_filename(filename: str) -> str:
    """Strip path separators and odd characters so this can never write
    outside the configured output directory."""
    name = os.path.basename(filename.strip())
    name = _SAFE_NAME_RE.sub("_", name)
    return name or "research_output.txt"


@tool
def save_tool(data: str, filename: str = "research_output.txt") -> str:
    """Save compiled research findings to a local file inside the configured
    output directory. Supports .txt, .md, and .json extensions."""
    safe_name = _sanitize_filename(filename)
    path = os.path.join(settings.output_dir, safe_name)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        if safe_name.endswith(".json"):
            payload = {"timestamp": timestamp, "data": data}
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        else:
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n")
        logger.info("Saved research output to %s", path)
        return f"Data successfully saved to {path}"
    except OSError as exc:
        logger.exception("save_tool failed to write file")
        return f"Failed to save data: {exc}"
