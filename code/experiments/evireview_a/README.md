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
```

OpenRouter embedding retrieval requires `OPENROUTER_API_KEY`. The default free embedding model is
`nvidia/llama-nemotron-embed-vl-1b-v2:free`; override it with `OPENROUTER_EMBEDDING_MODEL`.

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

Raw and row-level CLAIMCHECK text files are intentionally ignored because no upstream repository LICENSE file was detected.
OpenRouter embedding caches are also ignored; only aggregate metrics and reports are committed.

The feature verifier intentionally excludes gold-only fields such as target-claim count, annotation confidence,
target-claim text, and human weakness type annotations to avoid label leakage.
