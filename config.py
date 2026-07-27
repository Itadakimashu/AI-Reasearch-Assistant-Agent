"""Central configuration for the research agent, loaded from environment variables."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    model_name: str = os.getenv("MODEL_NAME", "gemini-3.5-flash")
    google_api_key: str | None = os.getenv("GOOGLE_API_KEY")
    output_dir: str = os.getenv("OUTPUT_DIR", "outputs")
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "8"))
    verbose: bool = _get_bool("VERBOSE", False)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()

if not settings.google_api_key:
    raise EnvironmentError(
        "GOOGLE_API_KEY is not set. Create a .env file (see .env.example) "
        "or export it in your shell before running the agent."
    )

os.makedirs(settings.output_dir, exist_ok=True)
