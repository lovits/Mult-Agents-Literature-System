from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from common import DATA_DIR


ROOT = Path(__file__).resolve().parents[4]
RESULT_PATH = ROOT / ".omx/specs/autoresearch-phase2h-experiment-optimization/result.json"


def load(name: str) -> dict[str, Any]:
    path = DATA_DIR / name
    if not path.exists():
        raise ValueError(f"missing artifact: {name}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> dict[str, Any]:
    provider = load("generated_reviewer_comparison_metrics.json")
    graph = load("graph_ablation_metrics.json")
    retrieval = load("dense_hybrid_retrieval_metrics.json")
    unified = load("unified_metrics.json")

    generators = provider.get("generators", {})
    if not {"rubric_agent", "glm_reviewer", "minimax_reviewer"} <= set(generators):
        raise ValueError("provider paired comparison is incomplete")
    profiles = graph.get("profiles", {})
    if set(profiles) != {"full", "no_verifier", "no_ranker"}:
        raise ValueError("graph ablation profiles are incomplete")
    full_support = profiles["full"]["mean_reference_support"]
    if full_support < max(profiles["no_verifier"]["mean_reference_support"], profiles["no_ranker"]["mean_reference_support"]):
        raise ValueError("full graph does not preserve the strongest mean reference support")
    methods = retrieval.get("methods", {})
    if set(methods) != {"bm25_sparse", "openrouter_dense", "bm25_openrouter_rrf_hybrid"}:
        raise ValueError("dense/hybrid methods are incomplete")
    if methods["openrouter_dense"]["main"]["hit_at_3"] <= methods["bm25_sparse"]["main"]["hit_at_3"]:
        raise ValueError("dense retrieval did not improve main Hit@3 over BM25")
    if methods["bm25_openrouter_rrf_hybrid"]["main"]["mrr"] <= methods["bm25_sparse"]["main"]["mrr"]:
        raise ValueError("hybrid retrieval did not improve main MRR over BM25")
    sources = {record.get("source_artifact") for record in unified}
    required_sources = {
        "generated_reviewer_comparison_metrics.json",
        "graph_ablation_metrics.json",
        "dense_hybrid_retrieval_metrics.json",
    }
    if not required_sources <= sources:
        raise ValueError(f"unified metrics missing sources: {sorted(required_sources - sources)}")
    return {
        "provider_generators": sorted(generators),
        "graph_profiles": sorted(profiles),
        "dense_main_hit_at_3": methods["openrouter_dense"]["main"]["hit_at_3"],
        "hybrid_main_mrr": methods["bm25_openrouter_rrf_hybrid"]["main"]["mrr"],
        "unified_metric_records": len(unified),
    }


def main() -> None:
    try:
        evidence = validate()
    except Exception as exc:
        result = {
            "status": "failed",
            "passed": False,
            "validation_mode": "mission-validator-script",
            "summary": str(exc),
        }
        RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        raise
    result = {
        "status": "passed",
        "passed": True,
        "validation_mode": "mission-validator-script",
        "summary": "Phase 2H-B provider, graph ablation, dense/hybrid, and unified export gates passed.",
        "output_artifact_path": "docs/progress/agent_rag_refactor_phase_2h_2026-06-07.md",
        "evidence": evidence,
    }
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["summary"])


if __name__ == "__main__":
    main()
