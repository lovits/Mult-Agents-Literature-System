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

## Baselines

| Baseline | Test Accuracy | Test Macro-F1 | Prediction Counts |
| --- | ---: | ---: | --- |
| `majority_train_label` | 0.5634 | 0.3604 | `Unsupported: 552` |
| `transparent_context_cue_v0` | 0.5109 | 0.509 | `Supported: 277, Unsupported: 275` |
| `multinomial_naive_bayes_v0` | 0.6467 | 0.6411 | `Supported: 242, Unsupported: 310` |

- Best test Macro-F1: `multinomial_naive_bayes_v0`.
- Best test gold labels: `Supported: 241, Unsupported: 311`
- `transparent_context_cue_v0` selects its threshold on train Macro-F1.
- `multinomial_naive_bayes_v0` is a no-new-dependency supervised bag-of-words verifier over claim-local review context.

## Best Per-label Test F1

| Label | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| Supported | 0.595 | 0.5975 | 0.5963 | 241 |
| Unsupported | 0.6871 | 0.6849 | 0.686 | 311 |

## Confusion Matrix

- Best baseline confusion: `{'Supported': {'Supported': 144, 'Unsupported': 97}, 'Unsupported': {'Supported': 98, 'Unsupported': 213}}`

## Interpretation

- This is the first valid gold-label verifier check in the project because the labels come from human annotated Eval/Jus span pairs.
- The task is review-internal substantiation detection, not paper-text grounding. It validates the verifier layer's ability to distinguish claims with explicit support from unsupported review assertions.
- The local OpenReview ICLR 2024 sample remains useful for the end-to-end EviReview-Lite pipeline and paper-evidence retrieval, but it should not be presented as human-gold verifier evaluation until annotated.
- CLAIMCHECK is a closer benchmark for paper-claim grounding and should be added next if its released data is directly accessible.
