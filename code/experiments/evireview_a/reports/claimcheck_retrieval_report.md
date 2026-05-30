# CLAIMCHECK Claim Retrieval Experiment

This report evaluates dependency-free retrieval baselines for mapping reviewer weaknesses to source-paper claims.

## Setup

- Dataset: CLAIMCHECK
- Task: weakness-to-paper-claim retrieval
- Gold definition: Target claims are mapped back to extracted candidate claims by token cosine >= 0.7 before ranking evaluation.
- License note: Raw CLAIMCHECK text and row-level rankings are not committed because no upstream repository LICENSE was detected.

## Main Split Results

| Method | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR | Mapped / Grounded |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lexical_token_overlap` | 0.1944 | 0.3194 | 0.4306 | 0.5417 | 0.3106 | 72 / 108 |
| `char_trigram_overlap` | 0.1667 | 0.375 | 0.5139 | 0.6806 | 0.334 | 72 / 108 |
| `tfidf_cosine` | 0.2083 | 0.3472 | 0.4167 | 0.5694 | 0.3301 | 72 / 108 |
| `bm25` | 0.1806 | 0.3611 | 0.4167 | 0.5833 | 0.3135 | 72 / 108 |
| `hybrid_equal_weight` | 0.2083 | 0.3472 | 0.4583 | 0.5556 | 0.333 | 72 / 108 |

## Interpretation

- Best main Hit@3: `char_trigram_overlap` at 0.375.
- Character trigram overlap improves top-k coverage over plain token overlap, suggesting that surface-form variation and partial phrase matching matter.
- The absolute scores remain low for a paper-grounding task, so the next experiment should introduce embedding retrieval or an LLM reranker.
- These results strengthen the thesis argument that simple lexical matching is an insufficient verifier backend for grounded peer-review critique.
