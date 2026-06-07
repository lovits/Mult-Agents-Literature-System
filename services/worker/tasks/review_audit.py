from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.repositories.sqlite_run_repository import SQLiteRunRepository
from evireview_core.domain.models import EvidenceBlock, VerificationResult, Weakness
from evireview_core.generation.structured_reviewer import StructuredReviewerGenerator
from evireview_core.providers.minimax import MiniMaxProvider
from evireview_core.retrieval.bm25 import RetrievedEvidence
from evireview_core.verification.structured_judge import StructuredEvidenceVerifier
from evireview_core.workflow.deterministic import run_deterministic_review_audit
from evireview_core.workflow.state import ReviewAuditState, WeaknessGenerationResult


WeaknessGenerator = Callable[[ReviewAuditState], WeaknessGenerationResult]
GeneratorFactory = Callable[[str], WeaknessGenerator | None]
EvidenceVerifier = Callable[[Weakness, list[RetrievedEvidence]], VerificationResult]
VerifierFactory = Callable[[str], EvidenceVerifier | None]


def build_weakness_generator(name: str) -> WeaknessGenerator | None:
    if name == "imported":
        return None
    if name == "minimax":
        return StructuredReviewerGenerator(MiniMaxProvider(), source="minimax_reviewer")
    raise KeyError(f"weakness generator not found: {name}")


def build_verifier(name: str) -> EvidenceVerifier | None:
    if name == "heuristic":
        return None
    if name == "minimax":
        return StructuredEvidenceVerifier(MiniMaxProvider(), source="minimax_evidence_judge")
    raise KeyError(f"verifier not found: {name}")


def run_next_job(
    repository: SQLiteRunRepository,
    generator_factory: GeneratorFactory = build_weakness_generator,
    verifier_factory: VerifierFactory = build_verifier,
) -> dict[str, Any] | None:
    return _execute_claimed_job(repository, repository.claim_next_job(), generator_factory, verifier_factory)


def run_job(
    repository: SQLiteRunRepository,
    job_id: str,
    generator_factory: GeneratorFactory = build_weakness_generator,
    verifier_factory: VerifierFactory = build_verifier,
) -> dict[str, Any] | None:
    return _execute_claimed_job(repository, repository.claim_job(job_id), generator_factory, verifier_factory)


def _execute_claimed_job(
    repository: SQLiteRunRepository,
    job: dict[str, Any] | None,
    generator_factory: GeneratorFactory,
    verifier_factory: VerifierFactory,
) -> dict[str, Any] | None:
    if job is None:
        return None

    run_id = str(job["run_id"])
    job_id = str(job["job_id"])
    attempt_token = str(job["attempt_token"])
    try:
        payload = repository.load_input(run_id)
        weaknesses = [Weakness.from_dict(item) for item in payload["weaknesses"]]
        if "evidence_blocks" in payload:
            block_payloads = payload["evidence_blocks"]
        elif "paper_version_id" in payload:
            block_payloads = repository.get_version_evidence_blocks_by_ids(
                str(payload["paper_id"]),
                str(payload["paper_version_id"]),
                [str(item) for item in payload.get("evidence_block_ids", [])],
            )
        else:
            block_payloads = repository.get_evidence_blocks_by_ids(
                str(payload["paper_id"]),
                [str(item) for item in payload.get("evidence_block_ids", [])],
            )
        blocks = [EvidenceBlock.from_dict(item) for item in block_payloads]
        weakness_generator_name = str(payload.get("weakness_generator", "imported"))
        verifier_name = str(payload.get("verifier", "heuristic"))
        result = run_deterministic_review_audit(
            weaknesses,
            blocks,
            top_k=int(payload.get("top_k", 5)),
            finding_top_k=int(payload.get("finding_top_k", 3)),
            graph_profile=str(payload.get("graph_profile", "full")),
            query_planner=str(payload.get("query_planner", "direct")),
            retriever=str(payload.get("retriever", "hierarchical")),
            weakness_generator=generator_factory(weakness_generator_name),
            weakness_generator_name=weakness_generator_name,
            verifier=verifier_factory(verifier_name),
            verifier_name=verifier_name,
        )
        repository.save_result(run_id, job_id, attempt_token, result)
        return {"run_id": run_id, "job_id": job_id, "status": "succeeded"}
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        if not repository.mark_failed(run_id, job_id, attempt_token, error):
            return {"run_id": run_id, "job_id": job_id, "status": "superseded", "error": error}
        return {"run_id": run_id, "job_id": job_id, "status": "failed", "error": error}


def recover_and_run(repository: SQLiteRunRepository) -> list[dict[str, Any]]:
    repository.recover_running_jobs()
    results: list[dict[str, Any]] = []
    while True:
        result = run_next_job(repository)
        if result is None:
            return results
        results.append(result)
