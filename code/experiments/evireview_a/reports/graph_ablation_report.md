# Agent-RAG Graph Ablation

| Profile | Candidates | Deduplicated | Removed | Reduction | Selected | Mean reference support | Reference partial+ | Reference unsupported | Top-K overlap with full |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full | 194 | 172 | 22 | 0.1134 | 139 | 0.3609 | 0.036 | 0.0 | 1.0 |
| no_dedup | 194 | 194 | 0 | 0.0 | 141 | 0.3632 | 0.0355 | 0.0 | 0.8652 |
| no_verifier | 194 | 172 | 22 | 0.1134 | 139 | 0.3569 | 0.0288 | 0.0 | 0.9424 |
| no_ranker | 194 | 172 | 22 | 0.1134 | 139 | 0.3583 | 0.0216 | 0.0 | 0.9353 |

All metrics use the full graph heuristic verifier as a shared silver reference. This is an ablation diagnostic, not human-gold evaluation.
