from __future__ import annotations

from enum import Enum


class VerifierLabel(str, Enum):
    SUPPORTED = "Supported"
    PARTIALLY_SUPPORTED = "Partially Supported"
    MENTIONED_NOT_PROBLEM = "Mentioned but Not Problem"
    GENERIC_VAGUE = "Generic / Vague"
    UNSUPPORTED = "Unsupported"
    CONTRADICTED = "Contradicted"


SUPPORTED_OR_BETTER = {
    VerifierLabel.SUPPORTED.value,
    VerifierLabel.PARTIALLY_SUPPORTED.value,
}


def is_supported_or_better(label: str) -> bool:
    return label in SUPPORTED_OR_BETTER
