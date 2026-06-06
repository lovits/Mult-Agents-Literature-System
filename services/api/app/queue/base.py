from __future__ import annotations

from typing import Protocol


class JobQueue(Protocol):
    def enqueue(self, job_id: str) -> str:
        ...
