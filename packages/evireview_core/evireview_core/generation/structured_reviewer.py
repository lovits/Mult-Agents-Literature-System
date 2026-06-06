from __future__ import annotations

from typing import Any, Protocol

from evireview_core.domain.models import Weakness
from evireview_core.providers.base import ProviderGeneration
from evireview_core.workflow.state import ReviewAuditState, WeaknessGenerationResult


class StructuredJsonProvider(Protocol):
    def generate_json(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> ProviderGeneration: ...


class StructuredReviewerGenerator:
    def __init__(self, provider: StructuredJsonProvider, source: str = "provider_reviewer") -> None:
        self.provider = provider
        self.source = source

    def __call__(self, state: ReviewAuditState) -> WeaknessGenerationResult:
        excerpts = "\n\n".join(
            f"[{block.section_type}] {block.section_path}\n{block.text[:1200]}" for block in state.evidence_blocks
        )[:10000]
        result = self.provider.generate_json(
            "You are an evidence-grounded scientific peer reviewer. Return valid JSON only.",
            (
                "Generate exactly 3 concrete, evidence-checkable weaknesses from the supplied paper excerpts. "
                'Return {"weaknesses":[{"weakness_text":"...","category":"experiment|method|related_work|'
                'reproducibility|clarity|validity|other","severity":"major|minor"}]}.\n\n'
                f"Paper excerpts:\n{excerpts}"
            ),
            prompt_version="structured_reviewer_v1",
            schema_version="weaknesses_v1",
        )
        paper_id = state.evidence_blocks[0].paper_id if state.evidence_blocks else "unknown"
        weaknesses = []
        for index, item in enumerate(result.payload.get("weaknesses", [])[:3], start=1):
            if not isinstance(item, dict) or not str(item.get("weakness_text", "")).strip():
                continue
            category = str(item.get("category", "other"))
            if category not in {"experiment", "method", "related_work", "reproducibility", "clarity", "validity", "other"}:
                category = "other"
            severity = str(item.get("severity", "unknown")).lower()
            if severity not in {"major", "minor"}:
                severity = "unknown"
            weaknesses.append(
                Weakness(
                    weakness_id=f"{paper_id}_{self.source}_{index:02d}",
                    paper_id=paper_id,
                    weakness_text=str(item["weakness_text"]).strip(),
                    category=category,
                    severity=severity,
                    source=self.source,
                )
            )
        return WeaknessGenerationResult(weaknesses=weaknesses, metadata=result.metadata)
