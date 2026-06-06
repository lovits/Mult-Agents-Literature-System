from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProviderGeneration:
    payload: dict[str, Any]
    metadata: dict[str, Any]


class ProviderCallError(RuntimeError):
    """Public provider error that intentionally excludes private response details."""

