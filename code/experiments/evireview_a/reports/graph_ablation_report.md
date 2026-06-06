# Agent-RAG Graph Ablation

| Profile | Selected | Mean reference support | Reference partial+ | Reference unsupported | Top-K overlap with full |
| --- | ---: | ---: | ---: | ---: | ---: |
| full | 141 | 0.3632 | 0.0355 | 0.0 | 1.0 |
| no_verifier | 141 | 0.3569 | 0.0071 | 0.0 | 0.9362 |
| no_ranker | 141 | 0.3583 | 0.0142 | 0.0 | 0.9078 |

All metrics use the full graph heuristic verifier as a shared silver reference. This is an ablation diagnostic, not human-gold evaluation.
