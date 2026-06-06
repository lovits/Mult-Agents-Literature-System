from __future__ import annotations

import json

from common import DATA_DIR


def main() -> None:
    path = DATA_DIR / "dense_hybrid_retrieval_metrics.json"
    if not path.exists():
        raise SystemExit("dense_hybrid_retrieval_metrics.json missing")
    payload = json.loads(path.read_text(encoding="utf-8"))
    methods = payload.get("methods", {})
    required = {"bm25_sparse", "openrouter_dense", "bm25_openrouter_rrf_hybrid"}
    if set(methods) != required:
        raise SystemExit(f"method set mismatch: {sorted(methods)}")
    for name in required:
        for split in ("pilot", "main"):
            metrics = methods[name].get(split, {})
            for metric in ("hit_at_1", "hit_at_3", "hit_at_5", "hit_at_10", "mrr"):
                value = metrics.get(metric)
                if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                    raise SystemExit(f"invalid {name}.{split}.{metric}: {value}")
    print("dense/hybrid retrieval validator passed")


if __name__ == "__main__":
    main()
