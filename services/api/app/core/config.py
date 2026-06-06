from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    sqlite_path: Path
    redis_url: str
    queue_name: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            sqlite_path=Path(os.getenv("EVIREVIEW_SQLITE_PATH", "storage/evireview.sqlite3")),
            redis_url=os.getenv("EVIREVIEW_REDIS_URL", "redis://localhost:6379/0"),
            queue_name=os.getenv("EVIREVIEW_QUEUE_NAME", "evireview"),
        )
