# EviReview-Lite A Version Experiments

This experiment directory implements the first reproducible pass of the EviReview-Lite thesis plan.

Main dataset:

`code/dataset/prism_iclr2024_sample`

Human-annotated verifier benchmark:

`SubstanReview` from `https://github.com/YanzhuGuo/SubstanReview`

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
```

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
