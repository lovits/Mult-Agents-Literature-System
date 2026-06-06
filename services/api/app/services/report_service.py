from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from app.repositories.sqlite_run_repository import SQLiteRunRepository
from evireview_core.reporting.markdown_report import render_review_audit_markdown


class ReportService:
    def __init__(self, repository: SQLiteRunRepository, report_root: Path) -> None:
        self.repository = repository
        self.report_root = report_root

    def create_for_run(self, run_id: str) -> dict[str, Any]:
        run = self.repository.get_run(run_id)
        if run["status"] != "succeeded":
            raise RuntimeError("report requires a succeeded run")
        job = self.repository.get_job_for_run(run_id)
        trace = self.repository.list_events(job["job_id"])
        markdown = render_review_audit_markdown(run, trace)
        report_id = f"report-{uuid4().hex}"
        self.report_root.mkdir(parents=True, exist_ok=True)
        artifact_path = self.report_root / f"{report_id}.md"
        temporary = artifact_path.with_suffix(".tmp")
        temporary.write_text(markdown, encoding="utf-8")
        temporary.replace(artifact_path)
        self.repository.create_report(
            report_id,
            run_id,
            run["paper_id"],
            str((run.get("result") or {}).get("metric_boundary", "silver diagnostic")),
            str(artifact_path),
        )
        return self.get_report(report_id)

    def get_report(self, report_id: str) -> dict[str, Any]:
        report = self.repository.get_report(report_id)
        return {key: value for key, value in report.items() if key != "artifact_path"}

    def get_markdown(self, report_id: str) -> str:
        report = self.repository.get_report(report_id)
        return Path(report["artifact_path"]).read_text(encoding="utf-8")
