from __future__ import annotations

from uuid import uuid4

from app.repositories.sqlite_run_repository import SQLiteRunRepository
from app.queue.base import JobQueue
from app.schemas.runs import ReviewAuditRequest
from evireview_core.domain.models import EvidenceBlock, Weakness


class QueueDeliveryError(RuntimeError):
    def __init__(self, message: str, run_id: str | None = None) -> None:
        super().__init__(message)
        self.run_id = run_id


class ReviewAuditService:
    def __init__(self, repository: SQLiteRunRepository, queue: JobQueue | None = None) -> None:
        self.repository = repository
        self.queue = queue

    def create_review_audit(self, request: ReviewAuditRequest) -> dict[str, dict]:
        return self._create_review_audit(request.to_payload())

    def _create_review_audit(self, payload: dict) -> dict[str, dict]:
        run_id = f"run-{uuid4().hex}"
        job_id = f"job-{uuid4().hex}"
        self.repository.create_run_and_job(run_id, job_id, payload)
        return {
            "run": self._public_run(self.repository.get_run(run_id)),
            "job": self._public_job(self.repository.get_job(job_id)),
        }

    def create_and_enqueue(self, request: ReviewAuditRequest) -> dict:
        self._require_queue()
        return self._enqueue_created(self.create_review_audit(request))

    def create_from_paper_and_enqueue(
        self,
        paper_id: str,
        weaknesses: list[Weakness],
        top_k: int = 5,
        finding_top_k: int = 3,
        graph_profile: str = "full",
    ) -> dict:
        self._require_queue()
        version_id = str(self.repository.get_active_paper_version(paper_id)["version_id"])
        block_ids = self.repository.list_version_evidence_block_ids(paper_id, version_id)
        blocks = [
            EvidenceBlock.from_dict(item)
            for item in self.repository.get_version_evidence_blocks_by_ids(paper_id, version_id, block_ids)
        ]
        request = ReviewAuditRequest(
            paper_id=paper_id,
            weaknesses=weaknesses,
            evidence_blocks=blocks,
            top_k=top_k,
            finding_top_k=finding_top_k,
            graph_profile=graph_profile,
        )
        payload = request.to_payload()
        payload.pop("evidence_blocks")
        payload["paper_version_id"] = version_id
        payload["evidence_block_ids"] = block_ids
        payload["evidence_source"] = "persisted_paper_version"
        return self._enqueue_created(self._create_review_audit(payload))

    def _enqueue_created(self, created: dict[str, dict]) -> dict:
        self._require_queue()
        try:
            delivery_id = self.queue.enqueue(created["job"]["job_id"])
        except Exception as exc:
            self.repository.mark_delivery_failed(created["run"]["run_id"], created["job"]["job_id"], str(exc))
            raise QueueDeliveryError("queue delivery failed", run_id=created["run"]["run_id"]) from exc
        return {**created, "delivery_id": delivery_id}

    def _require_queue(self) -> None:
        if self.queue is None:
            raise QueueDeliveryError("queue is not configured")

    def get_run(self, run_id: str) -> dict:
        return self._public_run(self.repository.get_run(run_id))

    def list_runs_for_paper(self, paper_id: str) -> list[dict]:
        return [self._public_run(run) for run in self.repository.list_runs_for_paper(paper_id)]

    def get_workspace(self, run_id: str) -> dict:
        run = self.repository.get_run(run_id)
        input_payload = self.repository.load_input(run_id)
        result = run.get("result") or {}
        version_id = input_payload.get("paper_version_id")
        if version_id:
            evidence_blocks = self.repository.list_version_evidence_blocks(run["paper_id"], version_id)
        else:
            evidence_blocks = list(input_payload.get("evidence_blocks", []))
        reports = [
            {key: value for key, value in report.items() if key != "artifact_path"}
            for report in self.repository.list_reports_for_run(run_id)
        ]
        return {
            "paper": self.repository.get_paper(run["paper_id"]),
            "run": {
                **self._public_run(run),
                "paper_version_id": version_id,
                "evidence_source": input_payload.get("evidence_source", "inline"),
            },
            "metric_boundary": result.get("metric_boundary", run["config"].get("metric_boundary", "silver diagnostic")),
            "weaknesses": list(input_payload.get("weaknesses", [])),
            "evidence_blocks": [
                {key: value for key, value in block.items() if key not in {"ordinal", "version_id"}}
                for block in evidence_blocks
            ],
            "retrieval": result.get("retrieval", {}),
            "verification": result.get("verification", {}),
            "ranked_findings": result.get("ranked_findings", []),
            "trace": self.get_trace(run_id),
            "reports": reports,
        }

    def get_job(self, job_id: str) -> dict:
        return self._public_job(self.repository.get_job(job_id))

    def get_findings(self, run_id: str) -> list[dict]:
        result = self.repository.get_run(run_id).get("result") or {}
        return list(result.get("ranked_findings", []))

    def get_trace(self, run_id: str) -> list[dict]:
        job = self.repository.get_job_for_run(run_id)
        return [self._public_event(event) for event in self.repository.list_events(job["job_id"])]

    def get_agent_trace(self, run_id: str) -> list[dict]:
        result = self.repository.get_run(run_id).get("result") or {}
        return [
            {
                key: event[key]
                for key in ("node", "status", "error_type")
                if key in event
            }
            for event in result.get("agent_trace", [])
        ]

    @staticmethod
    def _public_run(run: dict) -> dict:
        hidden = {"config_json", "input_json", "result_json", "result"}
        public = {key: value for key, value in run.items() if key not in hidden}
        if public.get("error"):
            public["error"] = "internal_error"
        return public

    @staticmethod
    def _public_job(job: dict) -> dict:
        hidden = {"attempt_token", "lease_expires_at"}
        public = {key: value for key, value in job.items() if key not in hidden}
        if public.get("error"):
            public["error"] = "internal_error"
        return public

    @staticmethod
    def _public_event(event: dict) -> dict:
        payload = event.get("payload") or {}
        public_payload = {"progress": payload["progress"]} if "progress" in payload else {}
        return {
            "event_id": event["event_id"],
            "job_id": event["job_id"],
            "event_type": event["event_type"],
            "payload": public_payload,
            "created_at": event["created_at"],
        }
