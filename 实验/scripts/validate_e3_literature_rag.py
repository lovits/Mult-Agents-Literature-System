import json
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent
EXPECTED_SYSTEMS = {
    "L0_no_literature",
    "L1_keyword",
    "L2_hybrid",
    "L3_hybrid_metadata_filter",
}


def validate(metrics_path: Path | None = None) -> dict:
    result = json.loads(
        (metrics_path or EXPERIMENT_ROOT / "outputs/metrics/e3_literature_rag.json").read_text(
            encoding="utf-8"
        )
    )
    protocol = result["protocol"]
    dataset = result["dataset"]
    systems = result["systems"]
    filtered = systems["L3_hybrid_metadata_filter"]
    baseline = systems["L0_no_literature"]
    hybrid = systems["L2_hybrid"]
    checks = {
        "protocol": {
            "passed": (
                protocol["name"] == "controlled-literature-rag-v1"
                and protocol["frozen_local_corpus"] is True
                and protocol["online_retrieval"] is False
                and protocol["metadata_year_filter"] is True
            ),
            "protocol": protocol["name"],
        },
        "dataset": {
            "passed": (
                dataset["markdown_docs"] >= 30
                and dataset["metadata_complete_docs"] >= 30
                and dataset["source_exists"] is True
            ),
            "markdown_docs": dataset["markdown_docs"],
            "metadata_complete_docs": dataset["metadata_complete_docs"],
        },
        "queries": {
            "passed": result["queries"]["count"] >= 6,
            "count": result["queries"]["count"],
        },
        "systems": {
            "passed": set(systems) == EXPECTED_SYSTEMS,
            "systems": sorted(systems),
        },
        "baseline_improvement": {
            "passed": filtered["recall@10"] > baseline["recall@10"],
            "baseline_recall@10": baseline["recall@10"],
            "filtered_recall@10": filtered["recall@10"],
        },
        "metadata_boundary": {
            "passed": filtered["future_leakage_count"] <= hybrid["future_leakage_count"],
            "hybrid_future_leakage": hybrid["future_leakage_count"],
            "filtered_future_leakage": filtered["future_leakage_count"],
        },
        "citation_validity": {
            "passed": filtered["citation_validity_rate"] >= 0.95,
            "citation_validity_rate": filtered["citation_validity_rate"],
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "Controlled Literature-RAG E3 baselines validate frozen local literature retrieval and metadata-year filtering.",
        "checks": checks,
        "metrics": {
            "baseline_recall@10": baseline["recall@10"],
            "keyword_recall@10": systems["L1_keyword"]["recall@10"],
            "hybrid_recall@10": hybrid["recall@10"],
            "controlled_recall@10": filtered["recall@10"],
            "controlled_mrr": filtered["mrr"],
            "controlled_future_leakage_count": filtered["future_leakage_count"],
            "controlled_citation_validity_rate": filtered["citation_validity_rate"],
        },
        "next_experiment": "Use E3 literature evidence only for novelty, related-work, and missing-baseline claims, then proceed to E5 Meta-Reviewer Ranker.",
    }


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-e3-literature-rag/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
