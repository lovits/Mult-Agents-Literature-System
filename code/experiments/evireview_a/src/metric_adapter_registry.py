from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from evireview_core.evaluation.metrics import MetricRecord


@dataclass(frozen=True)
class ArtifactSpec:
    filename: str
    dataset: str
    task: str
    module: str
    boundary: str
    method_container: tuple[str, ...] = ()
    fixed_method: str = "aggregate"


ARTIFACT_SPECS = (
    ArtifactSpec("retrieval_proxy_eval.json", "Local OpenReview/PRISM", "retrieval", "paper_rag", "proxy", ("results",)),
    ArtifactSpec("peerqa_xt_retrieval_metrics.json", "PeerQA-XT", "retrieval", "paper_rag", "proxy", ("methods",)),
    ArtifactSpec("peerreview_bench_baseline_metrics.json", "PeerReview Bench", "review_quality", "verifier", "gold", ("tasks",)),
    ArtifactSpec("substanreview_baseline_metrics.json", "SubstanReview", "substantiation", "verifier", "gold", ("baselines",)),
    ArtifactSpec("claimcheck_feature_verifier_metrics.json", "CLAIMCHECK", "groundedness", "verifier", "diagnostic", ("feature_verifier",), "feature_verifier"),
    ArtifactSpec("claimcheck_evidence_ranker_metrics.json", "CLAIMCHECK", "ranker", "evidence_ranker", "diagnostic", ("metrics",)),
    ArtifactSpec("dense_hybrid_retrieval_metrics.json", "CLAIMCHECK", "retrieval", "paper_rag", "gold", ("methods",)),
    ArtifactSpec("live_qdrant_retrieval_metrics.json", "CLAIMCHECK", "retrieval", "paper_rag_qdrant", "gold", ("methods",)),
    ArtifactSpec("query_planner_ablation_metrics.json", "CLAIMCHECK", "retrieval", "query_planner", "gold", ("planners",)),
    ArtifactSpec("local_decision_classifier_metrics.json", "Local OpenReview/PRISM", "classification", "auxiliary_classifier", "diagnostic", ("results",)),
    ArtifactSpec("generated_reviewer_comparison_metrics.json", "Local OpenReview/PRISM", "generation", "reviewer_comparison", "diagnostic", ("generators",)),
    ArtifactSpec("generated_hierarchical_retrieval_summary.json", "Local OpenReview/PRISM", "retrieval", "generated_weakness_rag", "diagnostic", ("sources",)),
    ArtifactSpec("generated_weakness_ranker_metrics.json", "Local OpenReview/PRISM", "ranker", "generated_weakness_ranker", "diagnostic", ("sources",)),
    ArtifactSpec("rubric_agent_coverage_metrics.json", "Local OpenReview/PRISM", "generation", "rubric_agent", "proxy"),
    ArtifactSpec("glm_reviewer_coverage_metrics.json", "Local OpenReview/PRISM", "generation", "glm_reviewer", "diagnostic"),
    ArtifactSpec("minimax_reviewer_coverage_metrics.json", "Local OpenReview/PRISM", "generation", "minimax_reviewer", "diagnostic"),
    ArtifactSpec("rubric_agent_verifier_summary.json", "Local OpenReview/PRISM", "verification", "rubric_agent", "silver"),
    ArtifactSpec("glm_reviewer_verifier_summary.json", "Local OpenReview/PRISM", "verification", "glm_reviewer", "silver"),
    ArtifactSpec("minimax_reviewer_verifier_summary.json", "Local OpenReview/PRISM", "verification", "minimax_reviewer", "silver"),
    ArtifactSpec("graph_ablation_metrics.json", "Local OpenReview/PRISM", "ablation", "agent_rag_graph", "silver", ("profiles",)),
)


def _at_path(payload: Any, path: tuple[str, ...]) -> Any:
    current = payload
    for key in path:
        if not isinstance(current, dict):
            return {}
        current = current.get(key, {})
    return current


def _numeric_leaves(payload: Any, prefix: str = "") -> Iterable[tuple[str, int | float]]:
    if isinstance(payload, bool):
        return
    if isinstance(payload, (int, float)):
        yield prefix, payload
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "threshold":
                continue
            child = f"{prefix}.{key}" if prefix else str(key)
            yield from _numeric_leaves(value, child)
        return
    if isinstance(payload, list):
        for index, value in enumerate(payload):
            if isinstance(value, dict) and "threshold" in value:
                threshold = value["threshold"]
                for key, metric_value in value.items():
                    if key != "threshold":
                        yield from _numeric_leaves(metric_value, f"{key}_at_{threshold}")
            else:
                yield from _numeric_leaves(value, f"{prefix}.{index}" if prefix else str(index))


def _records_for_spec(data_dir: Path, spec: ArtifactSpec) -> list[MetricRecord]:
    path = data_dir / spec.filename
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    source = spec.filename
    container = _at_path(payload, spec.method_container)
    records = []
    if spec.method_container and isinstance(container, dict) and spec.fixed_method == "aggregate":
        method_payloads = container.items()
    elif spec.method_container:
        method_payloads = ((spec.fixed_method, container),)
    else:
        method_payloads = ((spec.fixed_method, payload),)
    for method, method_payload in method_payloads:
        for metric, value in _numeric_leaves(method_payload):
            records.append(
                MetricRecord(spec.dataset, spec.task, spec.module, str(method), metric, value, spec.boundary, source)
            )
    return records


def collect_historical_metrics(data_dir: Path) -> list[MetricRecord]:
    records = []
    for spec in ARTIFACT_SPECS:
        records.extend(_records_for_spec(data_dir, spec))
    return records
