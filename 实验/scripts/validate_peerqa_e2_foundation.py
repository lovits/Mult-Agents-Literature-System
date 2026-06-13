import json
from pathlib import Path

from evireview.dao.peerqa import PeerQADataset
from evireview.evaluation.retrieval_metrics import evaluate_ranking


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parent


def validate() -> dict:
    peerqa_root = EXPERIMENT_ROOT / "dataset/raw/evaluation/peerqa"
    dataset = PeerQADataset.from_jsonl(
        peerqa_root / "papers.jsonl",
        peerqa_root / "qa.jsonl",
    )
    sample = dataset.examples[0]
    sample_ranking = list(sample.relevant_evidence_ids)
    metrics = evaluate_ranking(sample_ranking, sample.relevant_evidence_ids, cutoffs=(1, 5))
    checks = {
        "peerqa_adapter": {
            "passed": len(dataset.examples) > 0 and len(dataset.blocks_by_paper) > 0,
            "mapped_examples": len(dataset.examples),
            "papers": len(dataset.blocks_by_paper),
            "blocks": sum(len(blocks) for blocks in dataset.blocks_by_paper.values()),
        },
        "gold_evidence_mapping": {
            "passed": all(example.relevant_evidence_ids for example in dataset.examples),
            "sample_question_id": sample.question_id,
            "sample_gold_count": len(sample.relevant_evidence_ids),
        },
        "retrieval_metrics": {
            "passed": metrics["recall@5"] == 1.0 and metrics["mrr"] == 1.0,
            "metrics": metrics,
        },
    }
    passed = all(check["passed"] for check in checks.values())
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "summary": "PeerQA E2 dataset mapping and retrieval metrics are validated.",
        "checks": checks,
    }


def main() -> None:
    result = validate()
    output = REPO_ROOT / ".omx/specs/autoresearch-peerqa-e2-foundation/result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
