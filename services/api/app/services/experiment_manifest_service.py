from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.repositories.sqlite_run_repository import SQLiteRunRepository


class ExperimentManifestService:
    def __init__(self, repository: SQLiteRunRepository) -> None:
        self.repository = repository

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

    def list(self) -> list[dict[str, Any]]:
        return [self._public_manifest(item, include_runs=False) for item in self.repository.list_experiment_manifests()]

    def get(self, manifest_id: str) -> dict[str, Any]:
        manifest = self.repository.get_experiment_manifest(manifest_id)
        public = self._public_manifest(manifest, include_runs=False)
        public["runs"] = [self._run_snapshot(run_id) for run_id in self.repository.list_experiment_run_ids(manifest_id)]
        return public

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
