# EviReview-Lite Dataset Registry

Date: 2026-05-31

This registry records reliable dataset sources for the Agent + RAG paper review evaluation system. The first version uses datasets with public papers, official repositories, dataset cards, or OpenReview provenance.

## Selection Criteria

Datasets are scored against the current thesis objective:

1. Paper text or paper-level metadata is available.
2. Human peer reviews or critique labels are available.
3. Accept/reject, rating, substantiation, or groundedness labels are available.
4. Licensing and redistribution constraints are clear enough for reproducible thesis work.
5. The dataset directly supports at least one EviReview module: retrieval, verifier, ranker, reviewer generation, or auxiliary classification.

## Recommended Dataset Tiers

| Tier | Dataset | Source | Best Use | Decision |
| --- | --- | --- | --- | --- |
| A | Local PRISM/OpenReview ICLR 2024 sample | Existing local dataset derived from OpenReview | End-to-end system workflow, section-aware Paper-RAG, final demo | Keep as local application dataset |
| A | SubstanReview | https://github.com/YanzhuGuo/SubstanReview and https://aclanthology.org/2023.findings-emnlp.684/ | Supervised substantiation baseline | Keep as verifier floor |
| A | CLAIMCHECK | https://arxiv.org/abs/2503.21717 and https://aclanthology.org/2025.findings-emnlp.1185/ | Paper-grounded critique retrieval, verifier, ranker diagnostics | Keep, but commit only aggregate metrics until license is clarified |
| B | PeerRead | https://github.com/allenai/PeerRead and https://arxiv.org/abs/1804.09635 | Auxiliary accept/reject and score prediction baseline | Add only if A-version classification needs expansion |
| B | NLPeer | https://arxiv.org/abs/2211.06651 and https://aclanthology.org/2023.acl-long.277/ | Multi-venue review reports, guided skimming, structured peer-review study | Candidate for B-version generalization |
| B | OpenReview Raw | https://huggingface.co/datasets/priorcomputers/openreview_raw and https://docs.openreview.net/ | Larger-scale OpenReview mining | Use for scaling after A-version pipeline is stable |
| C | PRISM benchmark | https://arxiv.org/abs/2605.26730 | Multi-dimensional review-quality evaluation | Monitor for data/code release; use as related work now |
| C | LLM-as-a-Reviewer benchmark | https://arxiv.org/abs/2605.25415 | Rating calibration, divergence, prompt-injection robustness | Monitor for data/code release; use robustness framing now |
| C | SoundnessBench | https://arxiv.org/abs/2605.30329 | Methodological soundness judging | Monitor for data/code release; use as soundness motivation now |

## Current Experimental Mapping

| Experiment Module | Primary Dataset | Secondary Dataset | Notes |
| --- | --- | --- | --- |
| Paper-RAG retrieval | Local PRISM/OpenReview sample | CLAIMCHECK | Local data tests evidence-block retrieval; CLAIMCHECK tests claim association. |
| Evidence verifier | CLAIMCHECK | SubstanReview | CLAIMCHECK is paper-grounded; SubstanReview is review-internal substantiation. |
| Evidence-aware ranker | CLAIMCHECK | Local silver labels | Use CLAIMCHECK for aggregate ranker diagnostics; local labels remain pipeline debugging until human gold labels exist. |
| Review generation | Local PRISM/OpenReview sample | NLPeer | Do after verifier/ranker are stable. |
| Accept/reject classification | Local PRISM/OpenReview sample | PeerRead | Keep as auxiliary, not main contribution. |
| Robustness / prompt injection | LLM-as-a-Reviewer benchmark | Local adversarial PDF/text cases | Add after system demo exists. |

## Implementation Policy

- Commit licensed datasets only when the license allows redistribution.
- For datasets without clear redistribution terms, commit scripts, manifests, aggregate metrics, and reports only.
- Keep raw PDFs and raw row-level text out of git unless license and size policy are both clear.
- Prefer small, reproducible A-version diagnostics over broad, expensive scraping.
- Use OpenRouter free models only for bounded inference experiments; rate limits make them unsuitable as the only path to completion.
