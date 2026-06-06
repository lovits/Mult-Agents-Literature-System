from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable


METRIC_BOUNDARIES = frozenset({"gold", "silver", "proxy", "diagnostic"})


@dataclass(frozen=True)
class MetricRecord:
    dataset: str
    task: str
    module: str
    method: str
    metric: str
    value: int | float
    metric_boundary: str
    source_artifact: str

    def __post_init__(self) -> None:
        if self.metric_boundary not in METRIC_BOUNDARIES:
            raise ValueError(f"unknown metric boundary: {self.metric_boundary}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def sort_metric_records(records: Iterable[MetricRecord]) -> list[MetricRecord]:
    return sorted(
        records,
        key=lambda item: (item.dataset, item.task, item.module, item.method, item.metric, item.source_artifact),
    )


def metric_records_json(records: Iterable[MetricRecord]) -> str:
    return json.dumps([item.to_dict() for item in sort_metric_records(records)], ensure_ascii=False, indent=2) + "\n"

