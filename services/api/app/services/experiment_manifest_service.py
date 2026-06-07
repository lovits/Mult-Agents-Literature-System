from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.repositories.sqlite_run_repository import SQLiteRunRepository
from app.schemas.runs import PersistedPaperReviewAuditRequest
from app.services.review_audit_service import QueueDeliveryError, ReviewAuditService
from evireview_core.evaluation.metrics import MetricRecord, sort_metric_records


class ExperimentManifestService:
    def __init__(self, repository: SQLiteRunRepository, review_audit_service: ReviewAuditService | None = None) -> None:
        self.repository = repository
        self.review_audit_service = review_audit_service

    def create(
        self,
        name: str,
        dataset_name: str,
        dataset_version: str,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        manifest_id = f"experiment-{uuid4().hex}"
        self.repository.create_experiment_manifest(manifest_id, name, dataset_name, dataset_version, config)
        return self.get(manifest_id)

    def attach_run(self, manifest_id: str, run_id: str) -> dict[str, Any]:
        self.repository.attach_run_to_experiment(manifest_id, run_id)
        return self.get(manifest_id)

    def schedule_paper_audits(
        self,
        manifest_id: str,
        items: list[PersistedPaperReviewAuditRequest],
    ) -> dict[str, Any]:
        self.repository.get_experiment_manifest(manifest_id)
        if self.review_audit_service is None:
            raise QueueDeliveryError("review audit service is not configured")

        results = [self._schedule_paper_audit(manifest_id, index, item) for index, item in enumerate(items)]
        scheduled_count = sum(item["status"] == "scheduled" for item in results)
        return {
            "manifest_id": manifest_id,
            "requested_count": len(items),
            "scheduled_count": scheduled_count,
            "failed_count": len(items) - scheduled_count,
            "results": results,
        }

    def _schedule_paper_audit(
        self,
        manifest_id: str,
        index: int,
        item: PersistedPaperReviewAuditRequest,
    ) -> dict[str, Any]:
        try:
            created = self.review_audit_service.create_from_paper_and_enqueue(
                item.paper_id,
                item.weaknesses,
                top_k=item.top_k,
                finding_top_k=item.finding_top_k,
                graph_profile=item.graph_profile,
                query_planner=item.query_planner,
                retriever=item.retriever,
                weakness_generator=item.weakness_generator,
                verifier=item.verifier,
            )
        except KeyError:
            return self._failed_item(index, item.paper_id, "paper_not_found")
        except ValueError:
            return self._failed_item(index, item.paper_id, "invalid_paper_input")
        except QueueDeliveryError as exc:
            if exc.run_id is not None:
                self.repository.attach_run_to_experiment(manifest_id, exc.run_id)
            return self._failed_item(index, item.paper_id, "queue_unavailable", run_id=exc.run_id)

        self.repository.attach_run_to_experiment(manifest_id, created["run"]["run_id"])
        return {
            "index": index,
            "paper_id": item.paper_id,
            "status": "scheduled",
            "run_id": created["run"]["run_id"],
            "job_id": created["job"]["job_id"],
            "delivery_id": created["delivery_id"],
        }

    @staticmethod
    def _failed_item(index: int, paper_id: str, error_code: str, run_id: str | None = None) -> dict[str, Any]:
        result = {
            "index": index,
            "paper_id": paper_id,
            "status": "failed",
            "error_code": error_code,
        }
        if run_id is not None:
            result["run_id"] = run_id
        return result

    def list(self) -> list[dict[str, Any]]:
        return [self._public_manifest(item, include_runs=False) for item in self.repository.list_experiment_manifests()]

    def get(self, manifest_id: str) -> dict[str, Any]:
        manifest = self.repository.get_experiment_manifest(manifest_id)
        public = self._public_manifest(manifest, include_runs=False)
        public["runs"] = [self._run_snapshot(run_id) for run_id in self.repository.list_experiment_run_ids(manifest_id)]
        return public

    def metrics(self, manifest_id: str) -> list[dict[str, Any]]:
        manifest = self.repository.get_experiment_manifest(manifest_id)
        runs = [self.repository.get_run(run_id) for run_id in self.repository.list_experiment_run_ids(manifest_id)]
        source = f"manifest:{manifest_id}"
        values: list[MetricRecord] = [
            MetricRecord(manifest["dataset_name"], "review_audit", "agent_rag", "manifest", "run_count", len(runs), "silver", source)
        ]
        for status in ("queued", "running", "succeeded", "failed", "cancelled"):
            count = sum(run["status"] == status for run in runs)
            if count:
                values.append(
                    MetricRecord(
                        manifest["dataset_name"], "review_audit", "agent_rag", "manifest", f"{status}_run_count", count, "silver", source
                    )
                )
        succeeded = [run for run in runs if run["status"] == "succeeded"]
        values.append(
            MetricRecord(
                manifest["dataset_name"],
                "review_audit",
                "agent_rag",
                "manifest",
                "succeeded_rate",
                round(len(succeeded) / len(runs), 4) if runs else 0.0,
                "silver",
                source,
            )
        )
        results = [run["result"] for run in succeeded if isinstance(run.get("result"), dict)]
        support_scores = [
            float(item["support_score"])
            for result in results
            for item in result.get("verification", {}).values()
            if isinstance(item, dict) and isinstance(item.get("support_score"), (int, float))
        ]
        if support_scores:
            values.append(
                MetricRecord(
                    manifest["dataset_name"],
                    "review_audit",
                    "verification",
                    "manifest",
                    "mean_support_score",
                    round(sum(support_scores) / len(support_scores), 4),
                    "silver",
                    source,
                )
            )
        values.extend(
            [
                MetricRecord(
                    manifest["dataset_name"],
                    "review_audit",
                    "generation",
                    "manifest",
                    "weakness_count",
                    sum(int(result.get("weakness_count", 0)) for result in results),
                    "silver",
                    source,
                ),
                MetricRecord(
                    manifest["dataset_name"],
                    "review_audit",
                    "ranking",
                    "manifest",
                    "ranked_finding_count",
                    sum(len(result.get("ranked_findings", [])) for result in results),
                    "silver",
                    source,
                ),
            ]
        )
        return [item.to_dict() for item in sort_metric_records(values)]

    def _run_snapshot(self, run_id: str) -> dict[str, Any]:
        run = self.repository.get_run(run_id)
        input_payload = self.repository.load_input(run_id)
        reports = [
            {key: value for key, value in report.items() if key != "artifact_path"}
            for report in self.repository.list_reports_for_run(run_id)
        ]
        return {
            "run_id": run["run_id"],
            "paper_id": run["paper_id"],
            "paper_version_id": input_payload.get("paper_version_id"),
            "evidence_source": input_payload.get("evidence_source", "inline"),
            "status": run["status"],
            "run_config": run["config"],
            "reports": reports,
            "created_at": run["created_at"],
            "updated_at": run["updated_at"],
        }

    @staticmethod
    def _public_manifest(manifest: dict[str, Any], include_runs: bool) -> dict[str, Any]:
        public = {
            key: manifest[key]
            for key in (
                "manifest_id",
                "name",
                "dataset_name",
                "dataset_version",
                "config",
                "created_at",
                "updated_at",
            )
        }
        if include_runs:
            public["runs"] = []
        return public
