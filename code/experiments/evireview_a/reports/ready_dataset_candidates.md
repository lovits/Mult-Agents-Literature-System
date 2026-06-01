# Ready-to-use Dataset Candidates

This report lists external datasets that can support the thesis experiments without creating new manual labels first.

| Dataset | License | Rows / Probe | Best use | Decision |
| --- | --- | ---: | --- | --- |
| [PeerReview Bench](https://huggingface.co/datasets/prometheus-eval/peerreview-bench) | cc-by-4.0 | 3881 | verifier/ranker/review-quality labels: correctness, significance, evidence | A-tier add now |
| [PeerQA-XT](https://huggingface.co/datasets/UKPLab/PeerQA-XT) | cc-by-nc-sa-4.0 | 1252 | Paper-RAG retrieval QA over full scientific papers with peer-review-derived questions | A-tier add next |
| [RottenReviews](https://huggingface.co/datasets/Reviewerly/RottenReviews) | cc-by-4.0 | 177 | review quality dimensions and human quality annotations | B-tier quality/ranker supplement |
| [ReviewBench](https://huggingface.co/datasets/Samarth0710/reviewbench) | cc-by-4.0 | 22532 | multi-conference OpenReview papers, reviews, rebuttals, decisions, markdown | B-tier scaling/generalization |
| [PRISM paper data](https://huggingface.co/datasets/anoyresearcher/prism_paper_data) | other | - | large OpenReview-derived paper/review corpus and PRISM-style review-quality framing | B-tier with license caution |
| [SPECS Review Benchmark](https://huggingface.co/datasets/ut-amrl/SPECS-Review-Benchmark) | cc-by-4.0 | - | controlled injected-flaw detection for reviewer robustness | B-tier robustness experiment |
| [PeerCheck](https://huggingface.co/datasets/TrustAIRLab/PeerCheck) | apache-2.0 | - | human vs LLM review quality and alignment | B-tier reviewer generation comparison |
| [OpenReview Raw](https://huggingface.co/datasets/priorcomputers/openreview_raw) | odc-by | - | large-scale OpenReview review mining and auxiliary classification | C-tier scaling only; very large |

## Recommendation

1. Add PeerReview Bench first because it directly labels review items for correctness, significance, and evidence.
2. Add PeerQA-XT next for Paper-RAG retrieval QA over full scientific papers.
3. Use RottenReviews and ReviewBench as B-version quality/generalization datasets.
4. Keep PRISM/OpenReview Raw as scaling corpora with license and size safeguards.
