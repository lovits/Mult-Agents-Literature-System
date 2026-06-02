from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from common import DATA_DIR, REPORT_DIR, ensure_dirs

GLM_API_KEY_ENV_NAMES = ("GLM_API_KEY", "ZHIPU_API_KEY", "ZHIPUAI_API_KEY", "BIGMODEL_API_KEY", "ZAI_API_KEY")


def load_json(name: str, default: Any = None) -> Any:
    path = DATA_DIR / name
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def metric_line(module: str, dataset: str, metric: str, result: Any, status: str, note: str) -> str:
    return f"| {module} | {dataset} | {metric} | {fmt(result)} | {status} | {note} |"


def openrouter_status() -> str:
    return "set" if os.getenv("OPENROUTER_API_KEY") else "missing"


def glm_status() -> str:
    return "set" if any(os.getenv(name) for name in GLM_API_KEY_ENV_NAMES) else "missing"


def dashboard_lines() -> list[str]:
    source = load_json("source_reliability_report.json", {})
    human = load_json("human_weaknesses_summary.json", {})
    evidence = load_json("evidence_blocks_summary.json", {})
    retrieval = load_json("retrieval_proxy_eval.json", {})
    substan = load_json("substanreview_baseline_metrics.json", {})
    claimcheck = load_json("claimcheck_summary.json", {})
    claim_retrieval = load_json("claimcheck_openrouter_embedding_metrics.json", {})
    claim_verifier = load_json("claimcheck_feature_verifier_metrics.json", {})
    claim_ranker = load_json("claimcheck_evidence_ranker_metrics.json", {})
    local_classifier = load_json("local_decision_classifier_metrics.json", {})
    rubric_generation = load_json("rubric_agent_weaknesses_summary.json", {})
    rubric_coverage = load_json("rubric_agent_coverage_metrics.json", {})
    rubric_verifier = load_json("rubric_agent_verifier_summary.json", {})
    glm_generation = load_json("glm_reviewer_weaknesses_summary.json", {})
    glm_coverage = load_json("glm_reviewer_coverage_metrics.json", {})
    glm_verifier = load_json("glm_reviewer_verifier_summary.json", {})
    generated_comparison = load_json("generated_reviewer_comparison_metrics.json", {})
    hierarchical_retrieval = load_json("generated_hierarchical_retrieval_summary.json", {})
    human_hierarchical = load_json("retrieval_human_hierarchical_summary.json", {})
    retrieval_queue = load_json("retrieval_comparison_annotation_queue_summary.json", {})
    retrieval_comparison_gold = load_json("retrieval_comparison_gold_summary.json", {})
    retrieval_comparison_metrics = load_json("retrieval_comparison_gold_metrics.json", {})
    ready_datasets = load_json("ready_dataset_candidates.json", {})
    peerreview_bench = load_json("peerreview_bench_baseline_metrics.json", {})
    peerreview_summary = load_json("peerreview_bench_summary.json", {})
    peerqa_xt = load_json("peerqa_xt_retrieval_metrics.json", {})
    reranker = load_json("claimcheck_openrouter_rerank_metrics.json", {})

    retrieval_results = retrieval.get("results", {})
    section_hybrid = retrieval_results.get("section_aware_hybrid", {})
    substan_nb = substan.get("baselines", {}).get("multinomial_naive_bayes_v0", {}).get("test", {})
    claim_main = claim_retrieval.get("splits", {}).get("main", {})
    feature_verifier = claim_verifier.get("feature_verifier", {})
    ranker_metrics = claim_ranker.get("metrics", {})
    best_ranker_name = "-"
    best_ranker = {}
    if ranker_metrics:
        best_ranker_name, best_ranker = max(
            ranker_metrics.items(),
            key=lambda item: (item[1].get("map", 0.0), item[1].get("top1_grounded_rate", 0.0)),
        )
    classifier_results = local_classifier.get("results", [])
    best_classifier = next(
        (item for item in classifier_results if item.get("name") == local_classifier.get("best_method")),
        {},
    )
    coverage_018 = next(
        (item for item in rubric_coverage.get("coverage_by_threshold", []) if item.get("threshold") == 0.18),
        {},
    )
    glm_coverage_018 = next(
        (item for item in glm_coverage.get("coverage_by_threshold", []) if item.get("threshold") == 0.18),
        {},
    )
    comparison_generators = generated_comparison.get("generators", {})
    comparison_rubric = comparison_generators.get("rubric_agent", {})
    comparison_glm = comparison_generators.get("glm_reviewer", {})
    comparison_rubric_018 = next(
        (item for item in comparison_rubric.get("coverage_by_threshold", []) if item.get("threshold") == 0.18),
        {},
    )
    comparison_glm_018 = next(
        (item for item in comparison_glm.get("coverage_by_threshold", []) if item.get("threshold") == 0.18),
        {},
    )
    hierarchical_sources = hierarchical_retrieval.get("sources", {})
    hierarchical_glm = hierarchical_sources.get("glm_reviewer", {})
    hierarchical_rubric = hierarchical_sources.get("rubric_agent", {})
    glm_error_count = len(glm_generation.get("errors", []))
    glm_effective_papers = glm_generation.get("papers_with_generation", 0)
    peerreview_tasks = peerreview_bench.get("tasks", {})
    peerreview_sig_nb = (
        peerreview_tasks.get("significance", {})
        .get("baselines", {})
        .get("balanced_multinomial_naive_bayes_v1", {})
    )
    peerreview_evidence_context = (
        peerreview_tasks.get("evidence", {})
        .get("baselines", {})
        .get("balanced_context_multinomial_naive_bayes_v2", {})
    )
    peerreview_evidence_feature = (
        peerreview_tasks.get("evidence", {})
        .get("baselines", {})
        .get("evidence_aware_feature_logistic_v1", {})
    )
    peerqa_hybrid = peerqa_xt.get("methods", {}).get("hybrid_question", {})
    peerqa_bm25 = peerqa_xt.get("methods", {}).get("bm25_question", {})
    peerqa_section = peerqa_xt.get("methods", {}).get("section_aware_question", {})
    peerqa_hierarchical = peerqa_xt.get("methods", {}).get("hierarchical_question", {})
    peerqa_methods = {
        name: item for name, item in peerqa_xt.get("methods", {}).items() if name != "oracle_answer_query"
    }
    peerqa_oracle = peerqa_xt.get("methods", {}).get("oracle_answer_query", {})
    peerqa_best_hit3_name = "-"
    peerqa_best_hit3 = {}
    if peerqa_methods:
        peerqa_best_hit3_name, peerqa_best_hit3 = max(
            peerqa_methods.items(),
            key=lambda item: (
                item[1].get("answer_support_hit_at_3", 0.0),
                item[1].get("answer_support_hit_at_1", 0.0),
            ),
        )
    ready_count = len([item for item in ready_datasets.get("candidates", []) if item.get("status") == "reachable"])

    lines = [
        "# EviReview-Lite Experiment Dashboard",
        "",
        "This dashboard aggregates the current A-version experiment state across dataset audit, retrieval, verification, ranking, generation, and auxiliary classification.",
        "",
        "## Environment",
        "",
        f"- OpenRouter API key: `{openrouter_status()}`",
        f"- GLM/Zhipu API key: `{glm_status()}`; accepted env names: `{', '.join(GLM_API_KEY_ENV_NAMES)}`.",
        "- Raw CLAIMCHECK row-level text policy: do not commit raw text because no upstream LICENSE was detected.",
        "- Local OpenReview/PRISM sample remains the end-to-end application dataset.",
        "",
        "## Module Metrics",
        "",
        "| Module | Dataset | Primary metric | Result | Status | Note |",
        "| --- | --- | --- | ---: | --- | --- |",
        metric_line(
            "Source audit",
            "Local OpenReview/PRISM",
            "Matched papers",
            f"{source.get('matched_count', 50)} / {source.get('manifest_count', 50)}",
            "done",
            "OpenReview source chain validated.",
        ),
        metric_line(
            "Human weakness extraction",
            "Local OpenReview/PRISM",
            "Weakness items",
            human.get("weakness_item_count"),
            "done",
            "Human-review upper-bound source for generation coverage.",
        ),
        metric_line(
            "Evidence blocks",
            "Local OpenReview/PRISM",
            "Blocks",
            evidence.get("evidence_block_count"),
            "done",
            "Paper-RAG substrate.",
        ),
        metric_line(
            "Section-aware retrieval",
            "Local OpenReview/PRISM",
            "Top-3 section alignment",
            section_hybrid.get("top3_any_section_alignment_rate"),
            "done",
            "Best local retrieval proxy so far.",
        ),
        metric_line(
            "Substantiation verifier floor",
            "SubstanReview",
            "Naive Bayes Macro-F1",
            substan_nb.get("macro_f1"),
            "done",
            "Licensed supervised review-internal substantiation baseline.",
        ),
        metric_line(
            "Ready dataset search",
            "External datasets",
            "Reachable candidates",
            ready_count,
            ready_datasets.get("status", "not run"),
            "Prioritizes no-new-manual-label datasets aligned with the opening report.",
        ),
        metric_line(
            "PeerReview Bench baseline",
            "PeerReview Bench",
            "Significance NB Macro-F1",
            peerreview_sig_nb.get("macro_f1"),
            peerreview_bench.get("status", "not run"),
            f"{peerreview_summary.get('downloaded_rows', 0)} rows; evidence-aware feature Macro-F1 {fmt(peerreview_evidence_feature.get('macro_f1'))}.",
        ),
        metric_line(
            "Paper-RAG QA retrieval",
            "PeerQA-XT",
            f"{peerqa_best_hit3_name} Hit@3",
            peerqa_best_hit3.get("answer_support_hit_at_3"),
            peerqa_xt.get("status", "not run"),
            f"{peerqa_xt.get('downloaded_rows', 0)} rows; section-aware Hit@3 {fmt(peerqa_section.get('answer_support_hit_at_3'))}; oracle ceiling Hit@3 {fmt(peerqa_oracle.get('answer_support_hit_at_3'))}.",
        ),
        metric_line(
            "Claim retrieval",
            "CLAIMCHECK",
            "OpenRouter embedding Hit@3",
            claim_main.get("hit_at_3"),
            "done",
            "Semantic retrieval improves over lexical baselines.",
        ),
        metric_line(
            "Groundedness verifier",
            "CLAIMCHECK",
            "Feature verifier Macro-F1",
            feature_verifier.get("macro_f1"),
            "diagnostic",
            "Verifier still weak, especially as final decision module.",
        ),
        metric_line(
            "Evidence-aware ranker",
            "CLAIMCHECK",
            f"{best_ranker_name} MAP",
            best_ranker.get("map"),
            "diagnostic",
            "BM25 currently beats feature-verifier probability for ranking.",
        ),
        metric_line(
            "Auxiliary classifier",
            "Local OpenReview/PRISM",
            f"{local_classifier.get('best_method', '-')} Macro-F1",
            best_classifier.get("aggregate", {}).get("macro_f1"),
            "diagnostic",
            "Classification remains auxiliary; metadata baseline is strongest.",
        ),
        metric_line(
            "Rubric-agent generation",
            "Local OpenReview/PRISM",
            "Coverage recall @ 0.18",
            coverage_018.get("human_weakness_recall"),
            "pipeline baseline",
            "Deterministic reviewer validates Agent -> RAG interface.",
        ),
        metric_line(
            "GLM-4.6V reviewer sample",
            "Local OpenReview/PRISM",
            "Coverage recall @ 0.18",
            glm_coverage_018.get("human_weakness_recall"),
            glm_generation.get("status", "not run"),
            f"{glm_generation.get('generated_weakness_count', 0)} generated; labels: {glm_verifier.get('label_counts', {})}",
        ),
        metric_line(
            "Paired reviewer comparison",
            "GLM overlap papers",
            "Coverage recall @ 0.18",
            comparison_glm_018.get("human_weakness_recall"),
            "diagnostic",
            f"GLM vs rubric: {comparison_glm_018.get('human_weakness_recall', '-')} vs {comparison_rubric_018.get('human_weakness_recall', '-')}",
        ),
        metric_line(
            "Hierarchical Paper-RAG",
            "Generated weaknesses",
            "GLM mean support",
            hierarchical_glm.get("mean_support_score"),
            "diagnostic",
            f"GLM partial+ {hierarchical_glm.get('partially_supported_or_better_rate', '-')}; rubric support {hierarchical_rubric.get('mean_support_score', '-')}",
        ),
        metric_line(
            "Human hierarchical retrieval",
            "Local OpenReview/PRISM",
            "Top-1 section alignment",
            human_hierarchical.get("top1_section_alignment_rate"),
            "diagnostic",
            f"{human_hierarchical.get('query_count', 0)} human weaknesses; top tools {human_hierarchical.get('top1_tool_mix', {})}",
        ),
        metric_line(
            "Retrieval comparison queue",
            "Human weaknesses",
            "Selected annotation rows",
            retrieval_queue.get("selected_rows"),
            retrieval_queue.get("status", "not run"),
            f"Top-1 disagreement {retrieval_queue.get('top1_disagreement_rate', '-')}; Top-3 disagreement {retrieval_queue.get('top3_disagreement_rate', '-')}",
        ),
        metric_line(
            "Retrieval comparison gold",
            "Human weaknesses",
            "Gold rows",
            retrieval_comparison_gold.get("gold_rows", 0),
            retrieval_comparison_gold.get("status", "not imported"),
            f"Evaluation status: {retrieval_comparison_metrics.get('status', 'not run')}",
        ),
        metric_line(
            "Generated weakness verifier/ranker",
            "Local OpenReview/PRISM",
            "Generated weaknesses verified",
            rubric_verifier.get("generated_weakness_count"),
            "pipeline baseline",
            f"Label counts: {rubric_verifier.get('label_counts', {})}",
        ),
    ]

    lines.extend(
        [
            "",
            "## Dataset Coverage",
            "",
            "| Dataset | Current use | Evidence | Remaining gap |",
            "| --- | --- | --- | --- |",
            f"| Local OpenReview/PRISM | End-to-end A-version dataset | {human.get('paper_count', 50)} papers, {human.get('weakness_item_count', 0)} human weakness items, {evidence.get('evidence_block_count', 0)} evidence blocks | Human weakness-evidence gold labels still incomplete |",
            f"| SubstanReview | Supervised substantiation floor | Test Macro-F1 {fmt(substan_nb.get('macro_f1'))} | Review-internal evidence only, not full paper-grounding |",
            f"| PeerReview Bench | No-manual-label review-quality/verifier baseline | {peerreview_summary.get('downloaded_rows', 0)} local rows from {peerreview_summary.get('total_available_rows', '-')} expert annotations; significance balanced review Macro-F1 {fmt(peerreview_sig_nb.get('macro_f1'))}; evidence-aware feature Macro-F1 {fmt(peerreview_evidence_feature.get('macro_f1'))} | Labels remain imbalanced; evidence minority recall improved but is still the main gap |",
            f"| PeerQA-XT | No-manual-label Paper-RAG QA retrieval | {peerqa_xt.get('downloaded_rows', 0)} local retrieval rows from {peerqa_xt.get('total_available_rows', '-')} test rows; best Hit@3 {fmt(peerqa_best_hit3.get('answer_support_hit_at_3'))} via {peerqa_best_hit3_name} | No gold evidence spans; current metric is answer-token support proxy |",
            f"| CLAIMCHECK | Paper-grounded critique benchmark | {claimcheck.get('main', {}).get('weakness_count', 155)} main weaknesses; embedding Hit@3 {fmt(claim_main.get('hit_at_3'))} | Raw row-level text not committed; verifier still weak |",
            "",
            "## Current Risks",
            "",
            f"- OpenRouter chat reranker status: `{reranker.get('status', 'unknown')}`; reason: {reranker.get('reason', 'not recorded')}.",
            f"- GLM-4.6V reviewer result now covers {glm_effective_papers} valid papers; current JSON parsing failures: {glm_error_count}.",
            "- Paired GLM-vs-rubric comparison currently covers only the GLM overlap papers.",
            "- Hierarchical Paper-RAG currently uses silver verifier labels; treat support gains as architecture diagnostics, not final truth.",
            "- Human hierarchical retrieval has high section-alignment proxy scores, but true evidence support still needs the 300-row comparison queue to be labeled.",
            f"- Retrieval comparison gold status: `{retrieval_comparison_gold.get('status', 'not imported')}`; current gold rows: {retrieval_comparison_gold.get('gold_rows', 0)}.",
            "- Generated rubric-agent weaknesses are mostly heuristic structure warnings; current verifier labels are mostly Unsupported / Mentioned.",
            "- Local classification is exploratory: metadata baseline is stronger than evidence-proxy features.",
            "- PeerReview Bench sample labels are imbalanced, so Macro-F1 is more important than accuracy.",
            "- PeerQA-XT does not provide gold evidence spans; answer-support Hit@K is a retrieval proxy, not final evidence precision.",
            "- CLAIMCHECK and local silver labels are diagnostics until human gold labels or licensed row-level benchmark evaluation are stronger.",
            "",
            "## Next Experiments",
            "",
            "1. Add context-aware PeerReview Bench features or an LLM verifier because full-data review-item NB still misses minority evidence labels.",
            "2. Improve PeerQA-XT query decomposition using data-driven or LLM-generated subqueries; current hand-written expansion hurts retrieval while section-aware scoring only ties the best lexical floor.",
            "3. Freeze the clean 10-paper GLM diagnostic table for the experiment chapter, while keeping the conclusion scoped as silver-label evidence rather than human-gold evaluation.",
            "4. Keep OpenRouter chat reranker/verifier as optional because the free provider is rate-limited.",
            "5. Label the 300-row retrieval comparison queue only if external ready-label datasets still leave a gap in local Paper-RAG evidence support.",
        ]
    )
    return lines


def main() -> None:
    ensure_dirs()
    out_path = REPORT_DIR / "experiment_dashboard.md"
    out_path.write_text("\n".join(dashboard_lines()) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
