from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "packages" / "evireview_core"))
sys.path.insert(0, str(REPO_ROOT / "services" / "api"))

from app.repositories.sqlite_run_repository import SQLiteRunRepository
from app.services.experiment_manifest_service import ExperimentManifestService
from common import DATA_DIR, REPORT_DIR, ensure_dirs
from evireview_core.evaluation.export import render_metrics_csv, render_metrics_markdown
from evireview_core.evaluation.metrics import MetricRecord, metric_records_json
from metric_adapter_registry import collect_historical_metrics


def collect_manifest_metrics(sqlite_path: Path) -> list[MetricRecord]:
    if not sqlite_path.exists():
        return []
    repository = SQLiteRunRepository(sqlite_path)
    repository.initialize()
    service = ExperimentManifestService(repository)
    return [
        MetricRecord(**row)
        for manifest in service.list()
        for row in service.metrics(manifest["manifest_id"])
    ]


def main() -> None:
    ensure_dirs()
    sqlite_path = Path(os.getenv("EVIREVIEW_SQLITE_PATH", str(REPO_ROOT / "storage" / "evireview.sqlite3")))
    records = [*collect_historical_metrics(DATA_DIR), *collect_manifest_metrics(sqlite_path)]
    (DATA_DIR / "unified_metrics.json").write_text(metric_records_json(records), encoding="utf-8")
    (DATA_DIR / "unified_metrics.csv").write_text(render_metrics_csv(records), encoding="utf-8")
    (REPORT_DIR / "unified_metrics.md").write_text(render_metrics_markdown(records), encoding="utf-8")
    print(f"unified_metrics records={len(records)} manifests={len(ExperimentManifestService(SQLiteRunRepository(sqlite_path)).list()) if sqlite_path.exists() else 0}")


if __name__ == "__main__":
    main()
