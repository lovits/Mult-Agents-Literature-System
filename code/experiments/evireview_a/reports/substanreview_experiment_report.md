# SubstanReview Human-Annotated Verifier Benchmark

This experiment uses an existing human-annotated peer-review dataset before relying on local silver labels or new manual annotation.

## Dataset

- Source repository: https://github.com/YanzhuGuo/SubstanReview
- Paper: https://aclanthology.org/2023.findings-emnlp.684/
- Upstream license: Apache-2.0, saved at `data/substanreview_raw/LICENSE`.
- Gold definition: Eval spans with a same-index Jus span are Supported; Eval spans without a paired Jus span are Unsupported.
- Train: 440 reviews, 2225 Eval spans.
- Test: 110 reviews, 552 Eval spans.
- Overall label counts: `Supported: 1232, Unsupported: 1545`

## Baseline

- Verifier: `transparent_context_cue_v0`
- Threshold selection: maximize train Macro-F1 over thresholds 0.20..0.90
- Train Macro-F1: 0.5382 at threshold 0.78
- Test Accuracy: 0.5109
- Test Macro-F1: 0.509
- Test gold labels: `Supported: 241, Unsupported: 311`
- Test predictions: `Supported: 277, Unsupported: 275`

## Per-label Test F1

| Label | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| Supported | 0.4477 | 0.5145 | 0.4788 | 241 |
| Unsupported | 0.5745 | 0.508 | 0.5392 | 311 |

## Interpretation

- This is the first valid gold-label verifier check in the project because the labels come from human annotated Eval/Jus span pairs.
- The task is review-internal substantiation detection, not paper-text grounding. It validates the verifier layer's ability to distinguish claims with explicit support from unsupported review assertions.
- The local OpenReview ICLR 2024 sample remains useful for the end-to-end EviReview-Lite pipeline and paper-evidence retrieval, but it should not be presented as human-gold verifier evaluation until annotated.
- CLAIMCHECK is a closer benchmark for paper-claim grounding and should be added next if its released data is directly accessible.
