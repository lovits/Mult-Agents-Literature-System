from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from common import DATA_DIR, REPORT_DIR, ensure_dirs


DOCS_PROGRESS_DIR = Path(__file__).resolve().parents[4] / "docs" / "progress"
OUT_REPORT = "thesis_experiment_tables.md"


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


def coverage_at(payload: dict[str, Any], threshold: float) -> dict[str, Any]:
    return next((row for row in payload.get("coverage_by_threshold", []) if row.get("threshold") == threshold), {})


def method_row(name: str, row: dict[str, Any]) -> str:
    return (
        f"| {name} | {fmt(row.get('answer_support_hit_at_1'))} | "
        f"{fmt(row.get('answer_support_hit_at_3'))} | {fmt(row.get('answer_support_hit_at_5'))} | "
        f"{fmt(row.get('mean_answer_token_recall_at_3'))} |"
    )


def table_lines() -> list[str]:
    source = load_json("source_reliability_report.json", {})
    human = load_json("human_weaknesses_summary.json", {})
    evidence = load_json("evidence_blocks_summary.json", {})
    substan = load_json("substanreview_baseline_metrics.json", {})
    peerreview = load_json("peerreview_bench_baseline_metrics.json", {})
    peerreview_summary = load_json("peerreview_bench_summary.json", {})
    peerqa = load_json("peerqa_xt_retrieval_metrics.json", {})
    claimcheck = load_json("claimcheck_summary.json", {})
    claim_feature = load_json("claimcheck_feature_verifier_metrics.json", {})
    claim_ranker = load_json("claimcheck_evidence_ranker_metrics.json", {})
    retrieval = load_json("retrieval_proxy_eval.json", {})
    generated_comparison = load_json("generated_reviewer_comparison_metrics.json", {})
    generated_hierarchical = load_json("generated_hierarchical_retrieval_summary.json", {})
    generated_ranker = load_json("generated_weakness_ranker_metrics.json", {})
    rubric_generation = load_json("rubric_agent_weaknesses_summary.json", {})
    rubric_coverage = load_json("rubric_agent_coverage_metrics.json", {})
    glm_generation = load_json("glm_reviewer_weaknesses_summary.json", {})
    glm_coverage = load_json("glm_reviewer_coverage_metrics.json", {})
    local_classifier = load_json("local_decision_classifier_metrics.json", {})
    claimcheck_main = claimcheck.get("splits", {}).get("main", {})

    substan_nb = substan.get("baselines", {}).get("multinomial_naive_bayes_v0", {}).get("test", {})
    peerreview_tasks = peerreview.get("tasks", {})
    peerreview_evidence = (
        peerreview_tasks.get("evidence", {})
        .get("baselines", {})
        .get("evidence_aware_feature_logistic_v1", {})
    )
    peerreview_sig = (
        peerreview_tasks.get("significance", {})
        .get("baselines", {})
        .get("balanced_multinomial_naive_bayes_v1", {})
    )
    peerreview_correct = (
        peerreview_tasks.get("correctness", {})
        .get("baselines", {})
        .get("balanced_context_multinomial_naive_bayes_v2", {})
    )
    peerqa_methods = peerqa.get("methods", {})
    retrieval_results = retrieval.get("results", {})
    generated_sources = generated_hierarchical.get("sources", {})
    generated_ranker_sources = generated_ranker.get("sources", {})
    comparison_generators = generated_comparison.get("generators", {})
    comparison_rubric = comparison_generators.get("rubric_agent", {})
    comparison_glm = comparison_generators.get("glm_reviewer", {})
    comparison_rubric_018 = coverage_at(comparison_rubric, 0.18)
    comparison_glm_018 = coverage_at(comparison_glm, 0.18)
    rubric_018 = coverage_at(rubric_coverage, 0.18)
    glm_018 = coverage_at(glm_coverage, 0.18)
    claim_ranker_metrics = claim_ranker.get("metrics", {})
    best_claim_ranker_name = "-"
    best_claim_ranker = {}
    if claim_ranker_metrics:
        best_claim_ranker_name, best_claim_ranker = max(
            claim_ranker_metrics.items(),
            key=lambda item: (item[1].get("map", 0.0), item[1].get("top1_grounded_rate", 0.0)),
        )
    best_classifier = next(
        (
            item
            for item in local_classifier.get("results", [])
            if item.get("name") == local_classifier.get("best_method")
        ),
        {},
    )

    lines = [
        "# EviReview-Lite Thesis Experiment Tables",
        "",
        "用途：本文件把当前 A 版实验结果整理成毕业论文实验章节可直接引用的表格。所有数值来自已落盘的 metrics JSON；未人工标注的结果统一写成 proxy / diagnostic。",
        "",
        "## Table 1. 数据集与实验角色",
        "",
        "| 数据集 / 样本 | 当前规模 | 用途 | 标签 / 监督来源 | 写作口径 |",
        "| --- | ---: | --- | --- | --- |",
        (
            f"| Local OpenReview/PRISM | {human.get('paper_count', 0)} papers / "
            f"{human.get('weakness_item_count', 0)} weaknesses / {evidence.get('evidence_block_count', 0)} blocks | "
            "端到端论文评审辅助主数据 | OpenReview human reviews + paper text | 主应用场景；evidence gold 未完成 |"
        ),
        (
            f"| SubstanReview | {substan_nb.get('count', 0)} test claims | "
            "substantiation verifier floor | Eval/Jus span pair | 外部人标 verifier 参照 |"
        ),
        (
            f"| PeerReview Bench | {peerreview_summary.get('downloaded_rows', peerreview.get('row_count', 0))} annotations | "
            "review-quality/verifier baseline | correctness / significance / evidence labels | 无需新增人工标注的 verifier 辅助实验 |"
        ),
        (
            f"| PeerQA-XT | {peerqa.get('downloaded_rows', 0)} / {peerqa.get('total_available_rows', '-')} test rows | "
            "Paper-RAG QA retrieval | peer-review-derived question + answer | answer-token support proxy，不是 gold evidence span |"
        ),
        (
            f"| CLAIMCHECK | {claimcheck_main.get('weakness_count', 0)} main weaknesses | "
            "paper-grounded critique verifier/ranker | Grounded / Ungrounded labels | 只提交聚合结果，不提交 raw row text |"
        ),
        (
            f"| GLM-4.6V reviewer sample | {glm_generation.get('papers_with_generation', 0)} papers / "
            f"{glm_generation.get('generated_weakness_count', 0)} weaknesses | LLM reviewer candidate generation | model-generated + silver verifier | clean 10-paper diagnostic，不是最终 provider benchmark |"
        ),
        "",
        "## Table 2. 本地 OpenReview Paper-RAG 检索",
        "",
        "| 方法 | Query count | Non-empty | Top-1 section align | Top-3 section align | 说明 |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for name, label in [
        ("bm25", "BM25"),
        ("tfidf_cosine", "TF-IDF cosine"),
        ("hybrid_bm25_tfidf", "Hybrid"),
        ("section_aware_hybrid", "Section-aware hybrid"),
        ("human_hierarchical_paper_rag", "Hierarchical Paper-RAG"),
    ]:
        row = retrieval_results.get(name, {})
        lines.append(
            f"| {label} | {row.get('query_count', '-')} | {fmt(row.get('non_empty_rate'))} | "
            f"{fmt(row.get('top1_section_alignment_rate'))} | {fmt(row.get('top3_any_section_alignment_rate'))} | "
            "section-alignment proxy |"
        )

    lines.extend(
        [
            "",
            "## Table 3. PeerQA-XT Paper-RAG QA 检索",
            "",
            "| 方法 | Hit@1 | Hit@3 | Hit@5 | Mean answer-token recall@3 |",
            "| --- | ---: | ---: | ---: | ---: |",
            method_row("BM25 question", peerqa_methods.get("bm25_question", {})),
            method_row("Hybrid question", peerqa_methods.get("hybrid_question", {})),
            method_row("Section-aware question", peerqa_methods.get("section_aware_question", {})),
            method_row("Hierarchical question", peerqa_methods.get("hierarchical_question", {})),
            method_row("PRF section-aware question", peerqa_methods.get("prf_section_aware_question", {})),
            method_row("Query decomposed question", peerqa_methods.get("query_decomposed_question", {})),
            method_row("Domain section-aware question", peerqa_methods.get("domain_section_aware_question", {})),
            method_row("Oracle answer query", peerqa_methods.get("oracle_answer_query", {})),
            "",
            "结论口径：section-aware 是当前最稳 non-oracle 方法；oracle answer query 显示检索空间存在足够证据，但手写 query decomposition 与 PRF expansion 都会降低结果。",
            "",
            "## Table 4. Verifier / Review-quality Baselines",
            "",
            "| 数据集 | 任务 | 方法 | 主指标 | 少数类 / 关键类表现 | 写作口径 |",
            "| --- | --- | --- | ---: | --- | --- |",
            (
                f"| SubstanReview | claim substantiation | Multinomial NB | Macro-F1 {fmt(substan_nb.get('macro_f1'))} | "
                f"Supported F1 {fmt(substan_nb.get('per_label', {}).get('Supported', {}).get('f1'))} | supervised verifier floor |"
            ),
            (
                f"| CLAIMCHECK | Grounded/Ungrounded | Feature verifier | Macro-F1 {fmt(claim_feature.get('feature_verifier', {}).get('macro_f1'))} | "
                f"Ungrounded F1 {fmt(claim_feature.get('feature_verifier', {}).get('per_label', {}).get('Ungrounded', {}).get('f1'))} | diagnostic; verifier 仍弱 |"
            ),
            (
                f"| PeerReview Bench | evidence | Evidence-aware feature logistic | Macro-F1 {fmt(peerreview_evidence.get('macro_f1'))} | "
                f"Requires More recall {fmt(peerreview_evidence.get('per_label', {}).get('Requires More', {}).get('recall'))} | 少数类 recall 是主要缺口 |"
            ),
            (
                f"| PeerReview Bench | significance | Balanced NB | Macro-F1 {fmt(peerreview_sig.get('macro_f1'))} | "
                f"Not Significant recall {fmt(peerreview_sig.get('per_label', {}).get('Not Significant', {}).get('recall'))} | review-quality auxiliary |"
            ),
            (
                f"| PeerReview Bench | correctness | Balanced context NB | Macro-F1 {fmt(peerreview_correct.get('macro_f1'))} | "
                f"Not Correct recall {fmt(peerreview_correct.get('per_label', {}).get('Not Correct', {}).get('recall'))} | review-quality auxiliary |"
            ),
            "",
            "## Table 5. Reviewer Agent 生成与同批对比",
            "",
            "| 生成器 | Papers | Generated weaknesses | Generic rate | Coverage recall@0.18 | Mean support | Partial+ rate | 说明 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
            (
                f"| Rubric-agent full baseline | 50 | {rubric_generation.get('generated_weakness_count', 0)} | "
                f"{fmt(rubric_coverage.get('generic_rate'))} | {fmt(rubric_018.get('human_weakness_recall'))} | "
                "- | - | deterministic pipeline baseline |"
            ),
            (
                f"| GLM-4.6V clean sample | {glm_generation.get('papers_with_generation', 0)} | "
                f"{glm_generation.get('generated_weakness_count', 0)} | {fmt(glm_coverage.get('generic_rate'))} | "
                f"{fmt(glm_018.get('human_weakness_recall'))} | {fmt(load_json('glm_reviewer_verifier_summary.json', {}).get('mean_support_score'))} | "
                f"{fmt((load_json('glm_reviewer_verifier_summary.json', {}).get('label_counts', {}).get('Partially Supported', 0) + load_json('glm_reviewer_verifier_summary.json', {}).get('label_counts', {}).get('Supported', 0)) / max(load_json('glm_reviewer_verifier_summary.json', {}).get('verified_count', 0), 1))} | clean 10-paper diagnostic |"
            ),
            (
                f"| Rubric-agent on GLM overlap | {comparison_rubric.get('paper_count', 0)} | {comparison_rubric.get('generated_weakness_count', 0)} | "
                f"{fmt(comparison_rubric.get('generic_rate'))} | {fmt(comparison_rubric_018.get('human_weakness_recall'))} | "
                f"{fmt(comparison_rubric.get('support', {}).get('mean_support_score'))} | "
                f"{fmt(comparison_rubric.get('support', {}).get('partially_supported_or_better_rate'))} | paired comparison |"
            ),
            (
                f"| GLM-4.6V on overlap | {comparison_glm.get('paper_count', 0)} | {comparison_glm.get('generated_weakness_count', 0)} | "
                f"{fmt(comparison_glm.get('generic_rate'))} | {fmt(comparison_glm_018.get('human_weakness_recall'))} | "
                f"{fmt(comparison_glm.get('support', {}).get('mean_support_score'))} | "
                f"{fmt(comparison_glm.get('support', {}).get('partially_supported_or_better_rate'))} | paired comparison |"
            ),
            "",
            "## Table 6. Hierarchical Paper-RAG 与 Generated Weakness Ranker",
            "",
            "| Source | Candidates | Hierarchical mean support | Hierarchical partial+ | Top-3 rows | Top-3 mean support | Top-3 partial+ | 写作口径 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for source, display in [("glm_reviewer", "GLM-4.6V reviewer"), ("rubric_agent", "Rubric-agent")]:
        h_row = generated_sources.get(source, {})
        r_row = generated_ranker_sources.get(source, {})
        lines.append(
            f"| {display} | {h_row.get('generated_weakness_count', r_row.get('candidate_count', 0))} | "
            f"{fmt(h_row.get('mean_support_score'))} | {fmt(h_row.get('partially_supported_or_better_rate'))} | "
            f"{r_row.get('top3_count', 0)} | {fmt(r_row.get('top3_mean_support'))} | "
            f"{fmt(r_row.get('top3_partially_supported_or_better_rate'))} | silver-label diagnostic |"
        )

    lines.extend(
        [
            "",
            "## Table 7. Evidence-aware Ranker 外部诊断与辅助分类",
            "",
            "| 模块 | 数据集 | 方法 | 指标 | 说明 |",
            "| --- | --- | --- | ---: | --- |",
            (
                f"| Claim evidence ranker | CLAIMCHECK | {best_claim_ranker_name} | MAP {fmt(best_claim_ranker.get('map'))} | "
                f"Top-1 grounded rate {fmt(best_claim_ranker.get('top1_grounded_rate'))} |"
            ),
            (
                f"| Auxiliary accept/reject classifier | Local OpenReview/PRISM | {local_classifier.get('best_method', '-')} | "
                f"Macro-F1 {fmt(best_classifier.get('aggregate', {}).get('macro_f1'))} | 只作为辅助案例分析 |"
            ),
            "",
            "## 实验章节写作口径",
            "",
            "- 主贡献写成：Reviewer Agent 生成候选弱点，Paper-RAG 检索证据，Verifier 判定支持度，Ranker 输出可审计 top weaknesses。",
            "- PeerQA-XT、PeerReview Bench、SubstanReview、CLAIMCHECK 都是不新增人工标注的外部实验支撑，但各自只覆盖 retrieval / verifier / ranker 的一部分。",
            "- GLM-4.6V clean 10-paper 结果用于 provider diagnostic；不能写成最终模型优劣排名。",
            "- Local OpenReview 的 300-row retrieval comparison queue 仍未人工标注，因此 section-aware vs hierarchical 的最终 evidence hit 不能下定论。",
            "- Accept/reject classification 是 auxiliary，不应成为系统主指标。",
        ]
    )
    return lines


def main() -> None:
    ensure_dirs()
    DOCS_PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    text = "\n".join(table_lines()) + "\n"
    report_path = REPORT_DIR / OUT_REPORT
    docs_path = DOCS_PROGRESS_DIR / "evireview_thesis_experiment_tables_2026-06-02.md"
    report_path.write_text(text, encoding="utf-8")
    docs_path.write_text(text, encoding="utf-8")
    print(f"Wrote {report_path}")
    print(f"Wrote {docs_path}")


if __name__ == "__main__":
    main()
