# EviReview-Lite A Version Experiments

This experiment directory implements the first reproducible pass of the EviReview-Lite thesis plan.

Main dataset:

`code/dataset/prism_iclr2024_sample`

Human-annotated verifier benchmark:

`SubstanReview` from `https://github.com/YanzhuGuo/SubstanReview`

Paper-grounded weakness benchmark:

`CLAIMCHECK` from `https://github.com/JHU-CLSP/CLAIMCHECK`

Primary A-version tasks:

1. Prepare a clean manifest and dataset audit.
2. Validate the OpenReview source chain.
3. Extract human reviewer weaknesses from review text.
4. Build paper evidence blocks and retrieval baselines in later steps.

Run from the repository root:

```bash
python3 code/experiments/evireview_a/src/prepare_manifest.py
python3 code/experiments/evireview_a/src/validate_openreview_source.py
python3 code/experiments/evireview_a/src/extract_human_weaknesses.py
python3 code/experiments/evireview_a/src/build_evidence_blocks.py
python3 code/experiments/evireview_a/src/retrieve_bm25.py
python3 code/experiments/evireview_a/src/retrieve_tfidf.py
python3 code/experiments/evireview_a/src/retrieve_hybrid_section.py
python3 code/experiments/evireview_a/src/evaluate_retrieval_proxy.py
python3 code/experiments/evireview_a/src/build_annotation_candidates.py
python3 code/experiments/evireview_a/src/export_annotation_sheet.py
python3 code/experiments/evireview_a/src/bootstrap_silver_labels.py
python3 code/experiments/evireview_a/src/verify_evidence_baseline.py
python3 code/experiments/evireview_a/src/render_verifier_report.py
python3 code/experiments/evireview_a/src/select_gold_pilot_batch.py
python3 code/experiments/evireview_a/src/import_gold_labels.py
python3 code/experiments/evireview_a/src/evaluate_verifier_against_gold.py
python3 code/experiments/evireview_a/src/fetch_substanreview.py
python3 code/experiments/evireview_a/src/prepare_substanreview.py
python3 code/experiments/evireview_a/src/evaluate_substanreview_baseline.py
python3 code/experiments/evireview_a/src/render_substanreview_report.py
python3 code/experiments/evireview_a/src/probe_ready_datasets.py
python3 code/experiments/evireview_a/src/prepare_peerreview_bench.py
python3 code/experiments/evireview_a/src/evaluate_peerreview_bench_baseline.py
python3 code/experiments/evireview_a/src/evaluate_peerqa_xt_retrieval.py
python3 code/experiments/evireview_a/src/fetch_claimcheck_texts.py
python3 code/experiments/evireview_a/src/prepare_claimcheck.py
python3 code/experiments/evireview_a/src/evaluate_claimcheck_baseline.py
python3 code/experiments/evireview_a/src/render_claimcheck_report.py
python3 code/experiments/evireview_a/src/evaluate_claimcheck_retrieval.py
python3 code/experiments/evireview_a/src/render_claimcheck_retrieval_report.py
python3 code/experiments/evireview_a/src/evaluate_claimcheck_openrouter_embeddings.py
python3 code/experiments/evireview_a/src/render_claimcheck_openrouter_report.py
python3 code/experiments/evireview_a/src/evaluate_claimcheck_openrouter_reranker.py
python3 code/experiments/evireview_a/src/render_claimcheck_openrouter_rerank_report.py
python3 code/experiments/evireview_a/src/evaluate_claimcheck_openrouter_verifier.py
python3 code/experiments/evireview_a/src/render_claimcheck_openrouter_verifier_report.py
python3 code/experiments/evireview_a/src/evaluate_claimcheck_feature_verifier.py
python3 code/experiments/evireview_a/src/render_claimcheck_feature_verifier_report.py
python3 code/experiments/evireview_a/src/evaluate_claimcheck_evidence_ranker.py
python3 code/experiments/evireview_a/src/render_claimcheck_evidence_ranker_report.py
python3 code/experiments/evireview_a/src/evaluate_local_decision_classifier.py
python3 code/experiments/evireview_a/src/render_local_decision_classifier_report.py
python3 code/experiments/evireview_a/src/generate_rubric_agent_weaknesses.py
python3 code/experiments/evireview_a/src/evaluate_rubric_agent_coverage.py
python3 code/experiments/evireview_a/src/retrieve_rubric_agent_evidence.py
python3 code/experiments/evireview_a/src/verify_rubric_agent_weaknesses.py
python3 code/experiments/evireview_a/src/render_rubric_agent_report.py
python3 code/experiments/evireview_a/src/run_glm_reviewer_experiment.py
python3 code/experiments/evireview_a/src/compare_generated_reviewers.py
python3 code/experiments/evireview_a/src/retrieve_generated_hierarchical.py
python3 code/experiments/evireview_a/src/retrieve_human_hierarchical.py
python3 code/experiments/evireview_a/src/build_retrieval_comparison_annotation_queue.py
python3 code/experiments/evireview_a/src/import_retrieval_comparison_gold.py
python3 code/experiments/evireview_a/src/evaluate_retrieval_comparison_gold.py
python3 code/experiments/evireview_a/src/render_experiment_dashboard.py
```

OpenRouter embedding retrieval requires `OPENROUTER_API_KEY`. The default free embedding model is
`nvidia/llama-nemotron-embed-vl-1b-v2:free`; override it with `OPENROUTER_EMBEDDING_MODEL`.

GLM-4.6V reviewer generation requires one of `GLM_API_KEY`, `ZHIPU_API_KEY`, `ZHIPUAI_API_KEY`,
`BIGMODEL_API_KEY`, or `ZAI_API_KEY`. The experiment records only the environment-variable name used,
never the secret value. Override the model or endpoint with `GLM_MODEL` and `GLM_ENDPOINT`.
The default `GLM_PAPER_LIMIT` is 10. The script preserves existing generated GLM rows and only calls
the provider for selected papers that do not already have GLM output; if no API key is set, it exits
without overwriting the previous successful sample.

Current retrieval outputs:

- `retrieval_bm25_top5.jsonl`
- `retrieval_tfidf_top5.jsonl`
- `retrieval_hybrid_top5.jsonl`
- `retrieval_section_hybrid_top5.jsonl`
- `retrieval_proxy_eval.json`
- `reports/retrieval_proxy_eval.md`

Annotation and verifier outputs:

- `annotation_sheet_section_hybrid.csv`
- `weakness_evidence_silver.jsonl`
- `verifier_rule_based_predictions.jsonl`
- `reports/verifier_rule_based_report.md`
- `annotation_pilot_batch_60.csv`
- `weakness_evidence_gold.jsonl` after manual labels are filled
- `verification_metrics_rule_based.json` after gold labels exist

External human-annotated benchmark outputs:

- `substanreview_raw/train.jsonl`
- `substanreview_raw/test.jsonl`
- `substanreview_raw/LICENSE`
- `substanreview_train_claims.jsonl`
- `substanreview_test_claims.jsonl`
- `substanreview_baseline_predictions.jsonl`
- `substanreview_baseline_metrics.json`
- `reports/substanreview_experiment_report.md`
- `ready_dataset_candidates.json`
- `reports/ready_dataset_candidates.md`
- `peerreview_bench_expert_annotations.jsonl`
- `peerreview_bench_summary.json`
- `peerreview_bench_baseline_metrics.json`
- `peerreview_bench_baseline_predictions.jsonl`
- `reports/peerreview_bench_baseline_report.md`
- `peerqa_xt_retrieval_metrics.json`
- `peerqa_xt_retrieval_predictions.jsonl`
- `reports/peerqa_xt_retrieval_report.md`

CLAIMCHECK benchmark outputs:

- `claimcheck_raw_manifest.json`
- `claimcheck_summary.json`
- `claimcheck_baseline_metrics.json`
- `claimcheck_retrieval_metrics.json`
- `claimcheck_openrouter_embedding_metrics.json`
- `claimcheck_openrouter_rerank_metrics.json`
- `claimcheck_openrouter_verifier_metrics.json`
- `claimcheck_feature_verifier_metrics.json`
- `claimcheck_evidence_ranker_metrics.json`
- `reports/claimcheck_experiment_report.md`
- `reports/claimcheck_retrieval_report.md`
- `reports/claimcheck_openrouter_embedding_report.md`
- `reports/claimcheck_openrouter_rerank_report.md`
- `reports/claimcheck_openrouter_verifier_report.md`
- `reports/claimcheck_feature_verifier_report.md`
- `reports/claimcheck_evidence_ranker_report.md`
- `local_decision_classifier_metrics.json`
- `reports/local_decision_classifier_report.md`
- `rubric_agent_weaknesses.jsonl`
- `rubric_agent_weaknesses_summary.json`
- `rubric_agent_coverage_metrics.json`
- `rubric_agent_retrieval_top5.jsonl`
- `rubric_agent_retrieval_summary.json`
- `rubric_agent_verified_weaknesses.jsonl`
- `rubric_agent_ranked_top3.jsonl`
- `rubric_agent_verifier_summary.json`
- `reports/rubric_agent_generation_report.md`
- `glm_reviewer_weaknesses.jsonl`
- `glm_reviewer_weaknesses_summary.json`
- `glm_reviewer_coverage_metrics.json`
- `glm_reviewer_retrieval_top5.jsonl`
- `glm_reviewer_verified_weaknesses.jsonl`
- `glm_reviewer_verifier_summary.json`
- `generated_reviewer_comparison_metrics.json`
- `generated_hierarchical_retrieval_top5.jsonl`
- `generated_hierarchical_verified_weaknesses.jsonl`
- `generated_hierarchical_retrieval_summary.json`
- `retrieval_human_hierarchical_top5.jsonl`
- `retrieval_human_hierarchical_summary.json`
- `retrieval_comparison_annotation_queue.jsonl`
- `retrieval_comparison_annotation_queue.csv`
- `retrieval_comparison_annotation_queue_summary.json`
- `retrieval_comparison_gold.jsonl` after comparison labels are filled
- `retrieval_comparison_gold_summary.json`
- `retrieval_comparison_gold_metrics.json`
- `reports/glm_reviewer_experiment_report.md`
- `reports/generated_reviewer_comparison_report.md`
- `reports/hierarchical_paper_rag_report.md`
- `reports/human_hierarchical_retrieval_report.md`
- `reports/retrieval_comparison_annotation_queue.md`
- `reports/retrieval_comparison_gold_report.md`
- `reports/experiment_dashboard.md`

Raw and row-level CLAIMCHECK text files are intentionally ignored because no upstream repository LICENSE file was detected.
OpenRouter embedding caches are also ignored; only aggregate metrics and reports are committed.

The feature verifier intentionally excludes gold-only fields such as target-claim count, annotation confidence,
target-claim text, and human weakness type annotations to avoid label leakage.

## Refactor boundary

`code/experiments/evireview_a` remains the reproducible experiment sandbox. Stable, dependency-free logic is being extracted into `packages/evireview_core` so that future API, worker, and frontend code can reuse the same domain contracts.

Current boundary:

- Keep experiment scripts and existing metrics in this directory.
- Put reusable dataclasses, JSONL helpers, markdown section parsing, BM25 retrieval, hierarchical retrieval, heuristic verification, evidence-aware ranking, and deterministic workflow helpers in `packages/evireview_core`.
- Do not store provider secrets in either location.
- Treat heuristic or model-generated labels as `silver diagnostic` outputs only; do not treat them as human gold labels.

Run the core regression suite from repo root:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest discover -s tests/evireview_core -v
```
