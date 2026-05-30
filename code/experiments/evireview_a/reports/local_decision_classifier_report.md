# Local OpenReview Accept/Reject Classifier

This report evaluates whether metadata, weakness, and evidence-verification proxy features contain signal for the final OpenReview decision.

## Setup

- Status: `ok`
- Dataset: Local PRISM/OpenReview ICLR 2024 sample
- Validation: 5-fold stratified cross-validation over 50 papers, with balanced Accept/Reject folds.
- Papers: 50
- Decision counts: {'Reject': 25, 'Accept': 25}
- Silver feature coverage: 30 papers
- Warning: Exploratory only: human weakness features are an upper-bound proxy, and silver evidence labels are rule-generated debugging labels, not final human gold.

## Results

| Method | Features | Accuracy | Macro-F1 | ROC-AUC | Accept F1 | Reject F1 | Fold Macro-F1 mean +/- std |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Majority baseline | 0 | 0.5 | 0.4505 | 0.5 | 0.2857 | 0.6154 | 0.3333 +/- 0.0 |
| Metadata baseline | 7 | 0.68 | 0.68 | 0.6896 | 0.68 | 0.68 | 0.6755 +/- 0.0783 |
| Human weakness upper-bound | 11 | 0.62 | 0.6198 | 0.6512 | 0.6275 | 0.6122 | 0.5822 +/- 0.1983 |
| Silver evidence proxy | 9 | 0.44 | 0.4253 | 0.448 | 0.3333 | 0.5172 | 0.3884 +/- 0.1298 |
| Metadata + human weakness | 18 | 0.64 | 0.64 | 0.6736 | 0.64 | 0.64 | 0.6318 +/- 0.1492 |
| Metadata + silver evidence | 16 | 0.6 | 0.5994 | 0.6704 | 0.5833 | 0.6154 | 0.5968 +/- 0.0904 |
| Fusion proxy | 27 | 0.58 | 0.5785 | 0.6496 | 0.5532 | 0.6038 | 0.5625 +/- 0.1435 |

## Interpretation

- Best method in this exploratory diagnostic: Metadata baseline with Macro-F1 0.68 and ROC-AUC 0.6896.
- This is not a final classifier result because human-review weakness features are upper-bound proxies and silver evidence labels are rule-generated.
- The experiment is useful for the thesis because it tests whether evidence-aware features carry decision-related signal before investing in agent-generated weakness classification.
