from __future__ import annotations

from typing import Any

from app.repositories.sqlite_run_repository import SQLiteRunRepository
from evireview_core.domain.models import EvidenceBlock, Weakness
from evireview_core.workflow.deterministic import run_deterministic_review_audit


def run_next_job(repository: SQLiteRunRepository) -> dict[str, Any] | None:
    return _execute_claimed_job(repository, repository.claim_next_job())


def run_job(repository: SQLiteRunRepository, job_id: str) -> dict[str, Any] | None:
    return _execute_claimed_job(repository, repository.claim_job(job_id))


def _execute_claimed_job(repository: SQLiteRunRepository, job: dict[str, Any] | None) -> dict[str, Any] | None:
    if job is None:
        return None

    run_id = str(job["run_id"])
    job_id = str(job["job_id"])
    attempt_token = str(job["attempt_token"])
    try:
        payload = repository.load_input(run_id)
        weaknesses = [Weakness.from_dict(item) for item in payload["weaknesses"]]
        blocks = [EvidenceBlock.from_dict(item) for item in payload["evidence_blocks"]]
        result = run_deterministic_review_audit(
            weaknesses,
            blocks,
            top_k=int(payload.get("top_k", 5)),
            finding_top_k=int(payload.get("finding_top_k", 3)),
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
