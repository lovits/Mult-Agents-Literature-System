from __future__ import annotations

import csv
import io
from typing import Iterable

from evireview_core.evaluation.metrics import MetricRecord, sort_metric_records


FIELDS = ("dataset", "task", "module", "method", "metric", "value", "metric_boundary", "source_artifact")


def render_metrics_csv(records: Iterable[MetricRecord]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(item.to_dict() for item in sort_metric_records(records))
    return output.getvalue()


def render_metrics_markdown(records: Iterable[MetricRecord]) -> str:
    lines = [
        "# Unified Experiment Metrics",
        "",
        "| Dataset | Task | Module | Method | Metric | Value | Boundary | Source artifact |",
        "| --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for item in sort_metric_records(records):
        lines.append(
            f"| {item.dataset} | {item.task} | {item.module} | {item.method} | {item.metric} | "
            f"{item.value} | {item.metric_boundary} | {item.source_artifact} |"
        )
    return "\n".join(lines) + "\n"
