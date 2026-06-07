from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "packages" / "evireview_core"))

from common import DATA_DIR, REPORT_DIR, ensure_dirs, read_jsonl, write_json
from evaluate_local_decision_classifier import classification_metrics
from evireview_core.classification.auxiliary import classify_auxiliary_decision
from evireview_core.domain.models import VerificationResult, Weakness


def main() -> None:
    ensure_dirs()
    human_lookup = {row["weakness_id"]: row for row in read_jsonl(DATA_DIR / "human_weaknesses.jsonl")}
    silver_by_paper: dict[str, list[dict]] = defaultdict(list)
    for row in read_jsonl(DATA_DIR / "weakness_evidence_silver.jsonl"):
        silver_by_paper[row["paper_id"]].append(row)

    gold: list[str] = []
    predicted: list[str] = []
    accept_probabilities: list[float] = []
    for paper_id, items in sorted(silver_by_paper.items()):
        weaknesses = []
        verification = {}
        for item in items:
            human = human_lookup[item["weakness_id"]]
            weakness = Weakness(
                weakness_id=item["weakness_id"],
                paper_id=paper_id,
                weakness_text=item["weakness_text"],
                category=item["category_rule"],
                severity=human["severity_hint"],
                source="human_review",
            )
            weaknesses.append(weakness)
            verification[weakness.weakness_id] = VerificationResult(
                weakness_id=weakness.weakness_id,
                label=item["silver_label"],
                support_score=float(item["silver_support_score"]),
                evidence_block_ids=tuple(item["silver_evidence_block_ids"]),
                rationale=item["silver_rationale"],
                verifier="silver_rule",
            )
        signal = classify_auxiliary_decision(weaknesses, verification)
        decision = items[0]["decision"]
        gold.append(decision)
        predicted.append(signal.label)
        accept_probabilities.append(1.0 - signal.reject_score)

    majority = Counter(gold).most_common(1)[0][0]
    majority_probability = sum(label == "Accept" for label in gold) / len(gold)
    payload = {
        "status": "ok",
        "dataset": "Local PRISM/OpenReview ICLR 2024 sample",
        "task": "transparent evidence-risk auxiliary decision signal",
        "metric_boundary": "diagnostic",
        "warning": "This signal is not for automated paper decisions and does not affect the Agent-RAG audit pipeline.",
        "paper_count": len(gold),
        "decision_counts": dict(Counter(gold)),
        "evidence_risk_signal": classification_metrics(gold, predicted, accept_probabilities),
        "majority_baseline": classification_metrics(
            gold,
            [majority] * len(gold),
            [majority_probability] * len(gold),
        ),
        "existing_metadata_baseline_macro_f1": 0.68,
    }
    write_json(DATA_DIR / "auxiliary_decision_signal_metrics.json", payload)
    signal = payload["evidence_risk_signal"]
    baseline = payload["majority_baseline"]
    lines = [
        "# Auxiliary Evidence-Risk Decision Signal",
        "",
        "This is a transparent diagnostic output after ranking. It is not an automated paper decision.",
        "",
        "| Method | Papers | Accuracy | Macro-F1 | ROC-AUC |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| Evidence-risk signal | {signal['count']} | {signal['accuracy']} | {signal['macro_f1']} | {signal['roc_auc']} |",
        f"| Majority baseline | {baseline['count']} | {baseline['accuracy']} | {baseline['macro_f1']} | {baseline['roc_auc']} |",
        f"| Existing metadata baseline | 50 | - | {payload['existing_metadata_baseline_macro_f1']} | - |",
        "",
        "The evidence-risk signal remains auxiliary unless it clearly exceeds the metadata baseline under stronger validation.",
    ]
    (REPORT_DIR / "auxiliary_decision_signal_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"auxiliary_decision_signal papers={len(gold)} macro_f1={signal['macro_f1']} "
        f"majority_macro_f1={baseline['macro_f1']}"
    )


if __name__ == "__main__":
    main()
