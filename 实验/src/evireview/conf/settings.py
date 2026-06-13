from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EVIREVIEW_",
        env_file=".env",
        extra="ignore",
    )

    llm_base_url: str
    llm_model: str
    llm_api_key: str | None = None
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    random_seed: int = 42
    output_root: Path = Path("outputs")
