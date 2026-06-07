from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "packages" / "evireview_core"))

from common import DATA_DIR, REPORT_DIR, read_jsonl, write_json
from evireview_core.domain.models import EvidenceBlock, Weakness
from evireview_core.verification.labels import is_supported_or_better
from evireview_core.workflow.graph import ReviewAuditGraph
from evireview_core.workflow.state import ReviewAuditState


PROFILES = ("full", "no_dedup", "no_verifier", "no_ranker")


def mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def main() -> None:
    weaknesses_by_paper: dict[str, list[Weakness]] = defaultdict(list)
    for row in read_jsonl(DATA_DIR / "rubric_agent_weaknesses.jsonl"):
        weaknesses_by_paper[row["paper_id"]].append(
            Weakness(
                weakness_id=row["generated_weakness_id"],
                paper_id=row["paper_id"],
                weakness_text=row["weakness_text"],
                category=row["category"],
                severity=row["severity"],
                source="rubric_agent",
            )
        )
    blocks_by_paper: dict[str, list[EvidenceBlock]] = defaultdict(list)
    for row in read_jsonl(DATA_DIR / "evidence_blocks.jsonl"):
        blocks_by_paper[row["paper_id"]].append(EvidenceBlock.from_dict(row))

    selected: dict[str, list[tuple[str, str]]] = defaultdict(list)
    profile_candidate_counts: dict[str, int] = defaultdict(int)
    profile_deduplicated_counts: dict[str, int] = defaultdict(int)
    profile_duplicate_counts: dict[str, int] = defaultdict(int)
    reference: dict[str, Any] = {}
    for paper_id, weaknesses in weaknesses_by_paper.items():
        full = ReviewAuditGraph("full").run(
            ReviewAuditState(weaknesses=list(weaknesses), evidence_blocks=blocks_by_paper[paper_id])
        )
        reference.update(full.verification)
        selected["full"].extend((paper_id, item.weakness_id) for item in full.ranked_findings)
        profile_candidate_counts["full"] += len(full.weaknesses)
        profile_deduplicated_counts["full"] += len(full.deduplicated_weaknesses)
        profile_duplicate_counts["full"] += len(full.duplicate_of)
        for profile in ("no_dedup", "no_verifier", "no_ranker"):
            state = ReviewAuditGraph(profile).run(
                ReviewAuditState(weaknesses=list(weaknesses), evidence_blocks=blocks_by_paper[paper_id])
            )
            selected[profile].extend((paper_id, item.weakness_id) for item in state.ranked_findings)
            profile_candidate_counts[profile] += len(state.weaknesses)
            profile_deduplicated_counts[profile] += len(state.deduplicated_weaknesses)
            profile_duplicate_counts[profile] += len(state.duplicate_of)

    full_set = set(selected["full"])
    profiles = {}
    for profile in PROFILES:
        rows = selected[profile]
        reference_results = [reference[weakness_id] for _, weakness_id in rows]
        profiles[profile] = {
            "candidate_count": profile_candidate_counts[profile],
            "deduplicated_count": profile_deduplicated_counts[profile],
            "duplicate_count": profile_duplicate_counts[profile],
            "candidate_reduction_rate": mean(
                [profile_duplicate_counts[profile] / profile_candidate_counts[profile]]
            ),
            "selected_count": len(rows),
            "mean_reference_support": mean([item.support_score for item in reference_results]),
            "reference_partial_or_better_rate": mean(
                [float(is_supported_or_better(item.label)) for item in reference_results]
            ),
            "reference_unsupported_rate": mean([float(item.label == "Unsupported") for item in reference_results]),
            "topk_overlap_with_full": mean([float(item in full_set) for item in rows]),
        }
    payload = {
        "status": "ok",
        "dataset": "Local OpenReview/PRISM",
        "task": "agent_rag_graph_ablation",
        "metric_boundary": "silver",
        "paper_count": len(weaknesses_by_paper),
        "candidate_count": sum(len(items) for items in weaknesses_by_paper.values()),
        "profiles": profiles,
        "note": "All selected findings are evaluated against the full graph heuristic verifier as a shared silver reference.",
    }
    write_json(DATA_DIR / "graph_ablation_metrics.json", payload)
    lines = [
        "# Agent-RAG Graph Ablation",
        "",
        "| Profile | Candidates | Deduplicated | Removed | Reduction | Selected | Mean reference support | Reference partial+ | Reference unsupported | Top-K overlap with full |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for profile in PROFILES:
        row = profiles[profile]
        lines.append(
            f"| {profile} | {row['candidate_count']} | {row['deduplicated_count']} | {row['duplicate_count']} | "
            f"{row['candidate_reduction_rate']} | {row['selected_count']} | {row['mean_reference_support']} | "
            f"{row['reference_partial_or_better_rate']} | {row['reference_unsupported_rate']} | "
            f"{row['topk_overlap_with_full']} |"
        )
    lines.extend(
        [
            "",
            "All metrics use the full graph heuristic verifier as a shared silver reference. This is an ablation diagnostic, not human-gold evaluation.",
        ]
    )
    (REPORT_DIR / "graph_ablation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"graph_ablation papers={payload['paper_count']} candidates={payload['candidate_count']}")


if __name__ == "__main__":
    main()
