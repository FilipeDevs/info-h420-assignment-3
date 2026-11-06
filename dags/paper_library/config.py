import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """
    All configuration options of the pipeline, read from the environment (env.sh).
    """
    papers_dir: Path
    output_dir: Path
    db_path: Path
    markdown_dir: Path
    discord_webhook_url: str | None
    llm_base_url: str
    llm_model: str

    @classmethod
    def from_env(cls) -> "Settings":
        db_path = Path(os.environ["DB_PATH"])

        return cls(
            papers_dir=Path(os.environ["PAPERS_DIR"]),
            output_dir=Path(os.environ["OUTPUT_DIR"]),
            db_path=db_path,
            markdown_dir=db_path.parent / "markdown",
            discord_webhook_url=os.environ.get("DISCORD_WEBHOOK_URL"),
            llm_base_url=os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1"),
            llm_model=os.environ.get("LLM_MODEL", "gemma4:12b"),
        )
